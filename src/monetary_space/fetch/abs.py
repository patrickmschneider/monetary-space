"""Australian Bureau of Statistics Data API (SDMX): data.api.abs.gov.au/rest/data/<flow>/<key>.

A key is the dimension codes in the flow's order, dot-separated, e.g. ITPI_IMP '1.6011001.Q'
(measure 1 = index numbers, index 6011001 = all groups, quarterly).
"""
from __future__ import annotations

import io

import pandas as pd

from .http import get

API = "https://data.api.abs.gov.au/rest/data/{flow}/{key}"


def parse_csv(text: str, freq: str, name: str) -> pd.Series:
    df = pd.read_csv(io.StringIO(text))
    if df.empty or "TIME_PERIOD" not in df:
        raise ValueError(f"ABS returned no observations for {name}")
    df = df.dropna(subset=["OBS_VALUE"])
    idx = pd.PeriodIndex(df["TIME_PERIOD"].str.replace(r"-Q(\d)", r"Q\1", regex=True), freq=freq)
    s = pd.Series(df["OBS_VALUE"].astype(float).to_numpy(), index=idx, name=name)
    return s[~s.index.duplicated(keep="last")].sort_index()


def series(flow: str, key: str, freq: str, name: str = "") -> pd.Series:
    r = get(API.format(flow=flow, key=key), params={"format": "csv"}, timeout=120)
    return parse_csv(r.text, freq, name or f"{flow}:{key}")
