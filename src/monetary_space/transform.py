"""Series transforms, benchmarks and scales (spec Sections 3–4). Pure pandas functions.

Series carry a pandas PeriodIndex at their native frequency ("M" or "Q").
Statistics are computed at native frequency; only then are quarterly series
carried forward to monthly (the ragged-edge rule: carry forward, never interpolate).
"""
from __future__ import annotations

import pandas as pd

PRE2020_END = pd.Period("2019-12", "M")
MIN_SAMPLE_YEARS = 10


def _one(inputs: list[pd.Series]) -> pd.Series:
    if len(inputs) != 1:
        raise ValueError(f"transform expects one input series, got {len(inputs)}")
    return inputs[0]


def level(inputs: list[pd.Series]) -> pd.Series:
    return _one(inputs)


def ratio(inputs: list[pd.Series]) -> pd.Series:
    if len(inputs) != 2:
        raise ValueError("ratio expects [numerator, denominator]")
    num, den = inputs
    return (num / den).dropna()


def annualised_3m3m(inputs: list[pd.Series]) -> pd.Series:
    """Growth of the latest three months on the previous three, annualised, in %."""
    x = _one(inputs)
    if x.index.freqstr != "M":
        raise ValueError("3m/3m growth needs a monthly series")
    s3 = x.rolling(3).sum()
    return ((s3 / s3.shift(3)) ** 4 - 1).mul(100).dropna()


def pct_change_12m(inputs: list[pd.Series]) -> pd.Series:
    x = _one(inputs)
    periods = 12 if x.index.freqstr == "M" else 4
    return x.pct_change(periods, fill_method=None).mul(100).dropna()


def growth_3m_yoy(inputs: list[pd.Series]) -> pd.Series:
    """Latest three months on the same three months a year earlier, in %."""
    x = _one(inputs)
    s3 = x.rolling(3).sum()
    return (s3 / s3.shift(12) - 1).mul(100).dropna()


def monthly_mean(inputs: list[pd.Series]) -> pd.Series:
    x = _one(inputs)
    return x.groupby(x.index.asfreq("M")).mean()


def monthly_last(inputs: list[pd.Series]) -> pd.Series:
    x = _one(inputs)
    return x.groupby(x.index.asfreq("M")).last()


TRANSFORMS = {
    "level": level,
    "ratio": ratio,
    "annualised_3m3m": annualised_3m3m,
    "pct_change_12m": pct_change_12m,
    "growth_3m_yoy": growth_3m_yoy,
    "monthly_mean": monthly_mean,
    "monthly_last": monthly_last,
}


def apply(name: str, inputs: list[pd.Series], drop_last: int = 0) -> pd.Series:
    """Apply a named transform. drop_last removes flash observations first."""
    if name not in TRANSFORMS:
        raise ValueError(f"unknown transform {name!r}; options: {sorted(TRANSFORMS)}")
    if drop_last:
        inputs = [s.iloc[:-drop_last] for s in inputs]
    return TRANSFORMS[name](inputs).astype(float)


def pre2020(x: pd.Series) -> pd.Series:
    return x[x.index.to_timestamp(how="end") <= PRE2020_END.to_timestamp(how="end")]


def sample_years(x: pd.Series) -> float:
    per_year = 12 if x.index.freqstr == "M" else 4
    return len(x) / per_year


def pre2020_mean(x: pd.Series) -> float:
    sample = pre2020(x)
    if sample.empty:
        raise ValueError("no pre-2020 observations for a pre-2020 mean")
    return float(sample.mean())


def pre2020_sd(x: pd.Series) -> float:
    """Step 2: standard deviation over the full pre-2020 sample (needs ≥10 years)."""
    sample = pre2020(x)
    years = sample_years(sample)
    if years < MIN_SAMPLE_YEARS:
        raise ValueError(
            f"only {years:.1f} years before 2020; set a config sigma with a rationale"
        )
    return float(sample.std(ddof=1))


def to_monthly(x: pd.Series) -> pd.Series:
    """Quarterly → monthly, each quarter's value stamped on its last month."""
    if x.index.freqstr == "M":
        return x
    out = x.copy()
    out.index = x.index.asfreq("M", how="end")
    return out


def carry_forward(x: pd.Series, until: pd.Period) -> pd.Series:
    """Monthly series extended to `until` by carrying the latest value forward."""
    m = to_monthly(x)
    idx = pd.period_range(m.index.min(), max(until, m.index.max()), freq="M")
    return m.reindex(idx).ffill()
