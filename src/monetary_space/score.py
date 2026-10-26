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


def block_score(zs: list[float], how: str = "mean", scale: float = 1.0) -> float:
    """Step 5: the equal-weighted mean of the block's z, or for a block of separate channels that add
    up (cost-push), their sum divided by `scale`, the pre-2020 SD of the sum, so it stays on the z scale."""
    if not zs:
        raise ValueError("block has no indicators")
    if how == "standardised_sum":
        return sum(zs) / scale
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


@dataclass(frozen=True)
class Borderline:
    """A score within `margin` of a line, and the verdict on the other side of it."""

    what: str          # "pressure" or "stance"
    value: float
    line: float
    alternative: str


def borderline(pressure: float, threshold: float, real_rate: float, band: tuple[float, float],
               pressure_margin: float, stance_margin: float) -> list[Borderline]:
    """Verdicts that a small change would flip: pressure within its margin of ±threshold, or the real
    rate within its margin of either edge of the neutral zone."""
    pc, sc = direction(pressure, threshold), stance(real_rate, band)
    out = []
    for line in (threshold, -threshold):
        if abs(pressure - line) <= pressure_margin:
            other = direction(line + (0.001 if pressure <= line else -0.001), threshold)
            if (alt := verdict(other, sc)) != verdict(pc, sc):
                out.append(Borderline("pressure", pressure, line, alt))
    for line in band:
        if abs(real_rate - line) <= stance_margin:
            other = stance(line + (0.001 if real_rate <= line else -0.001), band)
            if (alt := verdict(pc, other)) != verdict(pc, sc):
                out.append(Borderline("stance", real_rate, line, alt))
    return out


def driver(block_scores: dict[str, float], weights: dict[str, float]) -> str:
    """Step 9: the block with the largest weighted contribution (by absolute size)."""
    return max(weights, key=lambda k: abs(weights[k] * block_scores[k]))
