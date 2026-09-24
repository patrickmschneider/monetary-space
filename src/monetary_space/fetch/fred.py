"""FRED (Federal Reserve Bank of St. Louis). Needs FRED_API_KEY in the environment."""
from __future__ import annotations

import os

import pandas as pd

from .http import get

API = "https://api.stlouisfed.org/fred/series/observations"


def parse_observations(payload: dict, freq: str, name: str) -> pd.Series:
    obs = [(o["date"], o["value"]) for o in payload["observations"] if o["value"] not in (".", "")]
    if not obs:
        raise ValueError(f"FRED returned no observations for {name}")
    dates, values = zip(*obs)
    idx = pd.PeriodIndex(pd.to_datetime(list(dates)), freq=freq)
    return pd.Series(pd.to_numeric(values), index=idx, name=name).sort_index()


def series(series_id: str, freq: str = "D") -> pd.Series:
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise RuntimeError("FRED_API_KEY is not set")
    params = {"series_id": series_id, "api_key": key, "file_type": "json"}
    return parse_observations(get(API, params=params).json(), freq, series_id)
