"""Policy path chart: Bank Rate for the past two years, the market path implied by the OIS
forward curve, the nominal neutral zone (the r* zone plus year-ahead expected inflation, as in
the Stance block) and MPC dates as ticks. Greyscale: stance is never coloured.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape

import pandas as pd

from . import transform
from .charts import fig_note
from .config import Config

W, H = 1080, 330
ML, MR, MT, MB = 34, 150, 14, 28


@dataclass
class PathData:
    bank_rate: pd.Series          # daily, past window
    ois_path: pd.Series           # indexed by date (today + maturity)
    ois_date: pd.Timestamp
    band: tuple[float, float]     # nominal neutral band, %
    mpc_dates: list[pd.Timestamp]
    start: pd.Timestamp
    end: pd.Timestamp


def prepare(cfg: Config, data: dict, estimates: dict, stance, as_of: pd.Timestamp) -> PathData | None:
    if stance is None or "IUDBEDR" not in data:
        return None
    start = as_of - pd.DateOffset(years=2)
    br = data["IUDBEDR"]
    br = br[(br.index.to_timestamp() >= start)]
    fwd = {float(k.split(":")[1]): v for k, v in data.items() if k.startswith("OIS_FWD:")}
    path, priced = pd.Series(dtype=float), as_of
    if fwd:
        day = min(v.index[-1] for v in fwd.values())
        priced = day.to_timestamp()
        path = pd.Series({priced: float(data["IUDBEDR"].dropna().iloc[-1])} | {
            priced + pd.Timedelta(days=round(m * 365.25)): float(v[day]) for m, v in sorted(fwd.items())})
    mpc = pd.to_datetime(cfg.manual["mpc_dates"]["date"])
    end = as_of + pd.DateOffset(years=3)
    return PathData(
        bank_rate=br, ois_path=path, ois_date=priced,
        band=(stance.band[0] + stance.expected_inflation, stance.band[1] + stance.expected_inflation),
        mpc_dates=[d for d in mpc if start <= d <= end], start=start, end=end,
    )


def svg(p: PathData) -> str:
    span = (p.end - p.start).total_seconds()

    def px(t: pd.Timestamp) -> float:
        return ML + (t - p.start).total_seconds() / span * (W - ML - MR)

    vals = list(p.bank_rate) + list(p.ois_path) + list(p.band)
    lo, hi = min(0.0, min(vals)), max(vals) + 0.5
    lo, hi = float(int(lo)), float(int(hi) + 1)

    def py(v: float) -> float:
        return MT + (hi - v) / (hi - lo) * (H - MT - MB)

    out = []
    for t in range(int(lo), int(hi) + 1):
        out.append(f'<line x1="{ML}" x2="{W - MR}" y1="{py(t):.1f}" y2="{py(t):.1f}" class="grid"/>'
                   f'<text x="{ML - 6}" y="{py(t) + 3:.1f}" class="ytick">{t}</text>')
    b0, b1 = p.band
    out.append(f'<rect x="{ML}" y="{py(b1):.1f}" width="{W - ML - MR}" height="{py(b0) - py(b1):.1f}" class="band"/>')
    today = p.ois_date
    out.append(f'<line x1="{px(today):.1f}" x2="{px(today):.1f}" y1="{MT}" y2="{H - MB}" class="today"/>'
               f'<text x="{px(today) + 4:.1f}" y="{MT + 9}" class="note">{today:%-d %b %Y}</text>')
    for y in range(p.start.year + 1, p.end.year + 1):
        x = px(pd.Timestamp(f"{y}-01-01"))
        out.append(f'<text x="{x:.1f}" y="{H - 8}" class="xtick">{y}</text>')
    for d in p.mpc_dates:
        out.append(f'<line x1="{px(d):.1f}" x2="{px(d):.1f}" y1="{H - MB}" y2="{H - MB + 5}" class="mpc"/>')
    br = p.bank_rate
    pts = [(px(t.to_timestamp()), py(v)) for t, v in br.items()]
    if pts:
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" + "".join(f"H{b[0]:.1f}V{b[1]:.1f}" for a, b in zip(pts, pts[1:]))
        d += f"H{px(today):.1f}"
        out.append(f'<path d="{d}" class="bank-rate"/>')
    if len(p.ois_path):
        op = "M" + "L".join(f"{px(t):.1f},{py(v):.1f}" for t, v in p.ois_path.items())
        out.append(f'<path d="{op}" class="ois"/>')
    # direct labels at the right edge
    labels = []
    if len(p.ois_path):
        labels.append((py(p.ois_path.iloc[-1]), f"Market path {p.ois_path.iloc[-1]:.2f}%"))
    if pts:
        labels.append((pts[-1][1], f"Bank Rate {br.iloc[-1]:.2f}%"))
    labels.append(((py(b0) + py(b1)) / 2, f"Neutral {b0:.1f}–{b1:.1f}%"))
    labels.sort()
    last = -99.0
    for y, text in labels:                      # nudge apart so labels never overlap
        y = max(y, last + 12)
        last = y
        out.append(f'<text x="{W - MR + 6}" y="{y + 3:.1f}" class="label">{escape(text)}</text>')
    desc = (f"Bank Rate {br.iloc[-1]:.2f}%; market path reaches {p.ois_path.max():.2f}% "
            f"and ends at {p.ois_path.iloc[-1]:.2f}% in three years; nominal neutral band {b0:.1f}–{b1:.1f}%."
            if len(p.ois_path) and len(br) else "Policy path")
    return (f'<svg viewBox="0 0 {W} {H}" class="path-chart" role="img" aria-label="{escape(desc)}">'
            + "".join(out) + "</svg>")


def section(p: PathData | None, number: int, stance) -> str:
    if p is None:
        return ""
    return f"""
<section class="story-section" id="policy-path" aria-labelledby="h-path">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">POLICY PATH</p>
      <h2 id="h-path">Where markets expect Bank Rate to go</h2>
      <p class="takeaway">Bank Rate over the past two years and the path priced in sterling overnight index swaps (OIS) on {p.ois_date:%-d %B %Y}, against the nominal neutral zone: the r* zone plus year-ahead expected inflation ({stance.expected_inflation:.1f}%), as in the stance above. Ticks mark MPC decisions.</p>
    </div>
  </div>
  <figure class="path-frame">{svg(p)}</figure>
  {fig_note("OIS forwards are SONIA rates, which run a few basis points below Bank Rate, and include term premia. The neutral zone uses expected inflation over the next year; further ahead it is only indicative.", "Bank of England; Monetary Space estimates of r*")}
</section>"""


CSS = """
.path-frame{margin:0}
.path-chart{width:100%;height:auto;display:block;font-family:inherit}
.path-chart .grid{stroke:var(--rule-soft)}
.path-chart .ytick,.path-chart .xtick{font-size:10px;fill:var(--muted)}
.path-chart .ytick{text-anchor:end}.path-chart .xtick{text-anchor:middle}
.path-chart .band{fill:var(--band);opacity:.8}
.path-chart .today{stroke:var(--border);stroke-dasharray:2 3}
.path-chart .note{font-size:10px;fill:var(--muted)}
.path-chart .mpc{stroke:var(--muted)}
.path-chart .bank-rate{fill:none;stroke:var(--ink);stroke-width:2}
.path-chart .ois{fill:none;stroke:var(--ink);stroke-width:1.4}
.path-chart .label{font-size:10.5px;fill:var(--fg)}
"""
