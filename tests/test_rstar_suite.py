from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from monetary_space import config, rstar_suite, stance, trend_cycle

ROOT = Path(__file__).resolve().parents[1]


def test_suite_loads_and_sets_the_neutral_zone():
    cfg = config.load(ROOT)
    suite = rstar_suite.load(cfg.analysis)
    if suite is None:
        pytest.skip("no suite results")
    lo, hi = suite.range
    assert lo <= suite.headline <= hi and hi - lo >= 0.5
    assert suite.headline % 0.25 == 0
    weights = [v["weight"] for v in suite.estimators.values() if v]
    assert sum(weights) == pytest.approx(1.0, abs=1e-3)
    d = pd.period_range("2025-01-01", "2026-09-23", freq="D")
    st = stance.compute(cfg, {"OIS_2Y": pd.Series(4.6, index=d)}, suite, pd.Timestamp("2026-09-24"))
    assert st.r_star == suite.headline
    assert st.band[0] <= lo and st.band[1] >= hi          # never narrower than the suite's range


def test_trend_cycle_recovers_a_trend_through_missing_short_rates():
    rng = np.random.default_rng(3)
    n = 120
    idx = pd.period_range("1994Q1", periods=n, freq="Q")
    rbar = 2.5 - np.linspace(0, 2.0, n) + np.cumsum(rng.normal(0, 0.03, n))
    pibar = 2.0 + np.cumsum(rng.normal(0, 0.03, n))
    cyc = lambda s: np.array(pd.Series(rng.normal(0, s, n)).ewm(alpha=0.3).mean())
    df = pd.DataFrame({"R": rbar + pibar + cyc(1.0), "pi": pibar + cyc(1.0),
                       "yn": rbar + pibar + 0.5 + cyc(0.5), "yr": rbar - 0.5 + cyc(0.5)}, index=idx)
    est = trend_cycle.estimate(df, 0.05, 0.07, elb=("2009Q1", "2016Q4"))
    err = est.r_bar.iloc[8:] - rbar[8:]
    assert err.abs().mean() < 0.4
    assert est.r_bar.iloc[-1] < est.r_bar.iloc[8] - 1.0     # captures the decline
