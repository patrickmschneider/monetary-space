"""Decide whether this workflow run should build. Writes run=true|false to $GITHUB_OUTPUT.

Cron runs in UTC, so each local slot is scheduled for every UTC offset its country uses
(GMT and BST for the UK). A scheduled run proceeds only if its cron time equals a slot
under that country's offset today. The check uses the cron string, not the clock, so a
run that starts late still counts. Every run builds every edition.

  uk  07:10 daily           cron "10 6 * * *" (BST) and "10 7 * * *" (GMT)
  uk  12:15 on MPC days     cron "15 11 * * *" (BST) and "15 12 * * *" (GMT)
  us  08:45 daily           cron "45 12 * * *" (EDT) and "45 13 * * *" (EST)   after the 08:30 releases
  us  14:15 on FOMC days    cron "15 18 * * *" (EDT) and "15 19 * * *" (EST)   after the 14:00 statement
  au  11:45 daily           cron "45 0 * * *" (AEDT) and "45 1 * * *" (AEST)    after the 11:30 ABS releases
  au  14:45 on Board days   cron "45 3 * * *" (AEDT) and "45 4 * * *" (AEST)    after the 14:30 decision

Usage: python scripts/gate.py <event_name> [<cron>]
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys
from pathlib import Path
from typing import NamedTuple
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


class Slot(NamedTuple):
    country: str
    tz: str
    time: tuple[int, int]      # local hour, minute
    decision_days: bool        # only on the country's policy announcement days
    label: str


SLOTS = [
    Slot("uk", "Europe/London", (7, 10), False, "07:10 UK daily build"),
    Slot("uk", "Europe/London", (12, 15), True, "12:15 UK MPC-day build"),
    Slot("us", "America/New_York", (8, 45), False, "08:45 New York daily build"),
    Slot("us", "America/New_York", (14, 15), True, "14:15 New York FOMC-day build"),
    Slot("au", "Australia/Sydney", (11, 45), False, "11:45 Sydney daily build"),
    Slot("au", "Australia/Sydney", (14, 45), True, "14:45 Sydney Board-day build"),
]


def calendar_dates() -> set[str]:
    """Announcement dates from the Bank's calendar page; empty if unreachable."""
    import re
    import urllib.request
    try:
        req = urllib.request.Request("https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates",
                                     headers={"User-Agent": "Mozilla/5.0 (compatible; monetary-space)"})
        page = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return set()
    out = set()
    for year, body in re.findall(r"<h2>\s*(\d{4}) confirmed dates\s*</h2>(.*?)</table>", page, flags=re.S):
        for day, month in re.findall(r"<td>[A-Za-z]+(?:&nbsp;|\s)+(\d{1,2}) ([A-Z][a-z]+)", body):
            out.add(dt.datetime.strptime(f"{day} {month} {year}", "%d %B %Y").date().isoformat())
    return out


def manual_dates(country: str) -> set[str]:
    path = ROOT / "manual" / country / "mpc_dates.csv"
    if not path.exists():
        return set()
    with path.open() as f:
        return {row["date"] for row in csv.DictReader(line for line in f if not line.startswith("#"))}


def decision_dates() -> dict[str, set[str]]:
    """Policy announcement dates by country: the manual CSV plus the live calendar where there is one."""
    out = {c: manual_dates(c) for c in {s.country for s in SLOTS}}
    out["uk"] |= calendar_dates()
    return out


def should_run(event: str, cron: str, now_utc: dt.datetime, decisions: dict[str, set[str]]) -> tuple[bool, str]:
    if event != "schedule":
        return True, f"{event} trigger"
    minute, hour = (int(v) for v in cron.split()[:2])
    skipped = []
    for s in SLOTS:
        tz = ZoneInfo(s.tz)
        today = now_utc.astimezone(tz).date()
        offset = dt.datetime.combine(today, dt.time(12), tz).utcoffset() // dt.timedelta(hours=1)
        if ((hour + offset) % 24, minute) != s.time:
            continue
        if not s.decision_days or today.isoformat() in decisions.get(s.country, set()):
            return True, s.label
        skipped.append(f"{s.time[0]:02d}:{s.time[1]:02d} {s.country.upper()} slot, not a decision day")
    return False, "; ".join(skipped) or f"cron {cron!r} matches no build slot today"


def main() -> None:
    event, cron = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
    run, why = should_run(event, cron, dt.datetime.now(dt.timezone.utc), decision_dates())
    print(f"run={str(run).lower()}: {why}")
    if out := os.environ.get("GITHUB_OUTPUT"):
        with open(out, "a") as f:
            f.write(f"run={str(run).lower()}\n")


if __name__ == "__main__":
    main()
