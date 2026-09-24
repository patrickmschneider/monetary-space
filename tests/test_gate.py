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
    assert gate.should_run("schedule", cron, now, set())[0] is expected


def test_mpc_slot_only_on_mpc_days():
    now = dt.datetime(2026, 11, 5, 12, 20, tzinfo=UTC)
    assert gate.should_run("schedule", "15 12 * * *", now, {"2026-11-05"})[0]
    assert not gate.should_run("schedule", "15 12 * * *", now, set())[0]
    assert not gate.should_run("schedule", "15 11 * * *", now, {"2026-11-05"})[0]


def test_late_start_still_runs():
    late = dt.datetime(2026, 7, 1, 9, 55, tzinfo=UTC)
    assert gate.should_run("schedule", "10 6 * * *", late, set())[0]


@pytest.mark.parametrize("event", ["workflow_dispatch", "push"])
def test_manual_and_push_always_run(event):
    assert gate.should_run(event, "", SUMMER, set())[0]
