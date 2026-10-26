"""Country editions: config per country, store layout, edition switch, build isolation."""
import re
import shutil
from pathlib import Path

import pandas as pd
import pytest
import yaml

from monetary_space import build, config, render, store

ROOT = Path(__file__).resolve().parents[1]
UK = {"id": "uk", "name": "UK", "path": ""}
AU = {"id": "au", "name": "Australia", "path": "au/"}
US = {"id": "us", "name": "US", "path": "us/"}


def test_uk_is_the_default_edition_at_the_site_root():
    cfg = config.load(ROOT)
    assert cfg.country["id"] == "uk" and cfg.country["path"] == ""
    assert [c["id"] for c in config.countries(ROOT)][0] == "uk"


def test_country_yaml_must_be_complete(tmp_path):
    shutil.copytree(ROOT / "config", tmp_path / "config")
    shutil.copytree(ROOT / "manual", tmp_path / "manual")
    p = tmp_path / "config" / "uk" / "country.yaml"
    doc = yaml.safe_load(p.read_text())
    del doc["central_bank"]
    p.write_text(yaml.safe_dump(doc))
    with pytest.raises(ValueError, match="central_bank"):
        config.load(tmp_path)


def test_switch_hidden_with_one_edition():
    assert render.edition_switch(UK, [UK], "index.html") == ""


def test_switch_links_to_the_same_page_in_every_edition():
    from_root = render.edition_switch(UK, [UK, AU, US], "drivers.html")
    assert 'href="drivers.html" aria-current="page"' in from_root
    assert 'href="au/drivers.html"' in from_root and 'href="us/drivers.html"' in from_root
    from_au = render.edition_switch(AU, [UK, AU, US], "stance.html")
    assert 'href="../stance.html"' in from_au and 'href="../us/stance.html"' in from_au
    assert 'href="../au/stance.html" aria-current="page"' in from_au
    assert from_au.count("aria-current") == 1


def test_single_country_store_moves_into_its_folder(tmp_path):
    store.save_vintage(tmp_path, pd.Timestamp("2026-10-01"), {"X": pd.Series([1.0], index=pd.period_range("2026-09", periods=1, freq="M"))})
    store.append_log(tmp_path, [dict(run_at="2026-10-01T07:10:00+01:00", series_id="X", status="ok", last_period="2026-09", detail="")])
    log_before = (tmp_path / "fetch_log.csv").read_text()
    assert store.migrate_to_country(tmp_path, "uk")
    assert not (tmp_path / "vintages").exists() and not (tmp_path / "fetch_log.csv").exists()
    assert (tmp_path / "uk" / "fetch_log.csv").read_text() == log_before     # release dates come from the log
    day, data = store.load_vintage(tmp_path / "uk")
    assert day == pd.Timestamp("2026-10-01") and list(data) == ["X"]
    assert not store.migrate_to_country(tmp_path, "uk")                       # idempotent


def test_a_failing_edition_falls_back_to_its_stored_vintage(monkeypatch, tmp_path):
    calls = []

    def fake_run(root, store_root, out_root, fetch_data, country):
        calls.append((country, fetch_data))
        if country == "au" and fetch_data:
            raise RuntimeError("ABS changed its format")
        return {"country": country}

    monkeypatch.setattr(build, "run", fake_run)
    done = build.run_all(ROOT, tmp_path, tmp_path, True, ["uk", "au", "us"])
    assert set(done) == {"uk", "au", "us"}
    assert calls == [("uk", True), ("au", True), ("au", False), ("us", True)]


def test_an_edition_that_cannot_build_stops_the_deploy_after_the_others(monkeypatch, tmp_path):
    built = []

    def fake_run(root, store_root, out_root, fetch_data, country):
        if country == "au":
            raise RuntimeError("broken")
        built.append(country)
        return {}

    monkeypatch.setattr(build, "run", fake_run)
    with pytest.raises(SystemExit, match="au"):
        build.run_all(ROOT, tmp_path, tmp_path, True, ["uk", "au", "us"])
    assert built == ["uk", "us"]


UK_WORDS = ("Bank Rate", "Bank of England", "MPC", "MPR", "gilt", "ONS", "sterling", "SONIA", "Ofgem", "£", "LFS", "PAYE")


@pytest.mark.parametrize("country", ["us", "au"])
def test_edition_loads_and_has_no_uk_wording(country):
    cfg = config.load(ROOT, country)
    assert cfg.country["path"] == f"{country}/" and len(cfg.indicators) <= config.MAX_SCORED
    text = " ".join(str(v) for v in [cfg.country, cfg.indicators, cfg.charts, cfg.weights["stance"], cfg.series])
    text = text.replace("UK edition", "")                     # deliberate cross-references
    assert [w for w in UK_WORDS if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text)] == []


def test_every_edition_builds_its_switch_entry():
    ids = [c["id"] for c in config.countries(ROOT)]
    assert ids == ["uk", "au", "us"]
    for c in config.countries(ROOT):
        assert c["path"] == ("" if c["id"] == "uk" else f"{c['id']}/")
