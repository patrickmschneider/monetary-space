import pandas as pd
import pytest

from monetary_space import transform


def monthly(values, start="2010-01"):
    return pd.Series(values, index=pd.period_range(start, periods=len(values), freq="M"), dtype=float)


def test_annualised_3m3m():
    x = monthly([100, 100, 100, 101, 101, 101])
    assert transform.apply("annualised_3m3m", [x]).iloc[-1] == pytest.approx((1.01**4 - 1) * 100)


def test_drop_last_removes_flash_month():
    x = monthly([100, 100, 100, 101, 101, 101, 150])
    out = transform.apply("annualised_3m3m", [x], drop_last=1)
    assert out.index[-1] == pd.Period("2010-06", "M")
    assert out.iloc[-1] == pytest.approx((1.01**4 - 1) * 100)


def test_ratio_aligns_on_period():
    v, u = monthly([10, 20, 30]), monthly([20, 40], start="2010-02")
    out = transform.apply("ratio", [v, u])
    assert list(out.index.astype(str)) == ["2010-02", "2010-03"]
    assert list(out) == [1.0, 0.75]


def test_pct_change_12m_monthly_and_quarterly():
    m = monthly([100] * 12 + [110])
    assert transform.apply("pct_change_12m", [m]).iloc[-1] == pytest.approx(10)
    q = pd.Series([100, 100, 100, 100, 105.0], index=pd.period_range("2010Q1", periods=5, freq="Q"))
    assert transform.apply("pct_change_12m", [q]).iloc[-1] == pytest.approx(5)


def test_pre2020_sd_needs_ten_years():
    short = monthly(range(60), start="2015-01")
    with pytest.raises(ValueError, match="config sigma"):
        transform.pre2020_sd(short)
    long = monthly(range(240), start="2000-01")
    assert transform.pre2020_sd(long) == pytest.approx(pd.Series(range(240)).std())


def test_pre2020_excludes_2020_onwards():
    x = monthly([1.0] * 12 + [99.0], start="2019-01")
    assert transform.pre2020_mean(x) == 1.0


def test_quarterly_carried_forward_not_interpolated():
    q = pd.Series([1.0, 3.0], index=pd.period_range("2020Q1", periods=2, freq="Q"))
    out = transform.carry_forward(q, pd.Period("2020-08", "M"))
    assert list(out.index.astype(str)) == ["2020-03", "2020-04", "2020-05", "2020-06", "2020-07", "2020-08"]
    assert list(out) == [1.0, 1.0, 1.0, 3.0, 3.0, 3.0]
