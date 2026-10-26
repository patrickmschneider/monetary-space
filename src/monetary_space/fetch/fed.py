"""FOMC calendar, decisions and SEP projections from federalreserve.gov, the Fed staff's fitted
Treasury curves, and the New York Fed's Survey of Market Expectations.

- Calendar: /monetarypolicy/fomccalendars.htm lists each year's meetings with links to the
  statement and, at meetings marked *, the Summary of Economic Projections (SEP).
- Decision: the statement's target range and vote. Statements up to 2025 name every voter
  ("Voting for the monetary policy action were …"); from 2026 they give the count ("approved …
  by a 9 – 3 vote"). Dissents are named in both.
- SEP: Table 1's median row for PCE inflation (Q4 on Q4, by calendar year), the longer-run
  unemployment rate (the FOMC's u*) and the longer-run federal funds rate.

refresh() has the same contract as fetch/mpc.py: it fills only what manual/us/*.csv lack, and
anything it cannot parse is left to those files.
"""
from __future__ import annotations

import datetime as dt
import html
import io
import re
import time

import numpy as np
import pandas as pd
import requests

from .http import get

FED = "https://www.federalreserve.gov"
CALENDAR = f"{FED}/monetarypolicy/fomccalendars.htm"
GSW_NOMINAL = f"{FED}/data/yield-curve-tables/feds200628.csv"
GSW_REAL = f"{FED}/data/yield-curve-tables/feds200805.csv"
SME_DATA = "https://www.newyorkfed.org/medialibrary/media/markets/survey/{y}/{m}-{y}-data.xlsx"
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], start=1)}
SHORT = {m[:3]: i for m, i in MONTHS.items()}


def _text(fragment: str) -> str:
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    t = t.replace("‑", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", t).strip()


def _fraction(s: str) -> float:
    """'3-3/4' → 3.75, '1/4' → 0.25, '4' → 4.0."""
    s = s.strip()
    if "/" not in s:
        return float(s)
    whole, frac = s.split("-", 1) if "-" in s else ("0", s)
    v = float(whole)
    if frac:
        n, d = frac.split("/")
        v += float(n) / float(d)
    return v


# ------------------------------------------------------------------ calendar
def parse_calendar(page: str) -> pd.DataFrame:
    """One row per scheduled meeting: announcement date (the last day), statement and SEP links."""
    rows = []
    panels = re.split(r"<h4><a[^>]*>(\d{4}) FOMC Meetings</a></h4>", page)
    for year, body in zip(panels[1::2], panels[2::2]):
        for m in re.finditer(r'fomc-meeting__month[^>]*><strong>([^<]+)</strong>.*?fomc-meeting__date[^>]*>([^<]+)<(.*?)'
                             r'(?=fomc-meeting__month|$)', body, flags=re.S):
            month, days, rest = m.group(1).strip(), m.group(2).strip(), m.group(3)
            if "notation" in days or "unscheduled" in days.lower():
                continue
            stmt = re.search(r'href="(/newsevents/pressreleases/monetary(\d{8})a\.htm)"', rest)
            proj = re.search(r'href="(/monetarypolicy/fomcprojtabl\d{8}\.htm)"', rest)
            if stmt:
                date = pd.Timestamp(dt.datetime.strptime(stmt.group(2), "%Y%m%d"))
            else:
                last_day = int(re.findall(r"\d+", days)[-1])
                mon = month.split("/")[-1].strip().lower()
                date = pd.Timestamp(int(year), MONTHS.get(mon) or SHORT[mon[:3]], last_day)
            rows.append({"date": date, "sep": "*" in days,
                         "statement_url": FED + stmt.group(1) if stmt else "",
                         "sep_url": FED + proj.group(1) if proj else ""})
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def parse_statement(page: str) -> dict | None:
    """Target range midpoint and the vote, e.g. '9-3: 9 hold; 3 preferred to raise by 1/4pp (Hammack, Kashkari, Logan)'."""
    t = _text(page)
    rng = re.search(r"target range for the federal funds rate (?:by [\d/-]+ percentage point )?(?:at|to) "
                    r"([\d/-]+) to ([\d/-]+) percent", t)
    if not rng:
        return None
    lo, hi = _fraction(rng.group(1)), _fraction(rng.group(2))
    action = re.search(r"decided to (raise|lower|maintain)", t)
    act = {"raise": "raise", "lower": "cut", "maintain": "hold"}[action.group(1)] if action else "decision"
    groups = dissents(t)
    dissent_names = [n for names, _ in groups for n in names]
    count = re.search(r"by a (\d+)\s*-\s*(\d+) vote", t)
    if count:
        n_for, n_against = int(count.group(1)), int(count.group(2))
    else:
        voters = re.search(r"Voting for (?:the|this) (?:monetary policy )?action were (.*?)\.(?: Voting| For media|$)", t)
        if not voters:
            return None
        n_for = len([v for v in re.split(r";\s*(?:and\s+)?", voters.group(1)) if v.strip()])
        n_against = len(dissent_names)
    vote = f"{n_for}-{n_against}: {n_for} {act}"
    for names, pref in groups:
        pref = re.sub(r"\s+at this meeting$", "", pref)
        pref = pref.replace("the target range for the federal funds rate", "the range").replace(" percentage point", "pp")
        pref = re.sub(r"\d+-\d/\d|\d/\d", lambda f: f"{_fraction(f.group(0)):g}", pref)
        vote += f"; {len(names)} {pref} ({', '.join(n.split()[-1] for n in names)})"
    return {"bank_rate": (lo + hi) / 2, "range": f"{lo:g}-{hi:g}", "vote": vote}


NAME = r"[A-Z][a-z'-]+(?: [A-Z]\.)? [A-Z][A-Za-z'-]+"


def dissents(t: str) -> list[tuple[list[str], str]]:
    """Dissenters grouped by stated position: [(['Stephen I. Miran'], 'preferred to lower …'), …]."""
    m = re.search(r"Voting against (?:the|this) (?:monetary policy )?action (?:was|were) (.*?)\.(?= For media| Implementation|$)", t)
    if not m:
        return []
    pieces = re.split(r", who (preferred|supported) ", m.group(1))
    parts, verbs = [pieces[0]] + pieces[2::2], pieces[1::2]
    out, names = [], parts[0]
    for k, part in enumerate(parts[1:], start=1):
        if k < len(parts) - 1:                   # this position runs until the first separator before a name
            cuts = [(m.start(), m.end()) for m in re.finditer(r";? and |; |, and ", part)
                     if re.match(NAME, part[m.end():])]
            start, end = cuts[0]
            pref, nxt = part[:start], part[end:]
        else:
            pref, nxt = part, ""
        pref = re.split(r"(?<![A-Z])\.\s", pref)[0]   # one sentence ("Absent and not voting …" follows)
        out.append((re.findall(NAME, names), f"{verbs[k - 1]} {pref.strip()}"))
        names = nxt
    return out


def parse_sep(page: str, year: int) -> dict | None:
    """Median PCE inflation by year (Q4/Q4), longer-run unemployment and federal funds rate."""
    t = _text(page)
    head = re.search(r"Variable Median \S+ Central Tendency.*? ((?:\d{4} )+)Longer run", t)
    if not head:
        return None
    years = [int(y) for y in head.group(1).split()]

    def row(label: str) -> list[float] | None:
        m = re.search(label + r"\s+((?:-?\d+\.\d+\s+){%d}-?\d+\.\d+)" % len(years), t)
        return [float(v) for v in m.group(1).split()] if m else None

    pce, unemp, ffr = row(r"PCE inflation"), row(r"Unemployment rate"), row(r"Federal funds rate")
    if pce is None:
        return None
    out = {f"pce_{y}": v for y, v in zip(years, pce)}
    out["pce_years"] = years
    if unemp:
        out["u_star"] = unemp[-1]
    if ffr:
        out["ffr_lr"] = ffr[-1]
    gdp = row(r"Change in real GDP")
    if gdp:
        out["potential_growth"] = gdp[-1]
    return out


def year_ahead(sep: dict, date: pd.Timestamp, ahead: int = 1) -> tuple[str, float] | None:
    """Projection for the quarter `ahead` years after `date`, interpolated linearly between the Q4/Q4
    calendar-year medians on either side (e.g. 2027Q3 = ¼·2026 + ¾·2027)."""
    target = pd.Period(date, "Q") + 4 * ahead
    y, q = target.year, target.quarter
    if q == 4:
        v = sep.get(f"pce_{y}")
        return (str(target), v) if v is not None else None
    a, b = sep.get(f"pce_{y - 1}"), sep.get(f"pce_{y}")
    if a is None or b is None:
        return None
    return str(target), round((4 - q) / 4 * a + q / 4 * b, 2)


def _page(url: str) -> str | None:
    time.sleep(0.5)                              # federalreserve.gov throttles bursts of requests
    try:
        return get(url).content.decode("utf-8", "replace")   # no charset header; requests would assume Latin-1
    except requests.RequestException:
        return None


def refresh(mpc_dates: pd.DataFrame, mpr: pd.DataFrame, today: pd.Timestamp | None = None,
            log=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill in FOMC dates, decisions and SEP projections that the CSVs lack. Returns new frames."""
    today = pd.Timestamp(today) if today is not None else pd.Timestamp.now(tz="America/New_York")
    if today.tzinfo is not None:
        today = today.tz_localize(None)
    say = log or (lambda *a: None)
    cal = parse_calendar(get(CALENDAR).content.decode("utf-8", "replace"))
    cal = cal[cal["date"] >= pd.Timestamp("2024-01-01")]

    dates = mpc_dates.copy()
    dates["date"] = pd.to_datetime(dates["date"])
    for _, c in cal.iterrows():
        has_sep = "Y" if c["sep"] else "N"
        if (dates["date"] == c["date"]).any():
            i = dates.index[dates["date"] == c["date"]][0]
            dates.loc[i, "mpr"] = has_sep
        else:
            dates = pd.concat([dates, pd.DataFrame([{"date": c["date"], "mpr": has_sep, "source_url": c["statement_url"]}])],
                              ignore_index=True)
            i = dates.index[-1]
            say(f"FOMC calendar: added {c['date']:%d %b %Y}")
        if c["date"].normalize() <= today and c["statement_url"] and pd.isna(dates.loc[i].get("vote")):
            page = _page(c["statement_url"])
            d = parse_statement(page) if page else None
            if d:
                dates.loc[i, ["bank_rate", "vote", "source_url"]] = [d["bank_rate"], d["vote"], c["statement_url"]]
                say(f"FOMC decision {c['date']:%d %b %Y}: {d['vote']}, range {d['range']}%")

    proj = mpr.copy()
    proj["mpr_date"] = pd.to_datetime(proj["mpr_date"])
    for _, c in cal.iterrows():
        if not c["sep_url"] or c["date"].normalize() > today:
            continue
        existing = proj["mpr_date"] == c["date"]
        if existing.any() and proj.loc[existing, "cpi_1y"].notna().all():
            continue
        page = _page(c["sep_url"])
        p = parse_sep(page, c["date"].year) if page else None
        one, two = (year_ahead(p, c["date"], 1), year_ahead(p, c["date"], 2)) if p else (None, None)
        if not one:
            say(f"SEP {c['date']:%b %Y}: projection table not found; left to manual/us/mpr.csv")
            continue
        yrs = p["pce_years"]
        row = {"mpr_date": c["date"], "cpi_1y_quarter": one[0], "cpi_1y": one[1],
               "cpi_2y_quarter": two[0] if two else np.nan, "cpi_2y": two[1] if two else np.nan,
               "u_star": p.get("u_star", np.nan), "potential_growth": p.get("potential_growth", np.nan),
               "ffr_lr": p.get("ffr_lr", np.nan), "source_url": c["sep_url"],
               "notes": "Read automatically from SEP Table 1 medians. PCE (Q4/Q4) "
                        + ", ".join(f"{y} {p[f'pce_{y}']}" for y in yrs)
                        + "; year-ahead interpolated between calendar years"}
        if existing.any():
            for k, v in row.items():
                proj.loc[existing, k] = v
        else:
            proj = pd.concat([proj, pd.DataFrame([row])], ignore_index=True)
        say(f"SEP {c['date']:%b %Y}: PCE {one[1]}% in {one[0]}")

    dates = dates.sort_values("date").reset_index(drop=True)
    dates["date"] = dates["date"].dt.strftime("%Y-%m-%d")
    proj = proj.sort_values("mpr_date").reset_index(drop=True)
    proj["mpr_date"] = proj["mpr_date"].dt.strftime("%Y-%m-%d")
    return dates, proj


# ------------------------------------------------------------------ fitted Treasury curves
def _gsw(url: str) -> pd.DataFrame:
    text = get(url, timeout=120).text
    start = text.index("\nDate,") + 1
    df = pd.read_csv(io.StringIO(text[start:]), na_values=["NA"])
    df.index = pd.PeriodIndex(pd.to_datetime(df.pop("Date")), freq="D")
    return df


def svensson_forward(params: pd.DataFrame, m: float) -> pd.Series:
    """Instantaneous forward rate at maturity m (years) from the Svensson parameters, %."""
    b0, b1, b2, b3, t1, t2 = (params[c] for c in ("BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"))
    return (b0 + b1 * np.exp(-m / t1) + b2 * (m / t1) * np.exp(-m / t1)
            + b3 * (m / t2) * np.exp(-m / t2))


def treasury_forwards(maturities: list[float], since: str = "2024-01-01") -> dict[str, pd.Series]:
    """Forward curve for the policy path: under one year from Treasury bill yields (FRED constant
    maturity, 1, 3 and 6 months and 1 year: the forward between neighbouring maturities, stamped at
    the far end), from one year on the Fed staff (Gürkaynak–Sack–Wright) instantaneous forwards."""
    from . import fred
    start = pd.Period(since, "D")
    bills = {0.0833: "DGS1MO", 0.25: "DGS3MO", 0.5: "DGS6MO", 1.0: "DGS1"}
    y = pd.DataFrame({m: fred.series(c, "D") for m, c in bills.items()}).dropna()
    y = y[y.index >= start]
    out, prev_m, prev_y = {}, 0.0, None
    for m in sorted(bills):
        if m >= 1.0:
            break
        fwd = y[m] if prev_y is None else (y[m] * m - prev_y * prev_m) / (m - prev_m)
        if m in maturities:
            out[f"{m:g}"] = fwd.rename(f"{m:g}")
        prev_m, prev_y = m, y[m]
    gsw = _gsw(GSW_NOMINAL)
    gsw = gsw[gsw.index >= start].dropna(subset=["BETA0"])
    for m in maturities:
        if m >= 1.0:
            out[f"{m:g}"] = svensson_forward(gsw, m).rename(f"{m:g}")
    return out


def gsw_yields(columns: list[str], real: bool = False) -> dict[str, pd.Series]:
    """Daily zero-coupon yields from the Fed staff curves: nominal SVENYxx, TIPS TIPSYxx."""
    df = _gsw(GSW_REAL if real else GSW_NOMINAL)
    return {c: df[c].dropna().rename(c) for c in columns}


# ------------------------------------------------------------------ NY Fed Survey of Market Expectations
def parse_sme(content: bytes) -> dict | None:
    """Longer-run federal funds rate (median, 25th and 75th percentiles, %), longer-run GDP growth
    (median, %) and the survey date."""
    df = pd.read_excel(io.BytesIO(content))
    r = df[(df["value_tag"] == "fftr_modalpe_longerrun") & (df["panel_type"] == "Combined")]
    if r.empty:
        return None
    agg = dict(zip(r["aggregation"], r["aggregation_value"]))
    if "pctl50" not in agg:
        return None
    pct = lambda v: round(float(v) * 100, 3)
    out = {"date": pd.Timestamp(r["survey_release_date"].iloc[0]), "neutral": pct(agg["pctl50"]),
           "neutral_p25": pct(agg.get("pctl25", np.nan)), "neutral_p75": pct(agg.get("pctl75", np.nan)),
           "neutral_n": int(agg.get("count", 0))}
    g = df[(df["value_tag"] == "econoutlook_pathofmodes_realgdpgrowth_longerrun") & (df["panel_type"] == "Combined")
           & (df["aggregation"] == "pctl50")]
    if not g.empty:
        out["potential"] = pct(g["aggregation_value"].iloc[0])          # longer-run real GDP growth, median
    return out


def sme_history(start_year: int = 2025) -> pd.DataFrame:
    """Each Survey of Market Expectations round (combined dealer and participant panel, from 2025)."""
    rows, today = [], dt.date.today()
    for y in range(start_year, today.year + 1):
        for m in ["jan", "mar", "apr", "may", "jun", "jul", "sep", "oct", "nov", "dec"]:
            try:
                r = get(SME_DATA.format(y=y, m=m), allow_redirects=False)
            except requests.RequestException:
                continue
            if r.status_code != 200 or not r.content.startswith(b"PK"):
                continue
            p = parse_sme(r.content)
            if p:
                rows.append(p)
    if not rows:
        raise RuntimeError("no Survey of Market Expectations rounds found")
    df = pd.DataFrame(rows).drop_duplicates("date").sort_values("date")
    df.index = pd.PeriodIndex(df.pop("date"), freq="M")
    return df


# ------------------------------------------------------------------ Atlanta Fed Business Inflation Expectations
BIE_XLSX = "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/bie/data/bie.xlsx"


def parse_bie(content: bytes) -> pd.Series:
    """Mean year-ahead unit-cost expectation (the survey's question on the year ahead), monthly, %."""
    df = pd.read_excel(io.BytesIO(content), sheet_name="BIE Survey results", header=None)
    heads = {c: str(df.iloc[1, c]) for c in df.columns}
    q = next(c for c in df.columns if "Projecting ahead" in heads[c])
    col = next(c for c in df.columns if c > q and str(df.iloc[2, c]).strip() == "Mean")
    body = df.iloc[3:, [0, col]].dropna()
    dates = pd.to_datetime(body.iloc[:, 0], errors="coerce")
    body = body[dates.notna()]
    idx = pd.PeriodIndex(dates[dates.notna()], freq="M")
    s = pd.Series(body.iloc[:, 1].astype(float).to_numpy() * 100, index=idx, name="BIE_1Y")
    return s[~s.index.duplicated(keep="last")].sort_index()


def bie() -> pd.Series:
    return parse_bie(get(BIE_XLSX, timeout=60).content)
