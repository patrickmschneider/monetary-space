"""Read the r* suite (analysis/rstar_suite.py → analysis/results/rstar_suite.json).

The suite is estimated after data releases, not on every build. It provides the headline r*
and its range (the Stance block's neutral zone), a headline history for the real-rate gap and
the policy rule, and potential growth for the GDP benchmark.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


def _q(d: dict) -> pd.Series:
    return pd.Series({pd.Period(k, "Q"): (v[0] if isinstance(v, list) else v) for k, v in d.items()}).sort_index()


@dataclass
class Suite:
    headline: float              # rounded to 0.25pp
    range: tuple[float, float]
    r_star: pd.Series            # headline history, quarterly
    se: pd.Series                # half the range, for display compatibility
    growth: pd.Series            # potential growth, % a year
    estimators: dict
    history: dict
    raw: dict

    @property
    def band(self) -> tuple[float, float]:
        return self.range


def load(analysis: dict) -> Suite | None:
    res = analysis.get("rstar_suite")
    if not res:
        return None
    hist = _q(res["history"]["headline"])
    half = (res["range"][1] - res["range"][0]) / 2
    return Suite(
        headline=res["headline_rounded"], range=tuple(res["range"]), r_star=hist,
        se=pd.Series(half, index=hist.index), growth=_q(res["potential_growth"]),
        estimators=res["estimators"], history=res["history"], raw=res,
    )
