"""Command line: python -m monetary_space build [--no-fetch] [--store DIR] [--out DIR]"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from . import build


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
    r = sub.add_parser("refresh-calendar", help="update manual/mpc_dates.csv and manual/mpr.csv from the Bank's website")
    r.add_argument("--root", type=Path, default=Path("."))
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv(args.root / ".env")
    if args.cmd == "build":
        build.run(args.root, args.store, args.out, fetch_data=not args.no_fetch)
    elif args.cmd == "refresh-calendar":
        import pandas as pd
        from . import config
        cfg = config.load(args.root)
        build.refresh_calendar(cfg, pd.Timestamp.now(tz="Europe/London"))
        build.write_csv_keeping_header(args.root / "manual" / "mpc_dates.csv", cfg.manual["mpc_dates"])
        build.write_csv_keeping_header(args.root / "manual" / "mpr.csv", cfg.manual["mpr"])


if __name__ == "__main__":
    main()
