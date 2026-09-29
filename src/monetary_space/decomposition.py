"""'What's driving inflation': three model-based decompositions, shown side by side.

1. Shapiro-style split of household-spending inflation into demand- and supply-driven
   categories (analysis/shapiro_uk.py).
2. UK Bernanke–Blanchard model: contributions of energy, food and labour-market tightness
   (analysis/bb_uk.py).
3. Sign-identified VAR historical decomposition of CPI inflation (analysis/svar_uk.py).

All three are estimated after data releases, not on every build, and are labelled as
model-based illustrations. Greyscale: colour on this page means inflationary or not.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape

import pandas as pd

W, H = 360, 190
ML, MR, MT, MB = 24, 6, 8, 20
FILLS = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)", "var(--c5)", "var(--c6)"]


@dataclass
class Stacked:
    id: str
    title: str
    subtitle: str
    parts: pd.DataFrame        # quarterly index (str 'YYYYQn') × component
    labels: dict[str, str]
    line: pd.Series | None     # total inflation, drawn as a line
    line_label: str
    note: str


def _period(q: str) -> pd.Period:
    return pd.Period(q, "Q")


def shapiro(res: dict, since: str) -> Stacked | None:
    if not res:
        return None
    df = pd.DataFrame(res["series"]).T
    df.index = [_period(q) for q in df.index]
    df = df[df.index >= _period(since)]
    return Stacked(
        id="shapiro", title="Demand- or supply-driven? Category by category",
        subtitle="Household-spending inflation, % y/y: categories whose price and quantity surprises move together "
                 "count as demand-driven, opposite ways as supply-driven",
        parts=df[["demand", "supply", "ambiguous"]],
        labels={"demand": "Demand-driven", "supply": "Supply-driven", "ambiguous": "Ambiguous"},
        line=df["total"], line_label="Total",
        note=f"Shapiro (2022) method on {res.get('categories', '')} ONS spending categories; excludes imputed rents. "
             "Sign-based splits are only set-identified: read the direction of change more than the levels.")


def bernanke_blanchard(res: dict, since: str) -> Stacked | None:
    c = (res or {}).get("contributions_4q_avg")
    if not c:
        return None
    df = pd.DataFrame(c).T
    df.index = [_period(q) for q in df.index]
    df = df[df.index >= _period(since)]
    parts = df[["energy", "food", "labour_market"]].copy()
    gap = df["actual"] - 2.0
    parts["other"] = gap - parts.sum(axis=1)
    return Stacked(
        id="bb", title="Cost-push or labour market? A wage–price model",
        subtitle="CPI inflation above 2%, q/q annualised, 4-quarter average, pp: contributions relative to a 2019Q4 "
                 "labour market and no relative energy or food price growth",
        parts=parts,
        labels={"energy": "Energy prices", "food": "Food prices", "labour_market": "Labour-market tightness",
                "other": "Pay, expectations and other"},
        line=gap, line_label="CPI minus 2%",
        note="UK Bernanke–Blanchard (2023) model: wage, price and expectations equations, 2001–2026. "
             "'Pay, expectations and other' covers wage and expectations shocks and everything the model leaves out.")


def svar(res: dict, since: str) -> Stacked | None:
    if not res:
        return None
    rows = {q: {k: (v["median"] if isinstance(v, dict) else v) for k, v in r.items()} for q, r in res["series"].items()}
    df = pd.DataFrame(rows).T
    df.index = [_period(q) for q in df.index]
    df = df.rolling(4).mean()
    df = df[df.index >= _period(since)]
    parts = df[["energy", "demand", "supply", "monetary", "pandemic"]].copy()
    gap = df["actual"] - df["baseline"]
    parts["other"] = gap - parts.sum(axis=1)
    base = df["baseline"].iloc[-1]
    return Stacked(
        id="svar", title="Which shocks? A sign-identified VAR",
        subtitle=f"CPI inflation above the model's baseline ({base:.1f}%), q/q annualised, 4-quarter average, pp: "
                 "median contributions of identified shocks",
        parts=parts,
        labels={"energy": "Energy", "demand": "Demand", "supply": "Domestic supply", "monetary": "Monetary policy",
                "pandemic": "Pandemic swings", "other": "Other"},
        line=gap, line_label="CPI minus baseline",
        note=f"Bayesian VAR (oil, GDP, CPI, Bank Rate, sterling; 1993–), sign restrictions on impact, "
             f"{res.get('accepted_draws', '')} accepted draws. Model-based illustration, not a forecast.")


def svg(s: Stacked) -> str:
    parts = s.parts.fillna(0.0)
    n = len(parts)
    pos = parts.clip(lower=0).sum(axis=1)
    neg = parts.clip(upper=0).sum(axis=1)
    top = max(pos.max(), (s.line.max() if s.line is not None else 0), 1)
    bot = min(neg.min(), (s.line.min() if s.line is not None else 0), 0)
    top, bot = float(int(top) + 1), float(int(bot) - (1 if bot < 0 else 0))
    bw = (W - ML - MR) / n

    def py(v):
        return MT + (top - v) / (top - bot) * (H - MT - MB)

    out = []
    step = 2 if top - bot <= 8 else 4
    for t in range(int(bot), int(top) + 1):
        if t % step == 0:
            out.append(f'<line x1="{ML}" x2="{W - MR}" y1="{py(t):.1f}" y2="{py(t):.1f}" class="grid"/>'
                       f'<text x="{ML - 5}" y="{py(t) + 3:.1f}" class="ytick">{t}</text>')
    out.append(f'<line x1="{ML}" x2="{W - MR}" y1="{py(0):.1f}" y2="{py(0):.1f}" class="zero"/>')
    for i, (q, row) in enumerate(parts.iterrows()):
        x = ML + i * bw + bw * 0.12
        up = down = 0.0
        for j, (k, v) in enumerate(row.items()):
            if v >= 0:
                y0, y1 = py(up + v), py(up)
                up += v
            else:
                y0, y1 = py(down), py(down + v)
                down += v
            out.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw * 0.76:.1f}" height="{max(y1 - y0, 0):.1f}" '
                       f'fill="{FILLS[j % len(FILLS)]}"><title>{q}: {escape(s.labels[k])} {v:+.1f}pp</title></rect>')
        if q.quarter == 1 and q.year % 2 == 0 and i < n - 3:
            out.append(f'<text x="{x + bw * 0.38:.1f}" y="{H - 8}" class="xtick">{q.year}</text>')
    if s.line is not None:
        pts = " ".join(f"{ML + i * bw + bw / 2:.1f},{py(v):.1f}" for i, v in enumerate(s.line.fillna(0)))
        out.append(f'<polyline points="{pts}" class="total"/>')
    label = f"{s.title}. Latest quarter {parts.index[-1]}: " + ", ".join(
        f"{s.labels[k]} {v:+.1f}pp" for k, v in parts.iloc[-1].items())
    return (f'<svg viewBox="0 0 {W} {H}" class="stack-chart" role="img" aria-label="{escape(label)}">'
            + "".join(out) + "</svg>")


def panel(s: Stacked) -> str:
    legend = "".join(f'<span><i style="background:{FILLS[j % len(FILLS)]}"></i>{escape(s.labels[k])}</span>'
                     for j, k in enumerate(s.parts.columns))
    legend += f'<span><i class="line-key"></i>{escape(s.line_label)}</span>' if s.line is not None else ""
    last = s.parts.iloc[-1]
    return f"""
<figure class="chart-panel stack-panel">
  <figcaption class="panel-heading"><h3>{escape(s.title)}</h3><p>{escape(s.subtitle)}</p></figcaption>
  <p class="stack-legend">{legend}</p>
  {svg(s)}
  <p class="chart-note">Latest ({s.parts.index[-1]}): {", ".join(f"{escape(s.labels[k].lower())} {v:+.1f}pp" for k, v in last.items())}. {escape(s.note)}</p>
</figure>"""


def section(analysis: dict, number: int, since: str = "2016Q1") -> str:
    charts = [c for c in (shapiro(analysis.get("shapiro_uk"), since),
                          bernanke_blanchard(analysis.get("bb_uk"), "2020Q4"),
                          svar(analysis.get("svar_uk"), since)) if c is not None]
    if not charts:
        return ""
    return f"""
<section class="story-section" id="drivers" aria-labelledby="h-drivers">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">WHAT'S DRIVING INFLATION</p>
      <h2 id="h-drivers">Three ways to split inflation into its sources</h2>
      <p class="takeaway">Each method separates demand from supply and cost-push differently, and each is uncertain. Where they agree, the reading is more robust. They are re-estimated after data releases and are not scored.</p>
    </div>
  </div>
  <div class="stack-grid">{''.join(panel(c) for c in charts)}</div>
</section>"""


CSS = """
:root{--c1:#153f46;--c2:#4f767b;--c3:#8fa9ab;--c4:#c3d0cf;--c5:#a39e93;--c6:#e3e1da}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--c1:#dfe9e7;--c2:#9fbcbf;--c3:#6d8a8d;--c4:#40585b;--c5:#8a857b;--c6:#2e3a3b}}
:root[data-theme=dark]{--c1:#dfe9e7;--c2:#9fbcbf;--c3:#6d8a8d;--c4:#40585b;--c5:#8a857b;--c6:#2e3a3b}
.stack-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px 32px}
.stack-panel{border-top:1px solid var(--border);padding-top:14px}
.stack-chart{width:100%;height:auto;display:block;font-family:inherit}
.stack-chart .grid{stroke:var(--rule-soft)}.stack-chart .zero{stroke:var(--muted)}
.stack-chart .ytick,.stack-chart .xtick{font-size:10px;fill:var(--muted)}.stack-chart .ytick{text-anchor:end}.stack-chart .xtick{text-anchor:middle}
.stack-chart .total{fill:none;stroke:var(--fg);stroke-width:1.6}
.stack-legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:11px;color:var(--muted);margin:6px 0}
.stack-legend span{display:flex;align-items:center;gap:6px}
.stack-legend i{width:11px;height:11px;display:inline-block}
.stack-legend i.line-key{height:2px;background:var(--fg)}
@media(max-width:1000px){.stack-grid{grid-template-columns:1fr}}
"""
