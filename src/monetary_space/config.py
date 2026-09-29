"""Load and validate config/ and manual/. Everything tunable lives there, not in code."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import yaml

MAX_SCORED = 14
# Phillips-curve terms: π = expectations + slack (demand, supply) + cost-push. P is policy stance.
BLOCKS = ("E", "D", "S", "C")
BLOCK_TITLES = {
    "E": "Are inflation expectations anchored at 2%?",
    "D": "Is demand running ahead of the economy's capacity?",
    "S": "Is the economy's capacity growing more slowly than normal?",
    "C": "Are external costs pushing up prices?",
    "P": "Is policy stimulating or restraining the economy?",
}
BLOCK_EXPLAIN = {
    "E": "What people expect inflation to be. Expectations feed into wage and price setting, so if they drift above 2% inflation becomes harder to bring down. In the Phillips curve this is the expected-inflation term.",
    "D": "Whether spending is outstripping what the economy can produce. A tight labour market and fast growth push up wages and prices. This is the demand side of the slack (output gap) term.",
    "S": "Whether the economy's capacity is growing more slowly than normal. Weak productivity or fast-rising labour costs leave less room to grow without inflation, even if demand is not strong. This is the supply side of the slack term.",
    "C": "External costs: energy, import prices and the exchange rate. Their first effect on prices is usually temporary, so they get a smaller weight, which rises when inflation is already high and knock-on effects on pay and expectations are more likely.",
}
BLOCK_NAMES = {"E": "Expectations", "D": "Demand", "S": "Supply", "C": "Cost-push", "P": "Policy stance"}


@dataclass
class Config:
    sources: dict
    series: dict
    indicators: list[dict]
    weights: dict
    manual: dict[str, pd.DataFrame]
    charts: dict
    nairu: dict
    rstar: dict
    analysis: dict = field(default_factory=dict)   # analysis/results/*.json, re-estimated after releases


def load(root: Path) -> Config:
    ind = yaml.safe_load((root / "config" / "indicators.yaml").read_text())
    weights = yaml.safe_load((root / "config" / "weights.yaml").read_text())
    manual = {p.stem: pd.read_csv(p, comment="#") for p in sorted((root / "manual").glob("*.csv"))}
    charts_path = root / "config" / "charts.yaml"
    charts = yaml.safe_load(charts_path.read_text()) if charts_path.exists() else {}
    nairu_path = root / "config" / "nairu.yaml"
    nairu = yaml.safe_load(nairu_path.read_text()) if nairu_path.exists() else {}
    rstar_path = root / "config" / "rstar.yaml"
    rstar = yaml.safe_load(rstar_path.read_text()) if rstar_path.exists() else {}
    analysis = {p.stem: json.loads(p.read_text()) for p in sorted((root / "analysis" / "results").glob("*.json"))}
    cfg = Config(ind["sources"], ind["series"], ind["indicators"], weights, manual, charts, nairu, rstar, analysis)
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
            if s.split(":")[0] not in cfg.series:
                raise ValueError(f"{i['id']}: unknown series {s}")
        sig = i["sigma"]
        if sig["method"] == "value" and not sig.get("rationale"):
            raise ValueError(f"{i['id']}: a config sigma needs a stated rationale")
    for sid, s in cfg.series.items():
        if s["source"] not in cfg.sources:
            raise ValueError(f"series {sid}: unknown source {s['source']}")
    for c in cfg.charts.get("charts", []):
        if c["series"].split(":")[0] not in cfg.series:
            raise ValueError(f"chart {c['id']}: unknown series {c['series']}")
    for role, sid in {**cfg.nairu.get("series", {}), **cfg.rstar.get("series", {})}.items():
        if sid not in cfg.series:
            raise ValueError(f"nairu.yaml {role}: unknown series {sid}")
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
