"""Pass-through of oil supply shocks to UK prices and pay: state-dependent local projections.

Following the literature review (reports/UK cost push pass through.md, §2(ii)):
  y_{t+h} − y_{t−1} = α_h + β_h·s_t + Σ controls + ε_{t+h},   h = 0..36 months
where s_t is Känzig's (2021, AER) oil supply news shock, and y is 100·log of a price
index or pay. Responses are scaled to a 10% rise in the sterling oil price on impact
(β_h / b_0 × 10, with b_0 the impact response of the log sterling Brent price).
Also estimated as LP-IV: Δlog sterling Brent instrumented with Känzig's surprise series.

State dependence: s_t interacted with a lagged 0/1 state (CPI inflation above 3%, or
vacancies per unemployed above their median), as in Ramey–Zubairy (2018).

Output: analysis/results/passthrough_lp.json and a printed summary. Run after ONS/BoE
releases, not daily:  python analysis/passthrough_lp.py
"""
from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monetary_space.fetch import boe, fred, ons  # noqa: E402

KANZIG = "https://raw.githubusercontent.com/dkaenzig/oilsupplynews/master/oilSupplyNewsShocks_{v}.xlsx"
OUT = ROOT / "analysis" / "results"
H = 36
OUTCOMES = {   # 100·log of each index
    "cpi": "/economy/inflationandpriceindices/timeseries/d7bt/mm23",
    "core": "/economy/inflationandpriceindices/timeseries/dkc6/mm23",
    "services": "/economy/inflationandpriceindices/timeseries/d7f5/mm23",
    "goods": "/economy/inflationandpriceindices/timeseries/d7f4/mm23",
    "food": "/economy/inflationandpriceindices/timeseries/d7bu/mm23",
    "pay": "/employmentandlabourmarket/peopleinwork/earningsandworkinghours/timeseries/kai7/lms",
}


def kanzig(vintage: str = "2025M12") -> pd.DataFrame:
    r = requests.get(KANZIG.format(v=vintage), timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Monthly")
    df.index = pd.PeriodIndex(df["Date"].str.replace("M", "-"), freq="M")
    return df.rename(columns={"Oil supply surprise series": "surprise", "Oil supply news shock": "news"})[["surprise", "news"]]


def load() -> pd.DataFrame:
    d = {k: ons.timeseries(u, "M") for k, u in OUTCOMES.items()}
    for k in d:                                   # NSA price indices: remove stable seasonality
        if k != "pay":
            from monetary_space.rstar import seasonally_adjust
            d[k] = seasonally_adjust(d[k])
    brent = fred.series("DCOILBRENTEU")
    usd = boe.iadb("XUDLUSS", "01/Jan/1987")
    eri = boe.iadb("XUDLBK67", "01/Jan/1990")
    m = lambda s: s.groupby(s.index.asfreq("M")).mean()
    df = pd.DataFrame({k: 100 * np.log(v) for k, v in d.items()})
    df["oil_gbp"] = 100 * np.log(m(brent) / m(usd))
    df["eri"] = 100 * np.log(m(eri))
    df["cpi_yy"] = ons.timeseries("/economy/inflationandpriceindices/timeseries/d7g7/mm23", "M")
    u = ons.timeseries("/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/mgsx/lms", "M")
    v = ons.timeseries("/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/timeseries/ap2y/lms", "M")
    un = ons.timeseries("/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/mgsc/lms", "M")
    df["u"] = u
    df["vu"] = v / un
    return df.join(kanzig(), how="left")


def newey_west(X: np.ndarray, e: np.ndarray, lags: int) -> np.ndarray:
    XtX_inv = np.linalg.inv(X.T @ X)
    u = X * e[:, None]
    S = u.T @ u
    for l in range(1, lags + 1):
        w = 1 - l / (lags + 1)
        G = u[l:].T @ u[:-l]
        S += w * (G + G.T)
    return XtX_inv @ S @ XtX_inv


def lp(df: pd.DataFrame, y: str, shock: str, state: pd.Series | None = None, lags: int = 12,
       start: str = "1990-01", iv: bool = False) -> pd.DataFrame:
    """Coefficients and s.e. on the shock (or on each state interaction) for h = 0..H."""
    d = df[df.index >= pd.Period(start, "M")].copy()
    ctrl = {}
    for var in dict.fromkeys([y, "oil_gbp", "eri"]):
        for l in range(1, lags + 1):
            ctrl[f"d{var}_l{l}"] = d[var].diff().shift(l)
    ctrl["u_l1"] = d["u"].shift(1)
    C = pd.DataFrame(ctrl, index=d.index)
    rows = []
    for h in range(H + 1):
        lhs = d[y].shift(-h) - d[y].shift(1)
        if iv:                                    # 2SLS: Δlog oil_gbp instrumented by surprise
            endo = d["oil_gbp"] - d["oil_gbp"].shift(1)
            data = pd.concat([lhs.rename("lhs"), endo.rename("x"), d["surprise"].rename("z"), C], axis=1).dropna()
            W = np.column_stack([np.ones(len(data)), data[C.columns].to_numpy()])
            Z = np.column_stack([data["z"].to_numpy(), W])
            xhat = Z @ np.linalg.lstsq(Z, data["x"].to_numpy(), rcond=None)[0]
            X2 = np.column_stack([xhat, W])
            b = np.linalg.lstsq(X2, data["lhs"].to_numpy(), rcond=None)[0]
            e = data["lhs"].to_numpy() - np.column_stack([data["x"].to_numpy(), W]) @ b
            V = newey_west(X2, e, h + 1)
            rows.append({"h": h, "b": b[0] * 10, "se": np.sqrt(V[0, 0]) * 10, "n": len(data)})
            continue
        s = d[shock]
        if state is None:
            regs = {"shock": s}
        else:
            st = state.reindex(d.index).shift(1)
            regs = {"high": s * st, "low": s * (1 - st), "state": st}
        data = pd.concat([lhs.rename("lhs"), pd.DataFrame(regs), C], axis=1).dropna()
        X = np.column_stack([np.ones(len(data)), data.drop(columns="lhs").to_numpy()])
        b = np.linalg.lstsq(X, data["lhs"].to_numpy(), rcond=None)[0]
        e = data["lhs"].to_numpy() - X @ b
        V = newey_west(X, e, h + 1)
        names = list(data.drop(columns="lhs").columns)
        row = {"h": h, "n": len(data)}
        for k in regs:
            if k == "state":
                continue
            j = 1 + names.index(k)
            row[f"b_{k}"], row[f"se_{k}"] = b[j], np.sqrt(V[j, j])
        rows.append(row)
    return pd.DataFrame(rows).set_index("h")


def main() -> None:
    df = load()
    OUT.mkdir(parents=True, exist_ok=True)
    # Scale: impact response of sterling oil to the news shock → 10% oil rise
    oil = lp(df, "oil_gbp", "news")
    scale = 10 / oil.loc[0, "b_shock"]
    results = {"scale_per_10pct_oil": scale, "sample_start": "1990-01",
               "shock_vintage": "Känzig oilSupplyNewsShocks_2025M12", "linear": {}, "iv": {}, "state_inflation": {}, "state_vu": {}}
    states = {
        "state_inflation": (df["cpi_yy"] > 3.0).astype(float),
        "state_vu": (df["vu"] > df["vu"][df.index < pd.Period("2020-01", "M")].median()).astype(float).where(df["vu"].notna()),
    }
    for y in ["oil_gbp", *OUTCOMES]:
        lin = lp(df, y, "news")
        results["linear"][y] = {"b": (lin["b_shock"] * scale).round(4).tolist(), "se": (lin["se_shock"] * scale).round(4).tolist()}
        if y != "oil_gbp":
            iv = lp(df, y, "news", iv=True)
            results["iv"][y] = {"b": iv["b"].round(4).tolist(), "se": iv["se"].round(4).tolist()}
        for name, st in states.items():
            start = "2001-01" if name == "state_vu" else "1990-01"
            r = lp(df, y, "news", state=st, start=start)
            results[name][y] = {k: (r[k] * scale).round(4).tolist() for k in ("b_high", "se_high", "b_low", "se_low")}
    (OUT / "passthrough_lp.json").write_text(json.dumps(results, indent=1))

    print(f"Scale: {scale:.2f} (news-shock units per 10% sterling-oil rise)")
    print("Cumulative % response to a 10% oil supply shock (linear LP; IV in brackets)")
    for y in ["oil_gbp", *OUTCOMES]:
        l = results["linear"][y]
        iv = results["iv"].get(y)
        cells = [f"h={h:2d}: {l['b'][h]:+.2f}±{l['se'][h]:.2f}" + (f" [{iv['b'][h]:+.2f}]" if iv else "") for h in (0, 6, 12, 24, 36)]
        print(f"  {y:9} " + "  ".join(cells))
    for name in ("state_inflation", "state_vu"):
        print(f"State-dependent ({name}): high vs low at h=12, 24")
        for y in OUTCOMES:
            r = results[name][y]
            print(f"  {y:9} h12 high {r['b_high'][12]:+.2f}±{r['se_high'][12]:.2f} low {r['b_low'][12]:+.2f}±{r['se_low'][12]:.2f} | "
                  f"h24 high {r['b_high'][24]:+.2f}±{r['se_high'][24]:.2f} low {r['b_low'][24]:+.2f}±{r['se_low'][24]:.2f}")


if __name__ == "__main__":
    if not os.environ.get("FRED_API_KEY") and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    main()
