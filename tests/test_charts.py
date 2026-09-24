from pathlib import Path

import pandas as pd
import pytest

from monetary_space import charts, config, transform

ROOT = Path(__file__).resolve().parents[1]


def test_growth_3m_yoy():
    idx = pd.period_range("2020-01", periods=15, freq="M")
    x = pd.Series([100.0] * 12 + [110.0] * 3, index=idx)
    assert transform.apply("growth_3m_yoy", [x]).iloc[-1] == pytest.approx(10.0)


def test_daily_to_monthly_mean_and_last():
    idx = pd.period_range("2026-01-30", periods=4, freq="D")  # 30, 31 Jan; 1, 2 Feb
    x = pd.Series([1.0, 3.0, 5.0, 7.0], index=idx)
    assert list(transform.apply("monthly_mean", [x])) == [2.0, 6.0]
    assert list(transform.apply("monthly_last", [x])) == [3.0, 7.0]


def test_nice_ticks_cover_range():
    ticks = charts.nice_ticks(-0.3, 11.1)
    assert ticks[0] <= -0.3 and ticks[-1] >= 10 and len(ticks) <= 6


def test_off_scale_note_names_the_clipped_period():
    idx = pd.period_range("2020-01", periods=4, freq="M")
    note = charts.off_scale_note(pd.Series([1.0, -20.0, 25.0, 2.0], index=idx), -5, 10, "%", 1)
    assert "Feb 2020" in note and "Mar 2020" in note and "−20.0%" in note


def test_charts_prepare_and_render_from_config():
    cfg = config.load(ROOT)
    m = pd.period_range("2015-01", "2026-08", freq="M")
    d = pd.period_range("2015-01-01", "2026-09-23", freq="D")
    data = {"D7G7": pd.Series(2.0, index=m), "ECY2": pd.Series(100.0, index=m),
            "MGSX": pd.Series(4.5, index=m), "IUDBEDR": pd.Series(3.75, index=d),
            "XUDLUSS": pd.Series(1.3, index=d)}
    prepared = charts.prepare(cfg, data, pd.Timestamp("2026-09-24"))
    assert [c.id for c in prepared] == ["cpi", "gdp", "unemployment", "bank_rate", "cable"]
    html = charts.section(prepared, 1)
    assert html.count("<svg") == 5 and "3.75%" in html and "$1.30" in html
