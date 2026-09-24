"""Dated vintages of raw series. The store directory is a checkout of the `data` branch.

Layout:
  vintages/YYYY-MM-DD.parquet   one file per build day: series_id, freq, period, value
  fetch_log.csv                 one row per series per run: time, series_id, status, detail
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

LOG_FIELDS = ["run_at", "series_id", "status", "last_period", "detail"]


def _to_long(series: dict[str, pd.Series]) -> pd.DataFrame:
    frames = [
        pd.DataFrame({"series_id": sid, "freq": s.index.freqstr[0], "period": s.index.astype(str), "value": s.to_numpy()})
        for sid, s in series.items()
    ]
    return pd.concat(frames, ignore_index=True)


def _from_long(df: pd.DataFrame) -> dict[str, pd.Series]:
    out = {}
    for (sid, freq), g in df.groupby(["series_id", "freq"], sort=False):
        idx = pd.PeriodIndex(g["period"], freq=freq)
        out[sid] = pd.Series(g["value"].to_numpy(dtype=float), index=idx, name=sid)
    return out


def save_vintage(store: Path, day: pd.Timestamp, series: dict[str, pd.Series]) -> Path:
    path = store / "vintages" / f"{day:%Y-%m-%d}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    _to_long(series).to_parquet(path, index=False)
    return path


def vintage_dates(store: Path) -> list[pd.Timestamp]:
    return sorted(pd.Timestamp(p.stem) for p in (store / "vintages").glob("*.parquet"))


def load_vintage(store: Path, on_or_before: pd.Timestamp | None = None) -> tuple[pd.Timestamp | None, dict[str, pd.Series]]:
    """The latest vintage on or before a date (default: the latest overall)."""
    dates = [d for d in vintage_dates(store) if on_or_before is None or d <= on_or_before]
    if not dates:
        return None, {}
    day = dates[-1]
    return day, _from_long(pd.read_parquet(store / "vintages" / f"{day:%Y-%m-%d}.parquet"))


def append_log(store: Path, rows: list[dict]) -> None:
    path = store / "fetch_log.csv"
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
