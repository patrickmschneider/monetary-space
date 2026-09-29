"""A UK Bernanke–Blanchard (2023) wage–price model, as recommended in the literature review.

Quarterly, annualised growth rates (%). Four equations, four lags, homogeneity imposed
(the coefficients on the nominal terms sum to one), dummies for 2020Q2–2021Q2:

  wages      gw = Σ gw₋ᵢ + Σ cf1₋ᵢ + Σ vu₋ᵢ + Σ catchup₋ᵢ + trend productivity
  prices     gp = Σ gp₋ᵢ + Σ gw₋ᵢ (i=0..4) + Σ (energy − gw)₋ᵢ + Σ (food − gw)₋ᵢ − trend productivity
  short-run expectations  cf1 = Σ cf1₋ᵢ + Σ cf10₋ᵢ + Σ gp₋ᵢ
  long-run expectations   cf10 = Σ cf10₋ᵢ + Σ gp₋ᵢ

Data (free): CPI and food CPI (ONS, stable-seasonally adjusted), energy CPI derived from
CPI and CPI excluding energy with ONS energy weights, whole-economy regular pay (AWE),
vacancies/unemployed (ONS), household 1-year expectations (BoE IAS), 5y5y inflation
forward from BoE spot inflation curves, trend productivity (5-year mean of output per hour).
The shortage index BB use is omitted: the UK application found it small.

Outputs analysis/results/bb_uk.json: coefficients, long-run multipliers, contributions to
CPI inflation since 2019Q4 (energy, food, labour-market tightness, expectations, other),
and 'estimated weights' for the dashboard's Phillips-curve blocks.
Run after releases:  python analysis/bb_uk.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monetary_space.fetch import boe, ons  # noqa: E402
from monetary_space.rstar import quarterly_mean, seasonally_adjust  # noqa: E402

OUT = ROOT / "analysis" / "results"
P = 4
DUMMIES = ["2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2"]
T = lambda cdid, ds="mm23", topic="economy/inflationandpriceindices": f"/{topic}/timeseries/{cdid}/{ds}"


def ann(q: pd.Series) -> pd.Series:
    return ((q / q.shift(1)) ** 4 - 1) * 100


def load() -> pd.DataFrame:
    cpi = seasonally_adjust(ons.timeseries(T("d7bt"), "M"))
    xen = seasonally_adjust(ons.timeseries(T("dkc5"), "M"))
    food = seasonally_adjust(ons.timeseries(T("d7bu"), "M"))
    pay = ons.timeseries(T("kai7", "lms", "employmentandlabourmarket/peopleinwork/earningsandworkinghours"), "M")
    v = ons.timeseries(T("ap2y", "lms", "employmentandlabourmarket/peopleinwork/employmentandemployeetypes"), "M")
    un = ons.timeseries(T("mgsc", "lms", "employmentandlabourmarket/peoplenotinwork/unemployment"), "M")
    lz = ons.timeseries(T("lzvb", "prdy", "employmentandlabourmarket/peopleinwork/labourproductivity"), "Q")
    ias = boe.ias_median_1y()
    s5, s10 = boe.iadb("IUDSIZC", "01/Jan/1995"), boe.iadb("IUDMIZC", "01/Jan/1995")
    f55 = (10 * s10 - 5 * s5) / 5

    gp, gx, gf = ann(quarterly_mean(cpi)), ann(quarterly_mean(xen)), ann(quarterly_mean(food))
    wen = energy_weight()
    wq = pd.Series(wen.reindex(gp.index.year).to_numpy(), index=gp.index)
    ge = (gp - (1 - wq) * gx) / wq                       # energy CPI inflation implied by the aggregates
    df = pd.DataFrame({
        "gp": gp, "gen": ge, "gf": gf, "gw": ann(quarterly_mean(pay)),
        "vu": quarterly_mean(v / un), "cf1": ias, "cf10": quarterly_mean(f55),
        "gpty": ((lz / lz.shift(4)) - 1).mul(100).rolling(20).mean(),
    })
    df["rpe"], df["rpf"] = df["gen"] - df.gw, df.gf - df.gw
    df["catchup"] = df.gp - df.cf1
    df["cf1"] = df["cf1"].ffill(limit=1)
    df["gpty"] = df["gpty"].ffill()
    return df


def energy_weight() -> pd.Series:
    """ONS CPI weight of energy (parts per thousand → share), by year."""
    from monetary_space.fetch.http import get
    j = get("https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/a9f3/mm23/data").json()
    s = pd.Series({int(r["date"]): float(r["value"]) / 1000 for r in j["years"] if r["value"]})
    return s.reindex(range(1988, 2031)).ffill().bfill()


def lags(s: pd.Series, first: int, last: int, name: str) -> pd.DataFrame:
    return pd.DataFrame({f"{name}_{i}": s.shift(i) for i in range(first, last + 1)})


def constrained_ols(y: pd.Series, homog: pd.DataFrame, free: pd.DataFrame):
    """y = homog·a + free·b + e with Σa = 1: subtract the last homogeneity regressor."""
    ref = homog.columns[-1]
    Y = y - homog[ref]
    Xh = homog.drop(columns=ref).sub(homog[ref], axis=0)
    X = pd.concat([Xh, free], axis=1)
    data = pd.concat([Y.rename("y"), X], axis=1).dropna()
    b, *_ = np.linalg.lstsq(data.drop(columns="y").to_numpy(), data["y"].to_numpy(), rcond=None)
    coef = pd.Series(b, index=X.columns)
    coef[ref] = 1 - coef[Xh.columns].sum()
    resid = data["y"] - data.drop(columns="y").to_numpy() @ b
    r2 = 1 - resid.var() / (data["y"] + homog[ref].reindex(data.index)).var()
    return coef, resid, len(data), r2


def dummies(idx) -> pd.DataFrame:
    return pd.DataFrame({f"d{q}": (idx == pd.Period(q, "Q")).astype(float) for q in DUMMIES}, index=idx)


def estimate(df: pd.DataFrame, start="2001Q3"):
    d = df[df.index >= pd.Period(start, "Q")].copy()
    full = df
    D = dummies(full.index)
    eq = {}
    eq["gw"] = constrained_ols(
        full.gw, pd.concat([lags(full.gw, 1, P, "gw"), lags(full.cf1, 1, P, "cf1")], axis=1),
        pd.concat([lags(full.vu, 1, P, "vu"), lags(full.catchup, 1, P, "catchup"), full.gpty.shift(1).rename("gpty_1"),
                   pd.Series(1.0, index=full.index, name="const"), D], axis=1).loc[d.index])
    eq["gp"] = constrained_ols(
        full.gp, pd.concat([lags(full.gp, 1, P, "gp"), lags(full.gw, 0, P, "gw")], axis=1),
        pd.concat([lags(full.rpe, 0, P, "rpe"), lags(full.rpf, 0, P, "rpf"), full.gpty.shift(1).rename("gpty_1"),
                   pd.Series(1.0, index=full.index, name="const"), D], axis=1).loc[d.index])
    eq["cf1"] = constrained_ols(
        full.cf1, pd.concat([lags(full.cf1, 1, P, "cf1"), lags(full.cf10, 1, P, "cf10"), lags(full.gp, 1, P, "gp")], axis=1),
        pd.DataFrame({"const": 1.0}, index=full.index).loc[d.index])
    eq["cf10"] = constrained_ols(
        full.cf10, pd.concat([lags(full.cf10, 1, P, "cf10"), lags(full.gp, 1, P, "gp")], axis=1),
        pd.DataFrame({"const": 1.0}, index=full.index).loc[d.index])
    return {k: {"coef": v[0], "resid": v[1], "n": v[2], "r2": v[3]} for k, v in eq.items()}


def simulate(df: pd.DataFrame, eqs: dict, start: str, overrides: dict[str, pd.Series] | None = None,
             shocks: bool = True) -> pd.DataFrame:
    """Dynamic simulation from `start`, feeding the model's own lagged values; exogenous
    series (rpe, rpf, vu, gpty, dummies) come from data or `overrides`. With shocks=True
    the equation residuals are added back, so the baseline reproduces the data."""
    s = df.copy()
    for k, v in (overrides or {}).items():
        s.loc[v.index, k] = v
    idx = s.index[s.index >= pd.Period(start, "Q")]
    D = dummies(s.index)
    for t in idx:
        i = s.index.get_loc(t)
        def val(name, lag):
            return s[name].iloc[i - lag]
        for var in ("cf10", "cf1", "gw", "gp"):
            c = eqs[var]["coef"]
            x = 0.0
            for key, b in c.items():
                if key == "const":
                    x += b
                elif key.startswith("d") and key[1:] in DUMMIES:
                    x += b * D.loc[t, key]
                elif key == "gpty_1":
                    x += b * val("gpty", 1)
                else:
                    name, lag = key.rsplit("_", 1)
                    x += b * val(name, int(lag))
            if shocks and t in eqs[var]["resid"].index:
                x += eqs[var]["resid"][t]
            s.loc[t, var] = x
            if var == "gp":
                s.loc[t, "catchup"] = s.loc[t, "gp"] - s.loc[t, "cf1"]
            if var == "gw":
                s.loc[t, "rpe"] = s.loc[t, "gen"] - x if "rpe" not in (overrides or {}) else s.loc[t, "rpe"]
                s.loc[t, "rpf"] = s.loc[t, "gf"] - x if "rpf" not in (overrides or {}) else s.loc[t, "rpf"]
    return s


def main() -> None:
    df = load()
    eqs = estimate(df)
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"sample": f"2001Q3–{df.dropna(subset=['gp','gw','vu','cf1']).index[-1]}", "equations": {}}
    for k, e in eqs.items():
        c = e["coef"]
        groups = {}
        for key, b in c.items():
            g = key.rsplit("_", 1)[0] if "_" in key and not key.startswith("d20") else key
            groups[g] = groups.get(g, 0) + b
        res["equations"][k] = {"n": e["n"], "r2": round(e["r2"], 3), "sums": {g: round(v, 3) for g, v in groups.items()}}
        print(f"{k:5} n={e['n']} R²={e['r2']:.2f}  " + "  ".join(f"{g}={v:+.3f}" for g, v in groups.items() if not g.startswith("d20")))

    # Contributions to CPI inflation since 2019Q4 (BB-style counterfactuals, with residuals)
    start = "2020Q1"
    base = simulate(df, eqs, start)
    idx = base.index[base.index >= pd.Period(start, "Q")]
    cf = {
        "energy": {"rpe": pd.Series(0.0, index=idx)},
        "food": {"rpf": pd.Series(0.0, index=idx)},
        "labour_market": {"vu": pd.Series(df.vu[pd.Period("2019Q4", "Q")], index=idx)},
    }
    contrib = {}
    for name, ov in cf.items():
        alt = simulate(df, eqs, start, ov)
        contrib[name] = (base.gp - alt.gp).loc[idx]
    # Expectations: hold both expectation equations' shocks at zero
    eqs_noexp = {k: (dict(v, resid=v["resid"] * 0) if k in ("cf1", "cf10") else v) for k, v in eqs.items()}
    contrib["expectations_shocks"] = (base.gp - simulate(df, eqs_noexp, start).gp).loc[idx]
    contrib["actual"] = df.gp.loc[idx]
    c = pd.DataFrame(contrib)
    c4 = c.rolling(4).mean().dropna()
    res["contributions_4q_avg"] = {str(k): {kk: round(vv, 2) for kk, vv in r.items()} for k, r in c4.iterrows()}
    print("\nContributions to CPI inflation (4-quarter average, pp), vs a 2019Q4 labour market and no relative energy/food growth:")
    print(c4.iloc[::2].round(2).to_string())

    # Long-run responses (steady state) to a permanent 1-SD move in each driver → estimated block weights
    sd = {"vu": df.vu[:"2019Q4"].std(), "rpe": df.rpe[:"2019Q4"].std(), "rpf": df.rpf[:"2019Q4"].std(),
          "cf1": df.cf1[:"2019Q4"].std(), "gpty": df.gpty[:"2019Q4"].std()}
    horizon = pd.period_range("2010Q1", periods=16, freq="Q")
    windows = {"year_1": horizon[:4], "year_2": horizon[4:8], "year_3": horizon[8:12], "policy_horizon_2_3y": horizon[4:12]}
    calm = df.copy()
    calm.loc[:, ["gp", "gw", "cf1", "cf10"]] = 2.0
    calm["rpe"], calm["rpf"], calm["vu"], calm["gpty"] = 0.0, 0.0, df.vu[:"2019Q4"].mean(), 1.0
    calm["gen"], calm["gf"] = 2.0, 2.0
    base_c = simulate(calm, eqs, str(horizon[0]), shocks=False)
    effects = {}
    for drv, ov in {"slack_demand": {"vu": calm.vu.loc[horizon] + sd["vu"]},
                    "slack_supply": {"gpty": calm.gpty.loc[horizon] - sd["gpty"]},
                    "energy": {"rpe": pd.Series(sd["rpe"], index=horizon[:4])},
                    "food": {"rpf": pd.Series(sd["rpf"], index=horizon[:4])},
                    "cost_push": {"rpe": pd.Series(sd["rpe"], index=horizon[:4]),
                                  "rpf": pd.Series(sd["rpf"], index=horizon[:4])}}.items():
        alt = simulate(calm, eqs, str(horizon[0]), ov, shocks=False)
        effects[drv] = {w: float((alt.gp - base_c.gp).loc[q].mean()) for w, q in windows.items()}
    # expectations: permanent 1-SD shift in cf1 (exogenous)
    eqs_x = {k: v for k, v in eqs.items()}
    alt = calm.copy()
    alt.loc[horizon, "cf1"] = 2.0 + sd["cf1"]
    eqs_fix = dict(eqs)
    eqs_fix["cf1"] = {"coef": pd.Series({"const": 2.0 + sd["cf1"]}), "resid": pd.Series(dtype=float)}
    alt_s = simulate(calm, eqs_fix, str(horizon[0]), shocks=False)
    effects["expectations"] = {w: float((alt_s.gp - base_c.gp).loc[q].mean()) for w, q in windows.items()}
    res["effect_of_1sd_pp"] = {k: {w: round(x, 3) for w, x in v.items()} for k, v in effects.items()}
    blocks = ("expectations", "slack_demand", "slack_supply", "cost_push")
    ph = {k: max(effects[k]["policy_horizon_2_3y"], 0.0) for k in blocks}
    total = sum(ph.values())
    res["estimated_weights_policy_horizon"] = {k: round(v / total, 3) for k, v in ph.items()}
    print("\nEffect on CPI inflation of a 1-SD move (slack, expectations: permanent; energy/food: 4-quarter relative price shock), pp:")
    print(f"  {'':14} {'year 1':>8} {'year 2':>8} {'year 3':>8} {'2–3y':>8}  weight")
    for k, v in effects.items():
        wt = f"{ph[k] / total:.2f}" if k in ph else "  –"
        print(f"  {k:14} {v['year_1']:+8.2f} {v['year_2']:+8.2f} {v['year_3']:+8.2f} {v['policy_horizon_2_3y']:+8.2f}  {wt}")
    (OUT / "bb_uk.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    if not os.environ.get("FRED_API_KEY") and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    main()
