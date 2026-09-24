"""Decide whether this workflow run should build. Writes run=true|false to $GITHUB_OUTPUT.

Cron runs in UTC, so each UK slot is scheduled twice (for GMT and BST). A scheduled
run proceeds only if its cron time equals the UK slot under today's UK offset. The
check uses the cron string, not the clock, so a run that starts late still counts.

  07:10 UK daily           cron "10 6 * * *" (BST) and "10 7 * * *" (GMT)
  12:15 UK on MPC days     cron "15 11 * * *" (BST) and "15 12 * * *" (GMT)

Usage: python scripts/gate.py <event_name> [<cron>]
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")
DAILY, MPC = (7, 10), (12, 15)
MPC_DATES = Path(__file__).resolve().parents[1] / "manual" / "mpc_dates.csv"


def mpc_dates() -> set[str]:
    with MPC_DATES.open() as f:
        return {row["date"] for row in csv.DictReader(line for line in f if not line.startswith("#"))}


def should_run(event: str, cron: str, now_utc: dt.datetime, mpc: set[str]) -> tuple[bool, str]:
    if event != "schedule":
        return True, f"{event} trigger"
    minute, hour = (int(v) for v in cron.split()[:2])
    today_uk = now_utc.astimezone(UK).date()
    offset = dt.datetime.combine(today_uk, dt.time(12), UK).utcoffset() // dt.timedelta(hours=1)
    slot = ((hour + offset) % 24, minute)
    if slot == DAILY:
        return True, "07:10 UK daily build"
    if slot == MPC:
        on = today_uk.isoformat() in mpc
        return on, "12:15 UK MPC-day build" if on else "12:15 UK slot, not an MPC day"
    return False, f"cron {cron!r} is {slot[0]:02d}:{slot[1]:02d} UK today, not a build slot"


def main() -> None:
    event, cron = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
    run, why = should_run(event, cron, dt.datetime.now(dt.timezone.utc), mpc_dates())
    print(f"run={str(run).lower()}: {why}")
    if out := os.environ.get("GITHUB_OUTPUT"):
        with open(out, "a") as f:
            f.write(f"run={str(run).lower()}\n")


if __name__ == "__main__":
    main()
