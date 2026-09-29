"""MPC calendar, decision and MPR projection parsers (fixtures mirror the Bank's page layouts)."""
import pandas as pd

from monetary_space.fetch import mpc

CALENDAR = """<h2>2026 confirmed dates</h2> <table> <tbody>
<tr> <td>Thursday 5 November</td> <td><a href="/monetary-policy-summary-and-minutes/2026/november-2026">November MPC
Summary and minutes</a> and <a href="/monetary-policy-report/2026/november-2026">November Monetary Policy Report</a></td> </tr>
<tr> <td>Thursday&nbsp;17 December</td> <td><a href="/monetary-policy-summary-and-minutes/2026/december-2026">December</a></td> </tr>
</tbody> </table>
<h2>2027 confirmed dates</h2> <table> <tbody>
<tr> <td>Thursday&nbsp;4 February</td> <td><span><a href="/monetary-policy-summary-and-minutes/2027/february-2027">x</a> and
<a href="/monetary-policy-report/2027/february-2027">y</a>&nbsp;</span></td> </tr> </tbody> </table>"""

MAJORITY = """<p>At its meeting ending on 16 September 2026, the MPC voted by a majority of 6&ndash;3 to maintain Bank Rate
at 3.75%. Three members voted to increase Bank Rate by 0.25 percentage points, to 4%.</p>"""
CUT = """<p>The MPC voted by a majority of 5–4 to reduce Bank Rate by 0.25 percentage points, to 3.75%. Four members
voted to maintain Bank Rate at 4%.</p>"""
UNANIMOUS = "<p>The Committee voted unanimously to maintain Bank Rate at 3.75%.</p>"

PROJECTION = """<table><tr><th></th><th>2026 Q3</th><th>2027 Q3</th><th>2028 Q3</th><th>2029 Q3</th></tr>
<tr><td>Central projection</td></tr><tr><td>CPI inflation <sup>(b)</sup></td><td>2.9</td><td>2.6</td><td>1.8</td><td>1.9</td></tr>
<tr><td>GDP <sup>(c)</sup></td><td>1.1</td><td>1.1</td><td>1.7</td><td>1.6</td></tr></table>"""


def test_calendar():
    cal = mpc.parse_calendar(CALENDAR)
    assert list(cal["date"].dt.strftime("%Y-%m-%d")) == ["2026-11-05", "2026-12-17", "2027-02-04"]
    assert list(cal["mpr_url"].notna()) == [True, False, True]


def test_decisions():
    d = mpc.parse_decision(MAJORITY)
    assert d["bank_rate"] == 3.75 and d["vote"].startswith("6–3: Three members voted to increase")
    assert mpc.parse_decision(CUT)["bank_rate"] == 3.75
    assert mpc.parse_decision(CUT)["vote"].startswith("5–4")
    assert mpc.parse_decision(UNANIMOUS) == {"bank_rate": 3.75, "vote": "9–0: unanimous"}
    assert mpc.parse_decision("<p>Minutes will be published at noon.</p>") is None


def test_projection():
    p = mpc.parse_projection(PROJECTION)
    assert p == {"cpi_1y_quarter": "2027Q3", "cpi_1y": 2.6, "cpi_2y_quarter": "2028Q3", "cpi_2y": 1.8}
    assert mpc.parse_projection("<table><tr><td>Something else</td></tr></table>") is None


def test_refresh_fills_only_missing(monkeypatch):
    pages = {mpc.CALENDAR: CALENDAR,
             "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/november-2026": MAJORITY,
             "https://www.bankofengland.co.uk/monetary-policy-report/2026/november-2026": PROJECTION}
    monkeypatch.setattr(mpc, "get", lambda url: type("R", (), {"text": pages[url], "url": url})())
    dates = pd.DataFrame({"date": ["2026-09-17"], "bank_rate": [3.75], "vote": ["6–3"], "mpr": ["N"], "source_url": ["x"]})
    mpr = pd.DataFrame({"mpr_date": ["2026-07-30"], "cpi_1y_quarter": ["2027Q3"], "cpi_1y": [2.6], "cpi_2y_quarter": ["2028Q3"],
                        "cpi_2y": [1.8], "source_url": ["y"], "notes": [""]})
    d2, m2 = mpc.refresh(dates, mpr, pd.Timestamp("2026-11-05 13:00"))
    assert list(d2["date"]) == ["2026-09-17", "2026-11-05", "2026-12-17", "2027-02-04"]
    assert d2.loc[d2["date"] == "2026-11-05", "vote"].iloc[0].startswith("6–3")
    assert d2.loc[d2["date"] == "2026-12-17", "vote"].isna().all()          # future: not fetched
    assert list(m2["mpr_date"]) == ["2026-07-30", "2026-11-05"] and m2["cpi_1y"].iloc[-1] == 2.6
