"""Build the monthly NEM wholesale electricity price history (src/monetary_space/fetch/aemo.py)
into analysis/results/au/nem_monthly.csv. Run once, or to extend the start date:

    python analysis/nem_history.py [--start 2005-01]

Each build re-reads only the latest 14 months, so this rarely needs re-running.
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from monetary_space.fetch import aemo  # noqa: E402


def main(start: str) -> None:
    end = pd.Period(pd.Timestamp.now(tz="Australia/Sydney").tz_localize(None), "M") - 1
    months = list(pd.period_range(pd.Period(start, "M"), end, freq="M"))
    with ThreadPoolExecutor(max_workers=8) as pool:            # five files per month, ~3,000 in all
        prices = list(pool.map(aemo.month, months))
    rows = [(str(p), round(v, 3)) for p, v in zip(months, prices) if v is not None]
    for p, v in zip(months, prices):
        if v is None:
            print(p, "missing", flush=True)
    aemo.HISTORY.parent.mkdir(parents=True, exist_ok=True)
    aemo.HISTORY.write_text(
        "# NEM wholesale electricity price, $/MWh, monthly, demand-weighted across NSW, QLD, VIC, SA and TAS.\n"
        "# Source: AEMO aggregated price and demand data. Built by analysis/nem_history.py.\n"
        + pd.DataFrame(rows, columns=["month", "price"]).to_csv(index=False))
    print(f"wrote {len(rows)} months to {aemo.HISTORY}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2005-01")
    main(ap.parse_args().start)
