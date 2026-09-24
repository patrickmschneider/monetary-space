from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from monetary_space import config, policy_path, rstar, stance, transform
from monetary_space.fetch import fred, oecd
from monetary_space.score import EASE, HAWKISH, ON_TRACK

ROOT = Path(__file__).resolve().parents[1]


def fake_rstar(value=1.0, se=0.3):
    q = pd.period_range("2024Q1", "2025Q4", freq="Q")
    return SimpleNamespace(r_star=pd.Series(value, index=q), se=pd.Series(se, index=q))


def ois(level):
    d = pd.period_range("2025-01-01", "2026-09-23", freq="D")
    return pd.Series(level, index=d, dtype=float)


@pytest.mark.parametrize("ois_level,expected", [(3.6, "neutral"), (5.2, "tight"), (3.0, "loose")])
def test_stance_classes_against_band(ois_level, expected):
    cfg = config.load(ROOT)          # July 2026 MPR year-ahead CPI projection: 2.6%
    st = stance.compute(cfg, {"OIS_2Y": ois(ois_level)}, fake_rstar(1.0, 0.3), pd.Timestamp("2026-09-24"))
    assert st.expected_inflation == 2.6
    assert st.real_rate == pytest.approx(ois_level - 2.6)
    assert st.band == pytest.approx((0.5, 1.5))            # widened to the 0.5pp minimum half-width
    assert st.cls == expected and st.gap == pytest.approx(st.real_rate - 1.0)


def test_band_uses_standard_error_when_wider():
    cfg = config.load(ROOT)
    st = stance.compute(cfg, {"OIS_2Y": ois(4.6)}, fake_rstar(1.0, 1.2), pd.Timestamp("2026-09-24"))
    assert st.band == pytest.approx((-0.2, 2.2))


def test_verdict_combines_pressure_and_stance():
    cfg = config.load(ROOT)
    tight = stance.compute(cfg, {"OIS_2Y": ois(5.2)}, fake_rstar(), pd.Timestamp("2026-09-24"))
    assert stance.verdict(cfg, {"A": 0, "B": 0, "C": 0}, tight).verdict == EASE
    assert stance.verdict(cfg, {"A": 2, "B": 2, "C": 2}, tight).verdict == ON_TRACK
    loose = stance.compute(cfg, {"OIS_2Y": ois(3.0)}, fake_rstar(), pd.Timestamp("2026-09-24"))
    v = stance.verdict(cfg, {"A": 0.5, "B": 1.5, "C": 0.2}, loose)
    assert v.verdict == HAWKISH and v.driver == "B"
    assert v.pressure == pytest.approx(0.5 * 1.5 + 0.3 * 0.5 + 0.2 * 0.2)


def test_seasonal_adjustment_keeps_trend_and_removes_pattern():
    m = pd.period_range("1990-01", "2019-12", freq="M")
    season = np.tile([0.004, -0.002, 0.001, 0.0, -0.003, 0.0, 0.002, -0.001, 0.0, 0.001, -0.002, 0.0], len(m) // 12)
    idx = pd.Series(100 * np.exp(np.cumsum(0.02 / 12 + season)), index=m)
    sa = rstar.seasonally_adjust(idx)
    growth = np.log(sa).diff().dropna()
    assert growth.mean() * 12 == pytest.approx(0.02, abs=1e-3)
    assert growth.std() < 1e-3


def test_rstar_system_shapes():
    n = 12
    p = rstar.Params(a1=1.2, a2=-0.3, ar=-0.1, b1=0.5, by=0.05, sig1=0.4, sig2=1.0, sig3=0.2)
    Y, Z, d, T, RQR, H, x0, P0 = rstar.system(np.arange(n, dtype=float), np.ones(n), np.zeros(n), p,
                                              0.05, 0.03, 4.0, np.zeros(7), np.eye(7))
    assert Y.shape == (n, 2) and Z.shape == (n, 2, 7) and T.shape == (7, 7)
    assert np.isnan(Y[:4, 1]).all()          # the Phillips curve needs four lags of inflation
    assert RQR[5, 5] == pytest.approx((0.03 * 0.4 / 0.1) ** 2)


def test_chained_transform_and_weighted_mean():
    d = pd.period_range("2024-01-01", "2025-12-31", freq="D")
    x = pd.Series(np.where(d.year == 2024, 100.0, 110.0), index=d)
    out = transform.apply(["monthly_mean", "pct_change_12m"], [x])
    assert out.iloc[-1] == pytest.approx(10.0)
    m = pd.period_range("2024-01", periods=3, freq="M")
    w = transform.apply("weighted_mean", [pd.Series(100.0, m), pd.Series(102.0, m)], weights=[0.75, 0.25])
    assert (w == 100.5).all()


def test_oecd_and_fred_parsers():
    csv = "REF_AREA,TIME_PERIOD,OBS_VALUE\nUSA,2026-07,100.9\nUSA,2026-08,101.0\nDEU,2026-08,100.5\n"
    out = oecd.parse_cli(csv)
    assert out["USA"].iloc[-1] == 101.0 and str(out["DEU"].index[0]) == "2026-08"
    payload = {"observations": [{"date": "2026-09-21", "value": "116.15"}, {"date": "2026-09-22", "value": "."}]}
    s = fred.parse_observations(payload, "D", "DCOILBRENTEU")
    assert len(s) == 1 and s.iloc[0] == 116.15


def test_policy_rule():
    cfg = config.load(ROOT)
    m = pd.period_range("2024-01", "2026-08", freq="M")
    q = pd.period_range("2023Q1", "2026Q2", freq="Q")
    data = {"DKO8": pd.Series(3.0, index=m), "MGSX": pd.Series(5.0, index=m)}
    est = {"rstar": fake_rstar(1.0), "nairu": SimpleNamespace(u_star=pd.Series(4.5, index=q))}
    rule = policy_path.rule_path(cfg, data, est, pd.Period("2025-01", "M"))
    # 1 + 2 + 1.5·(3 − 2) + 0.5·(−2·(5 − 4.5)) = 4.0
    assert rule.iloc[-1] == pytest.approx(4.0)
