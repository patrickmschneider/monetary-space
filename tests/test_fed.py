"""FOMC calendar, statement and SEP parsers, the Fed staff curve, and the NY Fed and Atlanta Fed
surveys (fixtures mirror federalreserve.gov and the survey workbooks, trimmed)."""
import io

import numpy as np
import pandas as pd
import pytest

from monetary_space.fetch import fed, fred

CALENDAR = """<div class="panel panel-default"><div class="panel-heading"><h4><a id="42828">2026 FOMC Meetings</a></h4></div>
<div class="row fomc-meeting"><div class="fomc-meeting__month col-xs-5"><strong>July</strong></div>
<div class="fomc-meeting__date col-xs-4">28-29</div><div class="col-xs-12">
<strong>Statement:</strong><br><a href="/monetarypolicy/files/monetary20260729a1.pdf">PDF</a> | <a href="/newsevents/pressreleases/monetary20260729a.htm">HTML</a></div></div>
<div class="row fomc-meeting"><div class="fomc-meeting__month col-xs-5"><strong>September</strong></div>
<div class="fomc-meeting__date col-xs-4">15-16*</div><div class="col-xs-12">
<a href="/newsevents/pressreleases/monetary20260916a.htm">HTML</a>
<strong>Projection Materials</strong><br><a href="/monetarypolicy/fomcprojtabl20260916.htm">HTML</a></div></div>
<div class="row fomc-meeting"><div class="fomc-meeting__month col-xs-5"><strong>Oct/Nov</strong></div>
<div class="fomc-meeting__date col-xs-4">31-1</div><div class="col-xs-12"></div></div>
<div class="row fomc-meeting"><div class="fomc-meeting__month col-xs-5"><strong>December</strong></div>
<div class="fomc-meeting__date col-xs-4">8-9*</div><div class="col-xs-12"></div></div>
<div class="row fomc-meeting"><div class="fomc-meeting__month col-xs-5"><strong>October</strong></div>
<div class="fomc-meeting__date col-xs-4 col-lg-2">22 (notation vote)</div></div>
</div>"""

# 2026 format: the count in the preamble, dissents named
STATEMENT_2026 = """<p>The Federal Open Market Committee approved the following statement for release by a 9 &ndash; 3 vote:</p>
<p>The Committee decided to maintain the target range for the federal funds rate at 3-1/2 to 3-3/4 percent, in support of
the Federal Reserve's dual mandate.</p><p>Voting against the monetary policy action were Beth M. Hammack, Neel Kashkari,
and Lorie K. Logan, who preferred to raise the target range for the federal funds rate by 1/4 percentage point at this
meeting.</p><p>For media inquiries, please email us.</p>"""

# 2025 format: every voter named; two dissent groups; a non-breaking hyphen in the range
STATEMENT_2025 = """<p>The Committee decided to lower the target range for the federal funds rate by 1/4 percentage point to
3-1/2 to 3‑3/4 percent.</p><p>Voting for the monetary policy action were Jerome H. Powell, Chair; John C. Williams,
Vice Chair; Michael S. Barr; Michelle W. Bowman; Susan M. Collins; Lisa D. Cook; Philip N. Jefferson; Alberto G. Musalem;
and Christopher J. Waller. Voting against this action were Stephen I. Miran, who preferred to lower the target range for
the federal funds rate by 1/2 percentage point at this meeting; and Austan D. Goolsbee and Jeffrey R. Schmid, who
preferred no change to the target range for the federal funds rate at this meeting. For media inquiries, please email.</p>"""

# Dissents with different verbs, and a sentence after the dissents
STATEMENT_SUPPORTED = """<p>The Committee decided to maintain the target range for the federal funds rate at 3-1/2 to 3-3/4
percent.</p><p>Voting for the monetary policy action were Jerome H. Powell, Chair; John C. Williams, Vice Chair; Michael S.
Barr; Michelle W. Bowman; Lisa D. Cook; Philip N. Jefferson; Alberto G. Musalem; and Christopher J. Waller. Voting against
this action were Stephen I. Miran, who preferred to lower the target range for the federal funds rate by 1/4 percentage
point at this meeting; and Beth M. Hammack, Neel Kashkari, and Lorie K. Logan, who supported maintaining the target range
for the federal funds rate but did not support inclusion of an easing bias in the statement at this time. Absent and not
voting was Adriana D. Kugler. For media inquiries, please email.</p>"""

SEP = """Table 1. Economic projections of Federal Reserve Board members and Federal Reserve Bank presidents, September 2026
Percent Variable Median 1 Central Tendency 2 Range 3 2026 2027 2028 2029 Longer run 2026 2027 2028 2029 Longer run
Change in real GDP 2.3 2.4 2.2 2.1 2.0 2.2–2.4 2.2–2.6 2.1–2.3 2.0–2.2 2.0–2.2
Unemployment rate 4.1 4.1 4.1 4.1 4.2 4.1–4.2 4.0–4.2 4.0–4.2 4.0–4.3 4.0–4.3
PCE inflation 3.7 2.3 2.1 2.0 2.0 3.5–3.7 2.2–2.5 2.0–2.2 2.0 2.0
Core PCE inflation 4 3.4 2.4 2.1 2.0 3.3–3.5 2.3–2.6 2.0–2.2 2.0
Federal funds rate 4.1 4.1 3.9 3.6 3.2 4.1–4.4 3.6–4.4 3.1–4.1 3.1–3.6 3.0–3.6"""


def test_calendar_dates_links_and_seps():
    cal = fed.parse_calendar(CALENDAR)
    assert list(cal["date"].dt.strftime("%Y-%m-%d")) == ["2026-07-29", "2026-09-16", "2026-11-01", "2026-12-09"]
    assert list(cal["sep"]) == [False, True, False, True]
    assert cal.loc[1, "sep_url"].endswith("fomcprojtabl20260916.htm")
    assert cal.loc[2, "statement_url"] == ""                       # future meeting: date from the calendar text


def test_statement_with_vote_count():
    d = fed.parse_statement(STATEMENT_2026)
    assert d["bank_rate"] == 3.625 and d["range"] == "3.5-3.75"
    assert d["vote"] == "9-3: 9 hold; 3 preferred to raise the range by 0.25pp (Hammack, Kashkari, Logan)"


def test_statement_with_named_voters_and_two_dissent_groups():
    d = fed.parse_statement(STATEMENT_2025)
    assert d["bank_rate"] == 3.625
    assert d["vote"] == ("9-3: 9 cut; 1 preferred to lower the range by 0.5pp (Miran); "
                         "2 preferred no change to the range (Goolsbee, Schmid)")


def test_statement_dissent_verbs_and_trailing_sentence():
    d = fed.parse_statement(STATEMENT_SUPPORTED)
    assert d["vote"].startswith("8-4: 8 hold; 1 preferred to lower the range by 0.25pp (Miran); 3 supported maintaining")
    assert d["vote"].endswith("(Hammack, Kashkari, Logan)") and "Kugler" not in d["vote"]


def test_sep_medians_and_year_ahead_interpolation():
    p = fed.parse_sep(SEP, 2026)
    assert (p["pce_2026"], p["pce_2027"], p["u_star"], p["ffr_lr"], p["potential_growth"]) == (3.7, 2.3, 4.2, 3.2, 2.0)
    assert fed.year_ahead(p, pd.Timestamp("2026-09-16")) == ("2027Q3", 2.65)        # ¼·3.7 + ¾·2.3
    assert fed.year_ahead(p, pd.Timestamp("2026-12-09")) == ("2027Q4", 2.3)          # Q4: the calendar-year median
    assert fed.year_ahead(p, pd.Timestamp("2026-09-16"), 2) == ("2028Q3", 2.15)


def test_svensson_forward_formula():
    p = pd.DataFrame({"BETA0": [4.0], "BETA1": [-1.0], "BETA2": [2.0], "BETA3": [0.5], "TAU1": [1.5], "TAU2": [8.0]})
    m = 2.0
    expected = 4.0 - np.exp(-m / 1.5) + 2.0 * (m / 1.5) * np.exp(-m / 1.5) + 0.5 * (m / 8.0) * np.exp(-m / 8.0)
    assert fed.svensson_forward(p, m).iloc[0] == pytest.approx(expected)
    assert fed.svensson_forward(p, 0.0).iloc[0] == pytest.approx(3.0)          # β0 + β1 at maturity zero


def _xlsx(df: pd.DataFrame, **kw) -> bytes:
    buf = io.BytesIO()
    df.to_excel(buf, index=False, **kw)
    return buf.getvalue()


def test_sme_longer_run_rate_and_growth():
    rows = [("fftr_modalpe_longerrun", "Combined", a, v) for a, v in
            (("count", 62), ("pctl75", 0.035), ("pctl50", 0.0313), ("pctl25", 0.031))]
    rows += [("fftr_modalpe_longerrun", "Dealer", "pctl50", 0.0331),
             ("econoutlook_pathofmodes_realgdpgrowth_longerrun", "Combined", "pctl50", 0.02)]
    df = pd.DataFrame(rows, columns=["value_tag", "panel_type", "aggregation", "aggregation_value"])
    df.insert(0, "survey_release_date", "2026-09-02")
    p = fed.parse_sme(_xlsx(df))
    assert (p["neutral"], p["neutral_p25"], p["neutral_p75"], p["neutral_n"], p["potential"]) == (3.13, 3.1, 3.5, 62, 2.0)


def test_bie_year_ahead_unit_cost_mean():
    cols = 32
    head1 = [None] * cols
    head1[24] = "Question 4: Projecting ahead, to the best of your ability, ..."
    head2 = [None] * cols
    head2[21], head2[29] = "Mean", "Mean"                       # question 3 also has a Mean column
    body = [[pd.Timestamp("2026-09-19")] + [0.5] * 20 + [0.025] + [0.1] * 7 + [0.02366] + [0.0] * 2,
            [pd.Timestamp("2026-10-17")] + [0.5] * 20 + [0.025] + [0.1] * 7 + [0.0230] + [0.0] * 2]
    df = pd.DataFrame([[None] * cols, head1, head2] + body)
    buf = io.BytesIO()
    df.to_excel(buf, sheet_name="BIE Survey results", index=False, header=False)
    s = fed.parse_bie(buf.getvalue())
    assert list(s.index.astype(str)) == ["2026-09", "2026-10"]
    assert s.iloc[-1] == pytest.approx(2.30)


def test_fred_csv_without_a_key():
    s = fred.parse_csv("observation_date,UNRATE\n2026-08-01,4.3\n2026-09-01,.\n2026-10-01,4.2\n", "M", "UNRATE")
    assert list(s.index.astype(str)) == ["2026-08", "2026-10"] and s.iloc[-1] == 4.2
