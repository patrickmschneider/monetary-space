import json
from pathlib import Path

import pandas as pd
import pytest

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


def _dmp_xlsx(date_label):
    from io import BytesIO
    rows = [
        [None, "Realised price growth over the past year (%)", None, None, "Expected price growth over the next year (%)", None],
        [None] * 6,
        [None, "Mean realised price growth (%)", None, None, "Mean expected price growth (%)", None],
        [date_label, "Single month", "3 month average", None, "Single month", "3 month average"],
        ["Aug-26", 3.474, 3.675, None, 3.591, 3.771],
        ["Sep-26", 3.79, 3.709, None, 3.859, 3.708],
        ["Oct-26", 3.8, 3.7, None, 3.9, 3.75],
    ]
    buf = BytesIO()
    pd.DataFrame(rows).to_excel(buf, sheet_name="Price growth", header=False, index=False)
    return buf.getvalue()


def test_dmp_price_growth_with_and_without_date_header():
    from monetary_space.fetch import boe
    for label in ("Survey date", None):
        s = boe.parse_dmp_price_growth(_dmp_xlsx(label))
        assert s.index[-1] == pd.Period("2026-10", "M")
        assert s[pd.Period("2026-09", "M")] == 3.708


def test_fiscal_outlook_merges_history_and_latest_vintage():
    import json
    from pathlib import Path
    import pandas as pd
    from monetary_space.fetch import fiscal
    payload = json.loads((Path(__file__).parent / "fixtures" / "fiscal_outlook.json").read_text())
    out = fiscal.parse_outlook(payload)
    capd, psnb = out["CAPD"], out["PSNB"]
    assert capd.index.freqstr == "Y-MAR" and fiscal.fy_label(capd.index[-1]) == "2026-27"
    assert capd[pd.Period("2025", "Y-MAR")] == 2.17               # history: deficit = −balance
    assert capd[pd.Period("2026", "Y-MAR")] == 1.0                # the latest vintage overrides history
    assert psnb[pd.Period("2027", "Y-MAR")] == 4.2


def test_imf_fiscal_flips_balances_to_deficits():
    from monetary_space.fetch import fiscal
    payloads = {
        "DEFICIT": {"values": {"GGXCNL_G01_GDP_PT": {"USA": {"2025": -7.1, "2026": -8.5}, "AUS": {"2026": -3.2}}}},
        "CAPD": {"values": {"GGCBP_G01_PGDP_PT": {"USA": {"2025": -4.4, "2026": -4.9}}}},
    }
    out = fiscal.parse_imf(payloads, "USA")
    assert out["CAPD"].index.freqstr.startswith("Y")
    assert out["CAPD"][pd.Period("2026", "Y")] == 4.9
    assert out["DEFICIT"].tolist() == [7.1, 8.5]
    with pytest.raises(ValueError):
        fiscal.parse_imf(payloads, "AUS")   # no CAPD for Australia in this payload
