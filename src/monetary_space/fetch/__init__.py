"""One module per publisher. FETCHERS maps a config `fetcher` name to a callable."""
from __future__ import annotations

import pandas as pd

from . import boe, fred, oecd, ons

FETCHERS = {
    "ons_timeseries": lambda s: ons.timeseries(s["uri"], s["freq"]),
    "ons_rti_payrolls": lambda s: ons.rti_payrolls(s["uri"]),
    "dmp_price_growth": lambda s: boe.dmp_price_growth(),
    "ias_median_1y": lambda s: boe.ias_median_1y(),
    "agents_capacity": lambda s: boe.agents_capacity(),
    "boe_iadb": lambda s: boe.iadb(s["code"], s.get("start", "01/Jan/1990")),
    "ons_sap_gas": lambda s: ons.sap_gas(s["uri"]),
    "oecd_cli": lambda s: oecd.cli(s["areas"], s.get("start", "1985-01")),
    "fred": lambda s: fred.series(s["code"], s.get("freq", "D")),
    "boe_ois_spot": lambda s: boe.ois_spot(s["maturity"]),
    "boe_ois_forwards": lambda s: boe.ois_forwards(s["maturities"], s.get("since", "2024-01-01")),
}


def fetch(spec: dict) -> pd.Series | dict[str, pd.Series]:
    """One series, or a dict of named series (stored as '<series id>:<name>')."""
    s = FETCHERS[spec["fetcher"]](spec)
    for x in (s.values() if isinstance(s, dict) else [s]):
        x.index.name = None
    return s
