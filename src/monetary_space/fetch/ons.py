"""ONS website JSON (the old api.ons.gov.uk was retired in Nov 2024).

Time series: GET https://www.ons.gov.uk{uri}/data returns months/quarters/years.
Datasets: GET {uri}/current/data lists the latest file; download via /file?uri=.
"""
from __future__ import annotations

import io

import pandas as pd

from .http import get

BASE = "https://www.ons.gov.uk"


def parse_timeseries(payload: dict, freq: str) -> pd.Series:
    """ONS /data JSON → Series on a PeriodIndex. Dates look like '2026 JUN' or '2026 Q2'.

    Rolling three-month series (LFS, vacancies) are dated by their middle month,
    with labels like '2026 MAY-JUL'; these are re-stamped on the window's end month.
    """
    key = {"M": "months", "Q": "quarters"}[freq]
    obs = [r for r in payload.get(key) or [] if r["value"] not in ("", None)]
    if not obs:
        raise ValueError(f"no {key} observations in ONS payload")
    values = [r["value"] for r in obs]
    if freq == "M":
        idx = pd.PeriodIndex(pd.to_datetime([r["date"] for r in obs], format="%Y %b"), freq="M")
        rolling = ["-" in r.get("label", "") for r in obs]
        idx = pd.PeriodIndex([p + 1 if roll else p for p, roll in zip(idx, rolling)], freq="M")
    else:
        dates = [r["date"] for r in obs]
        idx = pd.PeriodIndex([d.replace(" ", "") for d in dates], freq="Q")
    return pd.Series(pd.to_numeric(values), index=idx, name=payload["description"]["cdid"]).sort_index()


def timeseries(uri: str, freq: str = "M") -> pd.Series:
    return parse_timeseries(get(BASE + uri + "/data").json(), freq)


def dataset_file(uri: str) -> bytes:
    """Download the current file attached to an ONS dataset page."""
    meta = get(f"{BASE}{uri}/current/data").json()
    name = meta["downloads"][0]["file"]
    return get(f"{BASE}/file?uri={uri}/current/{name}").content


def parse_rti_payrolls(xlsx: bytes) -> pd.Series:
    """PAYE RTI reference table, sheet 1: payrolled employees, UK, seasonally adjusted."""
    df = pd.read_excel(io.BytesIO(xlsx), sheet_name="1. Payrolled employees (UK)", header=None)
    header = df.index[df.iloc[:, 0].astype(str).str.strip().eq("Date")][0]
    body = df.iloc[header + 1 :, :2].dropna()
    idx = pd.PeriodIndex(pd.to_datetime(body.iloc[:, 0].astype(str).str.strip(), format="%B %Y"), freq="M")
    return pd.Series(pd.to_numeric(body.iloc[:, 1]).to_numpy(dtype=float), index=idx, name="RTI_PAYROLLS").sort_index()


def rti_payrolls(uri: str) -> pd.Series:
    return parse_rti_payrolls(dataset_file(uri))
