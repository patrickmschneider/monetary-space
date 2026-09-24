"""NAIRU (u*) from a wage Phillips curve with a time-varying u*, estimated by Kalman filter.

    y_t   = a·y_{t−1} − β·(u_t − u*_t) + ε_t,     ε ~ N(0, σ_ε²)
    u*_t  = u*_{t−1} + η_t,                       η ~ N(0, σ_η²)

y_t is real pay growth in excess of trend productivity: private-sector regular pay
growth − (re-centred) household inflation expectations − trend productivity growth.
With no constant, u* is the unemployment rate at which real pay grows in line with
productivity. σ_η (how fast u* may move) is fixed in config: the likelihood cannot
pin it down well (the "pile-up" problem). a, β and σ_ε are estimated by maximum
likelihood; u* is the Kalman-smoothed state, with its standard error.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class KalmanOutput:
    loglik: float
    filtered: np.ndarray
    filtered_var: np.ndarray
    predicted: np.ndarray
    predicted_var: np.ndarray


def kalman(y: np.ndarray, u: np.ndarray, ylag: np.ndarray, a: float, beta: float,
           sig_eps: float, sig_eta: float, s0: float, p0: float) -> KalmanOutput:
    """Scalar random-walk state; observations with NaN in y or ylag are skipped."""
    n = len(y)
    q, h = sig_eta ** 2, sig_eps ** 2
    s, p, ll = s0, p0, 0.0
    fs, fp, ps, pp = (np.empty(n) for _ in range(4))
    for t in range(n):
        s_pred, p_pred = s, p + q
        ps[t], pp[t] = s_pred, p_pred
        if np.isfinite(y[t]) and np.isfinite(ylag[t]):
            # y_t − a·y_{t−1} + β·u_t = β·u*_t + ε_t
            v = y[t] - a * ylag[t] + beta * u[t] - beta * s_pred
            f = beta ** 2 * p_pred + h
            k = p_pred * beta / f
            s, p = s_pred + k * v, p_pred - k * beta * p_pred
            ll += -0.5 * (np.log(2 * np.pi * f) + v ** 2 / f)
        else:
            s, p = s_pred, p_pred
        fs[t], fp[t] = s, p
    return KalmanOutput(ll, fs, fp, ps, pp)


def smooth(k: KalmanOutput) -> tuple[np.ndarray, np.ndarray]:
    """Rauch–Tung–Striebel smoother for a random-walk state."""
    n = len(k.filtered)
    ss, sp = k.filtered.copy(), k.filtered_var.copy()
    for t in range(n - 2, -1, -1):
        j = k.filtered_var[t] / k.predicted_var[t + 1]
        ss[t] = k.filtered[t] + j * (ss[t + 1] - k.predicted[t + 1])
        sp[t] = k.filtered_var[t] + j ** 2 * (sp[t + 1] - k.predicted_var[t + 1])
    return ss, sp


@dataclass
class Estimate:
    u_star: pd.Series        # smoothed, quarterly
    se: pd.Series            # standard error of u*, pp
    a: float
    beta: float
    sig_eps: float
    sig_eta: float
    loglik: float
    nobs: int
    sample: str


def estimate(y: pd.Series, u: pd.Series, sig_eta: float, prior_sd: float = 2.0) -> Estimate:
    """Maximum likelihood over (a, log β, log σ_ε) given σ_η; then smooth u*."""
    df = pd.DataFrame({"y": y, "u": u}).dropna(subset=["u"])
    df["ylag"] = df["y"].shift(1)
    yv, uv, lv = df["y"].to_numpy(float), df["u"].to_numpy(float), df["ylag"].to_numpy(float)
    s0, p0 = float(np.nanmean(uv[:8])), prior_sd ** 2

    def nll(theta):
        a, lb, ls = theta
        if not -0.99 < a < 0.99:
            return 1e10
        return -kalman(yv, uv, lv, a, np.exp(lb), np.exp(ls), sig_eta, s0, p0).loglik

    best = min(
        (minimize(nll, x0, method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
         for x0 in ([0.7, np.log(0.5), np.log(0.8)], [0.3, np.log(1.5), np.log(1.2)], [0.9, np.log(0.2), np.log(0.6)])),
        key=lambda r: r.fun,
    )
    a, lb, ls = best.x
    k = kalman(yv, uv, lv, a, np.exp(lb), np.exp(ls), sig_eta, s0, p0)
    ss, sp = smooth(k)
    used = np.isfinite(yv) & np.isfinite(lv)
    return Estimate(
        u_star=pd.Series(ss, index=df.index, name="u_star"),
        se=pd.Series(np.sqrt(sp), index=df.index, name="u_star_se"),
        a=float(a), beta=float(np.exp(lb)), sig_eps=float(np.exp(ls)), sig_eta=sig_eta,
        loglik=float(k.loglik), nobs=int(used.sum()), sample=f"{df.index[0]}–{df.index[-1]}",
    )


def quarterly(x: pd.Series) -> pd.Series:
    """Monthly 3-month-average series → quarterly, taking each quarter's final month."""
    if x.index.freqstr.startswith("Q"):
        return x
    q = x[x.index.month % 3 == 0]
    return pd.Series(q.to_numpy(), index=q.index.asfreq("Q"))


def quarterly_mean(x: pd.Series) -> pd.Series:
    """Monthly → quarterly average, complete quarters only."""
    g = x.groupby(x.index.asfreq("Q"))
    return g.mean()[g.size() == 3]


def build_inputs(pay_level: pd.Series, unemp: pd.Series, household_exp: pd.Series, cpi: pd.Series,
                 productivity: pd.Series, spec: dict) -> tuple[pd.Series, pd.Series]:
    """Assemble quarterly y (real pay growth over trend productivity) and u, per config/nairu.yaml.

    y = pay growth (q/q annualised) − expected inflation − trend productivity growth, where
    expected inflation = w·(household expectations, re-centred) + (1 − w)·(CPI inflation, lagged).
    """
    wq = quarterly_mean(pay_level)
    w = ((wq / wq.shift(1)) ** 4 - 1) * 100
    hh = household_exp - (household_exp[household_exp.index.year < 2020].mean() - spec["recentre_expectations_to"])
    pie = spec["household_weight"] * hh + (1 - spec["household_weight"]) * quarterly_mean(cpi).shift(spec["cpi_lag_quarters"])
    growth = (productivity / productivity.shift(4) - 1) * 100
    trend = growth.rolling(spec["productivity_trend_quarters"]).mean()
    idx = w.index
    trend = trend.reindex(trend.index.union(idx)).ffill()      # ragged edge: carry forward
    pie = pie.reindex(pie.index.union(idx)).ffill(limit=1)
    y = (w - pie - trend).dropna()
    y = y[y.index >= pd.Period(spec["start"], "Q")]
    for lo, hi in spec.get("exclude", []):
        y[(y.index >= pd.Period(lo, "Q")) & (y.index <= pd.Period(hi, "Q"))] = np.nan
    u = quarterly(unemp)
    u = u[(u.index >= y.index[0]) & (u.index <= y.index[-1])]
    return y.reindex(u.index), u


def from_config(data: dict[str, pd.Series], spec: dict) -> Estimate:
    s = spec["series"]
    y, u = build_inputs(data[s["pay_level"]], data[s["unemployment"]], data[s["household_expectations"]],
                        data[s["cpi"]], data[s["productivity"]], spec)
    return estimate(y, u, spec["sigma_eta"])
