"""Command line: python -m monetary_space build [--country ID|all] [--no-fetch] [--store DIR] [--out DIR]"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from . import build, config


def load_dotenv(path: Path) -> None:
    """Minimal .env reader for local runs (Actions passes secrets as env vars)."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    p = argparse.ArgumentParser(prog="monetary_space")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="fetch, store, score and render the page")
    b.add_argument("--root", type=Path, default=Path("."), help="repo root holding config/ and manual/")
    b.add_argument("--store", type=Path, default=Path("store"), help="checkout of the data branch")
    b.add_argument("--out", type=Path, default=Path("site"))
    b.add_argument("--no-fetch", action="store_true", help="rebuild from the latest stored vintage")
    b.add_argument("--country", default="all", help="one edition (uk, au, us) or all")
    r = sub.add_parser("refresh-calendar", help="update manual/<country>/mpc_dates.csv and mpr.csv from the central bank's website")
    r.add_argument("--root", type=Path, default=Path("."))
    r.add_argument("--country", default=config.DEFAULT_COUNTRY)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv(args.root / ".env")
    if args.cmd == "build":
        build.run_all(args.root, args.store, args.out, fetch_data=not args.no_fetch,
                      countries=None if args.country == "all" else [args.country])
    elif args.cmd == "refresh-calendar":
        import pandas as pd
        cfg = config.load(args.root, args.country)
        build.refresh_calendar(cfg, pd.Timestamp.now(tz=cfg.country["time_zone"]))
        manual = args.root / "manual" / args.country
        build.write_csv_keeping_header(manual / "mpc_dates.csv", cfg.manual["mpc_dates"])
        build.write_csv_keeping_header(manual / "mpr.csv", cfg.manual["mpr"])


if __name__ == "__main__":
    main()
