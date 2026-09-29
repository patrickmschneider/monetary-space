"""MPC calendar, decisions and MPR projections from the Bank of England website.

- Calendar: /monetary-policy/upcoming-mpc-dates lists each year's announcement dates, with
  links to the Monetary Policy Summary and, on MPR dates, the Monetary Policy Report.
- Decision: the Summary page's standard wording, e.g. "voted by a majority of 6–3 to
  maintain Bank Rate at 3.75%. Three members voted to increase Bank Rate by 0.25
  percentage points, to 4%."
- MPR projection: the 'Central projection' table's CPI inflation row, whose columns are the
  current quarter and one, two and three years ahead.

refresh() merges what it finds into the hand-maintained CSVs (manual/mpc_dates.csv,
manual/mpr.csv), filling only what is missing. Anything that cannot be parsed is left to
the CSVs, so a layout change degrades to the manual files rather than breaking the build.
"""
from __future__ import annotations

import datetime as dt
import html
import re

import pandas as pd
import requests

from .http import get

BOE = "https://www.bankofengland.co.uk"
CALENDAR = f"{BOE}/monetary-policy/upcoming-mpc-dates"
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}


def _text(fragment: str) -> str:
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_calendar(page: str) -> pd.DataFrame:
    rows = []
    for m in re.finditer(r"<h2>\s*(\d{4}) confirmed dates\s*</h2>(.*?)</table>", page, flags=re.S):
        year = int(m.group(1))
        for tr in re.findall(r"<tr>(.*?)</tr>", m.group(2), flags=re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)
            if len(cells) < 2:
                continue
            day = re.search(r"(\d{1,2}) ([A-Z][a-z]+)", _text(cells[0]))
            if not day:
                continue
            date = pd.Timestamp(dt.datetime.strptime(f"{day[1]} {day[2]} {year}", "%d %B %Y"))
            summary = re.search(r'href="(/monetary-policy-summary-and-minutes/[^"]+)"', cells[1])
            report = re.search(r'href="(/monetary-policy-report/[^"]+)"', cells[1])
            rows.append({"date": date, "summary_url": BOE + summary[1] if summary else None,
                         "mpr_url": BOE + report[1] if report else None})
    if not rows:
        raise ValueError("no MPC dates found on the calendar page")
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def parse_decision(page: str) -> dict | None:
    """Bank Rate decided and the vote, or None if the page has no decision yet."""
    t = _text(page)
    m = re.search(r"voted (unanimously|by a majority of (\d)[–-](\d)) to (maintain|reduce|increase|raise|cut) Bank Rate"
                  r"[^%]*?(?:at|to) (\d+(?:\.\d+)?)%", t)
    if not m:
        return None
    rate = float(m[5])
    if m[1] == "unanimously":
        return {"bank_rate": rate, "vote": "9–0: unanimous"}
    split = f"{m[2]}–{m[3]}"
    dissent = re.findall(r"((?:One|Two|Three|Four) members? voted to .*?\d+(?:\.\d+)?%)(?=\.(?:\s|$))", t[m.end():m.end() + 800])
    return {"bank_rate": rate, "vote": f"{split}: " + "; ".join(dissent) if dissent else split}


def parse_projection(page: str) -> dict | None:
    """Central-projection CPI inflation one and two years ahead from the MPR page."""
    for table in re.findall(r"<table.*?</table>", page, flags=re.S):
        t = _text(table)
        if "Central projection" not in t or "CPI inflation" not in t:
            continue
        quarters = re.findall(r"(\d{4}) Q([1-4])", t)
        row = re.search(r"CPI inflation(?:\s*\(\s*\w\s*\))?((?:\s+-?\d+\.\d)+)", t)
        if len(quarters) < 3 or not row:
            continue
        vals = [float(v) for v in row[1].split()]
        if len(vals) < 3:
            continue
        q = [f"{y}Q{n}" for y, n in quarters]
        return {"cpi_1y_quarter": q[1], "cpi_1y": vals[1], "cpi_2y_quarter": q[2], "cpi_2y": vals[2]}
    return None


def _page(url: str) -> str | None:
    try:
        r = get(url)
    except requests.RequestException:
        return None
    return None if "/error/404" in r.url else r.text


def refresh(mpc_dates: pd.DataFrame, mpr: pd.DataFrame, today: pd.Timestamp | None = None,
            log=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill in dates, decisions and MPR projections that the CSVs lack. Returns new frames."""
    today = pd.Timestamp(today) if today is not None else pd.Timestamp.now(tz="Europe/London")
    if today.tzinfo is not None:
        today = today.tz_localize(None)
    say = log or (lambda *a: None)
    cal = parse_calendar(get(CALENDAR).text)

    dates = mpc_dates.copy()
    dates["date"] = pd.to_datetime(dates["date"])
    for _, c in cal.iterrows():
        has_mpr = "Y" if c["mpr_url"] else "N"
        if (dates["date"] == c["date"]).any():
            i = dates.index[dates["date"] == c["date"]][0]
            dates.loc[i, "mpr"] = has_mpr
        else:
            dates = pd.concat([dates, pd.DataFrame([{"date": c["date"], "mpr": has_mpr, "source_url": c["summary_url"]}])],
                              ignore_index=True)
            i = dates.index[-1]
            say(f"MPC calendar: added {c['date']:%d %b %Y}")
        if c["date"].normalize() <= today and c["summary_url"] and pd.isna(dates.loc[i].get("vote")):
            page = _page(c["summary_url"])
            d = parse_decision(page) if page else None
            if d:
                dates.loc[i, ["bank_rate", "vote", "source_url"]] = [d["bank_rate"], d["vote"], c["summary_url"]]
                say(f"MPC decision {c['date']:%d %b %Y}: {d['vote']}, Bank Rate {d['bank_rate']}%")

    proj = mpr.copy()
    proj["mpr_date"] = pd.to_datetime(proj["mpr_date"])
    for _, c in cal.iterrows():
        if not c["mpr_url"] or c["date"].normalize() > today:
            continue
        existing = proj["mpr_date"] == c["date"]
        if existing.any() and proj.loc[existing, "cpi_1y"].notna().all():
            continue
        page = _page(c["mpr_url"])
        p = parse_projection(page) if page else None
        if not p:
            say(f"MPR {c['date']:%b %Y}: projection table not found; left to manual/mpr.csv")
            continue
        row = {"mpr_date": c["date"], **p, "source_url": c["mpr_url"],
               "notes": "Read automatically from the MPR central-projection table"}
        if existing.any():
            for k, v in row.items():
                proj.loc[existing, k] = v
        else:
            proj = pd.concat([proj, pd.DataFrame([row])], ignore_index=True)
        say(f"MPR {c['date']:%b %Y}: CPI {p['cpi_1y']}% in {p['cpi_1y_quarter']}, {p['cpi_2y']}% in {p['cpi_2y_quarter']}")

    dates = dates.sort_values("date").reset_index(drop=True)
    dates["date"] = dates["date"].dt.strftime("%Y-%m-%d")
    proj = proj.sort_values("mpr_date").reset_index(drop=True)
    proj["mpr_date"] = proj["mpr_date"].dt.strftime("%Y-%m-%d")
    return dates, proj
