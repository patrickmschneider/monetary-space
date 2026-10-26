"""RBA table, decision, schedule and SMP parsers; the ABS API and AEMO price files (fixtures mirror
rba.gov.au, data.api.abs.gov.au and AEMO layouts, trimmed)."""
import pandas as pd
import pytest

from monetary_space.fetch import abs as abs_
from monetary_space.fetch import aemo, rba

TABLE = """﻿G3 INFLATION EXPECTATIONS
Title,Business inflation expectations – 3-months ahead,Union officials' inflation expectations – 1-year ahead
Frequency,Quarterly,Quarterly
Units,Per cent,Per cent
Source,NAB,Workplace Research Centre
Publication date,15-Oct-2026,15-Oct-2026
Series ID,GBUSEXP,GUNIEXPY
30/06/2026,1.9,Not available for publication
30/09/2026,2.0,
"""

DAILY = """Title,Cash Rate Target
Series ID,FIRMMCRTD
28-Sep-2026,4.35
30-Sep-2026,4.60
"""

SCHEDULE = """<h2>Board meeting schedules 2026</h2><table><tr><th>Month</th><th>Monetary Policy Board</th><th>Payments System Board</th></tr>
<tr><td>February</td><td>2–3 February</td><td></td></tr><tr><td>March</td><td>16–17 March</td><td>5 March</td></tr>
<tr><td>November</td><td>2–3 November</td><td>19 November</td></tr></table>
<h2>Board meeting schedules 2027</h2><table><tr><th>Month</th><th>Monetary Policy Board</th><th>Payments System Board</th></tr>
<tr><td>February</td><td>8–9 February</td><td>24 February</td></tr></table><h2>Related Information</h2>"""

LINKS = """<li><a href="/media-releases/2026/mr-26-27.html">29 September 2026</a></li>
<li><a href="/media-releases/2026/mr-26-12.html">5 May 2026</a></li>"""

UNANIMOUS = """<p>At its meeting today, the Board decided to increase the cash rate target by 25 basis points to 4.60 per cent.</p>
<h2>Decision</h2><p>Today’s policy decision was unanimous.</p>"""
MAJORITY_WORDS = """<p>At its meeting today, the Board decided to increase the cash rate target by 25 basis points to 4.35 per cent.</p>
<p>Today’s policy decision was made by majority: eight members voted to increase the cash rate target by 25&nbsp;basis
points to 4.35&nbsp;per&nbsp;cent; one member voted to leave the cash rate target unchanged at 4.10&nbsp;per&nbsp;cent.</p>"""
MAJORITY_COUNT = """<p>At its meeting today, the Board decided to leave the cash rate target unchanged at 3.85 per cent.</p>
<p>Today’s policy decision was made by majority: 6 in favour, 3 against.</p>"""
NO_TARGET_NO_VOTE = "<p>At its meeting today, the Board decided to leave the cash rate unchanged at 3.60 per cent.</p>"

SMP = """<table><caption>Table 3.1: Detailed Forecast Table</caption><tr><th></th><th>Jun 2026</th><th>Dec 2026</th>
<th>Jun 2027</th><th>Dec 2027</th><th>Jun 2028</th><th>Dec 2028</th></tr>
<tr><td>Gross domestic product</td><td>1.9</td><td>1.4</td><td>1.5</td><td>1.6</td><td>1.6</td><td>1.8</td></tr>
<tr><td>Terms of trade</td><td>&minus;3.1</td><td>&minus;2.8</td><td>0.7</td><td>0.5</td><td>0.5</td><td>1.1</td></tr>
<tr><td>Consumer Price Index</td><td>3.9</td><td>3.6</td><td>2.8</td><td>2.6</td><td>2.4</td><td>2.4</td></tr>
<tr><td>Trimmed mean inflation</td><td>3.6</td><td>3.3</td><td>3.0</td><td>2.6</td><td>2.4</td><td>2.4</td></tr></table>"""


def test_table_series_drops_text_and_reads_both_date_formats():
    s = rba.table_series(TABLE, "GBUSEXP", "Q")
    assert list(s.index.astype(str)) == ["2026Q2", "2026Q3"] and s.iloc[-1] == 2.0
    with pytest.raises(ValueError):
        rba.table_series(TABLE, "GUNIEXPY", "Q")              # only 'Not available' and blanks
    d = rba.table_series(DAILY, "FIRMMCRTD", "D")
    assert str(d.index[-1]) == "2026-09-30" and d.iloc[-1] == 4.6


def test_schedule_takes_the_decision_day():
    sch = rba.parse_schedule(SCHEDULE)
    assert list(sch["date"].dt.strftime("%Y-%m-%d")) == ["2026-02-03", "2026-03-17", "2026-11-03", "2027-02-09"]


def test_decision_links():
    links = rba.parse_decision_links(LINKS)
    assert links[pd.Timestamp("2026-09-29")].endswith("/media-releases/2026/mr-26-27.html")


@pytest.mark.parametrize("page,rate,vote", [
    (UNANIMOUS, 4.60, "unanimous: raise"),
    (MAJORITY_WORDS, 4.35, "8-1: 8 raise; 1 hold"),
    (MAJORITY_COUNT, 3.85, "6-3: 6 hold; 3 against"),
    (NO_TARGET_NO_VOTE, 3.60, ""),
])
def test_decisions(page, rate, vote):
    d = rba.parse_decision(page)
    assert d["bank_rate"] == pytest.approx(rate) and d["vote"] == vote


def test_smp_headline_cpi_and_year_ahead():
    pts = rba.parse_smp(SMP)
    assert pts == {"2026Q2": 3.9, "2026Q4": 3.6, "2027Q2": 2.8, "2027Q4": 2.6, "2028Q2": 2.4, "2028Q4": 2.4}
    assert rba.year_ahead(pts, pd.Timestamp("2026-08-11")) == ("2027Q3", 2.7)      # halfway between 2.8 and 2.6
    assert rba.year_ahead(pts, pd.Timestamp("2026-05-05")) == ("2027Q2", 2.8)      # on a half-year point
    assert rba.year_ahead(pts, pd.Timestamp("2028-02-03")) is None                 # beyond the table


def test_abs_csv_quarters():
    text = ("DATAFLOW,MEASURE,INDEX,FREQ,TIME_PERIOD,OBS_VALUE\nABS:ITPI_IMP(1.0.0),1,6011001,Q,2026-Q1,135.5\n"
            "ABS:ITPI_IMP(1.0.0),1,6011001,Q,2026-Q2,143.2\n")
    s = abs_.parse_csv(text, "Q", "ITPI_IMP")
    assert list(s.index.astype(str)) == ["2026Q1", "2026Q2"] and s.iloc[-1] == 143.2


def test_aemo_demand_weighted_month():
    text = ("REGION,SETTLEMENTDATE,TOTALDEMAND,RRP,PERIODTYPE\nNSW1,2026/09/01 00:05:00,100,50,TRADE\n"
            "NSW1,2026/09/01 00:10:00,300,150,TRADE\n")
    num, den = aemo.parse_month(text)
    assert num / den == pytest.approx((100 * 50 + 300 * 150) / 400)


def test_asx_futures_curve_by_maturity_from_settlement():
    text = ('{"Crnt_Stlmnt_Dt": "2026-10-26", "RBA_Trgt_Cash_Rate": 4.6, "months": ['
            '{"Expiry_Month": "Oct-26", "Implied_Yield": 4.6}, {"Expiry_Month": "Nov-26", "Implied_Yield": 4.74},'
            '{"Expiry_Month": "Mar-28", "Implied_Yield": 4.725}]}')
    c = rba.parse_asx_curve(text)
    assert list(c) == ["0.0548", "1.3854"]                       # October is half over: skipped; mid-November = 20 days
    assert str(c["0.0548"].index[0]) == "2026-10-26" and c["1.3854"].iloc[0] == 4.725
