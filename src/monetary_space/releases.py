"""When each observation first reached the page, read from the fetch log.

Every build logs each series' latest period. The first successful run that
logged a period is when that observation was first seen: the morning build
after the release, or the release day itself for the 07:00 ONS releases.
Periods already present on the first logged run were first seen "by" that date.
Daily market series are labelled by their latest day instead.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

TZ = "Europe/London"   # default; each edition passes its own country.yaml time_zone


@dataclass(frozen=True)
class Seen:
    period: str                  # latest period of the series, as logged
    first_seen: pd.Timestamp     # date of the first successful run that logged it
    at_log_start: bool           # already there on the first logged run: released on or before first_seen

    @property
    def daily(self) -> bool:
        """Market data: a new day arrives every build, so it is never "new"."""
        return len(self.period) == 10


def read_log(store: Path) -> pd.DataFrame:
    path = store / "fetch_log.csv"
    if not path.exists():
        return pd.DataFrame(columns=["run_at", "series_id", "status", "last_period", "detail"])
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def first_seen(log: pd.DataFrame, tz: str = TZ) -> dict[str, Seen]:
    """For each series, its latest logged period and when that period first appeared."""
    ok = log[(log["status"] == "ok") & (log["last_period"] != "")].copy()
    if ok.empty:
        return {}
    ok["day"] = pd.to_datetime(ok["run_at"], utc=True).dt.tz_convert(tz).dt.tz_localize(None).dt.normalize()
    start = ok["day"].min()
    out = {}
    for sid, g in ok.groupby("series_id", sort=False):
        g = g.sort_values("day")
        latest = g["last_period"].iloc[-1]
        day = g.loc[g["last_period"] == latest, "day"].min()
        out[sid] = Seen(latest, day, day == start)
    return out


def indicator_seen(series: list[str], seen: dict[str, Seen]) -> Seen | None:
    """An indicator is as new as its most recently updated input series."""
    hits = [seen[s.split(":")[0]] for s in series if s.split(":")[0] in seen]
    return max(hits, key=lambda s: s.first_seen) if hits else None


def is_new(s: Seen | None, as_of: pd.Timestamp, days: int) -> bool:
    return s is not None and not s.daily and not s.at_log_start and (as_of - s.first_seen).days < days
