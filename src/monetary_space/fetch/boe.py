"""Bank of England survey spreadsheets: Decision Maker Panel, Inflation Attitudes Survey, Agents' scores.

The DMP file name changes each release, so its link is discovered from the DMP
data page, with the BoE monthly release pages as a fallback. The other two files
are overwritten in place.
"""
from __future__ import annotations

import datetime as dt
import functools
import io
import re
import zipfile

import numpy as np
import pandas as pd
import requests

from .http import get

BOE = "https://www.bankofengland.co.uk"
DMP_DATA_PAGE = "https://decisionmakerpanel.co.uk/data/"
MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]


# ------------------------------------------------------------ Decision Maker Panel
def discover_dmp_url() -> str:
    try:
        html = get(DMP_DATA_PAGE).text
        links = set(re.findall(
            r'href="(https?://[^"]*monthly-dmp-data-([a-z]+)-(\d{4})(?:-\d+)?\.xlsx)"', html, re.I))
        if links:
            return max(links, key=lambda t: (int(t[2]), MONTHS.index(t[1].lower()), t[0]))[0]
    except (requests.RequestException, ValueError):
        pass
    d = dt.date.today().replace(day=1)
    for _ in range(6):
        page = f"{BOE}/decision-maker-panel/{d.year}/{MONTHS[d.month - 1]}-{d.year}"
        try:
            r = get(page)
        except requests.RequestException:
            r = None
        if r is not None and "/error/404" not in r.url:
            m = re.search(r'href="([^"]*monthly-dmp-data-[^"]*\.xlsx)"', r.text)
            if m:
                return requests.compat.urljoin(BOE, m.group(1))
        d = (d - dt.timedelta(days=1)).replace(day=1)
    raise RuntimeError("DMP spreadsheet link not found")


def parse_dmp_price_growth(xlsx: bytes, measure: str = "3 month average") -> pd.Series:
    """Sheet 'Price growth': mean expected own-price growth over the next year, %."""
    raw = pd.read_excel(io.BytesIO(xlsx), sheet_name="Price growth", header=None)
    r0, c0 = next((i, j) for (i, j), v in raw.stack().items()
                  if isinstance(v, str) and v.strip().lower().startswith("mean expected price growth"))
    hdr = r0 + 1
    col = next(j for j in range(c0, c0 + 3) if str(raw.iat[hdr, j]).strip().lower() == measure.lower())
    datecol = next(j for j in range(raw.shape[1]) if str(raw.iat[hdr, j]).lower().startswith("survey date"))
    body = raw.iloc[hdr + 1:, [datecol, col]].dropna()
    idx = pd.PeriodIndex(pd.to_datetime(body.iloc[:, 0].astype(str).str.strip(), format="%b-%y"), freq="M")
    s = pd.Series(pd.to_numeric(body.iloc[:, 1], errors="coerce").to_numpy(dtype=float), index=idx)
    return s.dropna().sort_index().rename("DMP_PRICE_1Y")


def dmp_price_growth() -> pd.Series:
    return parse_dmp_price_growth(get(discover_dmp_url()).content)


# ------------------------------------------------------ Inflation Attitudes Survey
IAS_URL = f"{BOE}/-/media/boe/files/inflation-attitudes-survey/long-run.xlsx"


def parse_ias_median_1y(xlsx: bytes) -> pd.Series:
    """LONG-RUN sheet: median expected change in shop prices over the next 12 months, by quarter."""
    raw = pd.read_excel(io.BytesIO(xlsx), sheet_name=0, header=None)
    lab = raw.iloc[:, 0].astype(str).str.strip()
    drow = next(i for i in range(15)
                if raw.iloc[i, 1:].map(lambda x: isinstance(x, (dt.datetime, pd.Timestamp))).sum() > 10)
    q = lab[lab.str.match(r"^Q\.?\s*2a\b", case=False)].index[0]
    med = lab[(lab.str.lower() == "median") & (lab.index > q)].index[0]
    dates = pd.to_datetime(raw.iloc[drow, 1:], errors="coerce")
    vals = pd.to_numeric(raw.iloc[med, 1:], errors="coerce")
    ok = dates.notna() & vals.notna()
    idx = pd.PeriodIndex(pd.DatetimeIndex(dates[ok]), freq="Q")
    s = pd.Series(vals[ok].to_numpy(dtype=float), index=idx)
    return s[~s.index.duplicated(keep="last")].sort_index().rename("IAS_MEDIAN_1Y")


def ias_median_1y() -> pd.Series:
    return parse_ias_median_1y(get(IAS_URL).content)


# ------------------------------------------------------------------ Agents' scores
AGENTS_URL = f"{BOE}/-/media/boe/files/agents-summary/agentsscores.xlsx"


def parse_agents_capacity(xlsx: bytes) -> pd.Series:
    """'Quarterly scores' sheet: current capacity utilisation (0 = normal, about −5..+5)."""
    raw = pd.read_excel(io.BytesIO(xlsx), sheet_name="Quarterly scores", header=None)
    col = next(j for j in range(raw.shape[1])
               if re.search(r"capacity utilisation", " ".join(str(x) for x in raw.iloc[:5, j] if pd.notna(x)), re.I))
    body = raw.iloc[5:, [0, col]]
    body = body[body.iloc[:, 0].astype(str).str.match(r"^\d{4} Q[1-4]$")]
    idx = pd.PeriodIndex(body.iloc[:, 0].str.replace(" ", ""), freq="Q")
    s = pd.Series(pd.to_numeric(body.iloc[:, 1], errors="coerce").to_numpy(dtype=float), index=idx)
    return s.dropna().sort_index().rename("AGENTS_CAPACITY")


def agents_capacity() -> pd.Series:
    return parse_agents_capacity(get(AGENTS_URL).content)


# ------------------------------------------------------------ Bank of England Database
IADB = f"{BOE}/boeapps/database/_iadb-fromshowcolumns.asp"


def parse_iadb_csv(text: str, code: str) -> pd.Series:
    """Database CSV export (CSVF=TN): DATE,<code> with dates like '23 Sep 2026'."""
    df = pd.read_csv(io.StringIO(text))
    if code not in df.columns:
        raise ValueError(f"{code} not in Bank of England database response")
    idx = pd.PeriodIndex(pd.to_datetime(df["DATE"], format="%d %b %Y"), freq="D")
    s = pd.Series(pd.to_numeric(df[code], errors="coerce").to_numpy(dtype=float), index=idx, name=code)
    return s.dropna().sort_index()


def iadb(code: str, start: str = "01/Jan/1990") -> pd.Series:
    params = {"csv.x": "yes", "Datefrom": start, "Dateto": "now", "SeriesCodes": code,
              "CSVF": "TN", "UsingCodes": "Y", "VPD": "Y", "VFD": "N"}
    return parse_iadb_csv(get(IADB, params=params).text, code)


# ------------------------------------------------------------------ OIS (SONIA) curves
# Bank of England yield curves: archive (2009 to last month) + current-month file,
# both overwritten in place. Rates are continuously compounded zero-coupon, in %.
# The monthly-maturity "short end" sheets (1/12y to 5y) exist in every file.
YC = f"{BOE}/-/media/boe/files/statistics/yield-curves/"
OIS_ARCHIVE, OIS_LATEST = YC + "oisddata.zip", YC + "latest-yield-curve-data.zip"
FWD_SHEETS = ("1. fwds, short end", "1. fwd curve")      # 2016+ / 2009–2015 file
SPOT_SHEETS = ("3. spot, short end", "2. spot curve")


def _parse_curve_sheet(raw: pd.DataFrame) -> pd.DataFrame:
    col_a = raw.iloc[:, 0]
    yrs_row = raw.index[col_a.astype(str).str.strip().str.lower() == "years:"][0]
    mats = pd.to_numeric(raw.loc[yrs_row].iloc[1:], errors="coerce")
    is_date = col_a.map(lambda v: hasattr(v, "year"))
    data = raw.loc[is_date & (raw.index > yrs_row)]
    df = data.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    df.index = pd.to_datetime(data.iloc[:, 0])
    keep = mats.notna().to_numpy()
    df = df.loc[:, keep]
    df.columns = np.round(mats[keep].astype(float).to_numpy(), 4)
    return df.dropna(how="all")


@functools.lru_cache(maxsize=2)
def _ois_zip(url: str) -> bytes:
    content = get(url).content
    if not content.startswith(b"PK"):
        raise RuntimeError(f"{url} did not return a zip file")
    return content


def _ois_curves(sheets: tuple[str, ...]) -> pd.DataFrame:
    frames = []
    for url in (OIS_ARCHIVE, OIS_LATEST):                  # latest last, so it wins on overlap
        with zipfile.ZipFile(io.BytesIO(_ois_zip(url))) as z:
            for name in sorted(z.namelist()):
                if name.startswith("OIS daily data") and name.endswith(".xlsx"):
                    xl = pd.ExcelFile(io.BytesIO(z.read(name)), engine="openpyxl")
                    sheet = next(s for s in sheets if s in xl.sheet_names)
                    frames.append(_parse_curve_sheet(xl.parse(sheet, header=None)))
    df = pd.concat(frames)
    return df[~df.index.duplicated(keep="last")].sort_index()


def ois_spot(maturity: float) -> pd.Series:
    s = _ois_curves(SPOT_SHEETS)[round(float(maturity), 4)].dropna()
    return pd.Series(s.to_numpy(), index=pd.PeriodIndex(s.index, freq="D"), name=f"OIS_{maturity:g}Y")


def ois_forwards(maturities: list[float], since: str) -> dict[str, pd.Series]:
    """Instantaneous forward rates at the given maturities (years), daily from `since`."""
    df = _ois_curves(FWD_SHEETS)
    df = df[df.index >= pd.Timestamp(since)]
    return {f"{m:g}": pd.Series(df[round(float(m), 4)].to_numpy(), index=pd.PeriodIndex(df.index, freq="D")).dropna()
            for m in maturities}
