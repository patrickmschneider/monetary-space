"""The r* suite: several estimators of the UK neutral real rate, combined into a headline and a
range, following reports/UK neutral rate estimation methods.md.

Estimators                                       role            headline weight
  1. Trend-cycle model (Del Negro et al.-style)   long-run        0.40  (anchor)
  2. Repaired HLW-style model                     policy horizon  0.25  (dropped if the IS slope is at its bound)
  3. Market Participants Survey neutral − 2%      policy horizon  0.35
  4. Index-linked gilt 5y5y real forward          long-run        0     (includes term and liquidity premia)
  5. 10-year average of the ex-ante real Bank Rate  benchmark     0

Combination: weighted mean of the available core estimators (1–3), excluding any more than
1.5pp from their median, rounded to 0.25pp; the range spans the core estimates, rounded
outward to 0.25pp and at least 0.5pp wide. Also writes a potential-growth series for the
GDP benchmark (MaPS long-run potential growth, spliced onto a 10-year trailing average).

Output: analysis/results/rstar_suite.json.  Run after releases:  python analysis/rstar_suite.py
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monetary_space import rstar, trend_cycle  # noqa: E402
from monetary_space.fetch import boe, ons  # noqa: E402
from monetary_space.fetch.http import session  # noqa: E402

OUT = ROOT / "analysis" / "results"
WEIGHTS = {"trend_cycle": 0.40, "hlw": 0.25, "maps": 0.35}
MAPS_PAGE = "https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/{y}market-participants-survey-results-{m}-{yy}"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september",
          "october", "november", "december"]


def round_to(x: float, step: float = 0.25, how: str = "nearest") -> float:
    f = {"nearest": np.round, "down": np.floor, "up": np.ceil}[how]
    return float(f(x / step) * step)


# ------------------------------------------------------------------ data
def maps_history(start_year: int = 2022) -> pd.DataFrame:
    """Neutral Bank Rate and long-run potential growth from each MaPS round (HTML tables)."""
    s = session()
    rows, today = [], dt.date.today()
    for y in range(start_year, today.year + 1):
        for mi, m in enumerate(MONTHS, start=1):
            if (y, mi) > (today.year, today.month):
                break
            text = None
            for prefix in (f"{y}/", ""):
                r = s.get(MAPS_PAGE.format(y=prefix, m=m, yy=y), timeout=30, allow_redirects=False)
                if r.status_code == 200 and "neither expansionary nor contractionary" in r.text:
                    text = r.text
                    break
                time.sleep(0.2)
            if text is None:
                continue
            t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))
            row = {"round": f"{y}-{mi:02d}"}
            q = re.search(r"neither expansionary nor contractionary.*?Number of responses\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)", t)
            if q:
                row.update(neutral_p25=float(q[1]), neutral=float(q[2]), neutral_p75=float(q[3]), neutral_n=int(q[4]))
            g = re.search(r"Long run \(potential\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)", t)
            if g:
                row.update(potential=float(g[2]))
            if len(row) > 1:
                rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("no MaPS rounds found")
    df.index = pd.PeriodIndex(df.pop("round"), freq="M")
    return df


def load() -> dict:
    m = lambda cdid, ds="mm23", topic="economy/inflationandpriceindices": ons.timeseries(f"/{topic}/timeseries/{cdid}/{ds}", "M")
    q = rstar.quarterly_mean
    d = {
        "gdp": ons.timeseries("/economy/grossdomesticproductgdp/timeseries/abmi/qna", "Q"),
        "core_idx": m("dkc6"), "cpi_yy": m("d7g7"),
        "bank": boe.iadb("IUDBEDR", "01/Jan/1990"),
        "yn10": boe.iadb("IUDMNZC", "01/Jan/1990"), "yr10": boe.iadb("IUDMRZC", "01/Jan/1990"),
        "yr5": boe.iadb("IUDSRZC", "01/Jan/1990"),
        "ias": boe.ias_median_1y(),
    }
    d["q"] = q
    return d


# ------------------------------------------------------------------ estimators
def run_trend_cycle(d: dict, sd_r: float = 0.05, sd_pi: float = 0.0707) -> trend_cycle.Estimate:
    q = d["q"]
    cpi = d["cpi_yy"]
    df = pd.DataFrame({"R": q(d["bank"]), "pi": cpi.groupby(cpi.index.asfreq("Q")).mean(),
                       "yn": q(d["yn10"]), "yr": q(d["yr10"])})
    df = df[df.index >= pd.Period("1993Q1", "Q")].dropna(how="all")
    return trend_cycle.estimate(df, sd_r, sd_pi)


def run_hlw(d: dict) -> rstar.Estimate:
    spec = {"start": "1993Q1", "exclude": [], "deflator": "household"}
    y, pi, r, idx = rstar.build_inputs(d["gdp"], d["core_idx"], d["bank"], spec, d["ias"])
    est = rstar.estimate(y, pi, r, lam_g=0.05, lam_z=0.0, ar=None)
    return est


def market_forward(d: dict) -> pd.Series:
    """Real 5y5y forward from index-linked gilt spot rates (continuous compounding)."""
    f = (10 * d["yr10"] - 5 * d["yr5"]) / 5
    return d["q"](f)


def real_rate_ma(d: dict) -> pd.Series:
    """10-year trailing average of Bank Rate minus households' re-centred 1-year expectations."""
    q = d["q"]
    core = rstar.quarterly_mean(rstar.seasonally_adjust(d["core_idx"]))
    pi = ((core / core.shift(1)) ** 4 - 1) * 100
    real = q(d["bank"]) - rstar.expected_inflation(pi, d["ias"])
    return real.rolling(40).mean().dropna()


def potential_growth(d: dict, maps: pd.DataFrame | None) -> pd.Series:
    """Quarterly potential growth, % a year: MaPS long-run potential median where published,
    else a 10-year trailing mean of GDP growth excluding 2020–21."""
    g = d["gdp"]
    yy = (g / g.shift(4) - 1) * 100
    yy[(yy.index >= pd.Period("2020Q1", "Q")) & (yy.index <= pd.Period("2021Q4", "Q"))] = np.nan
    trailing = yy.rolling(40, min_periods=24).mean()
    if maps is not None and "potential" in maps:
        mp = maps["potential"].dropna()
        mp = mp.groupby(mp.index.asfreq("Q")).last()
        idx = trailing.index.union(mp.index)
        trailing = mp.reindex(idx).ffill().combine_first(trailing.reindex(idx))
    return trailing.dropna()


# ------------------------------------------------------------------ combine
def main() -> None:
    d = load()
    tc = run_trend_cycle(d)
    tc_loose = run_trend_cycle(d, 0.10, 0.1414)
    hlw = run_hlw(d)
    try:
        maps = maps_history()
    except Exception as e:  # noqa: BLE001
        print("MaPS unavailable:", e)
        maps = None
    fwd = market_forward(d)
    ma = real_rate_ma(d)

    est = {
        "trend_cycle": {"name": "Trend-cycle model", "role": "long-run", "value": float(tc.r_bar.iloc[-1]),
                        "se": float(tc.se.iloc[-1]), "date": str(tc.r_bar.index[-1]),
                        "basis": "Del Negro et al.-style: common trends in Bank Rate, CPI inflation and 10-year nominal and real gilt yields",
                        "status": "ok"},
        "hlw": {"name": "HLW-style model (repaired)", "role": "policy horizon", "value": float(hlw.r_star.iloc[-1]),
                "se": float(hlw.se.iloc[-1]), "date": str(hlw.r_star.index[-1]),
                "basis": f"IS/Phillips curves; λz = 0 (Buncic 2022), COVID and lower-bound variance scaling; IS slope {hlw.params.ar:.3f}",
                "status": "excluded: IS slope at its bound, so r* is not identified (as the NY Fed found for the UK)"
                if hlw.ar_at_bound else "ok"},
        "maps": None,
        "market_5y5y": {"name": "Index-linked gilt 5y5y real forward", "role": "long-run", "value": float(fwd.iloc[-1]),
                        "date": str(fwd.index[-1]), "basis": "Bank of England real spot curve; includes term and liquidity premia, CPIH basis after 2030",
                        "status": "shown, not weighted (term premia)"},
        "real_rate_ma": {"name": "10-year average real Bank Rate", "role": "benchmark", "value": float(ma.iloc[-1]),
                         "date": str(ma.index[-1]), "basis": "Bank Rate minus households' 1-year expectations (re-centred), trailing 40 quarters",
                         "status": "shown, not weighted (benchmark)"},
    }
    if maps is not None and "neutral" in maps:
        last = maps["neutral"].dropna()
        est["maps"] = {"name": "Market Participants Survey", "role": "policy horizon", "value": float(last.iloc[-1] - 2.0),
                       "p25": float(maps["neutral_p25"].dropna().iloc[-1] - 2), "p75": float(maps["neutral_p75"].dropna().iloc[-1] - 2),
                       "date": str(last.index[-1]), "basis": "median perceived neutral Bank Rate minus the 2% target",
                       "status": "ok"}
    core = {k: v for k, v in est.items() if k in WEIGHTS and v and v["status"] == "ok"}
    med = float(np.median([v["value"] for v in core.values()]))
    for k, v in list(core.items()):
        if abs(v["value"] - med) > 1.5:
            est[k]["status"] = f"excluded: more than 1.5pp from the median of core estimates ({med:.2f}%)"
            core.pop(k)
    w = {k: WEIGHTS[k] for k in core}
    tot = sum(w.values())
    headline = sum(w[k] / tot * core[k]["value"] for k in core)
    lo, hi = min(v["value"] for v in core.values()), max(v["value"] for v in core.values())
    lo, hi = round_to(lo, how="down"), round_to(hi, how="up")
    head_r = round_to(headline)
    if hi - lo < 0.5:
        lo, hi = min(lo, head_r - 0.25), max(hi, head_r + 0.25)
    for k in est:
        if est[k]:
            est[k]["weight"] = round(w.get(k, 0) / tot, 3) if k in w else 0.0

    # Headline history: trend-cycle r̄, blended with MaPS (real) where available, same weights.
    hist = tc.r_bar.copy()
    if est.get("maps") and est["maps"]["status"] == "ok":
        mq = (maps["neutral"].dropna() - 2.0)
        mq = mq.groupby(mq.index.asfreq("Q")).last().reindex(hist.index).ffill()
        wm = w.get("maps", 0) / (w.get("maps", 0) + w.get("trend_cycle", 0)) if "trend_cycle" in w else 1.0
        hist = hist.where(mq.isna(), (1 - wm) * hist + wm * mq)

    pg = potential_growth(d, maps)
    out = {
        "method": "Suite of r* estimators, weighted (trend-cycle 0.40, HLW 0.25, MaPS 0.35) over those that pass "
                  "diagnostics; range spans the core estimates. See reports/UK neutral rate estimation methods.md.",
        "headline": round(headline, 3), "headline_rounded": head_r, "range": [lo, hi],
        "nominal_headline": head_r + 2.0, "nominal_range": [lo + 2.0, hi + 2.0],
        "estimators": est,
        "history": {
            "headline": {str(k): round(float(v), 3) for k, v in hist.items()},
            "trend_cycle": {str(k): [round(float(v), 3), round(float(s), 3)] for k, v, s in zip(tc.r_bar.index, tc.r_bar, tc.se)},
            "trend_cycle_loose_prior": {str(k): round(float(v), 3) for k, v in tc_loose.r_bar.items()},
            "hlw": {str(k): round(float(v), 3) for k, v in hlw.r_star.items()},
            "market_5y5y": {str(k): round(float(v), 3) for k, v in fwd[fwd.index >= pd.Period("2000Q1", "Q")].items()},
            "real_rate_ma": {str(k): round(float(v), 3) for k, v in ma.items()},
            "maps": ({str(k): round(float(v) - 2, 3) for k, v in maps["neutral"].dropna().items()} if maps is not None else {}),
        },
        "potential_growth": {str(k): round(float(v), 3) for k, v in pg.items()},
        "trend_cycle_params": {k: (v if not isinstance(v, (np.floating, float)) else round(float(v), 3)) for k, v in tc.params.items()},
        "hlw_params": {k: round(float(v), 4) for k, v in hlw.params.__dict__.items()},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rstar_suite.json").write_text(json.dumps(out, indent=1, default=str))
    print(f"Headline r* {headline:.2f}% → {head_r:.2f}% (range {lo:.2f}–{hi:.2f}; nominal {head_r + 2:.2f}%, {lo + 2:.2f}–{hi + 2:.2f})")
    for k, v in est.items():
        if v:
            print(f"  {v['name']:40} {v['value']:6.2f}%  {v['date']:8} weight {v['weight']:.2f}  {v['status']}")
    print(f"  trend-cycle, looser prior: {tc_loose.r_bar.iloc[-1]:.2f}%; potential growth latest {pg.iloc[-1]:.2f}% ({pg.index[-1]})")


if __name__ == "__main__":
    if not os.environ.get("FRED_API_KEY") and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    main()
