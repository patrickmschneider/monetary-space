"""Scoring rules (spec Section 3). Pure functions: no I/O, no config loading.

Every threshold and weight is passed in, so the page can be reproduced by hand
from config and tooltips.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean

UP, NEUTRAL, DOWN = "up", "neutral", "down"
CLASS_VALUE = {UP: 1, NEUTRAL: 0, DOWN: -1}

TIGHT, LOOSE = "tight", "loose"
STANCE_VALUE = {TIGHT: 1, NEUTRAL: 0, LOOSE: -1}

HAWKISH, ON_TRACK, EASE = "Hawkish risk", "On track", "Room to ease"


@dataclass(frozen=True)
class Z:
    """A z-score with its inputs, so a tooltip can show the whole calculation."""

    x: float
    b: float
    sigma: float
    sign: int
    raw: float
    z: float

    @property
    def clipped(self) -> bool:
        return self.z != self.raw


def zscore(x: float, b: float, sigma: float, sign: int, clip: float = 3.0) -> Z:
    """Step 3: z = s·(x − b)/σ, clipped at ±clip. Positive always means inflationary."""
    if sign not in (1, -1):
        raise ValueError(f"sign must be +1 or -1, got {sign}")
    if not sigma > 0:
        raise ValueError(f"sigma must be positive, got {sigma}")
    raw = sign * (x - b) / sigma
    return Z(x=x, b=b, sigma=sigma, sign=sign, raw=raw, z=max(-clip, min(clip, raw)))


def direction(z: float, threshold: float = 0.5) -> str:
    """Step 4: up above +threshold, down below −threshold, else neutral."""
    if z > threshold:
        return UP
    if z < -threshold:
        return DOWN
    return NEUTRAL


def block_score(zs: list[float]) -> float:
    """Step 5: equal-weighted mean of the block's z."""
    if not zs:
        raise ValueError("block has no indicators")
    return fmean(zs)


def diffusion(zs: list[float], threshold: float = 0.5) -> dict[str, int]:
    """Step 5: count of indicators pointing up / neutral / down."""
    counts = {UP: 0, NEUTRAL: 0, DOWN: 0}
    for z in zs:
        counts[direction(z, threshold)] += 1
    return counts


def pressure(block_scores: dict[str, float], weights: dict[str, float]) -> float:
    """Step 6: weighted sum of block scores. Every weighted block must be present."""
    missing = set(weights) - set(block_scores)
    if missing:
        raise ValueError(f"pressure needs scores for blocks {sorted(missing)}")
    return sum(w * block_scores[k] for k, w in weights.items())


def rstar_band(low: float, high: float, min_half_width: float) -> tuple[float, float]:
    """Neutral zone for the real rate, widened symmetrically to the minimum half-width."""
    if low > high:
        raise ValueError(f"r* low {low} is above high {high}")
    mid = (low + high) / 2
    half = max((high - low) / 2, min_half_width)
    return mid - half, mid + half


def stance(real_rate: float, band: tuple[float, float]) -> str:
    """Step 7: tight above the r* band, loose below it, else neutral."""
    low, high = band
    if real_rate > high:
        return TIGHT
    if real_rate < low:
        return LOOSE
    return NEUTRAL


def verdict(pressure_class: str, stance_class: str) -> str:
    """Step 8: class(Pressure) − class(Stance), with Tight = +1."""
    d = CLASS_VALUE[pressure_class] - STANCE_VALUE[stance_class]
    if d >= 1:
        return HAWKISH
    if d <= -1:
        return EASE
    return ON_TRACK


def driver(block_scores: dict[str, float], weights: dict[str, float]) -> str:
    """Step 9: the block with the largest weighted contribution (by absolute size)."""
    return max(weights, key=lambda k: abs(weights[k] * block_scores[k]))
