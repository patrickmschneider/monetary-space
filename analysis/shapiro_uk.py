"""
Shapiro (2022) supply/demand decomposition of UK consumer price inflation
using ONS Consumer trends (HHFCE by COICOP, quarterly, seasonally adjusted).

Sources (discovered at run time via the ONS website JSON; see discover()):
  CP  SA: /economy/nationalaccounts/satelliteaccounts/datasets/consumertrendscurrentpriceseasonallyadjusted
          -> edition /current -> file cpsa.xlsx  (sheets 0CS, 01CS..12CS, ...)
  CVM SA: /economy/nationalaccounts/satelliteaccounts/datasets/consumertrendschainedvolumemeasureseasonallyadjusted
          -> edition /current -> file cvmsa.xlsx (sheets 0KS, 01KS..12KS, ...)

Each division sheet has two tables stacked vertically: "Table Na" (annual) and
"Table Nb" (quarterly). Each table has 3 header rows: labels ("Time period and
codes"), "COICOP identifier code", "CDID identifier code", then data rows,
terminated by "End of table Nb.". Whole-column "[x]" = not collected
(04.4.4, 04.5.5, 09.6).
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent / "cache"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
ONS = "https://www.ons.gov.uk"
BASE = "/economy/nationalaccounts/satelliteaccounts/datasets/"
DATASETS = {"cp": "consumertrendscurrentpriceseasonallyadjusted",
            "cvm": "consumertrendschainedvolumemeasureseasonallyadjusted",
            "ts": "consumertrends"}   # time-series dataset: ct.csv, all CDIDs, from 1985Q1


# ----------------------------------------------------------------- download
def _get(url, tries=8, wait=15, **kw):
    """GET with retry on ONS rate limiting (429 returns an HTML page)."""
    for i in range(tries):
        r = requests.get(url, headers=UA, timeout=300, **kw)
        if r.status_code == 200:
            return r
        if r.status_code in (429, 502, 503):
            time.sleep(wait * (i + 1))
            continue
        r.raise_for_status()
    raise RuntimeError(f"failed after {tries} tries: {url} ({r.status_code})")


def discover(key: str) -> dict:
    """Landing page JSON -> edition URI -> download filename (+ release info)."""
    page = BASE + DATASETS[key]
    lp = _get(ONS + page + "/data").json()
    ed_uri = lp["datasets"][0]["uri"]                 # .../current
    ed = _get(ONS + ed_uri + "/data").json()
    ext = ".csv" if key == "ts" else ".xlsx"
    fname = next(d["file"] for d in ed["downloads"] if d["file"].endswith(ext))
    return {"page": page, "edition_uri": ed_uri, "file": fname,
            "url": f"{ONS}/file?uri={ed_uri}/{fname}",
            "release_date": lp["description"].get("releaseDate"),
            "next_release": lp["description"].get("nextRelease")}


def download(key: str, outdir: Path = HERE, force=True) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    info = discover(key)
    path = outdir / info["file"]
    if force or not path.exists():
        r = _get(info["url"])
        if (key == "ts" and not r.content.startswith(b'"Title"')) or \
           (key != "ts" and r.content[:2] != b"PK"):
            raise RuntimeError("unexpected content (rate-limit HTML page?)")
        path.write_bytes(r.content)
    return path


# ------------------------------------------------------------------- parser
_QRE = re.compile(r"^(\d{4}) Q([1-4])$")


def _parse_sheet_quarterly(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return quarterly table of one sheet: PeriodIndex x COICOP code, labels."""
    col0 = df[0].astype(str)
    hdr = [i for i, v in col0.items() if v.startswith("Time period")]
    for h in hdr:                                     # find the quarterly table
        first = str(df.iloc[h + 3, 0]).strip()
        if _QRE.match(first):
            break
    else:
        raise ValueError("no quarterly table found")
    assert col0[h + 1].startswith("COICOP") and col0[h + 2].startswith("CDID")
    labels = df.iloc[h, 1:].astype(str).str.replace(r"\s*\n?\[note \d+\]", "", regex=True).str.strip()
    codes = df.iloc[h + 1, 1:].astype(str).str.strip()
    cdids = df.iloc[h + 2, 1:].astype(str).str.strip()
    rows = []
    i = h + 3
    while i < len(df) and _QRE.match(str(df.iloc[i, 0]).strip()):
        rows.append(i)
        i += 1
    block = df.iloc[rows, 1:]
    idx = pd.PeriodIndex([str(v).strip().replace(" ", "") for v in df.iloc[rows, 0]], freq="Q")
    vals = block.apply(pd.to_numeric, errors="coerce")   # "[x]" -> NaN
    vals.index, vals.columns = idx, codes.values
    meta = {c: {"label": l, "cdid": d} for c, l, d in zip(codes, labels, cdids)}
    return vals, meta


def parse_consumer_trends(path: Path) -> tuple[pd.DataFrame, dict]:
    """All COICOP series (divisions/groups/classes) in the 0xx and 01..12 sheets."""
    xl = pd.ExcelFile(path)
    sheets = [s for s in xl.sheet_names if re.fullmatch(r"(0|0[1-9]|1[0-2])(CS|KS)", s)]
    assert len(sheets) == 13, sheets
    frames, meta = [], {}
    for s in sheets:
        v, m = _parse_sheet_quarterly(xl.parse(s, header=None, dtype=object))
        frames.append(v)
        meta.update(m)
    out = pd.concat(frames, axis=1)
    out = out.loc[:, ~out.columns.duplicated()]
    return out, meta


def parse_ct_csv(path: Path) -> pd.DataFrame:
    """ct.csv: wide; row0 'Title', row1 'CDID', meta rows, then annual rows
    ('1948'), quarterly rows ('1955 Q1') and monthly rows. Returns quarterly
    PeriodIndex x CDID."""
    raw = pd.read_csv(path, header=None, dtype=str, low_memory=False)
    assert raw.iloc[0, 0] == "Title" and raw.iloc[1, 0] == "CDID"
    q = raw[raw[0].str.match(r"^\d{4} Q[1-4]$", na=False)]
    out = q.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    out.index = pd.PeriodIndex(q[0].str.replace(" ", ""), freq="Q")
    out.columns = raw.iloc[1, 1:].str.strip().values
    return out.loc[:, ~out.columns.duplicated()]


def coicop_level(code: str) -> int | None:
    if re.fullmatch(r"\d{2}", code):
        return 1
    if re.fullmatch(r"\d{2}\.\d", code):
        return 2
    if re.fullmatch(r"\d{2}\.\d\.\d", code):
        return 3
    return None


def load(level: int = 2, outdir: Path = HERE, force=True, long_history=True):
    """
    Returns dict with:
      nominal, real : DataFrame (quarterly PeriodIndex x category code), £m SA
      labels        : {code: label}
      total_nominal, total_real : Series, UK domestic HHFCE (COICOP '0')
      total_national_nominal/real : national concept (NAT, incl. net tourism)
    level=2 -> COICOP groups (xx.x), with divisions that have no group split
               (10 Education) kept at division level. level=3 -> classes.
    Categories that are entirely missing ([x]) are dropped.
    long_history: the xlsx tables start 1997Q1; the same CDIDs in the
    time-series file ct.csv start 1985Q1 (checked identical from 1997Q1).
    """
    cp, mcp = parse_consumer_trends(download("cp", outdir, force))
    kv, mkv = parse_consumer_trends(download("cvm", outdir, force))
    codes = [c for c in cp.columns if coicop_level(c) is not None]
    lv = {c: coicop_level(c) for c in codes}

    def leaves(target):
        keep = []
        for c in codes:
            if lv[c] == target:
                keep.append(c)
            elif lv[c] < target and not any(d.startswith(c + ".") for d in codes):
                keep.append(c)   # no finer split published (e.g. 10, 02.2)
        return keep

    cats = [c for c in leaves(level) if cp[c].notna().any() and kv[c].notna().any()]
    nominal, real = cp[cats].copy(), kv[cats].copy()
    tot = {"total_nominal": cp["0"], "total_real": kv["0"],
           "total_national_nominal": cp["NAT"], "total_national_real": kv["NAT"]}
    if long_history:
        ts = parse_ct_csv(download("ts", outdir, force))
        def ext(df, meta, keys):
            x = ts[[meta[c]["cdid"] for c in keys]].copy(); x.columns = keys
            ov = x.loc[df.index[0]:df.index[-1]]
            assert (ov - df[keys]).abs().max().max() < 1.0, "ct.csv != xlsx"
            return x.loc[:df.index[-1]].dropna(how="all")
        nominal, real = ext(cp, mcp, cats), ext(kv, mkv, cats)
        start = max(nominal.dropna().index[0], real.dropna().index[0])
        nominal, real = nominal.loc[start:], real.loc[start:]
        tc, tk = ext(cp, mcp, ["0", "NAT"]), ext(kv, mkv, ["0", "NAT"])
        tot = {"total_nominal": tc["0"].loc[start:], "total_real": tk["0"].loc[start:],
               "total_national_nominal": tc["NAT"].loc[start:],
               "total_national_real": tk["NAT"].loc[start:]}
    return {"nominal": nominal, "real": real,
            "labels": {c: mcp[c]["label"] for c in cats},
            "cdid_cp": {c: mcp[c]["cdid"] for c in cats},
            "cdid_cvm": {c: mkv[c]["cdid"] for c in cats},
            **tot, "all_cp": cp, "all_cvm": kv}


# ------------------------------------------------------------- Shapiro 2022
def _rolling_ar_resid(x: np.ndarray, p: int = 4, window: int = 40):
    """Residual at t from OLS x_s = c + sum_j a_j x_{s-j} + e, fit on the
    `window` observations s in (t-window, t]; also returns the in-window
    residual s.e. (for the ambiguous band)."""
    n = len(x)
    X = np.column_stack([np.ones(n)] + [np.r_[np.full(j, np.nan), x[:-j]] for j in range(1, p + 1)])
    out, sig = np.full(n, np.nan), np.full(n, np.nan)
    for t in range(window - 1, n):
        y, Z = x[t - window + 1:t + 1], X[t - window + 1:t + 1]
        if not (np.isfinite(y).all() and np.isfinite(Z).all()):
            continue                                   # require a full window
        b, *_ = np.linalg.lstsq(Z, y, rcond=None)
        u = y - Z @ b
        out[t] = u[-1]
        sig[t] = np.sqrt(u @ u / (window - p - 1))
    return out, sig


def residuals(nominal, real, p=4, window=40):
    """Unexpected log price / quantity changes. Returns ep, eq, sp, sq."""
    dp = np.log(nominal / real).diff()                 # implied deflator
    dq = np.log(real).diff()                           # CVM volume
    res = {}
    for name, df in (("p", dp), ("q", dq)):
        e, s = {}, {}
        for c in df.columns:
            e[c], s[c] = _rolling_ar_resid(df[c].values, p, window)
        res["e" + name] = pd.DataFrame(e, index=df.index)
        res["s" + name] = pd.DataFrame(s, index=df.index)
    return res["ep"], res["eq"], res["sp"], res["sq"]


def classify(ep, eq, sp=None, sq=None, band: float | None = None):
    """+1 demand (same sign), -1 supply (opposite sign), 0 ambiguous, NaN n/a.
    band: if set, obs with |ep| < band*sp or |eq| < band*sq (sp, sq = in-window
    regression s.e.) are labelled ambiguous (0)."""
    lab = (np.sign(ep) * np.sign(eq)).where(ep.notna() & eq.notna())
    if band is not None:
        amb = (ep.abs() < band * sp) | (eq.abs() < band * sq)
        lab = lab.mask(amb & lab.notna(), 0.0)
    return lab


def decompose(nominal, real, labels, horizon=4):
    """Contributions (pp) to y/y (horizon=4) deflator inflation:
    c_it = w_{i,t-4} * (P_it/P_i,t-4 - 1) * 100, allocated by label at t.
    w = nominal expenditure share among included categories, one year earlier.
    Also 'supply_q4'/'demand_q4': alternative that sums the last 4 quarterly
    contributions w_{i,t-1}*dlogP_it, each allocated by its own quarter's label."""
    P = nominal / real
    infl = (P / P.shift(horizon) - 1) * 100
    w = nominal.div(nominal.sum(1), axis=0)
    c = w.shift(horizon) * infl
    cq = w.shift(1) * np.log(P).diff() * 100
    ok = labels.notna().any(axis=1)
    res = pd.DataFrame(index=nominal.index)
    for k, v in (("demand", 1), ("supply", -1), ("ambiguous", 0)):
        res[k] = c.where(labels == v).sum(1).where(ok)
        res[k + "_q4"] = cq.where(labels == v).sum(1).rolling(horizon).sum().where(ok)
        res["w_" + k] = w.shift(horizon).where(labels == v).sum(1).where(ok)
    res["unclassified"] = c.where(labels.isna()).sum(1).where(ok)
    res["total"] = c.sum(1, min_count=1)
    return res


def aggregate_deflator_yoy(total_nominal, total_real, horizon=4):
    P = total_nominal / total_real
    return (P / P.shift(horizon) - 1) * 100


# -------------------------------------------------------------------- tests
def _tests(d):
    nom, real = d["nominal"], d["real"]
    assert isinstance(nom.index, pd.PeriodIndex) and nom.index.freqstr.startswith("Q")
    assert nom.index.equals(real.index) and list(nom.columns) == list(real.columns)
    assert nom.index[0] in (pd.Period("1985Q1"), pd.Period("1997Q1")) and nom.index.is_monotonic_increasing
    assert not nom.index.duplicated().any()
    assert (nom.index[1:] - nom.index[:-1]).map(lambda x: x.n).unique().tolist() == [1]
    assert nom.notna().all().all() and real.notna().all().all(), "gaps in categories"
    assert (nom > 0).all().all() and (real > 0).all().all()
    # hierarchy: groups sum to divisions in CP (CP is additive)
    cp = d["all_cp"]
    for div in [f"{i:02d}" for i in range(1, 13)]:
        kids = [c for c in nom.columns if c.split(".")[0] == div]
        gap = (nom.loc[cp.index, kids].sum(1) - cp[div]).abs().max()
        assert gap <= 3 * len(kids), (div, gap)       # rounding only
    # divisions sum to domestic total; domestic + tourism = national
    divs = cp[[f"{i:02d}" for i in range(1, 13)]].sum(1)
    assert (divs - cp["0"]).abs().max() <= 12
    assert ((cp["0"] + cp["TOUR"]) - cp["NAT"]).abs().max() <= 2
    # spot values checked by eye against the xlsx (June 2026 release)
    if nom.index[-1] == pd.Period("2026Q1"):
        assert cp.loc["2026Q1", "NAT"] == 455277 and cp.loc["2026Q1", "0"] == 451764
        assert d["all_cvm"].loc["1997Q1", "01"] == 26855
    # AR residual recovers white noise for a known AR(1)
    rng = np.random.default_rng(0)
    e = rng.normal(size=200); x = np.zeros(200)
    for t in range(1, 200):
        x[t] = 0.5 * x[t - 1] + e[t]
    r, _ = _rolling_ar_resid(x, 4, 40)
    assert np.corrcoef(r[50:], e[50:])[0, 1] > 0.9
    # residual at t equals statsmodels-free direct OLS on the same window
    t = 120; Z = np.column_stack([np.ones(40)] + [x[t - 39 - j:t + 1 - j] for j in range(1, 5)])
    bb = np.linalg.lstsq(Z, x[t - 39:t + 1], rcond=None)[0]
    assert abs(r[t] - (x[t] - Z[-1] @ bb)) < 1e-12
    # classification signs
    ep = pd.DataFrame({"a": [1.0, -1, 1, np.nan]}); eq = pd.DataFrame({"a": [2.0, -3, -1, 1]})
    assert classify(ep, eq)["a"].tolist()[:3] == [1, 1, -1] and np.isnan(classify(ep, eq)["a"].iloc[3])
    print("all tests passed")


# --------------------------------------------------------------------- main


# ------------------------------------------------------------------ dashboard output
EXCLUDE = ("04.2", "02.3", "12.2")   # imputed rents and modelled illegal activities: not in CPI
BAND = 0.05                           # residuals within 0.05 s.e. of zero are "ambiguous" (cf. Shapiro's band)


def main() -> None:
    import json
    d = load()
    _tests(d)
    keep = [c for c in d["nominal"].columns if not c.startswith(EXCLUDE)]
    nom, real = d["nominal"][keep], d["real"][keep]
    ep, eq, sp, sq = residuals(nom, real)
    lab = classify(ep, eq, sp, sq, band=BAND)
    dec = decompose(nom, real, lab)
    dec = dec[dec["total"].notna() & dec.index.isin(lab.dropna(how="all").index)]
    out = {
        "method": "Shapiro (2022) sign classification by COICOP group: 4-lag AR residuals over a rolling 40-quarter window; "
                  "same-sign price/quantity surprises = demand, opposite = supply; |residual| < 0.05 s.e. = ambiguous. "
                  "Excludes imputed rents (04.2) and modelled illegal activities. Contributions to y/y household-spending "
                  "deflator inflation, pp, year-ago expenditure shares.",
        "source": "ONS Consumer trends (household final consumption by COICOP, CP and CVM, SA), quarterly",
        "categories": len(keep),
        "series": {str(q): {k: round(float(r[k]), 3) for k in ("demand", "supply", "ambiguous", "total")}
                   for q, r in dec.iterrows()},
    }
    res = Path(__file__).resolve().parent / "results"
    res.mkdir(exist_ok=True)
    (res / "shapiro_uk.json").write_text(json.dumps(out, indent=1))
    print(dec[["demand", "supply", "ambiguous", "total"]].tail(10).round(2).to_string())


if __name__ == "__main__":
    main()
