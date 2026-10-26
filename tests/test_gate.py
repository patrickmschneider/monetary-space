import datetime as dt
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("gate", Path(__file__).resolve().parents[1] / "scripts" / "gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

UTC = dt.timezone.utc
SUMMER = dt.datetime(2026, 7, 1, 6, 30, tzinfo=UTC)   # BST
WINTER = dt.datetime(2026, 12, 1, 7, 30, tzinfo=UTC)  # GMT


@pytest.mark.parametrize("cron,now,expected", [
    ("10 6 * * *", SUMMER, True), ("10 7 * * *", SUMMER, False),
    ("10 6 * * *", WINTER, False), ("10 7 * * *", WINTER, True),
])
def test_daily_slot_follows_uk_clock(cron, now, expected):
    assert gate.should_run("schedule", cron, now, {})[0] is expected


def test_mpc_slot_only_on_mpc_days():
    now = dt.datetime(2026, 11, 5, 12, 20, tzinfo=UTC)
    assert gate.should_run("schedule", "15 12 * * *", now, {"uk": {"2026-11-05"}})[0]
    assert not gate.should_run("schedule", "15 12 * * *", now, {})[0]
    assert not gate.should_run("schedule", "15 11 * * *", now, {"uk": {"2026-11-05"}})[0]


def test_late_start_still_runs():
    late = dt.datetime(2026, 7, 1, 9, 55, tzinfo=UTC)
    assert gate.should_run("schedule", "10 6 * * *", late, {})[0]


@pytest.mark.parametrize("event", ["workflow_dispatch", "push"])
def test_manual_and_push_always_run(event):
    assert gate.should_run(event, "", SUMMER, {})[0]


def test_us_slots_follow_new_york_time():
    oct_edt = dt.datetime(2026, 10, 26, 13, 0, tzinfo=UTC)            # New York still on EDT (UK already GMT)
    assert gate.should_run("schedule", "45 12 * * *", oct_edt, {})[0]
    assert not gate.should_run("schedule", "45 13 * * *", oct_edt, {})[0]
    nov_est = dt.datetime(2026, 11, 10, 14, 0, tzinfo=UTC)
    assert gate.should_run("schedule", "45 13 * * *", nov_est, {})[0]


def test_us_fomc_slot_only_on_fomc_days():
    now = dt.datetime(2026, 10, 28, 18, 20, tzinfo=UTC)
    assert gate.should_run("schedule", "15 18 * * *", now, {"us": {"2026-10-28"}})[0]
    assert not gate.should_run("schedule", "15 18 * * *", now, {"uk": {"2026-10-28"}})[0]


def test_au_slots_follow_sydney_time():
    oct_aedt = dt.datetime(2026, 10, 27, 1, 0, tzinfo=UTC)            # Sydney on AEDT (UTC+11)
    assert gate.should_run("schedule", "45 0 * * *", oct_aedt, {})[0]
    assert not gate.should_run("schedule", "45 1 * * *", oct_aedt, {})[0]
    jul_aest = dt.datetime(2026, 7, 1, 2, 0, tzinfo=UTC)
    assert gate.should_run("schedule", "45 1 * * *", jul_aest, {})[0]
    board = dt.datetime(2026, 11, 3, 3, 50, tzinfo=UTC)               # 14:50 AEDT on a Board day
    assert gate.should_run("schedule", "45 3 * * *", board, {"au": {"2026-11-03"}})[0]
    assert not gate.should_run("schedule", "45 3 * * *", board, {})[0]
