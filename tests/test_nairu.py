import numpy as np
import pandas as pd
import pytest

from monetary_space import nairu


def simulate(n=120, a=0.3, beta=0.6, sig_eps=0.5, sig_eta=0.1, seed=1):
    rng = np.random.default_rng(seed)
    u_star = 5 + np.cumsum(rng.normal(0, sig_eta, n))
    u = u_star + 1.5 * np.sin(np.arange(n) / 8) + rng.normal(0, 0.2, n)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = a * y[t - 1] - beta * (u[t] - u_star[t]) + rng.normal(0, sig_eps)
    idx = pd.period_range("1996Q1", periods=n, freq="Q")
    return pd.Series(y, idx), pd.Series(u, idx), pd.Series(u_star, idx)


def test_recovers_parameters_and_u_star_path():
    for seed in (1, 2, 3):
        y, u, true = simulate(seed=seed)
        est = nairu.estimate(y, u, sig_eta=0.1)
        assert est.beta == pytest.approx(0.6, abs=0.2)
        assert est.a == pytest.approx(0.3, abs=0.3)
        err = (est.u_star - true).iloc[8:]
        assert err.abs().mean() < 0.3 and abs(err.mean()) < 0.2


def test_missing_quarters_are_skipped_not_fatal():
    y, u, _ = simulate()
    y.iloc[60:66] = np.nan
    est = nairu.estimate(y, u, sig_eta=0.1)
    assert est.nobs == len(y) - 1 - 7          # first obs has no lag; 6 missing + the one after
    assert est.se.iloc[62] > est.se.iloc[40]    # less certain where data are missing


def test_smoother_matches_filter_at_the_end():
    y, u, _ = simulate()
    df = pd.DataFrame({"y": y, "u": u})
    k = nairu.kalman(df.y.values, df.u.values, df.y.shift(1).values, 0.3, 0.6, 0.5, 0.1, 5.0, 4.0)
    ss, sp = nairu.smooth(k)
    assert ss[-1] == pytest.approx(k.filtered[-1]) and sp[-1] == pytest.approx(k.filtered_var[-1])
    assert (sp <= k.filtered_var + 1e-12).all()


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
