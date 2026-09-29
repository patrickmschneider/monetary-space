"""The Phillips-curve structure: new benchmarks, transforms and the decomposition charts."""
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from monetary_space import config, decomposition, indicators, transform

ROOT = Path(__file__).resolve().parents[1]


def test_blocks_are_phillips_curve_terms_and_cap_holds():
    cfg = config.load(ROOT)
    blocks = {i["block"] for i in cfg.indicators}
    assert blocks == {"E", "D", "S", "C"} and len(cfg.indicators) <= config.MAX_SCORED
    assert set(cfg.weights["pressure"]["weights"]) == blocks


def test_diff_12m():
    m = pd.period_range("2024-01", periods=13, freq="M")
    x = pd.Series(range(13), index=m, dtype=float)
    assert transform.apply("diff_12m", [x]).iloc[-1] == 12.0


def test_trailing_mean_and_potential_growth_benchmarks():
    cfg = config.load(ROOT)
    q = pd.period_range("2000Q1", "2026Q1", freq="Q")
    import numpy as np
    x = pd.Series(1.0 + 0.5 * np.sin(np.arange(len(q))), index=q)
    x.iloc[-5:] = -1.0
    spec = next(i for i in cfg.indicators if i["id"] == "productivity")
    ind = indicators.compute(spec, {"LZVD": x}, cfg, pd.Timestamp("2026-09-24"))
    assert ind.b == pytest.approx(x.iloc[-21:-1].mean())   # 5-year mean ending the quarter before
    assert ind.latest.z > 0                     # productivity below trend is inflationary (sign −1)
    gspec = next(i for i in cfg.indicators if i["id"] == "gdp")
    m = pd.period_range("1997-01", "2026-07", freq="M")
    est = {"rstar": SimpleNamespace(growth=pd.Series(1.25, index=q))}
    g = indicators.compute(gspec, {"ECY2": pd.Series([100 * 1.001 ** k for k in range(len(m))], index=m)},
                           cfg, pd.Timestamp("2026-09-24"), estimates=est)
    assert g.b == 1.25


def test_decomposition_charts_render_from_results():
    cfg = config.load(ROOT)
    if not cfg.analysis:
        pytest.skip("no analysis results")
    html = decomposition.section(cfg.analysis, 2)
    assert html.count("<svg") == 3
    assert "Demand-driven" in html and "Labour-market tightness" in html and "Monetary policy" in html
