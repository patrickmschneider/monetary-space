"""Policy stance (spec Section 3, step 7) and the verdict (steps 6, 8, 9).

Stance is in percentage points, not z: real rate r = 2-year OIS − the MPR's year-ahead
CPI projection; gap = r − r* midpoint; tight above the r* band, loose below it.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import score, transform
from .config import Config


@dataclass
class Stance:
    ois_2y: float
    ois_date: pd.Timestamp
    expected_inflation: float
    expectation_source: str
    real_rate: float
    r_star: float
    r_star_se: float
    r_star_quarter: pd.Period
    band: tuple[float, float]
    gap: float
    cls: str
    history: pd.Series            # monthly gap, pp


def mpr_path(cfg: Config, field: str) -> pd.Series:
    """Manual MPR values as a daily-effective step function, keyed by publication date."""
    m = cfg.manual["mpr"].dropna(subset=[field]).copy()
    m["mpr_date"] = pd.to_datetime(m["mpr_date"])
    return m.set_index("mpr_date")[field].astype(float).sort_index()


def as_of(path: pd.Series, when: pd.Timestamp) -> tuple[float, pd.Timestamp]:
    p = path[path.index <= when]
    if p.empty:
        raise ValueError(f"no MPR projection on or before {when.date()}")
    return float(p.iloc[-1]), p.index[-1]


def compute(cfg: Config, data: dict[str, pd.Series], rstar_est, as_of_day: pd.Timestamp) -> Stance:
    st = cfg.weights["stance"]
    ois = data[st["ois_series"]].dropna()
    ois = ois[ois.index.to_timestamp() <= as_of_day]
    proj = mpr_path(cfg, st["expected_inflation_field"])
    e, mpr_date = as_of(proj, as_of_day)
    rs, se = float(rstar_est.r_star.iloc[-1]), float(rstar_est.se.iloc[-1])
    half = max(cfg.rstar.get("band_z", 1.0) * se, st["rstar_band_min_half_width"])
    band = score.rstar_band(rs - half, rs + half, st["rstar_band_min_half_width"])
    real = float(ois.iloc[-1]) - e

    # Monthly history: monthly-average 2y OIS − projection in force − r* of that quarter.
    m = ois.groupby(ois.index.asfreq("M")).mean()
    exp_m = pd.Series([as_of(proj, p.end_time)[0] if (proj.index <= p.end_time).any() else float("nan")
                       for p in m.index], index=m.index)
    rstar_m = transform.carry_forward(rstar_est.r_star, m.index[-1]).reindex(m.index)
    hist = (m - exp_m - rstar_m).dropna()

    return Stance(
        ois_2y=float(ois.iloc[-1]), ois_date=ois.index[-1].to_timestamp(), expected_inflation=e,
        expectation_source=f"MPR {mpr_date:%B %Y} year-ahead CPI projection",
        real_rate=real, r_star=rs, r_star_se=se, r_star_quarter=rstar_est.r_star.index[-1],
        band=band, gap=real - rs, cls=score.stance(real, band), history=hist,
    )


@dataclass
class Verdict:
    pressure: float
    pressure_class: str
    stance_class: str
    verdict: str
    driver: str
    contributions: dict[str, float]


def verdict(cfg: Config, block_scores: dict[str, float], stance: Stance) -> Verdict:
    pw = cfg.weights["pressure"]
    p = score.pressure(block_scores, pw["weights"])
    pc = score.direction(p, pw["threshold"])
    return Verdict(
        pressure=p, pressure_class=pc, stance_class=stance.cls,
        verdict=score.verdict(pc, stance.cls),
        driver=score.driver(block_scores, pw["weights"]),
        contributions={k: w * block_scores[k] for k, w in pw["weights"].items()},
    )
