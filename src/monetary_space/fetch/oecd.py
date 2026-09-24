"""OECD SDMX: Composite Leading Indicators (amplitude adjusted, long-term average = 100)."""
from __future__ import annotations

import io

import pandas as pd

from .http import get

CLI = ("https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,/"
       "{areas}.M.LI.IX._Z.AA.IX._Z.H?startPeriod={start}&dimensionAtObservation=AllDimensions&format=csvfilewithlabels")


def parse_cli(text: str) -> dict[str, pd.Series]:
    df = pd.read_csv(io.StringIO(text))
    wide = df.pivot(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    wide.index = pd.PeriodIndex(wide.index, freq="M")
    return {area: wide[area].dropna().sort_index().astype(float) for area in wide.columns}


def cli(areas: list[str], start: str = "1985-01") -> dict[str, pd.Series]:
    out = parse_cli(get(CLI.format(areas="+".join(areas), start=start)).text)
    missing = set(areas) - set(out)
    if missing:
        raise ValueError(f"OECD CLI missing areas {sorted(missing)}")
    return out
