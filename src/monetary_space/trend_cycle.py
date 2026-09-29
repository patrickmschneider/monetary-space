"""r̄: the trend real interest rate from a UK trend-cycle model (after Del Negro, Giannone,
Giannoni & Tambalotti 2017/2019), the anchor of the r* suite.

Quarterly observables share random-walk trends in the real rate r̄ and inflation π̄:

    Bank Rate        R_t    = r̄_t + π̄_t + c^R_t            (missing 2009Q1–2021Q4: lower bound)
    CPI inflation    π_t    = π̄_t + c^π_t
    10y gilt, nominal y_t   = r̄_t + π̄_t + τ_n + c^n_t
    10y gilt, real   y^r_t  = r̄_t + τ_r + τ_post·1[t ≥ 2020Q4] + c^r_t
    r̄_t = r̄_{t−1} + η^r,  π̄_t = π̄_{t−1} + η^π,  cycles c^k_t = ρ_k c^k_{t−1} + ε^k

τ_n is a constant nominal term premium; τ_r a constant real-yield wedge (RPI basis, term and
liquidity premia), which shifts by τ_post after the RPI reform was announced (Nov 2020),
since index-linked real yields for post-2030 cash flows moved to a CPIH basis.

Trend-shock variances are fixed at DGGT's prior means (1/400 for r̄, 1/200 for π̄, annualised
%), with a looser setting as a sensitivity. Cycle parameters and wedges are estimated by
maximum likelihood (Kalman filter with missing data). DGGT use a VAR(5) cycle and Bayesian
estimation; independent AR(1) cycles are a simplification.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .nairu import kalman, smooth

OBS = ["R", "pi", "yn", "yr"]


@dataclass
class Estimate:
    r_bar: pd.Series             # smoothed trend real rate
    se: pd.Series
    r_bar_realtime: pd.Series    # filtered (one-sided)
    pi_bar: pd.Series
    params: dict
    loglik: float
    sample: str


def system(Y: np.ndarray, post: np.ndarray, th: np.ndarray, sd_r: float, sd_pi: float, rho_max: float = 0.9):
    tau_n, tau_r, tau_post = th[0:3]
    rho = rho_max * np.tanh(th[3:7])
    sig = np.exp(th[7:11])
    n = len(Y)
    # state: [r̄, π̄, cR, cπ, cn, cr]
    T = np.eye(6)
    T[2:, 2:] = np.diag(rho)
    RQR = np.diag([sd_r ** 2, sd_pi ** 2, *(sig ** 2)])
    Zb = np.array([[1, 1, 1, 0, 0, 0],
                   [0, 1, 0, 1, 0, 0],
                   [1, 1, 0, 0, 1, 0],
                   [1, 0, 0, 0, 0, 1]], dtype=float)
    Z = np.tile(Zb, (n, 1, 1))
    d = np.column_stack([np.zeros(n), np.zeros(n), np.full(n, tau_n), tau_r + tau_post * post])
    H = np.diag([0.01, 0.01, 0.01, 0.01])          # small measurement error for numerical stability
    a0 = np.array([np.nanmean(Y[:8, 3]) if np.isfinite(Y[:8, 3]).any() else 2.0, 2.0, 0, 0, 0, 0])
    P0 = np.diag([4.0, 4.0, 4.0, 4.0, 4.0, 4.0])
    return Y, Z, d, T, RQR, H, a0, P0


def estimate(df: pd.DataFrame, sd_r: float = 0.05, sd_pi: float = 0.0707, elb=("2009Q1", "2021Q4"),
             rho_max: float = 0.9) -> Estimate:
    """rho_max caps cycle persistence: uncapped, ML pushes the cycles to a unit root and they
    absorb the low-frequency movement that the trend should capture (the pile-up problem)."""
    d = df[OBS].copy()
    lo, hi = pd.Period(elb[0], "Q"), pd.Period(elb[1], "Q")
    d.loc[(d.index >= lo) & (d.index <= hi), "R"] = np.nan
    Y = d.to_numpy(float)
    post = (d.index >= pd.Period("2020Q4", "Q")).astype(float)

    def nll(th):
        return -kalman(*system(Y, post, th, sd_r, sd_pi, rho_max)).loglik

    starts = ([1.0, -1.0, 1.0, 1.0, 0.5, 1.0, 1.0, np.log(1.0), np.log(1.0), np.log(0.5), np.log(0.5)],
              [0.5, -0.5, 0.5, 0.5, 1.0, 0.5, 0.5, np.log(0.5), np.log(1.5), np.log(0.3), np.log(0.3)])
    best = min((minimize(nll, np.array(s), method="Nelder-Mead", options={"maxiter": 30000, "xatol": 1e-7, "fatol": 1e-9})
                for s in starts), key=lambda r: r.fun)
    Ys, Z, dd, T, RQR, H, a0, P0 = system(Y, post, best.x, sd_r, sd_pi, rho_max)
    k = kalman(Ys, Z, dd, T, RQR, H, a0, P0)
    s, Ps = smooth(k, T)
    th = best.x
    params = {"tau_n": th[0], "tau_r": th[1], "tau_post": th[2], "rho": dict(zip(OBS, (rho_max * np.tanh(th[3:7])).round(3))), "rho_max": rho_max,
              "sigma_cycle": dict(zip(OBS, np.exp(th[7:11]).round(3))), "sd_rbar": sd_r, "sd_pibar": sd_pi}
    return Estimate(
        r_bar=pd.Series(s[:, 0], index=d.index), se=pd.Series(np.sqrt(Ps[:, 0, 0]), index=d.index),
        r_bar_realtime=pd.Series(k.filtered[:, 0], index=d.index), pi_bar=pd.Series(s[:, 1], index=d.index),
        params=params, loglik=float(k.loglik), sample=f"{d.index[0]}–{d.index[-1]}",
    )
