"""Turn raw series into scored indicators and block scores, with a full audit trail."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import score, transform
from .config import BLOCKS, Config, manual_value


@dataclass
class Indicator:
    id: str
    name: str
    block: str
    unit: str
    x: pd.Series                 # transformed series, native frequency
    b: float
    b_label: str
    sigma: float
    sigma_label: str
    sign: int
    z_hist: pd.Series            # monthly, carried forward, clipped
    latest: score.Z
    period: pd.Period            # period of the latest observation
    direction: str
    stale: bool
    next_due: pd.Timestamp
    source: str
    attribution: str
    smoothing: str
    note: str
    clip_share: float
    clip_share_recent: float
    failed_series: list[str] = field(default_factory=list)


def _benchmark(spec: dict, x: pd.Series, cfg: Config, as_of: pd.Timestamp) -> tuple[float, str]:
    m = spec["method"]
    if m == "value":
        return float(spec["value"]), spec.get("label", "config value")
    if m == "pre2020_mean":
        sample = transform.pre2020(x)
        return transform.pre2020_mean(x), f"mean {sample.index[0]}–{sample.index[-1]}"
    if m == "manual":
        v, cite = manual_value(cfg, spec["field"], as_of)
        return v, f"{spec.get('label', spec['field'])} ({cite})"
    raise ValueError(f"unknown benchmark method {m!r}")


def _sigma(spec: dict, x: pd.Series) -> tuple[float, str]:
    if spec["method"] == "value":
        return float(spec["value"]), spec["rationale"]
    if spec["method"] == "pre2020_sd":
        sample = transform.pre2020(x)
        return transform.pre2020_sd(x), f"SD {sample.index[0]}–{sample.index[-1]}"
    raise ValueError(f"unknown sigma method {spec['method']!r}")


def next_due(period: pd.Period, lag_days: int) -> pd.Timestamp:
    """When the observation after `period` is usually published."""
    return (period + 1).end_time.normalize() + pd.Timedelta(days=lag_days)


def is_stale(period: pd.Period, lag_days: int, as_of: pd.Timestamp, grace_days: int) -> bool:
    return as_of > next_due(period, lag_days) + pd.Timedelta(days=grace_days)


def compute(spec: dict, data: dict[str, pd.Series], cfg: Config, as_of: pd.Timestamp,
            failed: set[str] = frozenset()) -> Indicator:
    w = cfg.weights
    clip = w["z_clip"]
    inputs = [data[s] for s in spec["series"]]
    x = transform.apply(spec["transform"], inputs, drop_last=spec.get("drop_last", 0))
    x = x[x.index.to_timestamp(how="start") <= as_of]
    b, b_label = _benchmark(spec["benchmark"], x, cfg, as_of)
    sigma, sigma_label = _sigma(spec["sigma"], x)
    sign = spec["sign"]

    raw = sign * (x - b) / sigma
    clipped = raw.clip(-clip, clip)
    recent = raw[raw.index.to_timestamp() >= pd.Timestamp(w["history"]["saturation_since"])]

    period = x.index[-1]
    latest = score.zscore(float(x.iloc[-1]), b, sigma, sign, clip)
    src = cfg.series[spec["series"][0]]["source"]
    return Indicator(
        id=spec["id"], name=spec["name"], block=spec["block"], unit=spec["unit"],
        x=x, b=b, b_label=b_label, sigma=sigma, sigma_label=sigma_label, sign=sign,
        z_hist=transform.carry_forward(clipped, pd.Period(as_of, "M")),
        latest=latest, period=period,
        direction=score.direction(latest.z, w["direction_threshold"]),
        stale=is_stale(period, spec["lag_days"], as_of, w["freshness"]["stale_grace_days"]),
        next_due=next_due(period, spec["lag_days"]),
        source=cfg.sources[src]["name"], attribution=cfg.sources[src]["attribution"],
        smoothing=spec.get("smoothing", "none"), note=spec.get("note", ""),
        clip_share=float((raw.abs() > clip).mean()),
        clip_share_recent=float((recent.abs() > clip).mean()) if len(recent) else 0.0,
        failed_series=[s for s in spec["series"] if s in failed],
    )


@dataclass
class Block:
    id: str
    indicators: list[Indicator]
    score: float
    diffusion: dict[str, int]
    history: pd.Series           # monthly block score


def blocks(inds: list[Indicator], threshold: float) -> dict[str, Block]:
    out = {}
    for b in BLOCKS:
        members = [i for i in inds if i.block == b]
        if not members:
            continue
        zs = [i.latest.z for i in members]
        hist = pd.concat([i.z_hist for i in members], axis=1).dropna().mean(axis=1)
        out[b] = Block(b, members, score.block_score(zs), score.diffusion(zs, threshold), hist)
    return out
