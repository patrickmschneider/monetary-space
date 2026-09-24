import shutil
from pathlib import Path

import pandas as pd
import pytest
import yaml

from monetary_space import build, config, indicators, store

ROOT = Path(__file__).resolve().parents[1]


def test_repo_config_is_valid():
    cfg = config.load(ROOT)
    assert len(cfg.indicators) <= config.MAX_SCORED


@pytest.fixture
def tmp_root(tmp_path):
    shutil.copytree(ROOT / "config", tmp_path / "config")
    shutil.copytree(ROOT / "manual", tmp_path / "manual")
    return tmp_path


def edit_indicator(root, ind_id, **changes):
    p = root / "config" / "indicators.yaml"
    doc = yaml.safe_load(p.read_text())
    next(i for i in doc["indicators"] if i["id"] == ind_id).update(changes)
    p.write_text(yaml.safe_dump(doc, sort_keys=False))


def test_config_caps_scored_indicators(tmp_root):
    p = tmp_root / "config" / "indicators.yaml"
    doc = yaml.safe_load(p.read_text())
    base = doc["indicators"][0]
    doc["indicators"] += [dict(base, id=f"extra{k}") for k in range(15)]
    p.write_text(yaml.safe_dump(doc))
    with pytest.raises(ValueError, match="cap"):
        config.load(tmp_root)


def test_config_sigma_needs_rationale(tmp_root):
    edit_indicator(tmp_root, "gdp", sigma={"method": "value", "value": 2.0})
    with pytest.raises(ValueError, match="rationale"):
        config.load(tmp_root)


def synthetic_gdp():
    idx = pd.period_range("1997-01", "2026-07", freq="M")
    return pd.Series([100 * 1.002**k for k in range(len(idx))], index=idx, dtype=float)


def test_changing_a_benchmark_changes_the_score_without_code(tmp_root):
    as_of = pd.Timestamp("2026-09-24")
    data = {"ECY2": synthetic_gdp()}
    spec = lambda: next(i for i in config.load(tmp_root).indicators if i["id"] == "gdp")
    before = indicators.compute(spec(), data, config.load(tmp_root), as_of)
    edit_indicator(tmp_root, "gdp", benchmark={"method": "value", "value": 0.0})
    after = indicators.compute(spec(), data, config.load(tmp_root), as_of)
    assert after.b == 0.0 and after.latest.raw > before.latest.raw


def test_staleness_uses_lag_and_grace():
    p = pd.Period("2026-06", "M")
    # July data usually due 31 Jul + 45 days = 14 Sep; stale after 14 more days.
    assert indicators.next_due(p, 45) == pd.Timestamp("2026-09-14")
    assert not indicators.is_stale(p, 45, pd.Timestamp("2026-09-28"), 14)
    assert indicators.is_stale(p, 45, pd.Timestamp("2026-09-29"), 14)


def test_failed_source_keeps_last_good_value(tmp_root, monkeypatch):
    cfg = config.load(tmp_root)
    good = synthetic_gdp()

    def fake_fetch(spec):
        if spec["uri"].endswith("/ecy2/mgdp"):
            raise ConnectionError("ONS down")
        return good

    monkeypatch.setattr(build, "fetch", fake_fetch)
    res = build.fetch_all(cfg, {"ECY2": good.iloc[:-1]}, "2026-09-24T07:10:00")
    assert "ECY2" in res.failed
    assert res.data["ECY2"].index[-1] == good.index[-2]
    assert any(r["series_id"] == "ECY2" and r["status"] == "kept_last_good" for r in res.log_rows)


def test_vintage_round_trip(tmp_path):
    q = pd.Series([1.5, 2.5], index=pd.period_range("2020Q1", periods=2, freq="Q"))
    m = synthetic_gdp().iloc[:5]
    store.save_vintage(tmp_path, pd.Timestamp("2026-09-24"), {"Q": q, "M": m})
    day, back = store.load_vintage(tmp_path)
    assert day == pd.Timestamp("2026-09-24")
    pd.testing.assert_series_equal(back["Q"], q, check_names=False)
    pd.testing.assert_series_equal(back["M"], m, check_names=False)
    assert store.load_vintage(tmp_path, pd.Timestamp("2026-09-23")) == (None, {})
