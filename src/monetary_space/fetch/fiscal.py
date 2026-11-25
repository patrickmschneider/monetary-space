"""UK public finances by fiscal year, from the Fiscal Space dashboard's published outlook.

Fiscal Space compiles the OBR public finances databank (outturn from 1975-76) and the
latest OBR Economic and fiscal outlook (forecast). Fiscal years run April–March and are
stored as annual periods ending in March: 2026-27 is Period("2027", "Y-MAR").

Series returned (% of GDP, positive = deficit):
  PSNB  public sector net borrowing (headline deficit)
  CAPD  cyclically adjusted primary deficit: borrowing excluding the cycle and debt interest
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


def parse_outlook(payload: dict) -> dict[str, pd.Series]:
    """History from the OBR databank; the latest OBR vintage overrides it where they overlap."""
    vintage = next(v for v in payload["vintages"] if v["id"] == payload["latestVintage"])
    cols = {"PSNB": lambda r: r.get("borrowingPct"),
            "CAPD": lambda r: None if r.get("structuralPrimaryBalancePct") is None else -r["structuralPrimaryBalancePct"]}
    out = {}
    for name, get_value in cols.items():
        values: dict[pd.Period, float] = {}
        for rows in (payload.get("deficitHistory") or [], vintage["rows"]):
            for r in rows:
                v = get_value(r)
                if v is not None:
                    values[fiscal_year(r["year"])] = float(v)
        if not values:
            raise ValueError(f"Fiscal Space outlook has no {name} values")
        s = pd.Series(values, name=name).sort_index()
        s.index = pd.PeriodIndex(s.index, freq=FY)
        dates = [vintage.get("publicationDate"), (payload.get("deficitHistoryMetadata") or {}).get("outturnAsOf")]
        s.attrs.update(released=max(pd.Timestamp(d) for d in dates if d), next_release="")
        out[name] = s
    return out


def outlook(url: str) -> dict[str, pd.Series]:
    return parse_outlook(get(url).json())



# --- Headline and primary deficits, United States and Australia --------------------------------
# Rolling one-year sums, % of GDP, positive = deficit. Primary = excluding net interest.

def rolling_pct(flow: pd.Series, gdp: pd.Series, n: int) -> pd.Series:
    """Sum of the last n periods of a flow as % of GDP over the same periods (GDP at the flow's frequency)."""
    return (flow.rolling(n).sum() / gdp.reindex(flow.index).rolling(n).sum() * 100).dropna()


# United States: Monthly Treasury Statement, federal government (released about the 8th business
# day of the next month). Net interest (MTS Table 9) starts in March 2015, so the primary deficit
# starts in February 2016.
MTS_DEFICIT = "MTSDS133FMS"            # FRED: federal surplus or deficit (−), $ millions, monthly
MTS_TABLE9 = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9"


def monthly_gdp(gdp_saar: pd.Series, until: pd.Period) -> pd.Series:
    """Quarterly nominal GDP at an annual rate ($ billions) → $ millions a month, each quarter's value
    on its three months, the latest quarter carried forward to `until`."""
    m = pd.Series({p: v for q, v in gdp_saar.items() for p in pd.period_range(q.asfreq("M", "start"), q.asfreq("M", "end"))})
    m.index = pd.PeriodIndex(m.index, freq="M")
    return m.reindex(pd.period_range(m.index[0], max(until, m.index[-1]), freq="M")).ffill() * 1000 / 12


def parse_net_interest(rows: list[dict]) -> pd.Series:
    s = pd.Series({pd.Period(r["record_date"][:7], "M"): float(r["current_month_rcpt_outly_amt"]) / 1e6
                   for r in rows if r.get("current_month_rcpt_outly_amt") not in (None, "null")})
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s.sort_index()


def us_deficits(balance: pd.Series, gdp_saar: pd.Series, net_interest: pd.Series) -> dict[str, pd.Series]:
    gdp = monthly_gdp(gdp_saar, balance.index[-1])
    deficit = rolling_pct(-balance, gdp, 12)
    common = net_interest.index.intersection(balance.index)
    primary = rolling_pct(-balance.reindex(common) - net_interest.reindex(common), gdp, 12)
    return {"DEFICIT": deficit.rename("DEFICIT"), "PRIMARY": primary.rename("PRIMARY")}


def us() -> dict[str, pd.Series]:
    from . import fred
    rows = get(MTS_TABLE9, params={"filter": "classification_desc:eq:Net Interest", "sort": "record_date",
                                   "fields": "record_date,current_month_rcpt_outly_amt", "page[size]": 10000}).json()["data"]
    return us_deficits(fred.series(MTS_DEFICIT, "M"), fred.series("GDP", "Q"), parse_net_interest(rows))


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
