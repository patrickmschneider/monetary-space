"""Load and validate config/ and manual/. Everything tunable lives there, not in code."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

MAX_SCORED = 14
BLOCKS = ("A", "B", "C")
BLOCK_TITLES = {
    "A": "Is the economy running hot or cold?",
    "B": "Is underlying inflation consistent with 2%?",
    "C": "Is the world pushing UK inflation up or down?",
    "D": "Is policy tight or loose, looking two years ahead?",
}
BLOCK_NAMES = {"A": "Demand", "B": "Domestic inflation", "C": "Global", "D": "Stance"}


@dataclass
class Config:
    sources: dict
    series: dict
    indicators: list[dict]
    weights: dict
    manual: dict[str, pd.DataFrame]


def load(root: Path) -> Config:
    ind = yaml.safe_load((root / "config" / "indicators.yaml").read_text())
    weights = yaml.safe_load((root / "config" / "weights.yaml").read_text())
    manual = {p.stem: pd.read_csv(p, comment="#") for p in sorted((root / "manual").glob("*.csv"))}
    cfg = Config(ind["sources"], ind["series"], ind["indicators"], weights, manual)
    validate(cfg)
    return cfg


def validate(cfg: Config) -> None:
    ids = [i["id"] for i in cfg.indicators]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate indicator ids")
    if len(ids) > MAX_SCORED:
        raise ValueError(f"{len(ids)} scored indicators; the cap is {MAX_SCORED}")
    for i in cfg.indicators:
        if i["block"] not in BLOCKS:
            raise ValueError(f"{i['id']}: block must be one of {BLOCKS}")
        if i["sign"] not in (1, -1):
            raise ValueError(f"{i['id']}: sign must be +1 or -1")
        for s in i["series"]:
            if s not in cfg.series:
                raise ValueError(f"{i['id']}: unknown series {s}")
        sig = i["sigma"]
        if sig["method"] == "value" and not sig.get("rationale"):
            raise ValueError(f"{i['id']}: a config sigma needs a stated rationale")
    for sid, s in cfg.series.items():
        if s["source"] not in cfg.sources:
            raise ValueError(f"series {sid}: unknown source {s['source']}")
    w = cfg.weights["pressure"]["weights"]
    if abs(sum(w.values()) - 1) > 1e-9:
        raise ValueError(f"pressure weights sum to {sum(w.values())}, not 1")


def manual_value(cfg: Config, field: str, as_of: pd.Timestamp) -> tuple[float, str]:
    """Latest MPR-based manual value on or before as_of, with a citation label."""
    mpr = cfg.manual["mpr"].copy()
    mpr["mpr_date"] = pd.to_datetime(mpr["mpr_date"])
    rows = mpr[(mpr["mpr_date"] <= as_of) & mpr[field].notna()].sort_values("mpr_date")
    if rows.empty:
        raise ValueError(f"manual/mpr.csv has no {field} on or before {as_of.date()}")
    row = rows.iloc[-1]
    return float(row[field]), f"MPR {row['mpr_date']:%B %Y}"
