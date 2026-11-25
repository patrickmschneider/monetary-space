"""UK public finances by fiscal year, from the Fiscal Space dashboard's published outlook.

Fiscal Space compiles the OBR public finances databank (outturn from 1975-76) and the
latest OBR Economic and fiscal outlook (forecast). Fiscal years run April–March and are
stored as annual periods ending in March: 2026-27 is Period("2027", "Y-MAR").

Series returned (% of GDP, positive = deficit):
  PSNB  public sector net borrowing (headline deficit)
  CAPD  cyclically adjusted primary deficit: borrowing excluding the cycle and debt interest
"""
from __future__ import annotations

import pandas as pd

from .http import get

FY = "Y-MAR"


def fiscal_year(label: str) -> pd.Period:
    """'2026-27' → the fiscal year ending March 2027."""
    return pd.Period(str(int(label[:4]) + 1), FY)


def fy_label(p: pd.Period) -> str:
    return f"{p.year - 1}-{p.year % 100:02d}"


def parse_outlook(payload: dict) -> dict[str, pd.Series]:
    """History from the OBR databank; the latest OBR vintage overrides it where they overlap."""
    vintage = next(v for v in payload["vintages"] if v["id"] == payload["latestVintage"])
    cols = {"PSNB": lambda r: r.get("borrowingPct"),
            "CAPD": lambda r: None if r.get("structuralPrimaryBalancePct") is None else -r["structuralPrimaryBalancePct"]}
    out = {}
    for name, get_value in cols.items():
        values: dict[pd.Period, float] = {}
        for rows in (payload.get("deficitHistory") or [], vintage["rows"]):
            for r in rows:
                v = get_value(r)
                if v is not None:
                    values[fiscal_year(r["year"])] = float(v)
        if not values:
            raise ValueError(f"Fiscal Space outlook has no {name} values")
        s = pd.Series(values, name=name).sort_index()
        s.index = pd.PeriodIndex(s.index, freq=FY)
        dates = [vintage.get("publicationDate"), (payload.get("deficitHistoryMetadata") or {}).get("outturnAsOf")]
        s.attrs.update(released=max(pd.Timestamp(d) for d in dates if d), next_release="")
        out[name] = s
    return out


def outlook(url: str) -> dict[str, pd.Series]:
    return parse_outlook(get(url).json())
