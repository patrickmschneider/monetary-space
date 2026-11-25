import pandas as pd

from monetary_space import releases

LOG = pd.DataFrame(
    [
        ("2026-09-24T07:10:00+01:00", "CPI", "ok", "2026-08"),
        ("2026-09-24T07:10:00+01:00", "DMP", "ok", "2026-08"),
        ("2026-10-21T07:10:00+01:00", "CPI", "ok", "2026-09"),
        ("2026-10-21T07:10:00+01:00", "DMP", "ok", "2026-09"),
        ("2026-10-22T07:10:00+01:00", "CPI", "ok", "2026-09"),
        ("2026-10-22T07:10:00+01:00", "DMP", "kept_last_good", "2026-09"),
        ("2026-10-26T07:10:00+00:00", "PAY", "ok", "2026-08"),
        ("2026-10-26T07:10:00+00:00", "GONE", "missing", ""),
    ],
    columns=["run_at", "series_id", "status", "last_period"],
)


def test_first_seen_is_the_first_ok_run_with_the_latest_period():
    seen = releases.first_seen(LOG)
    assert seen["CPI"] == releases.Seen("2026-09", pd.Timestamp("2026-10-21 07:10"), False)   # the run time, local
    assert seen["DMP"].first_seen == pd.Timestamp("2026-10-21 07:10")   # a later failed run does not move it
    assert "GONE" not in seen


def test_periods_present_when_the_log_began_are_marked():
    seen = releases.first_seen(LOG[LOG["run_at"] < "2026-10"])
    assert seen["CPI"].at_log_start
    assert not releases.is_new(seen["CPI"], pd.Timestamp("2026-09-25"), 7)


def test_indicator_takes_its_newest_input_and_is_new_within_the_window():
    seen = releases.first_seen(LOG)
    s = releases.indicator_seen(["CPI:core", "PAY"], seen)
    assert s.first_seen == pd.Timestamp("2026-10-26 07:10")
    assert releases.is_new(seen["CPI"], pd.Timestamp("2026-10-27"), 7)
    assert not releases.is_new(seen["CPI"], pd.Timestamp("2026-10-28"), 7)
    assert releases.indicator_seen(["NONE"], seen) is None


def test_daily_series_are_never_new():
    log = pd.DataFrame([("2026-10-26T07:10:00+00:00", "FX", "ok", "2026-10-23"),
                        ("2026-10-20T07:10:00+00:00", "FX", "ok", "2026-10-16")],
                       columns=["run_at", "series_id", "status", "last_period"])
    s = releases.first_seen(log)["FX"]
    assert s.daily and not releases.is_new(s, pd.Timestamp("2026-10-26"), 7)


def test_change_detection_ignores_dtype_but_not_revisions_or_new_periods():
    from monetary_space import build
    m = lambda v, end="2026-10": pd.Series(v, index=pd.period_range(end=end, periods=len(v), freq="M"))
    prev = {"A": m([1.0, 2.0]), "B": m([1.0])}
    assert build.changed_series(prev, {"A": m([1, 2]), "B": m([1.0])}) == []                      # int vs float
    assert build.changed_series(prev, {"A": m([1.0, 2.5]), "B": m([1.0])}) == ["A"]               # revision
    assert build.changed_series(prev, {"A": m([1.0, 2.0]), "B": m([1.0, 2.0], end="2026-11")}) == ["B"]


def test_fiscal_years_survive_the_store(tmp_path):
    from monetary_space import build, store
    from monetary_space.fetch import fiscal
    s = pd.Series([4.2, 3.4], index=pd.PeriodIndex([fiscal.fiscal_year("2026-27"), fiscal.fiscal_year("2027-28")], freq="Y-MAR"))
    store.save_vintage(tmp_path, pd.Timestamp("2026-11-25"), {"FISCAL:PSNB": s})
    back = store.load_vintage(tmp_path)[1]["FISCAL:PSNB"]
    assert back.index.freqstr == "Y-MAR" and back.index[0] == pd.Period("2027", "Y-MAR")
    assert build.changed_series({"x": s}, {"x": back}) == []
