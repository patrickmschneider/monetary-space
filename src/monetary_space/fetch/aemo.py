"""AEMO: National Electricity Market wholesale prices.

AEMO publishes one 'aggregated price and demand' CSV per region per month (5-minute intervals
from October 2021, 30-minute before): regional reference price (RRP, $/MWh) and total demand
(MW). The monthly NEM price here is demand-weighted across the five regions and all intervals:
Σ(RRP·demand) / Σ(demand).

Downloading every month since 2005 takes thousands of requests, so the history is built once by
analysis/nem_history.py into analysis/results/au/nem_monthly.csv, and each build re-reads only
the latest months and splices them on.
"""
from __future__ import annotations

import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from .http import get

URL = "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{ym}_{region}.csv"
REGIONS = ("NSW1", "QLD1", "VIC1", "SA1", "TAS1")
HISTORY = Path(__file__).resolve().parents[3] / "analysis" / "results" / "au" / "nem_monthly.csv"


def parse_month(text: str) -> tuple[float, float]:
    """Σ(RRP·demand) and Σ(demand) over a region-month file."""
    df = pd.read_csv(io.StringIO(text))
    return float((df["RRP"] * df["TOTALDEMAND"]).sum()), float(df["TOTALDEMAND"].sum())


def month(p: pd.Period) -> float | None:
    """Demand-weighted NEM price for one month, $/MWh; None if any region's file is missing."""
    num = den = 0.0
    for region in REGIONS:
        try:
            r = get(URL.format(ym=p.strftime("%Y%m"), region=region))
        except requests.RequestException:
            return None
        if not r.text.startswith("REGION"):
            return None
        a, b = parse_month(r.text)
        num, den = num + a, den + b
    return num / den if den else None


def monthly(start: pd.Period, end: pd.Period) -> pd.Series:
    months = list(pd.period_range(start, end, freq="M"))
    with ThreadPoolExecutor(max_workers=8) as pool:
        prices = list(pool.map(month, months))
    return pd.Series({p: v for p, v in zip(months, prices) if v is not None}, dtype=float, name="NEM_PRICE")


def nem_price(months_back: int = 14) -> pd.Series:
    """The stored history with the latest complete months re-read from AEMO."""
    hist = pd.read_csv(HISTORY, comment="#")
    s = pd.Series(hist["price"].to_numpy(float), index=pd.PeriodIndex(hist["month"], freq="M"), name="NEM_PRICE")
    last_full = pd.Period(pd.Timestamp.now(tz="Australia/Sydney").tz_localize(None), "M") - 1
    fresh = monthly(last_full - months_back + 1, last_full)
    if fresh.empty:
        raise RuntimeError("AEMO returned no recent months")
    return pd.concat([s[s.index < fresh.index[0]], fresh]).sort_index()
