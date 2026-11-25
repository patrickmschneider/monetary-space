"""Government deficits, % of GDP, positive = deficit: headline, and primary (excluding net interest).

Each edition uses its most timely official figures: rolling one-year sums of the monthly public
sector finances (UK) and Monthly Treasury Statement (US), and of the quarterly national accounts
(Australia). Fiscal-year helpers stay for annual April–March periods ("Y-MAR").
"""
from __future__ import annotations

import pandas as pd

from .http import get

FY = "Y-MAR"


def fiscal_year(label: str) -> pd.Period:
    """'2026-27' → the fiscal year ending March 2027."""
    return pd.Period(str(int(label[:4]) + 1), FY)


def fy_label(p: pd.Period) -> str:
    return f"{p.year - 1}-{p.year % 100:02d}"


# --- Headline and primary deficits: UK, United States, Australia ---------------------------------
# Rolling one-year sums, % of GDP, positive = deficit. Primary = excluding net interest.

def rolling_pct(flow: pd.Series, gdp: pd.Series, n: int) -> pd.Series:
    """Sum of the last n periods of a flow as % of GDP over the same periods (GDP at the flow's frequency)."""
    return (flow.rolling(n).sum() / gdp.reindex(flow.index).rolling(n).sum() * 100).dropna()


# United States: Monthly Treasury Statement, federal government (released about the 8th business
# day of the next month). Net interest (MTS Table 9) starts in March 2015, so the primary deficit
# starts in February 2016.
MTS_DEFICIT = "MTSDS133FMS"            # FRED: federal surplus or deficit (−), $ millions, monthly
MTS_TABLE9 = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9"


def monthly_gdp(gdp_q: pd.Series, until: pd.Period, per_month: float) -> pd.Series:
    """Quarterly nominal GDP → a monthly flow (each quarter's value × per_month on its three months),
    the latest quarter carried forward to `until`."""
    m = pd.Series({p: v for q, v in gdp_q.items() for p in pd.period_range(q.asfreq("M", "start"), q.asfreq("M", "end"))})
    m.index = pd.PeriodIndex(m.index, freq="M")
    return m.reindex(pd.period_range(m.index[0], max(until, m.index[-1]), freq="M")).ffill() * per_month


def monthly_deficits(deficit: pd.Series, interest: pd.Series, gdp_m: pd.Series) -> dict[str, pd.Series]:
    """12-month sums of monthly deficit and deficit less net interest, % of GDP (same currency units)."""
    common = interest.index.intersection(deficit.index)
    return {"DEFICIT": rolling_pct(deficit, gdp_m, 12).rename("DEFICIT"),
            "PRIMARY": rolling_pct(deficit.reindex(common) - interest.reindex(common), gdp_m, 12).rename("PRIMARY")}


def parse_net_interest(rows: list[dict]) -> pd.Series:
    s = pd.Series({pd.Period(r["record_date"][:7], "M"): float(r["current_month_rcpt_outly_amt"]) / 1e6
                   for r in rows if r.get("current_month_rcpt_outly_amt") not in (None, "null")})
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s.sort_index()


def us_deficits(balance: pd.Series, gdp_saar: pd.Series, net_interest: pd.Series) -> dict[str, pd.Series]:
    """balance: $ millions (negative = deficit); GDP: $ billions at an annual rate; net interest: $ millions."""
    return monthly_deficits(-balance, net_interest, monthly_gdp(gdp_saar, balance.index[-1], 1000 / 12))


def us() -> dict[str, pd.Series]:
    from . import fred
    rows = get(MTS_TABLE9, params={"filter": "classification_desc:eq:Net Interest", "sort": "record_date",
                                   "fields": "record_date,current_month_rcpt_outly_amt", "page[size]": 10000}).json()["data"]
    return us_deficits(fred.series(MTS_DEFICIT, "M"), fred.series("GDP", "Q"), parse_net_interest(rows))


# United Kingdom: ONS public sector finances (released about the 20th of the next month), public
# sector excluding public sector banks; net interest is central government's (local government
# interest is small). First estimates are revised, sometimes by several £bn.
ONS_PSF = "/economy/governmentpublicsectorandtaxes/publicsectorfinance/timeseries/"
UK_SERIES = {"borrowing": ONS_PSF + "j5ii/pusf",     # PSNB ex, £m, negative = borrowing, from 1993
             "interest": ONS_PSF + "nmfx/pusf",      # central government net interest payable, £m, from April 1997
             "gdp": "/economy/grossdomesticproductgdp/timeseries/ybha/pn2"}   # nominal GDP, £m a quarter


def uk_deficits(borrowing: pd.Series, interest: pd.Series, gdp_q: pd.Series) -> dict[str, pd.Series]:
    return monthly_deficits(-borrowing, interest, monthly_gdp(gdp_q, borrowing.index[-1], 1 / 3))


def uk() -> dict[str, pd.Series]:
    from . import ons
    return uk_deficits(ons.timeseries(UK_SERIES["borrowing"], "M"), ons.timeseries(UK_SERIES["interest"], "M"),
                       ons.timeseries(UK_SERIES["gdp"], "Q"))


# Australia: ABS national accounts (5206.0), general government (all levels), original series,
# released with GDP about nine weeks after the quarter. Net lending is approximated by net saving
# less net investment (gross fixed capital formation less depreciation); capital transfers and
# land purchases are not in these tables.
ABS_5206 = "https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release"
ABS_TABLES = {"5206017": ["A2302280A", "A2302109A", "A2302089C", "A2302407X"],   # net saving, interest payable, receivable, depreciation
              "5206003": ["A2302555A", "A2302467A"]}                            # government GFCF, GDP (current prices)


def parse_abs_timeseries(content: bytes) -> dict[str, pd.Series]:
    """An ABS time-series spreadsheet (sheet Data1, series IDs on row 10) → series by ID."""
    import io
    d = pd.read_excel(io.BytesIO(content), sheet_name="Data1", header=None)
    body = d.iloc[10:]
    idx = pd.PeriodIndex(pd.to_datetime(body[0]), freq="Q")
    return {d.iloc[9, j]: pd.Series(pd.to_numeric(body[j], errors="coerce").to_numpy(), index=idx).dropna()
            for j in range(1, d.shape[1])}


def au_deficits(s: dict[str, pd.Series]) -> dict[str, pd.Series]:
    gdp = s["A2302467A"]
    deficit = rolling_pct(s["A2302555A"] - s["A2302407X"] - s["A2302280A"], gdp, 4)
    primary = rolling_pct(s["A2302555A"] - s["A2302407X"] - s["A2302280A"] - s["A2302109A"] + s["A2302089C"], gdp, 4)
    return {"DEFICIT": deficit.rename("DEFICIT"), "PRIMARY": primary.rename("PRIMARY")}


def au() -> dict[str, pd.Series]:
    import re
    page = get(ABS_5206).text
    s: dict[str, pd.Series] = {}
    for table, ids in ABS_TABLES.items():
        href = re.search(rf'href="([^"]*/{table}_[^"]*\.xlsx)"', page)
        if not href:
            raise ValueError(f"ABS 5206.0 latest release has no table {table}")
        got = parse_abs_timeseries(get("https://www.abs.gov.au" + href.group(1)).content)
        s.update({i: got[i] for i in ids})
    return au_deficits(s)
