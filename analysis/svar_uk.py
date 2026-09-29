"""Sign-identified Bayesian VAR: historical decomposition of UK CPI inflation.

A cut-down version of the Bank of England's model (Brignone & Piffer 2025, Macro Technical
Paper No. 3), as recommended in the literature review: a historical decomposition only,
labelled a model-based illustration; no forecasts.

Quarterly, 1993Q1 onward, 2 lags, constant, pandemic dummies (2020Q2–2021Q2):
  oil   Δlog real sterling Brent price (%)        gdp  Δlog real GDP (% q/q)
  cpi   CPI inflation, SA, % q/q annualised        rate Bank Rate (%)
  eri   Δlog sterling effective exchange rate (%)

Impact sign restrictions (Arias, Rubio-Ramírez & Waggoner 2018 style draws: posterior
draw of (B, Σ) under a flat prior, random orthogonal rotation, keep if all signs hold):
            oil   gdp   cpi   rate   eri
  energy     +     −     +
  demand           +     +     +
  supply     ≤0    −     +
  monetary         −     −     +      +
  other      (unrestricted residual shock)

Output: analysis/results/svar_uk.json with median contributions (and 16th/84th
percentiles) of each shock to CPI inflation relative to the model's baseline.
Run after releases:  python analysis/svar_uk.py
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
from monetary_space.fetch import boe, fred, ons  # noqa: E402
from monetary_space.rstar import quarterly_mean, seasonally_adjust  # noqa: E402

OUT = ROOT / "analysis" / "results"
VARS = ["oil", "gdp", "cpi", "rate", "eri"]
SHOCKS = ["energy", "demand", "supply", "monetary", "other"]
COMPONENTS = SHOCKS + ["pandemic", "baseline"]
SIGNS = {  # shock: {variable index: +1 / −1}; supply's oil ≤ 0 is −1
    "energy": {0: 1, 1: -1, 2: 1},
    "demand": {1: 1, 2: 1, 3: 1},
    "supply": {0: -1, 1: -1, 2: 1},
    "monetary": {1: -1, 2: -1, 3: 1, 4: 1},
}
LAGS, DRAWS, KEEP = 2, 20000, 400
DUMMIES = ["2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2"]


def load() -> pd.DataFrame:
    q = lambda s: quarterly_mean(s)
    cpi_idx = seasonally_adjust(ons.timeseries("/economy/inflationandpriceindices/timeseries/d7bt/mm23", "M"))
    cpiq = q(cpi_idx)
    brent = fred.series("DCOILBRENTEU")
    usd = boe.iadb("XUDLUSS", "01/Jan/1987")
    oil_gbp = q(brent.groupby(brent.index.asfreq("M")).mean() / usd.groupby(usd.index.asfreq("M")).mean())
    gdp = ons.timeseries("/economy/grossdomesticproductgdp/timeseries/abmi/qna", "Q")
    rate = q(boe.iadb("IUDBEDR", "01/Jan/1990"))
    eri = q(boe.iadb("XUDLBK67", "01/Jan/1990"))
    df = pd.DataFrame({
        "oil": 100 * np.log(oil_gbp / cpiq).diff(),
        "gdp": 100 * np.log(gdp).diff(),
        "cpi": ((cpiq / cpiq.shift(1)) ** 4 - 1) * 100,
        "rate": rate,
        "eri": 100 * np.log(eri).diff(),
    })
    return df[df.index >= pd.Period("1993Q1", "Q")].dropna()


def design(df: pd.DataFrame):
    Y = df[VARS].to_numpy()
    T, n = Y.shape
    X = [np.ones(T - LAGS)]
    for l in range(1, LAGS + 1):
        X.extend(Y[LAGS - l:T - l].T)
    idx = df.index[LAGS:]
    for d in DUMMIES:
        X.append((idx == pd.Period(d, "Q")).astype(float))
    return Y[LAGS:], np.column_stack(X), idx


def companion_ma(B: np.ndarray, n: int, H: int) -> np.ndarray:
    """MA coefficients Ψ_0..Ψ_{H−1} (n×n each) from lag coefficients."""
    A = [B[1 + (l - 1) * n: 1 + l * n].T for l in range(1, LAGS + 1)]
    Psi = [np.eye(n)]
    for h in range(1, H):
        Psi.append(sum(A[l - 1] @ Psi[h - l] for l in range(1, min(h, LAGS) + 1)))
    return np.array(Psi)


def main(seed: int = 7) -> None:
    rng = np.random.default_rng(seed)
    df = load()
    Y, X, idx = design(df)
    T, n = Y.shape
    k = X.shape[1]
    XtX_inv = np.linalg.inv(X.T @ X)
    B_ols = XtX_inv @ X.T @ Y
    U = Y - X @ B_ols
    S = U.T @ U
    chol_xx = np.linalg.cholesky(XtX_inv)
    contrib_draws = []
    tried = 0
    while len(contrib_draws) < KEEP and tried < DRAWS:
        tried += 1
        # Σ ~ IW(S, T − k); B | Σ ~ MN(B_ols, Σ, (X'X)⁻¹)
        Z = rng.standard_normal((T - k, n)) @ np.linalg.cholesky(np.linalg.inv(S)).T
        Sigma = np.linalg.inv(Z.T @ Z)
        B = B_ols + chol_xx @ rng.standard_normal((k, n)) @ np.linalg.cholesky(Sigma).T
        Q, R = np.linalg.qr(rng.standard_normal((n, n)))
        Q = Q @ np.diag(np.sign(np.diag(R)))
        A0 = np.linalg.cholesky(Sigma) @ Q          # impact matrix: columns are shocks
        order, used = [], set()
        for s in SHOCKS[:4]:                        # match each restricted shock to a column (with sign flips)
            hit = None
            for j in range(n):
                if j in used:
                    continue
                for sgn in (1, -1):
                    col = sgn * A0[:, j]
                    if all(np.sign(col[v]) == want for v, want in SIGNS[s].items()):
                        hit = (j, sgn)
                        break
                if hit:
                    break
            if hit is None:
                break
            used.add(hit[0])
            order.append(hit)
        if len(order) < 4:
            continue
        rest = [j for j in range(n) if j not in used]
        order.append((rest[0], 1))
        A0s = np.column_stack([sgn * A0[:, j] for j, sgn in order])
        U_d = Y - X @ B
        eps = np.linalg.solve(A0s, U_d.T).T            # structural shocks, T × n
        Psi = companion_ma(B, n, T)
        cpi_i = VARS.index("cpi")
        c = np.zeros((T, n + 2))
        dcoef = B[-len(DUMMIES):]                       # dummy rows: len(DUMMIES) × n
        dmat = X[:, -len(DUMMIES):]
        for t in range(T):
            for h in range(t + 1):
                c[t, :n] += (Psi[h] @ A0s)[cpi_i] * eps[t - h]
                c[t, n] += Psi[h][cpi_i] @ (dmat[t - h] @ dcoef)    # pandemic dummies, propagated
        c[:, n + 1] = Y[:, cpi_i] - c[:, :n + 1].sum(axis=1)       # baseline: constant + initial conditions
        contrib_draws.append(c)
    D = np.array(contrib_draws)                          # draws × T × shocks
    med = np.median(D, axis=0)
    lo, hi = np.percentile(D, 16, axis=0), np.percentile(D, 84, axis=0)
    out = {
        "method": "Sign-identified Bayesian VAR (flat prior), 5 variables, 2 lags, 1993Q1 onward, pandemic dummies; "
                  "historical decomposition of CPI inflation (q/q annualised, SA) relative to the model baseline. "
                  "Model-based illustration, not a forecast.",
        "accepted_draws": len(contrib_draws), "tried": tried,
        "shocks": SHOCKS, "signs": {s: {VARS[v]: ("+" if w > 0 else "−") for v, w in r.items()} for s, r in SIGNS.items()},
        "series": {str(q): {"actual": round(float(Y[t, VARS.index("cpi")]), 3),
                            **{s: {"median": round(float(med[t, j]), 3), "p16": round(float(lo[t, j]), 3), "p84": round(float(hi[t, j]), 3)}
                               for j, s in enumerate(COMPONENTS)}}
                   for t, q in enumerate(idx)},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "svar_uk.json").write_text(json.dumps(out, indent=1))
    print(f"accepted {len(contrib_draws)} of {tried} draws")
    tab = pd.DataFrame(med, index=idx, columns=COMPONENTS)
    tab["actual"] = Y[:, VARS.index("cpi")]
    print(tab.rolling(4).mean().loc["2019Q4":].iloc[::2].round(2).to_string())


if __name__ == "__main__":
    if not os.environ.get("FRED_API_KEY") and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    main()
