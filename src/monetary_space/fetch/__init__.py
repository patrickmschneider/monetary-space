"""One module per publisher. FETCHERS maps a config `fetcher` name to a callable."""
from __future__ import annotations

import pandas as pd

from . import boe, ons

FETCHERS = {
    "ons_timeseries": lambda s: ons.timeseries(s["uri"], s["freq"]),
    "ons_rti_payrolls": lambda s: ons.rti_payrolls(s["uri"]),
    "dmp_price_growth": lambda s: boe.dmp_price_growth(),
    "ias_median_1y": lambda s: boe.ias_median_1y(),
    "agents_capacity": lambda s: boe.agents_capacity(),
}


def fetch(spec: dict) -> pd.Series:
    s = FETCHERS[spec["fetcher"]](spec)
    s.index.name = None
    return s
