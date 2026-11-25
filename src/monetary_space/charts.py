"""Context charts (not scored): simple, self-contained SVG line charts.

Data preparation is separate from drawing so the numbers can be tested. Every
chart carries its points as JSON for the hover/keyboard readout; no JS library.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from html import escape

import pandas as pd

from . import transform
from .config import Config, manual_value


@dataclass
class ChartData:
    id: str
    title: str
    subtitle: str
    unit: str
    decimals: int
    step: bool
    x: pd.Series                       # monthly, from `since`
    reference: tuple[float, str] | None
    ref_path: tuple[pd.Series, pd.Series, pd.Series, str] | None   # (centre, low, high, label), monthly
    ylim: tuple[float, float] | None
    source: str
    attribution: str
    secondary: tuple[pd.Series, str] | None = None   # a second, dashed line on the same axis
    forecast_from: pd.Period | None = None           # first forecast period, shaded
    forecast_label: str = "Forecast"


def plabel(p: pd.Period, long: bool = False) -> str:
    """Point label: 'Oct 2026', or a fiscal year '2026-27'."""
    if p.freqstr == "Y-MAR":
        return f"{p.year - 1}-{p.year % 100:02d}"
    return p.strftime("%B %Y" if long else "%b %Y")


def _monthly_path(q: pd.Series, since: pd.Period, until: pd.Period) -> pd.Series:
    m = transform.carry_forward(q, until)
    return m[m.index >= since]


def prepare(cfg: Config, data: dict[str, pd.Series], as_of: pd.Timestamp,
            estimates: dict | None = None) -> list[ChartData]:
    out = []
    for c in cfg.charts.get("charts", []):
        sid = c["series"]
        if sid not in data:
            continue
        x = transform.apply(c.get("transform", "level"), [data[sid]])
        annual = x.index.freqstr[0] in "YA"
        if not annual and not x.index.freqstr.startswith("D"):
            x = transform.to_monthly(x)
        start = pd.Timestamp(c.get("since", cfg.charts.get("since", "2016-01")))
        since = pd.Period(cfg.charts.get("since", "2016-01"), "M")
        x = x[x.index.start_time >= start]
        secondary = None
        if (sec := c.get("secondary")) and sec["series"] in data:
            s2 = data[sec["series"]]
            secondary = (s2[s2.index.start_time >= start], sec.get("label", ""))
        forecast_from = None
        if c.get("forecast"):
            ahead = x.index[x.index.end_time > as_of]
            forecast_from = ahead[0] if len(ahead) else None
        ref, ref_path = None, None
        if (r := c.get("reference")) and r.get("nairu"):
            est = (estimates or {}).get("nairu")
            if est is not None:
                z = cfg.nairu.get("band_z", 1.645)
                end = x.index[-1]
                path = [_monthly_path(s, since, end) for s in (est.u_star, est.u_star - z * est.se, est.u_star + z * est.se)]
                ref_path = (*path, f"{r.get('label', 'u*')} {num(path[0].iloc[-1], 1)}")
        elif r:
            if "manual" in r:
                v, cite = manual_value(cfg, r["manual"], as_of)
                ref = (v, f"{r.get('label', r['manual'])} {num(v, 2)}")
            else:
                ref = (float(r["value"]), r.get("label", ""))
        src = cfg.series[sid.split(":")[0]]["source"]
        out.append(ChartData(
            id=c["id"], title=c["title"], subtitle=c["subtitle"], unit=c.get("unit", ""),
            decimals=c.get("decimals", 1), step=c.get("step", False), x=x, reference=ref, ref_path=ref_path,
            ylim=tuple(c["ylim"]) if c.get("ylim") else None,
            source=cfg.sources[src]["name"], attribution=cfg.sources[src]["attribution"],
            secondary=secondary, forecast_from=forecast_from, forecast_label=c.get("forecast_label", "Forecast"),
        ))
    return out


# ------------------------------------------------------------------------ drawing
W, H = 360, 190
ML, MR, MT, MB = 30, 46, 10, 22


def num(v: float, dp: int = 1) -> str:
    return f"{v:.{dp}f}".replace("-", "−")


def value_label(v: float, unit: str, dp: int) -> str:
    return f"${v:.{dp}f}".replace("-", "−") if unit == "$" else f"{num(v, dp)}{unit}"


def tick_label(t: float, ticks: list[float], decimals: int) -> str:
    """Axis labels: as few decimals as the tick step needs, never more than the series uses."""
    dp = 0 if all(float(v).is_integer() for v in ticks) else min(decimals, 2 if any(round(v * 10) != v * 10 for v in ticks) else 1)
    return num(t, dp)


def nice_ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    span = hi - lo or 1.0
    raw = span / (n - 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start = math.floor(lo / step) * step
    ticks, t = [], start
    while t <= hi + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    return ticks


def off_scale_note(x: pd.Series, lo: float, hi: float, unit: str, dp: int) -> str:
    out = x[(x < lo) | (x > hi)]
    if out.empty:
        return ""
    first, last = out.index[0].strftime("%b %Y"), out.index[-1].strftime("%b %Y")
    edge = lambda v: value_label(v, unit, 0 if float(v).is_integer() else dp)
    return (f"Axis cut off at {edge(lo)} to {edge(hi)}; between {first} and {last} "
            f"values reached {value_label(out.min(), unit, dp)} and {value_label(out.max(), unit, dp)}.")


def svg(c: ChartData, width: int = W) -> tuple[str, str]:
    """Return (svg markup, off-scale note)."""
    x = c.x.dropna()
    vals = list(x)
    lo, hi = (min(vals), max(vals))
    if c.reference:
        lo, hi = min(lo, c.reference[0]), max(hi, c.reference[0])
    if c.ref_path:
        lo, hi = min(lo, c.ref_path[1].min()), max(hi, c.ref_path[2].max())
    if c.secondary is not None:
        lo, hi = min(lo, c.secondary[0].min()), max(hi, c.secondary[0].max())
    if c.ylim:
        lo, hi = c.ylim
    if hi - lo < 1e-9:  # flat series: give the axis some height
        pad = max(abs(lo) * 0.05, 0.5)
        lo, hi = lo - pad, hi + pad
    ticks = nice_ticks(lo, hi)
    ylo, yhi = min(ticks[0], lo), max(ticks[-1], hi)
    t0, t1 = x.index[0].start_time, x.index[-1].end_time
    span = (t1 - t0).total_seconds()

    def px(p: pd.Period) -> float:
        mid = p.start_time + (p.end_time - p.start_time) / 2
        return ML + (mid - t0).total_seconds() / span * (width - ML - MR)

    def py(v: float) -> float:
        return MT + (yhi - v) / (yhi - ylo) * (H - MT - MB)

    pts = [(px(p), py(v)) for p, v in x.items()]
    if c.step:
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" + "".join(
            f"H{b[0]:.1f}V{b[1]:.1f}" for a, b in zip(pts, pts[1:]))
    else:
        d = "M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts)

    grid = "".join(
        f'<line x1="{ML}" x2="{width - MR}" y1="{py(t):.1f}" y2="{py(t):.1f}" class="grid"/>'
        f'<text x="{ML - 6}" y="{py(t) + 3:.1f}" class="ytick">{tick_label(t, ticks, c.decimals)}</text>'
        for t in ticks
    )
    years = range(x.index[0].start_time.year + (x.index[0].start_time.month > 1), x.index[-1].end_time.year + 1)
    step_years = next(s for s in (1, 2, 5, 10) if len(years) / s <= 8)
    xt = "".join(
        f'<text x="{px(pd.Period(f"{y}-01", "M")):.1f}" y="{H - 6}" class="xtick">{y}</text>'
        f'<line x1="{px(pd.Period(f"{y}-01", "M")):.1f}" x2="{px(pd.Period(f"{y}-01", "M")):.1f}" y1="{H - MB}" y2="{H - MB + 3}" class="axis"/>'
        for y in years if (y - years[0]) % step_years == 0
    )
    ref = ""
    if c.reference:
        v, label = c.reference
        cls = "zero" if v == 0 and not label else "ref"
        ref = f'<line x1="{ML}" x2="{width - MR}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="{cls}"/>'
        if label:
            ref += f'<text x="{width - MR + 4}" y="{py(v) + 3:.1f}" class="ref-label">{escape(label)}</text>'
    if c.ref_path:
        centre, low, high, label = c.ref_path
        upper = [(px(p), py(v)) for p, v in high.items()]
        lower = [(px(p), py(v)) for p, v in low.items()][::-1]
        band = " ".join(f"{a:.1f},{b:.1f}" for a, b in upper + lower)
        mid = "M" + "L".join(f"{px(p):.1f},{py(v):.1f}" for p, v in centre.items())
        ref += (f'<polygon points="{band}" class="ref-band"/><path d="{mid}" class="ref-path"/>'
                f'<text x="{width - MR + 4}" y="{py(centre.iloc[-1]) + 3:.1f}" class="ref-label">{escape(label)}</text>')
    second = ""
    if c.secondary is not None:
        s2, label = c.secondary
        s2 = s2[(s2.index >= x.index[0]) & (s2.index <= x.index[-1])].dropna()
        if len(s2):
            path = "M" + "L".join(f"{px(p):.1f},{py(v):.1f}" for p, v in s2.items())
            second = f'<path d="{path}" class="ref-path secondary"/>'
            if label:
                ref += f'<text x="{width - MR + 4}" y="{py(s2.iloc[-1]) + 3:.1f}" class="ref-label">{escape(label)}</text>'
    shade = ""
    if c.forecast_from is not None:
        fx = px(c.forecast_from) - (px(c.forecast_from) - px(c.forecast_from - 1)) / 2
        shade = (f'<rect x="{fx:.1f}" y="{MT}" width="{width - MR - fx:.1f}" height="{H - MT - MB}" class="forecast-band"/>'
                 f'<text x="{fx + 3:.1f}" y="{MT + 9}" class="forecast-label">{escape(c.forecast_label)}</text>')
    lx, ly = pts[-1]
    data = json.dumps({
        "x": [round(a, 1) for a, _ in pts], "y": [round(b, 1) if MT <= b <= H - MB else None for _, b in pts],
        "d": [plabel(p) + (" (forecast)" if c.forecast_from is not None and p >= c.forecast_from else "") for p in x.index],
        "v": [value_label(v, c.unit, c.decimals)
              + (f"; {c.secondary[1].lower()} {value_label(c.secondary[0][p], c.unit, c.decimals)}"
                 if c.secondary is not None and p in c.secondary[0].index else "") for p, v in x.items()],
    }, separators=(",", ":"))
    latest = f"{value_label(vals[-1], c.unit, c.decimals)} in {plabel(x.index[-1], True)}"
    label = (f"{c.title}, {plabel(x.index[0], True)} to {plabel(x.index[-1], True)}. "
             f"Latest {latest}. Range {value_label(min(vals), c.unit, c.decimals)} to {value_label(max(vals), c.unit, c.decimals)}.")
    markup = (
        f'<svg viewBox="0 0 {width} {H}" class="line-chart" role="img" aria-label="{escape(label)}" data-points=\'{escape(data)}\'>'
        f'{shade}{grid}{ref}<line x1="{ML}" x2="{width - MR}" y1="{H - MB}" y2="{H - MB}" class="axis"/>{xt}'
        f'<clipPath id="clip-{c.id}"><rect x="{ML}" y="{MT}" width="{width - ML - MR}" height="{H - MT - MB}"/></clipPath>'
        f'<g clip-path="url(#clip-{c.id})">{second}<path d="{d}" class="series"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.6" class="last"/></g>'
        f'<g class="hover" visibility="hidden"><line y1="{MT}" y2="{H - MB}" class="hover-rule"/><circle r="3.2" class="hover-dot"/></g>'
        "</svg>"
    )
    note = off_scale_note(x, *c.ylim, c.unit, c.decimals) if c.ylim else ""
    return markup, note


def fig_note(text: str = "", source: str = "") -> str:
    """A figure note: the first sentence shows; the rest, and the source, sit in a dropdown."""
    import re
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(‘'])", text.strip(), maxsplit=1) if text.strip() else []
    first = parts[0] if parts else (f"Source: {source}" if source else "")
    rest = " ".join(parts[1:])
    extra = " ".join(x for x in (rest, f"Source: {source}." if source and parts else "") if x)
    if not first:
        return ""
    if not extra:
        return f'<p class="fig-note-line">{escape(first)}</p>'
    return (f'<details class="fig-note"><summary><span>{escape(first)}</span></summary>'
            f'<p>{escape(extra)}</p></details>')


def panel(c: ChartData) -> str:
    markup, note = svg(c)
    x = c.x.dropna()
    if c.forecast_from is not None and (x.index >= c.forecast_from).any():
        x = x[x.index <= c.forecast_from]   # headline figure: the current year, not the last forecast year
    latest = value_label(x.iloc[-1], c.unit, c.decimals)
    return f"""
<figure class="chart-panel" tabindex="0" aria-describedby="tip-{c.id}">
  <figcaption class="panel-heading">
    <h3>{escape(c.title)}</h3>
    <p>{escape(c.subtitle)}</p>
  </figcaption>
  <p class="chart-latest"><strong>{escape(latest)}</strong> <span>{plabel(x.index[-1], True)}{" (OBR forecast)" if c.forecast_from is not None and x.index[-1] >= c.forecast_from else ""}</span></p>
  <div class="chart-frame">{markup}<div class="chart-tip" id="tip-{c.id}" aria-live="polite"></div></div>
  <div class="fig-foot" title="{escape(c.attribution)}">{fig_note(note, c.source)}</div>
</figure>"""


SCRIPT = """
(()=>{for(const fig of document.querySelectorAll('.chart-panel')){
const svg=fig.querySelector('svg[data-points]'),tip=fig.querySelector('.chart-tip');if(!svg||!tip)continue;const g=svg.querySelector('.hover');
const P=JSON.parse(svg.dataset.points),n=P.x.length;let i=n-1;
const show=k=>{i=Math.max(0,Math.min(n-1,k));g.setAttribute('visibility','visible');
g.querySelector('line').setAttribute('x1',P.x[i]);g.querySelector('line').setAttribute('x2',P.x[i]);
const c=g.querySelector('circle');c.setAttribute('cx',P.x[i]);c.setAttribute('cy',P.y[i]??0);c.setAttribute('visibility',P.y[i]===null?'hidden':'inherit');
tip.textContent=P.d[i]+': '+P.v[i];tip.style.left=(P.x[i]/svg.viewBox.baseVal.width*100)+'%';tip.hidden=false;};
const hide=()=>{g.setAttribute('visibility','hidden');tip.hidden=true;};
svg.addEventListener('pointermove',e=>{const pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;
const x=pt.matrixTransform(svg.getScreenCTM().inverse()).x;let b=0,bd=1e9;
for(let k=0;k<n;k++){const d=Math.abs(P.x[k]-x);if(d<bd){bd=d;b=k;}}show(b);});
svg.addEventListener('pointerleave',hide);fig.addEventListener('blur',hide);fig.addEventListener('focus',()=>show(n-1));
fig.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){show(i-1);e.preventDefault();}
else if(e.key==='ArrowRight'){show(i+1);e.preventDefault();}
else if(e.key==='Home'){show(0);e.preventDefault();}else if(e.key==='End'){show(n-1);e.preventDefault();}});
tip.hidden=true;}})();
"""


def section(charts: list[ChartData], number: int) -> str:
    if not charts:
        return ""
    return f"""
<section class="story-section" id="context" aria-labelledby="h-context">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">CONTEXT</p>
      <h2 id="h-context">The economy at a glance</h2>
      <p class="takeaway">Headline series for orientation; they are not scored. Hover a chart, or focus it and use the arrow keys, to read values.</p>
    </div>
  </div>
  <div class="chart-grid">{''.join(panel(c) for c in charts)}</div>
</section>"""


CSS = """
.chart-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:32px}
.chart-panel{margin:0;min-width:0;padding-top:14px;border-top:1px solid var(--border)}
.chart-grid>.chart-panel{display:grid;grid-template-rows:subgrid;grid-row:span 4;row-gap:0;margin-bottom:28px}
.fig-note{font-size:11px;color:var(--muted);line-height:1.5;margin:6px 0 0}
.fig-note>summary{cursor:pointer;list-style:none;display:flex;gap:6px;align-items:baseline}
.fig-note>summary::-webkit-details-marker{display:none}
.fig-note>summary::after{content:"more";flex:none;font-size:10px;color:var(--accent);text-decoration:underline;text-underline-offset:2px}
.fig-note[open]>summary::after{content:"less"}
.fig-note>p{margin:6px 0 0}
.fig-note-line{font-size:11px;color:var(--muted);line-height:1.5;margin:6px 0 0}
.chart-panel:focus-visible{outline:3px solid #bc843d;outline-offset:6px}
.chart-panel .panel-heading h3{font-size:17px;font-weight:650;letter-spacing:-.02em;color:var(--ink);margin:0 0 4px}
.chart-panel .panel-heading p{font-size:12px;color:var(--muted);line-height:1.5;margin:0;min-height:36px}
.chart-latest{margin:6px 0 4px;font-size:12px;color:var(--muted)}
.chart-latest strong{font-size:22px;font-weight:600;letter-spacing:-.5px;color:var(--fg);margin-right:4px}
.chart-frame{position:relative}
.line-chart{width:100%;height:auto;display:block;overflow:visible;font-family:inherit}
.line-chart .grid{stroke:var(--rule-soft);stroke-width:1}
.line-chart .axis{stroke:var(--border);stroke-width:1}
.line-chart .ytick{font-size:9.5px;fill:var(--muted);text-anchor:end}
.line-chart .xtick{font-size:9.5px;fill:var(--muted);text-anchor:middle}
.line-chart .series{fill:none;stroke:var(--ink);stroke-width:1.6;stroke-linejoin:round}
.line-chart .last{fill:var(--ink)}
.line-chart .ref{stroke:var(--muted);stroke-width:1;stroke-dasharray:4 3}
.line-chart .zero{stroke:var(--muted);stroke-width:1}
.line-chart .ref-path{fill:none;stroke:var(--muted);stroke-width:1.2;stroke-dasharray:4 3}
.line-chart .ref-band{fill:var(--band);opacity:.7}
.line-chart .secondary{stroke:var(--ink);opacity:.75}
.line-chart .forecast-band{fill:var(--rule-soft);opacity:.8}
.line-chart .forecast-label{font-size:9px;fill:var(--muted)}
.line-chart .ref-label{font-size:9.5px;fill:var(--muted);text-anchor:start}
.line-chart .hover-rule{stroke:var(--muted);stroke-width:1}
.line-chart .hover-dot{fill:var(--bg);stroke:var(--ink);stroke-width:1.6}
.chart-tip{position:absolute;top:-6px;transform:translateX(-50%);background:var(--ink);color:var(--bg);font-size:11px;padding:3px 7px;border-radius:4px;white-space:nowrap;pointer-events:none}
.chart-note{font-size:11px;color:var(--muted);line-height:1.5;margin:6px 0 0}
.chart-source{font-size:10px;color:var(--muted);margin:6px 0 0}
@media(max-width:1000px){.chart-grid{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.chart-grid{grid-template-columns:1fr;gap:22px}}
"""
