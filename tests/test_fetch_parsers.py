import json
from pathlib import Path

import pandas as pd

from monetary_space.fetch import ons

FIXTURES = Path(__file__).parent / "fixtures"


def test_ons_rolling_quarter_restamped_on_end_month():
    payload = json.loads((FIXTURES / "ons_mgsx.json").read_text())
    s = ons.parse_timeseries(payload, "M")
    # '2026 JUN' is labelled '2026 MAY-JUL': the window ends in July.
    assert s.index[-1] == pd.Period("2026-07", "M")
    assert s.name == "MGSX"


def test_ons_quarterly():
    payload = json.loads((FIXTURES / "ons_mgsx.json").read_text())
    s = ons.parse_timeseries(payload, "Q")
    assert s.index.freqstr.startswith("Q")
    assert s.index.is_monotonic_increasing
