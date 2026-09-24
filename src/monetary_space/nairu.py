"""u* (NAIRU) from a multivariate filter: unemployment trend plus a wage Phillips curve.

State: u*_t (random walk) and the unemployment gap g_t = u_t − u*_t (stationary AR(2)).

    u_t   = u*_t + g_t + e_t                     e ~ N(0, σ_u²)   small LFS sampling noise
    y_t   = c + a·y_{t−1} − β·g_t + ε_t          ε ~ N(0, σ_ε²)
    u*_t  = u*_{t−1} + η_t                       η ~ N(0, σ_η²)
    g_t   = ρ1·g_{t−1} + ρ2·g_{t−2} + ν_t        ν ~ N(0, σ_ν²)

y_t is real pay growth in excess of trend productivity (see build_inputs). Because the gap
must mean-revert, u* is the slow-moving trend of unemployment, placed by what pay growth
says about slack; the constant c absorbs any average excess of real pay over productivity.
σ_η, σ_u and a cap on gap persistence (ρ1 + ρ2) are fixed in config/nairu.yaml; without
the cap the likelihood drives the gap to a unit root and u* stops tracking u.
c, a, β, ρ1, ρ2, σ_ε and σ_ν are estimated by maximum likelihood.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class KalmanOutput:
    loglik: float
    filtered: np.ndarray        # (n, m)
    filtered_var: np.ndarray    # (n, m, m)
    predicted: np.ndarray
    predicted_var: np.ndarray


def kalman(Y: np.ndarray, Z: np.ndarray, d: np.ndarray, T: np.ndarray, RQR: np.ndarray, H: np.ndarray,
           a0: np.ndarray, P0: np.ndarray) -> KalmanOutput:
    """Linear Gaussian filter; NaN observations are skipped element by element."""
    n, m = len(Y), len(a0)
    a, P, ll = a0.copy(), P0.copy(), 0.0
    at, Pt, ap, Pp = np.zeros((n, m)), np.zeros((n, m, m)), np.zeros((n, m)), np.zeros((n, m, m))
    for t in range(n):
        a, P = T @ a, T @ P @ T.T + RQR
        ap[t], Pp[t] = a, P
        obs = np.isfinite(Y[t])
        if obs.any():
            Zt, Ht = Z[t][obs], H[np.ix_(obs, obs)]
            v = Y[t][obs] - d[t][obs] - Zt @ a
            F = Zt @ P @ Zt.T + Ht
            Fi = np.linalg.inv(F)
            K = P @ Zt.T @ Fi
            a, P = a + K @ v, P - K @ Zt @ P
            ll += -0.5 * (obs.sum() * np.log(2 * np.pi) + np.log(np.linalg.det(F)) + v @ Fi @ v)
        at[t], Pt[t] = a, P
    return KalmanOutput(ll, at, Pt, ap, Pp)


def smooth(k: KalmanOutput, T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rauch–Tung–Striebel smoother."""
    s, Ps = k.filtered.copy(), k.filtered_var.copy()
    for t in range(len(s) - 2, -1, -1):
        J = k.filtered_var[t] @ T.T @ np.linalg.inv(k.predicted_var[t + 1])
        s[t] = k.filtered[t] + J @ (s[t + 1] - k.predicted[t + 1])
        Ps[t] = k.filtered_var[t] + J @ (Ps[t + 1] - k.predicted_var[t + 1]) @ J.T
    return s, Ps


@dataclass
class Params:
    c: float
    a: float
    beta: float
    rho1: float
    rho2: float
    sig_eps: float
    sig_nu: float


def system(y: np.ndarray, u: np.ndarray, p: Params, sig_eta: float, sig_u: float):
    """State [u*, g, g_{−1}]; observations [u, y]."""
    n = len(y)
    ylag = np.r_[np.nan, y[:-1]]
    Y = np.column_stack([u, np.where(np.isfinite(ylag), y, np.nan)])
    T = np.array([[1.0, 0, 0], [0, p.rho1, p.rho2], [0, 1, 0]])
    RQR = np.diag([sig_eta ** 2, p.sig_nu ** 2, 0.0])
    Z = np.tile(np.array([[1.0, 1, 0], [0, -p.beta, 0]]), (n, 1, 1))
    d = np.column_stack([np.zeros(n), p.c + p.a * np.nan_to_num(ylag)])
    H = np.diag([sig_u ** 2, p.sig_eps ** 2])
    a0 = np.array([np.nanmean(u[:8]), 0.0, 0.0])
    P0 = np.diag([4.0, 1.0, 1.0])
    return Y, Z, d, T, RQR, H, a0, P0


def _unpack(th: np.ndarray) -> Params:
    return Params(c=th[0], a=np.tanh(th[1]), beta=np.exp(th[2]), rho1=th[3], rho2=th[4],
                  sig_eps=np.exp(th[5]), sig_nu=np.exp(th[6]))


@dataclass
class Estimate:
    u_star: pd.Series        # smoothed, quarterly
    se: pd.Series            # standard error of u*, pp
    u_star_realtime: pd.Series   # filtered: what the model said at each date with data to then
    params: Params
    sig_eta: float
    loglik: float
    nobs: int
    sample: str

    @property
    def beta(self) -> float:
        return self.params.beta

    @property
    def a(self) -> float:
        return self.params.a


def estimate(y: pd.Series, u: pd.Series, sig_eta: float, sig_u: float = 0.1,
             max_persistence: float = 0.9) -> Estimate:
    yv, uv = y.reindex(u.index).to_numpy(float), u.to_numpy(float)

    def nll(th):
        p = _unpack(th)
        # AR(2) stationarity triangle, with total persistence capped
        if not (abs(p.rho2) < 1 and p.rho1 + p.rho2 < max_persistence and p.rho2 - p.rho1 < 1):
            return 1e10
        return -kalman(*system(yv, uv, p, sig_eta, sig_u)).loglik

    starts = ([0.0, 0.2, np.log(0.5), 1.5, -0.6, np.log(1.4), np.log(0.2)],
              [0.5, 0.1, np.log(1.0), 1.2, -0.3, np.log(1.3), np.log(0.3)],
              [1.0, 0.1, np.log(0.8), 1.3, -0.5, np.log(1.3), np.log(0.25)])
    best = min((minimize(nll, np.array(x0), method="Nelder-Mead",
                         options={"maxiter": 20000, "xatol": 1e-7, "fatol": 1e-9}) for x0 in starts),
               key=lambda r: r.fun)
    p = _unpack(best.x)
    Y, Z, d, T, RQR, H, a0, P0 = system(yv, uv, p, sig_eta, sig_u)
    k = kalman(Y, Z, d, T, RQR, H, a0, P0)
    s, Ps = smooth(k, T)
    return Estimate(
        u_star=pd.Series(s[:, 0], index=u.index, name="u_star"),
        se=pd.Series(np.sqrt(Ps[:, 0, 0]), index=u.index, name="u_star_se"),
        u_star_realtime=pd.Series(k.filtered[:, 0], index=u.index, name="u_star_realtime"),
        params=p, sig_eta=sig_eta, loglik=float(k.loglik),
        nobs=int(np.isfinite(Y[:, 1]).sum()), sample=f"{u.index[0]}–{u.index[-1]}",
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
    return estimate(y, u, spec["sigma_eta"], spec.get("sigma_u", 0.1), spec.get("max_gap_persistence", 0.9))
