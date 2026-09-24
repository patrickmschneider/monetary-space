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
    ylim: tuple[float, float] | None
    source: str
    attribution: str


def prepare(cfg: Config, data: dict[str, pd.Series], as_of: pd.Timestamp) -> list[ChartData]:
    since = pd.Period(cfg.charts.get("since", "2016-01"), "M")
    out = []
    for c in cfg.charts.get("charts", []):
        sid = c["series"]
        if sid not in data:
            continue
        x = transform.apply(c.get("transform", "level"), [data[sid]])
        x = transform.to_monthly(x) if not x.index.freqstr.startswith("D") else x
        x = x[x.index >= since]
        ref = None
        if r := c.get("reference"):
            if "manual" in r:
                v, cite = manual_value(cfg, r["manual"], as_of)
                ref = (v, f"{r.get('label', r['manual'])} {num(v, 2)}")
            else:
                ref = (float(r["value"]), r.get("label", ""))
        src = cfg.series[sid]["source"]
        out.append(ChartData(
            id=c["id"], title=c["title"], subtitle=c["subtitle"], unit=c.get("unit", ""),
            decimals=c.get("decimals", 1), step=c.get("step", False), x=x, reference=ref,
            ylim=tuple(c["ylim"]) if c.get("ylim") else None,
            source=cfg.sources[src]["name"], attribution=cfg.sources[src]["attribution"],
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


def svg(c: ChartData) -> tuple[str, str]:
    """Return (svg markup, off-scale note)."""
    x = c.x.dropna()
    vals = list(x)
    lo, hi = (min(vals), max(vals))
    if c.reference:
        lo, hi = min(lo, c.reference[0]), max(hi, c.reference[0])
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
        return ML + (mid - t0).total_seconds() / span * (W - ML - MR)

    def py(v: float) -> float:
        v = max(ylo, min(yhi, v))
        return MT + (yhi - v) / (yhi - ylo) * (H - MT - MB)

    pts = [(px(p), py(v)) for p, v in x.items()]
    if c.step:
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" + "".join(
            f"H{b[0]:.1f}V{b[1]:.1f}" for a, b in zip(pts, pts[1:]))
    else:
        d = "M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts)

    grid = "".join(
        f'<line x1="{ML}" x2="{W - MR}" y1="{py(t):.1f}" y2="{py(t):.1f}" class="grid"/>'
        f'<text x="{ML - 6}" y="{py(t) + 3:.1f}" class="ytick">{tick_label(t, ticks, c.decimals)}</text>'
        for t in ticks
    )
    years = range(x.index[0].year + (x.index[0].month > 1), x.index[-1].year + 1)
    step_years = 2 if len(years) > 6 else 1
    xt = "".join(
        f'<text x="{px(pd.Period(f"{y}-01", "M")):.1f}" y="{H - 6}" class="xtick">{y}</text>'
        f'<line x1="{px(pd.Period(f"{y}-01", "M")):.1f}" x2="{px(pd.Period(f"{y}-01", "M")):.1f}" y1="{H - MB}" y2="{H - MB + 3}" class="axis"/>'
        for y in years if (y - years[0]) % step_years == 0
    )
    ref = ""
    if c.reference:
        v, label = c.reference
        cls = "zero" if v == 0 and not label else "ref"
        ref = f'<line x1="{ML}" x2="{W - MR}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="{cls}"/>'
        if label:
            ref += f'<text x="{W - MR + 4}" y="{py(v) + 3:.1f}" class="ref-label">{escape(label)}</text>'
    lx, ly = pts[-1]
    data = json.dumps({
        "x": [round(a, 1) for a, _ in pts], "y": [round(b, 1) for _, b in pts],
        "d": [p.strftime("%b %Y") for p in x.index], "v": [value_label(v, c.unit, c.decimals) for v in vals],
    }, separators=(",", ":"))
    latest = f"{value_label(vals[-1], c.unit, c.decimals)} in {x.index[-1].strftime('%B %Y')}"
    label = (f"{c.title}, {x.index[0].strftime('%B %Y')} to {x.index[-1].strftime('%B %Y')}. "
             f"Latest {latest}. Range {value_label(min(vals), c.unit, c.decimals)} to {value_label(max(vals), c.unit, c.decimals)}.")
    markup = (
        f'<svg viewBox="0 0 {W} {H}" class="line-chart" role="img" aria-label="{escape(label)}" data-points=\'{escape(data)}\'>'
        f'{grid}{ref}<line x1="{ML}" x2="{W - MR}" y1="{H - MB}" y2="{H - MB}" class="axis"/>{xt}'
        f'<path d="{d}" class="series"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.6" class="last"/>'
        f'<g class="hover" visibility="hidden"><line y1="{MT}" y2="{H - MB}" class="hover-rule"/><circle r="3.2" class="hover-dot"/></g>'
        "</svg>"
    )
    note = off_scale_note(x, *c.ylim, c.unit, c.decimals) if c.ylim else ""
    return markup, note


def panel(c: ChartData) -> str:
    markup, note = svg(c)
    x = c.x.dropna()
    latest = value_label(x.iloc[-1], c.unit, c.decimals)
    note_html = f'<p class="chart-note">{escape(note)}</p>' if note else ""
    return f"""
<figure class="chart-panel" tabindex="0" aria-describedby="tip-{c.id}">
  <figcaption class="panel-heading">
    <h3>{escape(c.title)}</h3>
    <p>{escape(c.subtitle)}</p>
  </figcaption>
  <p class="chart-latest"><strong>{escape(latest)}</strong> <span>{x.index[-1].strftime('%B %Y')}</span></p>
  <div class="chart-frame">{markup}<div class="chart-tip" id="tip-{c.id}" aria-live="polite"></div></div>
  {note_html}
  <p class="chart-source" title="{escape(c.attribution)}">Source: {escape(c.source)}</p>
</figure>"""


SCRIPT = """
(()=>{for(const fig of document.querySelectorAll('.chart-panel')){
const svg=fig.querySelector('svg'),tip=fig.querySelector('.chart-tip'),g=svg.querySelector('.hover');
const P=JSON.parse(svg.dataset.points),n=P.x.length;let i=n-1;
const show=k=>{i=Math.max(0,Math.min(n-1,k));g.setAttribute('visibility','visible');
g.querySelector('line').setAttribute('x1',P.x[i]);g.querySelector('line').setAttribute('x2',P.x[i]);
const c=g.querySelector('circle');c.setAttribute('cx',P.x[i]);c.setAttribute('cy',P.y[i]);
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
      <p class="takeaway">Headline series for orientation. They are not scored; the blocks below are. Hover a chart, or focus it and use the arrow keys, to read values.</p>
    </div>
  </div>
  <div class="chart-grid">{''.join(panel(c) for c in charts)}</div>
</section>"""


CSS = """
.chart-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px 32px}
.chart-panel{margin:0;min-width:0;padding-top:14px;border-top:1px solid var(--border)}
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
.line-chart .ref-label{font-size:9.5px;fill:var(--muted);text-anchor:start}
.line-chart .hover-rule{stroke:var(--muted);stroke-width:1}
.line-chart .hover-dot{fill:var(--bg);stroke:var(--ink);stroke-width:1.6}
.chart-tip{position:absolute;top:-6px;transform:translateX(-50%);background:var(--ink);color:var(--bg);font-size:11px;padding:3px 7px;border-radius:4px;white-space:nowrap;pointer-events:none}
.chart-note{font-size:11px;color:var(--muted);line-height:1.5;margin:6px 0 0}
.chart-source{font-size:10px;color:var(--muted);margin:6px 0 0}
@media(max-width:1000px){.chart-grid{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.chart-grid{grid-template-columns:1fr;gap:22px}}
"""
