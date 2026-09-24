import numpy as np
import pandas as pd
import pytest

from monetary_space import nairu


def simulate(n=140, beta=1.0, a=0.2, rho=(1.4, -0.55), sig_eps=0.6, sig_nu=0.2, sig_eta=0.15, seed=1):
    """Data from the filter's own model: u = u* + gap, y = a·y₋₁ − β·gap + ε."""
    rng = np.random.default_rng(seed)
    u_star = 5 + np.cumsum(rng.normal(0, sig_eta, n))
    g = np.zeros(n)
    for t in range(2, n):
        g[t] = rho[0] * g[t - 1] + rho[1] * g[t - 2] + rng.normal(0, sig_nu)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = a * y[t - 1] - beta * g[t] + rng.normal(0, sig_eps)
    idx = pd.period_range("1990Q1", periods=n, freq="Q")
    u = u_star + g + rng.normal(0, 0.1, n)
    return pd.Series(y, idx), pd.Series(u, idx), pd.Series(u_star, idx)


def test_recovers_u_star_path():
    for seed in (1, 2):
        y, u, true = simulate(seed=seed)
        est = nairu.estimate(y, u, sig_eta=0.15, max_persistence=0.95)
        err = (est.u_star - true).iloc[8:]
        assert err.abs().mean() < 0.35 and abs(err.mean()) < 0.25
        assert 0.4 < est.beta < 2.5          # the right sign and order of magnitude


def test_u_star_tracks_unemployment_trend():
    """The gap must mean-revert: u* cannot sit on one side of u for the whole sample."""
    y, u, _ = simulate(seed=4)
    est = nairu.estimate(y, u, sig_eta=0.15)
    above = (est.u_star > u).mean()
    assert 0.2 < above < 0.8


def test_missing_pay_quarters_are_skipped():
    y, u, _ = simulate()
    y.iloc[60:66] = np.nan
    est = nairu.estimate(y, u, sig_eta=0.15)
    assert est.nobs == len(y) - 1 - 7          # no lag for the first; 6 missing + the one after
    assert np.isfinite(est.u_star).all()


def test_smoother_matches_filter_at_the_end():
    y, u, _ = simulate()
    p = nairu.Params(c=0.0, a=0.2, beta=1.0, rho1=1.4, rho2=-0.55, sig_eps=0.6, sig_nu=0.2)
    Y, Z, d, T, RQR, H, a0, P0 = nairu.system(y.to_numpy(), u.to_numpy(), p, 0.15, 0.1)
    k = nairu.kalman(Y, Z, d, T, RQR, H, a0, P0)
    s, Ps = nairu.smooth(k, T)
    assert s[-1, 0] == pytest.approx(k.filtered[-1, 0])
    assert (Ps[:, 0, 0] <= k.filtered_var[:, 0, 0] + 1e-10).all()


def test_build_inputs_recentres_expectations_and_excludes_quarters():
    m = pd.period_range("2000-01", "2021-12", freq="M")
    q = pd.period_range("1995Q1", "2021Q4", freq="Q")
    pay = pd.Series([100 * 1.01 ** (k / 3) for k in range(len(m))], index=m)   # 4.06% a year
    spec = {"household_weight": 1.0, "cpi_lag_quarters": 1, "recentre_expectations_to": 2.0,
            "productivity_trend_quarters": 4, "start": "2001Q2", "exclude": [["2020Q1", "2020Q4"]]}
    y, u = nairu.build_inputs(pay, pd.Series(5.0, index=m), pd.Series(3.0, index=q),
                              pd.Series(2.0, index=m), pd.Series(100.0, index=q), spec)
    assert y["2005Q1"] == pytest.approx(1.01 ** 4 * 100 - 100 - 2.0, abs=1e-6)   # expectations 3 → 2
    assert y["2020Q1":"2020Q4"].isna().all() and y.index[0] == pd.Period("2001Q2", "Q")
