"""One module per publisher. FETCHERS maps a config `fetcher` name to a callable."""
from __future__ import annotations

import pandas as pd

from . import abs as abs_
from . import aemo, boe, fed, fred, oecd, ons, rba


def _fred(s: dict) -> pd.Series:
    x = fred.series(s["code"], s.get("freq", "D"))
    if s.get("yoy"):                                   # annual rate of an index, % (monthly or quarterly)
        x = (x / x.shift(12 if s.get("freq") == "M" else 4) - 1).dropna() * 100
    return x

FETCHERS = {
    "ons_timeseries": lambda s: ons.timeseries(s["uri"], s["freq"]),
    "ons_rti_payrolls": lambda s: ons.rti_payrolls(s["uri"]),
    "dmp_price_growth": lambda s: boe.dmp_price_growth(),
    "ias_median_1y": lambda s: boe.ias_median_1y(),
    "agents_capacity": lambda s: boe.agents_capacity(),
    "boe_iadb": lambda s: boe.iadb(s["code"], s.get("start", "01/Jan/1990")),
    "ons_sap_gas": lambda s: ons.sap_gas(s["uri"]),
    "oecd_cli": lambda s: oecd.cli(s["areas"], s.get("start", "1985-01")),
    "fred": _fred,
    "fed_funds_target": lambda s: fred.fed_funds_target(),
    "treasury_forwards": lambda s: fed.treasury_forwards(s["maturities"], s.get("since", "2024-01-01")),
    "atlanta_bie": lambda s: fed.bie(),
    "rba": lambda s: rba.series(s["table"], s["code"], s["freq"]),
    "rba_index_from_growth": lambda s: rba.index_from_growth(s["table"], s["code"], s["freq"]),
    "rba_headline_cpi": lambda s: rba.headline_cpi(),
    "asx_cash_futures": lambda s: rba.asx_cash_futures(),
    "rba_f17_forwards": lambda s: rba.f17_forwards(s["maturities"], s.get("since", "2024-01-01")),
    "abs": lambda s: abs_.series(s["flow"], s["key"], s["freq"], s.get("code", "")),
    "aemo_nem": lambda s: aemo.nem_price(),
    "gsw_yield": lambda s: fed.gsw_yields([s["column"]], real=s.get("real", False))[s["column"]],
    "boe_ois_spot": lambda s: boe.ois_spot(s["maturity"]),
    "boe_ois_forwards": lambda s: boe.ois_forwards(s["maturities"], s.get("since", "2024-01-01")),
}


def fetch(spec: dict) -> pd.Series | dict[str, pd.Series]:
    """One series, or a dict of named series (stored as '<series id>:<name>')."""
    s = FETCHERS[spec["fetcher"]](spec)
    for x in (s.values() if isinstance(s, dict) else [s]):
        x.index.name = None
    return s
