"""FRED (Federal Reserve Bank of St. Louis). Uses the API when FRED_API_KEY is set (the build on
GitHub), else the public CSV download, which needs no key (local runs)."""
from __future__ import annotations

import io
import os

import pandas as pd

from .http import get

API = "https://api.stlouisfed.org/fred/series/observations"
CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def parse_observations(payload: dict, freq: str, name: str) -> pd.Series:
    obs = [(o["date"], o["value"]) for o in payload["observations"] if o["value"] not in (".", "")]
    if not obs:
        raise ValueError(f"FRED returned no observations for {name}")
    dates, values = zip(*obs)
    idx = pd.PeriodIndex(pd.to_datetime(list(dates)), freq=freq)
    return pd.Series(pd.to_numeric(values), index=idx, name=name).sort_index()


def parse_csv(text: str, freq: str, name: str) -> pd.Series:
    df = pd.read_csv(io.StringIO(text), na_values=["."])
    df = df.dropna(subset=[df.columns[1]])
    if df.empty:
        raise ValueError(f"FRED returned no observations for {name}")
    idx = pd.PeriodIndex(pd.to_datetime(df.iloc[:, 0]), freq=freq)
    return pd.Series(pd.to_numeric(df.iloc[:, 1]).to_numpy(), index=idx, name=name).sort_index()


def series(series_id: str, freq: str = "D") -> pd.Series:
    key = os.environ.get("FRED_API_KEY")
    if key:
        params = {"series_id": series_id, "api_key": key, "file_type": "json"}
        return parse_observations(get(API, params=params).json(), freq, series_id)
    return parse_csv(get(CSV, params={"id": series_id}).text, freq, series_id)


def series_mean(series_ids: list[str], freq: str = "D") -> pd.Series:
    """Mean of several series on their common dates (e.g. the two ends of a target range)."""
    parts = [series(s, freq) for s in series_ids]
    return (sum(parts) / len(parts)).dropna()


def fed_funds_target() -> pd.Series:
    """The FOMC's target: the single target rate until 15 Dec 2008, then the midpoint of the range."""
    single = series("DFEDTAR", "D")
    mid = series_mean(["DFEDTARU", "DFEDTARL"], "D")
    out = pd.concat([single[single.index < mid.index[0]], mid])
    out.name = "FEDFUNDS_TARGET"
    return out
