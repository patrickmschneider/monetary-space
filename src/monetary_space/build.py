"""Fetch → store → score → render. One command: `python -m monetary_space build`."""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import charts, config, indicators, nairu, render, store
from .fetch import fetch

log = logging.getLogger("monetary_space")


@dataclass
class FetchResult:
    data: dict[str, pd.Series]
    failed: set[str]
    log_rows: list[dict]


def fetch_all(cfg: config.Config, previous: dict[str, pd.Series], run_at: str) -> FetchResult:
    """Fetch every series. A failure keeps the last good value (marked stale) and is logged."""
    data, failed, rows = {}, set(), []
    for sid, spec in cfg.series.items():
        try:
            s = fetch(spec)
            data[sid] = s
            rows.append(dict(run_at=run_at, series_id=sid, status="ok", last_period=str(s.index[-1]), detail=""))
            log.info("fetched %-16s %s", sid, s.index[-1])
        except Exception as e:  # noqa: BLE001 — any source failure must not stop the build
            failed.add(sid)
            detail = f"{type(e).__name__}: {e}"[:300]
            if sid in previous:
                data[sid] = previous[sid]
                rows.append(dict(run_at=run_at, series_id=sid, status="kept_last_good", last_period=str(previous[sid].index[-1]), detail=detail))
            else:
                rows.append(dict(run_at=run_at, series_id=sid, status="missing", last_period="", detail=detail))
            log.warning("FAILED %-16s %s", sid, detail)
    return FetchResult(data, failed, rows)


def estimate_all(cfg: config.Config, data: dict[str, pd.Series]) -> tuple[dict, list[str]]:
    """Model-based benchmarks. A failure disables only the indicators that use them."""
    estimates, problems = {}, []
    if cfg.nairu:
        try:
            est = nairu.from_config(data, cfg.nairu)
            estimates["nairu"] = est
            log.info("u* %s = %.2f (β=%.2f, a=%.2f, n=%d)", est.u_star.index[-1], est.u_star.iloc[-1], est.beta, est.a, est.nobs)
        except Exception as e:  # noqa: BLE001
            problems.append(f"u* estimate: {type(e).__name__}: {e}")
            log.warning("u* estimate failed: %s", e)
    return estimates, problems


def score_all(cfg: config.Config, data: dict[str, pd.Series], as_of: pd.Timestamp, failed: set[str],
              estimates: dict | None = None):
    inds, problems = [], []
    for spec in cfg.indicators:
        missing = [s for s in spec["series"] if s not in data]
        if missing:
            problems.append(f"{spec['id']}: no data for {', '.join(missing)}")
            continue
        try:
            inds.append(indicators.compute(spec, data, cfg, as_of, failed, estimates))
        except Exception as e:  # noqa: BLE001
            problems.append(f"{spec['id']}: {type(e).__name__}: {e}")
            log.warning("could not score %s: %s", spec["id"], e)
    blocks = indicators.blocks(inds, cfg.weights["direction_threshold"])
    return inds, blocks, problems


def run(root: Path, store_dir: Path, out_dir: Path, fetch_data: bool = True) -> dict:
    t0 = time.monotonic()
    cfg = config.load(root)
    now = pd.Timestamp.now(tz="Europe/London")
    as_of = now.tz_localize(None).normalize()

    prev_day, previous = store.load_vintage(store_dir)
    if fetch_data:
        res = fetch_all(cfg, previous, now.isoformat(timespec="seconds"))
        store.save_vintage(store_dir, as_of, res.data)
        store.append_log(store_dir, res.log_rows)
    else:
        if not previous:
            raise SystemExit("no stored vintage to build from; run with fetching enabled")
        res = FetchResult(previous, set(), [])

    estimates, est_problems = estimate_all(cfg, res.data)
    inds, blocks, problems = score_all(cfg, res.data, as_of, res.failed, estimates)
    problems = est_problems + problems
    try:
        context = charts.prepare(cfg, res.data, as_of, estimates)
    except Exception as e:  # noqa: BLE001 — context charts must never stop the build
        context = []
        problems.append(f"context charts: {type(e).__name__}: {e}")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = render.summary(cfg, inds, blocks, problems, now)
    (out_dir / "scores.json").write_text(json.dumps(summary, indent=2, default=str))
    (out_dir / "index.html").write_text(render.page(cfg, inds, blocks, problems, now, sorted(res.failed), context))
    log.info("built in %.1fs: %d indicators, %d blocks, %d problems",
             time.monotonic() - t0, len(inds), len(blocks), len(problems))
    return summary
