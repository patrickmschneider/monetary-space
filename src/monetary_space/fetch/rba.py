"""Reserve Bank of Australia: statistical tables, Monetary Policy Board decisions and the
Statement on Monetary Policy (SMP) forecasts.

- Statistical tables (rba.gov.au/statistics/tables/csv/<table>.csv): metadata rows, a
  'Series ID' row, then one row per date (dd/mm/yyyy or dd-Mon-yyyy).
- Calendar: /schedules-events/board-meeting-schedules.html lists Monetary Policy Board meetings;
  the decision is announced on the second day.
- Decision: the media release 'Statement by the Monetary Policy Board: Monetary Policy Decision'
  gives the cash rate target and, since 2025, the unattributed vote ('was unanimous', or 'made
  by majority: eight members voted to … one member voted to …').
- SMP: the outlook chapter's detailed forecast table gives year-ended CPI inflation at half-year
  points; the year-ahead value is interpolated between them.

refresh() has the same contract as fetch/mpc.py: it fills only what manual/au/*.csv lack.
"""
from __future__ import annotations

import csv
import html
import io
import re
import time

import numpy as np
import pandas as pd
import requests

from .http import get

RBA = "https://www.rba.gov.au"
TABLE = RBA + "/statistics/tables/csv/{table}.csv"
SCHEDULE = RBA + "/schedules-events/board-meeting-schedules.html"
DECISIONS = RBA + "/monetary-policy/int-rate-decisions/{year}/"
SMP = RBA + "/publications/smp/{year}/{mon}/outlook.html"
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], start=1)}
SMP_MONTHS = {2: "feb", 5: "may", 8: "aug", 11: "nov"}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}


def _text(fragment: str) -> str:
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", fragment)).replace("−", "-").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t).strip()


def _page(url: str) -> str | None:
    time.sleep(0.3)
    try:
        return get(url).content.decode("utf-8", "replace")
    except requests.RequestException:
        return None


# ------------------------------------------------------------------ statistical tables
def parse_table(text: str) -> tuple[list[str], dict[str, list[str]], list[list[str]]]:
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
    i = next(k for k, r in enumerate(rows) if r and r[0].strip() == "Series ID")
    ids = [c.strip() for c in rows[i][1:]]
    meta = {r[0].strip(): r[1:] for r in rows[:i] if r and r[0].strip()}
    return ids, meta, [r for r in rows[i + 1:] if r and r[0].strip()]


def table_series(text: str, series_id: str, freq: str) -> pd.Series:
    """One series from an RBA table at frequency 'D', 'M' or 'Q'; text such as 'Not available' is dropped."""
    ids, _, rows = parse_table(text)
    j = ids.index(series_id) + 1
    out = {}
    for r in rows:
        v = r[j].strip() if len(r) > j else ""
        if not re.fullmatch(r"-?\d+(\.\d+)?", v):
            continue
        out[pd.Period(pd.to_datetime(r[0].strip(), dayfirst=True, format="mixed"), freq)] = float(v)
    if not out:
        raise ValueError(f"RBA series {series_id} has no observations")
    return pd.Series(out, name=series_id).sort_index()


def series(table: str, series_id: str, freq: str) -> pd.Series:
    return table_series(get(TABLE.format(table=table)).content.decode("utf-8-sig", "replace"), series_id, freq)


def index_from_growth(table: str, series_id: str, freq: str = "Q") -> pd.Series:
    """A level index (start = 100) from a published period-on-period growth rate, % (e.g. the WPI)."""
    g = series(table, series_id, freq)
    return ((1 + g / 100).cumprod() * 100).rename(series_id)


def headline_cpi() -> pd.Series:
    """Year-ended headline CPI inflation, monthly: the monthly CPI (G4, from April 2025) spliced onto
    the quarterly CPI (G1), each quarter's value carried across its three months."""
    q = series("g1-data", "GCPIAGYP", "Q")
    m = series("g4-data", "GCPIAGYPM", "M")
    months = pd.period_range(q.index[0].asfreq("M", "start"), q.index[-1].asfreq("M", "end"), freq="M")
    qm = pd.Series([q[p.asfreq("Q")] for p in months], index=months)
    return pd.concat([qm[qm.index < m.index[0]], m]).rename("AU_CPI_YY")


# ------------------------------------------------------------------ forward curve (F17)
def f17_forwards(maturities: list[float], since: str = "2024-01-01") -> dict[str, pd.Series]:
    """Forward rates from the RBA's fitted zero-coupon government curve (F17, daily, published
    monthly): the forward between neighbouring tenors, stamped at the far tenor."""
    ids, meta, rows = parse_table(get(TABLE.format(table="f17-yields")).content.decode("utf-8-sig", "replace"))
    titles = meta["Title"]
    tenor = {}
    for j, t in enumerate(titles):
        m = re.search(r"Zero-coupon yield\s*[–-]\s*([\d.]+)\s*yrs?", t)
        if m and float(m.group(1)) > 0:
            tenor[float(m.group(1))] = j + 1
    df = {}
    for r in rows:
        d = pd.Period(pd.to_datetime(r[0].strip(), dayfirst=True, format="mixed"), "D")
        if d < pd.Period(since, "D"):
            continue
        df[d] = {m: float(r[j]) for m, j in tenor.items() if len(r) > j and r[j].strip()}
    y = pd.DataFrame.from_dict(df, orient="index").sort_index().dropna(how="all")
    out, prev = {}, None
    for m in sorted(tenor):
        fwd = y[m] if prev is None else (y[m] * m - y[prev] * prev) / (m - prev)
        if any(abs(m - x) < 1e-9 for x in maturities):
            out[f"{m:g}"] = fwd.dropna().rename(f"{m:g}")
        prev = m
    return out


# ------------------------------------------------------------------ Monetary Policy Board
def parse_schedule(page: str) -> pd.DataFrame:
    """Monetary Policy Board meeting dates (the decision day is the second day)."""
    t = _text(page)
    rows = []
    for year, body in re.findall(r"Board meeting schedules (\d{4}) Month Monetary Policy Board Payments System Board (.*?)(?=Board meeting schedules \d{4}|Related Information|$)", t):
        for d1, d2, month in re.findall(r"(\d{1,2})[–-](\d{1,2}) ([A-Z][a-z]+)", body):
            rows.append(pd.Timestamp(int(year), MONTHS[month.lower()], int(d2)))
    return pd.DataFrame({"date": sorted(set(rows))})


def parse_decision_links(page: str) -> dict[pd.Timestamp, str]:
    out = {}
    for href, day in re.findall(r'href="(/media-releases/\d{4}/mr-\d{2}-\d{2}\.html)">(\d{1,2} [A-Z][a-z]+ \d{4})</a>', page):
        out[pd.Timestamp(pd.to_datetime(day, format="%d %B %Y"))] = RBA + href
    return out


def parse_decision(page: str) -> dict | None:
    """Cash rate target and the vote, e.g. '8-1: 8 raise; 1 hold' or 'unanimous: hold'."""
    t = _text(page)
    m = re.search(r"decided to (increase|lower|reduce|decrease|leave|maintain|hold)[^.]*?cash rate(?: target)?[^.]*?"
                  r"(?:to|at) (\d+\.\d+) per cent", t)
    if not m:
        return None
    act = {"increase": "raise", "lower": "cut", "reduce": "cut", "decrease": "cut"}.get(m.group(1), "hold")
    vote = ""
    if re.search(r"decision was unanimous", t):
        vote = f"unanimous: {act}"
    elif count := re.search(r"made by majority: (\d+) in favour, (\d+) against", t):
        a, b = int(count.group(1)), int(count.group(2))
        vote = f"{a}-{b}: {a} {act}; {b} against"
    elif maj := re.search(r"made by majority: (.*?)\.(?= [A-Z]|$)", t):
        parts = []
        for n, what in re.findall(r"(\w+) members? voted to (increase|lower|reduce|leave|maintain|hold)", maj.group(1)):
            k = int(n) if n.isdigit() else WORDS.get(n.lower(), 0)
            parts.append((k, {"increase": "raise", "lower": "cut", "reduce": "cut"}.get(what, "hold")))
        if parts:
            vote = "-".join(str(k) for k, _ in parts) + ": " + "; ".join(f"{k} {w}" for k, w in parts)
    return {"bank_rate": float(m.group(2)), "vote": vote}


def parse_smp(page: str) -> dict[str, float] | None:
    """Year-ended headline CPI forecasts by half-year point, e.g. {'2026Q2': 3.9, '2026Q4': 3.6, …}."""
    t = _text(page)
    head = re.search(r"((?:(?:Jun|Dec) \d{4} ){3,})", t)
    row = re.search(r"(?:Consumer Price Index|Headline inflation|CPI inflation)\s*(?:\([a-z]\))?\s+((?:-?\d+(?:\.\d+)?\s+){3,})", t)
    if not head or not row:
        return None
    periods = re.findall(r"(Jun|Dec) (\d{4})", head.group(1))
    vals = [float(v) for v in row.group(1).split()][:len(periods)]
    return {f"{y}Q{2 if m == 'Jun' else 4}": v for (m, y), v in zip(periods, vals)}


def year_ahead(points: dict[str, float], date: pd.Timestamp, ahead: int = 1) -> tuple[str, float] | None:
    """The forecast for the quarter `ahead` years after `date`, interpolated linearly between half-year points."""
    target = pd.Period(date, "Q") + 4 * ahead
    s = pd.Series({pd.Period(k, "Q"): v for k, v in points.items()}).sort_index()
    if target in s.index:
        return str(target), float(s[target])
    before, after = s[s.index < target], s[s.index > target]
    if before.empty or after.empty:
        return None
    (p0, v0), (p1, v1) = (before.index[-1], before.iloc[-1]), (after.index[0], after.iloc[0])
    w = (target - p0).n / (p1 - p0).n
    return str(target), round((1 - w) * v0 + w * v1, 2)


def refresh(mpc_dates: pd.DataFrame, mpr: pd.DataFrame, today: pd.Timestamp | None = None,
            log=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill in Board dates, decisions and SMP forecasts that the CSVs lack. Returns new frames."""
    today = pd.Timestamp(today) if today is not None else pd.Timestamp.now(tz="Australia/Sydney")
    if today.tzinfo is not None:
        today = today.tz_localize(None)
    say = log or (lambda *a: None)
    sched = parse_schedule(get(SCHEDULE).content.decode("utf-8", "replace"))
    links: dict[pd.Timestamp, str] = {}
    for year in range(2024, today.year + 1):
        page = _page(DECISIONS.format(year=year))
        if page:
            links.update(parse_decision_links(page))
    meetings = sorted(set(sched["date"]) | set(links))

    dates = mpc_dates.copy()
    dates["date"] = pd.to_datetime(dates["date"])
    for d in meetings:
        smp = "Y" if d.month in SMP_MONTHS else "N"
        if (dates["date"] == d).any():
            i = dates.index[dates["date"] == d][0]
            dates.loc[i, "mpr"] = smp
        else:
            dates = pd.concat([dates, pd.DataFrame([{"date": d, "mpr": smp, "source_url": links.get(d, "")}])],
                              ignore_index=True)
            i = dates.index[-1]
            say(f"RBA calendar: added {d:%d %b %Y}")
        if d <= today and d in links and pd.isna(dates.loc[i].get("bank_rate")):
            page = _page(links[d])
            dec = parse_decision(page) if page else None
            if dec:
                dates.loc[i, ["bank_rate", "vote", "source_url"]] = [dec["bank_rate"], dec["vote"] or np.nan, links[d]]
                say(f"RBA decision {d:%d %b %Y}: {dec['vote'] or 'vote not published'}, cash rate {dec['bank_rate']}%")

    proj = mpr.copy()
    proj["mpr_date"] = pd.to_datetime(proj["mpr_date"])
    for d in meetings:
        if d.month not in SMP_MONTHS or d > today:
            continue
        existing = proj["mpr_date"] == d
        if existing.any() and proj.loc[existing, "cpi_1y"].notna().all():
            continue
        url = SMP.format(year=d.year, mon=SMP_MONTHS[d.month])
        page = _page(url)
        pts = parse_smp(page) if page else None
        one = year_ahead(pts, d) if pts else None
        if not one:
            say(f"SMP {d:%b %Y}: forecast table not found; left to manual/au/mpr.csv")
            continue
        two = year_ahead(pts, d, 2)
        row = {"mpr_date": d, "cpi_1y_quarter": one[0], "cpi_1y": one[1],
               "cpi_2y_quarter": two[0] if two else np.nan, "cpi_2y": two[1] if two else np.nan,
               "source_url": url,
               "notes": "Read automatically from the SMP forecast table (headline CPI, year-ended) "
                        + ", ".join(f"{k} {v}" for k, v in pts.items()) + "; year-ahead interpolated between half-year points"}
        if existing.any():
            for k, v in row.items():
                proj.loc[existing, k] = v
        else:
            proj = pd.concat([proj, pd.DataFrame([row])], ignore_index=True)
        say(f"SMP {d:%b %Y}: CPI {one[1]}% in {one[0]}")

    dates = dates.sort_values("date").reset_index(drop=True)
    dates["date"] = dates["date"].dt.strftime("%Y-%m-%d")
    proj = proj.sort_values("mpr_date").reset_index(drop=True)
    proj["mpr_date"] = proj["mpr_date"].dt.strftime("%Y-%m-%d")
    return dates, proj


# ------------------------------------------------------------------ ASX 30-day interbank cash rate futures
ASX_CURVE = "https://www.asx.com.au/content/dam/asx/data/yield_curve.csv"


def parse_asx_curve(text: str) -> dict[str, pd.Series]:
    """The ASX RBA Rate Tracker's futures-implied cash rate by contract month (JSON despite the name).
    Each contract settles on the month's average overnight cash rate, so it is dated mid-month and
    stored by maturity in years from the settlement date; months already half over are skipped."""
    import json
    doc = json.loads(text)
    settle = pd.Timestamp(doc["Crnt_Stlmnt_Dt"])
    out = {}
    for m in doc["months"]:
        mid = pd.Timestamp(pd.to_datetime(m["Expiry_Month"], format="%b-%y")) + pd.Timedelta(days=14)
        if mid <= settle:
            continue
        years = (mid - settle).days / 365.25
        out[f"{years:.4f}"] = pd.Series({pd.Period(settle, "D"): float(m["Implied_Yield"])}, name=f"{years:.4f}")
    if not out:
        raise ValueError("ASX yield curve has no future months")
    return out


def asx_cash_futures() -> dict[str, pd.Series]:
    return parse_asx_curve(get(ASX_CURVE, headers={"User-Agent": "Mozilla/5.0"}).text)
