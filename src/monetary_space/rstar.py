"""r* (the real neutral rate) from a Holston–Laubach–Williams-style model, by Kalman filter.

Quarterly; y is 100·log real GDP, π core CPI inflation (y/y), r the ex-ante real policy rate.

    IS:   ỹ_t = a1·ỹ_{t−1} + a2·ỹ_{t−2} + (ar/2)·Σ_{j=1,2}(r_{t−j} − r*_{t−j}) + ε1
    PC:   π_t = b1·π_{t−1} + (1 − b1)·mean(π_{t−2..t−4}) + by·ỹ_{t−1} + ε2
    y*_t = y*_{t−1} + g_{t−1} + ε3        g_t = g_{t−1} + ε4        z_t = z_{t−1} + ε5
    r*_t = c·g_t + z_t                    (c = 4: trend growth at an annual rate)

ỹ = y − y* is the output gap. As in HLW, the two small shock variances are tied to
others by ratios, σ4 = λg·σ3 and σ5 = λz·σ1/|ar|. HLW estimate λg and λz in earlier
median-unbiased stages; here they are fixed in config (a simplification). In UK data the
IS slope ar is not identified (real rates were negative for a decade without overheating),
so it is also fixed in config; a1, a2, b1, by, σ1, σ2, σ3 are estimated by maximum
likelihood with HLW's restriction by ≥ 0.025. π is seasonally adjusted core CPI inflation,
q/q annualised; expected inflation is its average over the past four quarters, as in HLW.

State x_t = [y*_t, y*_{t−1}, y*_{t−2}, g_{t−1}, g_{t−2}, z_{t−1}, z_{t−2}], so the filter
delivers r* for the quarter before the latest data (r*_{t−1} = c·g_{t−1} + z_{t−1}).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .nairu import kalman, smooth

AR_MAX, BY_MIN = -0.0025, 0.025


@dataclass
class Params:
    a1: float
    a2: float
    ar: float
    b1: float
    by: float
    sig1: float
    sig2: float
    sig3: float


def system(y, pi, r, p: Params, lam_g: float, lam_z: float, c: float, x0: np.ndarray, p0: np.ndarray):
    n = len(y)
    ylag1, ylag2 = np.r_[np.nan, y[:-1]], np.r_[np.nan, np.nan, y[:-2]]
    rlag1, rlag2 = np.r_[np.nan, r[:-1]], np.r_[np.nan, np.nan, r[:-2]]
    pilag1 = np.r_[np.nan, pi[:-1]]
    pibar = pd.Series(pi).shift(2).rolling(3).mean().to_numpy()
    Y = np.column_stack([y, pi])
    h = p.ar / 2
    Zrow_y = np.array([1.0, -p.a1, -p.a2, -h * c, -h * c, -h, -h])
    Zrow_pi = np.array([0.0, -p.by, 0, 0, 0, 0, 0])
    Z = np.tile(np.vstack([Zrow_y, Zrow_pi]), (n, 1, 1))
    d = np.column_stack([p.a1 * ylag1 + p.a2 * ylag2 + h * (rlag1 + rlag2),
                         p.b1 * pilag1 + (1 - p.b1) * pibar + p.by * ylag1])
    Y = np.where(np.isfinite(d), Y, np.nan)          # no observation without its lags
    d = np.nan_to_num(d)
    T = np.zeros((7, 7))
    T[0, 0] = T[0, 3] = 1          # y*_t = y*_{t−1} + g_{t−1}
    T[1, 0] = T[2, 1] = 1
    T[3, 3] = T[4, 3] = 1          # g random walk
    T[5, 5] = T[6, 5] = 1          # z random walk
    sig4, sig5 = lam_g * p.sig3, lam_z * p.sig1 / abs(p.ar)
    R = np.zeros((7, 3))
    R[0, 0] = R[0, 1] = R[3, 1] = R[5, 2] = 1
    RQR = R @ np.diag([p.sig3 ** 2, sig4 ** 2, sig5 ** 2]) @ R.T
    H = np.diag([p.sig1 ** 2, p.sig2 ** 2])
    return Y, Z, d, T, RQR, H, x0, p0


def _unpack(th, ar: float) -> Params:
    return Params(a1=th[0], a2=th[1], ar=ar, b1=1 / (1 + np.exp(-th[2])),
                  by=BY_MIN + np.exp(th[3]), sig1=np.exp(th[4]), sig2=np.exp(th[5]), sig3=np.exp(th[6]))


@dataclass
class Estimate:
    r_star: pd.Series            # smoothed, % a year, dated by quarter
    se: pd.Series
    r_star_realtime: pd.Series   # one-sided (filtered)
    growth: pd.Series            # trend growth, % a year
    z: pd.Series
    output_gap: pd.Series
    real_rate: pd.Series         # the ex-ante real policy rate the model uses
    params: Params
    lam_g: float
    lam_z: float
    loglik: float
    sample: str


def estimate(y: pd.Series, pi: pd.Series, r: pd.Series, lam_g: float, lam_z: float, ar: float,
             c: float = 4.0) -> Estimate:
    if ar > AR_MAX:
        raise ValueError(f"IS slope ar must be at most {AR_MAX}")
    idx = y.index
    yv, pv, rv = y.to_numpy(float), pi.reindex(idx).to_numpy(float), r.reindex(idx).to_numpy(float)
    first = np.flatnonzero(np.isfinite(yv))[:20]
    g0 = float(np.nanmean(np.diff(yv[first])))
    x0 = np.array([yv[first[0]], yv[first[0]] - g0, yv[first[0]] - 2 * g0, g0, g0, 0.0, 0.0])
    p0 = np.diag([1.0, 1.0, 1.0, 0.05, 0.05, 1.0, 1.0])

    def nll(th):
        p = _unpack(th, ar)
        if not (p.a1 + p.a2 < 0.98 and abs(p.a2) < 1):
            return 1e10
        return -kalman(*system(yv, pv, rv, p, lam_g, lam_z, c, x0, p0)).loglik

    starts = ([1.3, -0.4, 0.5, np.log(0.05), np.log(0.5), np.log(1.0), np.log(0.5)],
              [1.1, -0.2, 1.0, np.log(0.1), np.log(0.4), np.log(1.2), np.log(0.3)],
              [1.6, -0.7, -1.0, np.log(0.02), np.log(0.4), np.log(1.2), np.log(0.15)])
    best = min((minimize(nll, np.array(s), method="Nelder-Mead",
                         options={"maxiter": 30000, "xatol": 1e-7, "fatol": 1e-9}) for s in starts),
               key=lambda res: res.fun)
    p = _unpack(best.x, ar)
    Y, Z, d, T, RQR, H, _, _ = system(yv, pv, rv, p, lam_g, lam_z, c, x0, p0)
    k = kalman(Y, Z, d, T, RQR, H, x0, p0)
    s, Ps = smooth(k, T)
    w = np.zeros(7)
    w[3], w[5] = c, 1.0                                  # r*_{t−1} = c·g_{t−1} + z_{t−1}
    prev = idx - 1
    rs = s @ w
    rs_se = np.sqrt(np.einsum("i,tij,j->t", w, Ps, w))
    return Estimate(
        r_star=pd.Series(rs, index=prev, name="r_star"),
        se=pd.Series(rs_se, index=prev, name="r_star_se"),
        r_star_realtime=pd.Series(k.filtered @ w, index=prev, name="r_star_realtime"),
        growth=pd.Series(c * s[:, 3], index=prev, name="trend_growth"),
        z=pd.Series(s[:, 5], index=prev, name="z"),
        output_gap=pd.Series(yv - s[:, 0], index=idx, name="output_gap"),
        real_rate=pd.Series(rv, index=idx, name="real_rate"),
        params=p, lam_g=lam_g, lam_z=lam_z, loglik=float(k.loglik), sample=f"{idx[0]}–{idx[-1]}",
    )


def seasonally_adjust(index: pd.Series) -> pd.Series:
    """Stable-seasonal adjustment of a monthly price index: remove each calendar month's
    average log change in excess of the overall average (so the trend is kept). The
    full-sample averages are used, so history is revised slightly."""
    dl = np.log(index.astype(float)).diff()
    seasonal = dl.groupby(dl.index.month).transform("mean") - dl.mean()
    return np.exp((dl - seasonal).fillna(0).cumsum()) * float(index.iloc[0])


def quarterly_mean(x: pd.Series) -> pd.Series:
    """Monthly or daily → quarterly average, complete quarters only."""
    if x.index.freqstr.startswith("Q"):
        return x
    g = x.groupby(x.index.asfreq("Q"))
    months = g.apply(lambda s: s.index.asfreq("M").nunique())
    return g.mean()[months == 3]


def build_inputs(gdp: pd.Series, core_cpi_index: pd.Series, bank_rate: pd.Series, spec: dict):
    """100·log GDP, SA core inflation (q/q annualised) and the ex-ante real policy rate."""
    y = 100 * np.log(gdp.astype(float))
    q = quarterly_mean(seasonally_adjust(core_cpi_index))
    pi = ((q / q.shift(1)) ** 4 - 1) * 100
    r = quarterly_mean(bank_rate) - pi.rolling(4).mean()
    start, end = pd.Period(spec["start"], "Q"), y.index[-1]
    full = pd.period_range(start - 5, end, freq="Q")
    y, pi, r = (s.reindex(full) for s in (y, pi, r))
    for lo, hi in spec.get("exclude", []):
        mask = (full >= pd.Period(lo, "Q")) & (full <= pd.Period(hi, "Q"))
        y[mask] = np.nan
        pi[mask] = np.nan
    return y, pi, r, pd.period_range(start, end, freq="Q")


def from_config(data: dict[str, pd.Series], spec: dict) -> Estimate:
    s = spec["series"]
    y, pi, r, idx = build_inputs(data[s["gdp"]], data[s["core_cpi_index"]], data[s["policy_rate"]], spec)
    est = estimate(y, pi, r, spec["lambda_g"], spec["lambda_z"], spec["ar"], spec.get("c", 4.0))
    keep = est.r_star.index >= idx[0]
    return Estimate(**{**est.__dict__,
                       **{k: getattr(est, k)[keep] for k in ("r_star", "se", "r_star_realtime", "growth", "z")},
                       "output_gap": est.output_gap[est.output_gap.index >= idx[0]],
                       "real_rate": est.real_rate[est.real_rate.index >= idx[0]]})
