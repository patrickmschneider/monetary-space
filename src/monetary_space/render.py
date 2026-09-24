"""Render the static page, in the editorial style of the Fiscal Space dashboard.

Colour carries one meaning (spec Section 6): copper = inflationary, blue =
disinflationary, grey = neutral. The teal ink is chrome only (brand, links, labels).
"""
from __future__ import annotations

from html import escape

import pandas as pd

from .config import BLOCK_NAMES, BLOCK_TITLES, Config
from .indicators import Block, Indicator
from .score import DOWN, UP

ARROW = {"up": "▲", "down": "▼", "neutral": "●"}
WORD = {"up": "inflationary", "down": "disinflationary", "neutral": "neutral"}
SCALE = 3.0  # blocks and indicators share a fixed −3..+3 scale


def fmt(v: float, dp: int = 1) -> str:
    """Signed number with a true minus sign; zero unsigned."""
    s = f"{v:+.{dp}f}"
    if float(s) == 0:
        return f"{0:.{dp}f}"
    return s.replace("-", "−")


def num(v: float, dp: int = 1) -> str:
    return f"{v:.{dp}f}".replace("-", "−")


def period_label(p: pd.Period) -> str:
    return f"{p.year} Q{p.quarter}" if p.freqstr.startswith("Q") else p.strftime("%b %Y")


def direction_of(score: float, threshold: float) -> str:
    return UP if score > threshold else DOWN if score < -threshold else "neutral"


def tooltip(i: Indicator) -> str:
    z = i.latest
    lines = [
        f"{i.name}, {period_label(i.period)}",
        f"x = {num(z.x, 2)} {i.unit}",
        f"b = {num(z.b, 2)} ({i.b_label})",
        f"σ = {num(z.sigma, 2)} ({i.sigma_label})",
        f"s = {z.sign:+d}",
        f"z = s·(x − b)/σ = {num(z.raw, 2)}" + (f", clipped to {num(z.z, 1)}" if z.clipped else ""),
        f"Smoothing: {i.smoothing}",
        f"Source: {i.source}",
    ]
    if i.note:
        lines.append(f"Note: {i.note}")
    return "\n".join(lines)


def summary(cfg: Config, inds: list[Indicator], blocks: dict[str, Block], problems: list[str], now) -> dict:
    return {
        "built_at": now.isoformat(timespec="seconds"),
        "blocks": {k: {"score": round(b.score, 3), "diffusion": b.diffusion} for k, b in blocks.items()},
        "indicators": [
            {
                "id": i.id, "block": i.block, "period": str(i.period), "x": i.latest.x, "b": i.b,
                "sigma": i.sigma, "sign": i.sign, "z_raw": i.latest.raw, "z": i.latest.z,
                "direction": i.direction, "stale": i.stale, "next_due": str(i.next_due.date()),
                "clip_share": round(i.clip_share, 3), "clip_share_since_2021": round(i.clip_share_recent, 3),
                "failed_series": i.failed_series,
            }
            for i in inds
        ],
        "problems": problems,
    }


# ------------------------------------------------------------------ small graphics
def zbar(z: float, direction: str, label: str) -> str:
    """Diverging bullet bar on −3..+3 with the ±0.5 neutral band and a zero line."""
    half = min(abs(z), SCALE) / SCALE * 50
    left = 50 - half if z < 0 else 50
    return (
        f'<span class="zbar" role="img" aria-label="{escape(label)}">'
        f'<span class="zbar-band"></span><span class="zbar-fill {direction}" style="left:{left:.2f}%;width:{half:.2f}%"></span>'
        f'<span class="zbar-zero"></span></span>'
    )


def sparkline(hist: pd.Series, months: int, label: str) -> str:
    """Block score over the last `months`, on the fixed −3..+3 scale, zero line shown."""
    h = hist.dropna().iloc[-months:]
    if len(h) < 2:
        return ""
    w, ht = 160, 36
    xs = [k * w / (len(h) - 1) for k in range(len(h))]
    ys = [ht / 2 - max(-SCALE, min(SCALE, v)) / SCALE * (ht / 2 - 2) for v in h]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    first, last = period_label(h.index[0]), period_label(h.index[-1])
    return (
        f'<figure class="spark"><svg viewBox="0 0 {w} {ht}" role="img" aria-label="{escape(label)}" preserveAspectRatio="none">'
        f'<line x1="0" y1="{ht / 2}" x2="{w}" y2="{ht / 2}" class="spark-zero"/>'
        f'<polyline points="{pts}" class="spark-line"/>'
        f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.2" class="spark-dot"/></svg>'
        f"<figcaption>{first} – {last}</figcaption></figure>"
    )


def diffusion_dots(d: dict[str, int]) -> str:
    dots = "".join(f'<i class="dot {k}" aria-hidden="true"></i>' * d[k] for k in (UP, "neutral", DOWN))
    return f'<span class="dots">{dots}</span> {d[UP]} up · {d["neutral"]} neutral · {d[DOWN]} down'


# ------------------------------------------------------------------------- page
def in_sentence(name: str) -> str:
    """Lower-case a name's first word for mid-sentence use, unless it is an acronym."""
    first, _, rest = name.partition(" ")
    return name if first.isupper() else f"{first.lower()} {rest}".strip()


def lead_sentence(blocks: dict[str, Block], threshold: float) -> str:
    parts = []
    phrases = {
        "A": {UP: "Demand is running hot", DOWN: "Demand is running cool", "neutral": "Demand is close to normal"},
        "B": {UP: "domestic inflation is running above a 2%-consistent pace",
              DOWN: "domestic inflation is running below a 2%-consistent pace",
              "neutral": "domestic inflation is close to a 2%-consistent pace"},
    }
    for k in ("A", "B"):
        if k not in blocks:
            continue
        b = blocks[k]
        d = direction_of(b.score, threshold)
        movers = sorted((i for i in b.indicators if i.direction == d and d != "neutral"),
                        key=lambda i: -abs(i.latest.z))[:2]
        why = f", led by {' and '.join(in_sentence(i.name) for i in movers)}" if movers else ""
        parts.append(f"{phrases[k][d]} (<strong class=\"{d}\">{fmt(b.score)}</strong>){why}")
    if not parts:
        return "Scores are not yet available."
    text = "; ".join(parts)
    return text[0].upper() + text[1:] + "."


def headline_strip(blocks: dict[str, Block], cfg: Config) -> str:
    thr = cfg.weights["direction_threshold"]
    months = cfg.weights["history"]["sparkline_months"]
    cols = []
    for k in ("A", "B", "C", "D"):
        title = f"{k}. {BLOCK_NAMES[k]}"
        if k not in blocks:
            cols.append(
                f'<div class="metric pending"><h2>{title}</h2><p class="question">{escape(BLOCK_TITLES[k])}</p>'
                f'<p class="metric-value muted-value">—</p><p class="metric-detail">Arrives in Phase 2.</p></div>'
            )
            continue
        b = blocks[k]
        d = direction_of(b.score, thr)
        cols.append(
            f'<div class="metric"><h2><a href="#block-{k}">{title}</a></h2><p class="question">{escape(BLOCK_TITLES[k])}</p>'
            f'<p class="metric-value {d}">{fmt(b.score)} <span class="metric-word">{ARROW[d]} {WORD[d]}</span></p>'
            f'{zbar(b.score, d, f"Block score {fmt(b.score)} on a −3 to +3 scale")}'
            f'<p class="metric-detail">{diffusion_dots(b.diffusion)}</p>'
            f'{sparkline(b.history, months, f"{BLOCK_NAMES[k]} score, last {months} months")}</div>'
        )
    return f'<section class="headline-strip" aria-label="Block scores">{"".join(cols)}</section>'


def _flags(i: Indicator, saturation_share: float) -> str:
    flags = []
    if i.stale:
        flags.append(f"Stale: the next release was due {i.next_due:%-d %b %Y}")
    if i.failed_series:
        flags.append("Source failed this run; last good value shown")
    if i.clip_share_recent > saturation_share:
        flags.append(f"z clipped in {i.clip_share_recent:.0%} of periods since 2021")
    return "".join(f'<span class="flag">{escape(f)}</span>' for f in flags)


def block_section(b: Block, cfg: Config, number: int) -> str:
    thr = cfg.weights["direction_threshold"]
    sat = cfg.weights["history"]["saturation_note_share"]
    d = direction_of(b.score, thr)
    rows = []
    for i in b.indicators:
        rows.append(
            f'<tr class="{"stale" if i.stale else ""}">'
            f'<th scope="row">{escape(i.name)}{_flags(i, sat)}</th>'
            f'<td class="num">{num(i.latest.x)}<span class="unit"> {escape(i.unit)}</span></td>'
            f"<td>{period_label(i.period)}</td>"
            f'<td class="num">{num(i.b, 2)}</td>'
            f'<td class="num">{num(i.sigma, 2)}</td>'
            f'<td class="num">{"+1" if i.sign > 0 else "−1"}</td>'
            f'<td class="zcell" tabindex="0" title="{escape(tooltip(i))}">'
            f'<span class="znum {i.direction}">{fmt(i.latest.z)} {ARROW[i.direction]}</span>'
            f'{zbar(i.latest.z, i.direction, f"z {fmt(i.latest.z)}, {WORD[i.direction]}")}</td>'
            "</tr>"
        )
    sources = sorted({i.attribution for i in b.indicators})
    preview = " · ".join(sorted({i.source for i in b.indicators}))
    return f"""
<section class="story-section" id="block-{b.id}" aria-labelledby="h-{b.id}">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">{b.id}. {BLOCK_NAMES[b.id].upper()}</p>
      <h2 id="h-{b.id}">{escape(BLOCK_TITLES[b.id])}</h2>
      <p class="takeaway">Block score <strong class="{d}">{fmt(b.score)} {ARROW[d]} {WORD[d]}</strong>, the equal-weighted mean of {len(b.indicators)} indicators. {diffusion_dots(b.diffusion)}.</p>
    </div>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th scope="col">Indicator</th><th scope="col" class="num">Latest x</th><th scope="col">Date</th>
      <th scope="col" class="num">Benchmark b</th><th scope="col" class="num">Scale σ</th><th scope="col" class="num">Sign s</th>
      <th scope="col">z, −3 to +3</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <details class="source-line">
    <summary><span class="source-preview">Source: {escape(preview)}</span><svg class="source-chevron" width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></summary>
    <div class="source-details">{'<br>'.join(escape(s) for s in sources)}</div>
  </details>
</section>"""


def page(cfg: Config, inds: list[Indicator], blocks: dict[str, Block], problems: list[str], now, failed: list[str]) -> str:
    thr = cfg.weights["direction_threshold"]
    sections = "".join(block_section(b, cfg, n) for n, b in enumerate(blocks.values(), start=1))
    attributions = sorted({i.attribution for i in inds})
    notice = ""
    if problems or failed:
        items = [f"Source failed this run, last good value kept: {escape(s)}." for s in failed]
        items += [f"Not scored: {escape(p)}." for p in problems]
        notice = '<div class="notice" role="status">' + " ".join(items) + "</div>"
    latest = max((i.period.end_time for i in inds), default=None)
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#153f46">
<meta name="description" content="Is UK monetary policy tight enough for the inflation pressure? Official data, transparent scores.">
<title>Monetary Space</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="./"><span><strong>Monetary Space</strong><small>A GUIDE TO UK MONETARY POLICY</small></span></a>
    <p class="release-stamp"><span class="status-dot" aria-hidden="true"></span>Data as of <strong>{now:%-d %B %Y}</strong></p>
  </div>
</header>
<main id="main" class="page-shell editorial">
  <section class="briefing-lead">
    <p class="eyebrow">UK MONETARY POLICY · {now:%B %Y}</p>
    <h1 class="lead-sentence">{lead_sentence(blocks, thr)}</h1>
    <p class="basis-note">Scores are z-scores on a fixed −3 to +3 scale: z = s·(x − b)/σ, clipped at ±{cfg.weights['z_clip']:g}. Positive always means inflationary; beyond ±{thr:g} an indicator points up or down. Hover or focus any z for its calculation.</p>
  </section>
  {notice}
  {headline_strip(blocks, cfg)}
  <p class="legend"><span><i class="swatch up"></i>Inflationary (z above +{thr:g})</span><span><i class="swatch neutral"></i>Neutral</span><span><i class="swatch down"></i>Disinflationary (z below −{thr:g})</span><span><i class="swatch band"></i>Neutral band ±{thr:g}</span></p>
  {sections}
  <footer>
    <div><strong>Monetary Space</strong><p>Phase 1 preview: blocks A and B. The global and stance blocks, the verdict and the policy path follow.<br>Latest observation {latest:%B %Y}. Built {now:%-d %B %Y, %H:%M} UK time.</p></div>
    <div><p>{'<br>'.join(escape(a) for a in attributions)}</p><p>Not investment advice.</p></div>
  </footer>
</main>
</body>
</html>
"""


CSS = """
:root{--bg:#faf9f5;--fg:#253b3e;--ink:#153f46;--accent:#175d65;--muted:#58686a;--border:#d9dedb;--rule-soft:#edf0e9;--head:#f2f5ef;
--up:#a8561c;--down:#2c6aa0;--neutral:#646d6c;--track:#e8ebe7;--band:#dde2dc;--notice-bg:#fff3df;--notice-bd:#e4cd9f;--notice-fg:#765123;
color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121a1b;--fg:#dfe6e3;--ink:#e8efec;--accent:#7cc0c3;--muted:#9aa8a6;--border:#2d3a3b;--rule-soft:#223031;--head:#1a2526;
--up:#e8995a;--down:#7fb2e5;--neutral:#8f9a99;--track:#253233;--band:#2f3d3e;--notice-bg:#2b2416;--notice-bd:#5a4a2a;--notice-fg:#e6c690;color-scheme:dark}}
:root[data-theme=dark]{--bg:#121a1b;--fg:#dfe6e3;--ink:#e8efec;--accent:#7cc0c3;--muted:#9aa8a6;--border:#2d3a3b;--rule-soft:#223031;--head:#1a2526;
--up:#e8995a;--down:#7fb2e5;--neutral:#8f9a99;--track:#253233;--band:#2f3d3e;--notice-bg:#2b2416;--notice-bd:#5a4a2a;--notice-fg:#e6c690;color-scheme:dark}
*{box-sizing:border-box}
html{scroll-padding-top:24px}
body{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-synthesis:none;font-variant-numeric:tabular-nums}
a{color:inherit;text-underline-offset:3px}
a:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid #bc843d;outline-offset:3px}
h1,h2,h3,p{margin-top:0}
.skip-link{position:absolute;top:-100px;left:20px;background:var(--bg);padding:14px;z-index:10}
.skip-link:focus{top:10px}
.site-header{border-bottom:1px solid var(--border)}
.header-inner{max-width:1280px;margin:auto;padding:0 36px;height:104px;display:flex;align-items:center;justify-content:space-between;gap:24px}
.brand{text-decoration:none;color:var(--ink);font-family:Georgia,'Times New Roman',serif;font-size:26px;letter-spacing:-.9px;white-space:nowrap}
.brand strong{font-weight:600}
.brand small{display:block;font-family:system-ui,sans-serif;font-size:8px;letter-spacing:1.5px;font-weight:500;margin-top:9px;color:var(--muted)}
.release-stamp{font-size:11px;color:var(--muted);border:1px solid var(--border);border-radius:30px;padding:10px 14px;display:flex;align-items:center;gap:7px;white-space:nowrap;margin:0}
.release-stamp strong{color:var(--fg);font-weight:500}
.status-dot{width:6px;height:6px;background:#4b9270;border-radius:50%}
.page-shell{max-width:1216px;margin:auto;padding:40px 36px 0}
.editorial{max-width:1152px}
.eyebrow{font-size:10px;font-weight:700;letter-spacing:1.65px;color:var(--accent);margin-bottom:12px}
.briefing-lead{padding:0 0 8px}
.lead-sentence{font-size:clamp(18px,2vw,22px);font-weight:400;line-height:1.6;color:var(--fg);max-width:960px;margin:0 0 14px;letter-spacing:0}
.lead-sentence strong{font-weight:600}
.basis-note{font-size:12px;color:var(--muted);line-height:1.6;max-width:900px;margin:0 0 8px}
.up{color:var(--up)}.down{color:var(--down)}.neutral{color:var(--neutral)}
.notice{padding:12px 16px;background:var(--notice-bg);border:1px solid var(--notice-bd);color:var(--notice-fg);border-radius:8px;margin:14px 0;font-size:13px;line-height:1.6}
.headline-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:2px solid var(--ink);border-bottom:1px solid var(--border);margin-top:24px}
.metric{padding:20px 20px 18px;border-right:1px solid var(--border);min-width:0}
.metric:first-child{padding-left:0}
.metric:last-child{border-right:0}
.metric h2{font-size:11px;font-weight:600;color:var(--muted);letter-spacing:.2px;margin:0 0 4px}
.metric h2 a{text-decoration:none}
.metric h2 a:hover{text-decoration:underline;color:var(--accent)}
.question{font-size:12px;line-height:1.45;color:var(--fg);min-height:36px;margin:0 0 12px}
.metric-value{font-size:31px;font-weight:600;letter-spacing:-1px;line-height:1;margin:0 0 12px;white-space:nowrap}
.metric-word{font-size:12px;font-weight:600;letter-spacing:0;vertical-align:middle}
.muted-value{color:var(--border)}
.metric-detail{font-size:11px;color:var(--muted);line-height:1.6;margin:10px 0 0}
.pending .question{color:var(--muted)}
.zbar{position:relative;display:block;height:8px;background:var(--track);min-width:90px}
.zbar-band{position:absolute;top:0;bottom:0;left:41.667%;width:16.667%;background:var(--band)}
.zbar-fill{position:absolute;top:0;bottom:0}
.zbar-fill.up{background:var(--up)}.zbar-fill.down{background:var(--down)}.zbar-fill.neutral{background:var(--neutral)}
.zbar-zero{position:absolute;left:50%;top:-3px;bottom:-3px;border-left:1px solid var(--muted)}
.dots{display:inline-flex;gap:3px;vertical-align:middle;margin-right:4px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot.up{background:var(--up)}.dot.down{background:var(--down)}.dot.neutral{background:var(--neutral)}
.spark{margin:12px 0 0}
.spark svg{width:100%;height:36px;display:block;overflow:visible}
.spark-zero{stroke:var(--border);stroke-width:1}
.spark-line{fill:none;stroke:var(--ink);stroke-width:1.5;vector-effect:non-scaling-stroke}
.spark-dot{fill:var(--ink)}
.spark figcaption{font-size:10px;color:var(--muted);margin-top:4px}
.legend{display:flex;gap:10px 22px;flex-wrap:wrap;font-size:11px;color:var(--muted);margin:14px 0 4px}
.legend span{display:flex;align-items:center;gap:7px}
.swatch{width:12px;height:12px;display:inline-block}
.swatch.up{background:var(--up)}.swatch.down{background:var(--down)}.swatch.neutral{background:var(--neutral)}.swatch.band{background:var(--band)}
.story-section{padding:40px 0 30px;border-bottom:1px solid var(--border);scroll-margin-top:20px}
.story-heading{display:flex;gap:20px;align-items:flex-start;margin-bottom:22px}
.section-number{font-size:11px;font-weight:600;color:var(--muted);padding-top:2px}
.story-heading h2{font-size:24px;font-weight:650;letter-spacing:-.025em;line-height:1.25;color:var(--ink);margin:0 0 10px}
.takeaway{font-size:15px;line-height:1.65;color:var(--muted);margin:0;max-width:840px}
.takeaway strong{font-weight:600}
.table-wrap{max-width:100%;overflow-x:auto;border:1px solid var(--border);border-radius:7px;margin:0 0 14px}
table{border-collapse:collapse;width:100%;font-size:12px;text-align:left}
th,td{padding:12px 14px;border-bottom:1px solid var(--rule-soft);line-height:1.5;vertical-align:middle}
thead th{background:var(--head);color:var(--muted);font-size:11px;font-weight:600;white-space:nowrap}
tbody th{font-weight:500;color:var(--fg);min-width:190px}
tr:last-child th,tr:last-child td{border-bottom:0}
.num{text-align:right;white-space:nowrap}
.unit{color:var(--muted)}
.zcell{min-width:170px;cursor:help}
.znum{display:block;font-weight:600;margin-bottom:5px;white-space:nowrap}
.flag{display:block;font-size:10px;color:var(--muted);margin-top:3px}
.stale td,.stale th{color:var(--muted)}
.source-line{font-size:10px;color:var(--muted);line-height:1.7;border-top:1px solid var(--border);padding-top:8px;margin-top:8px}
.source-line>summary{display:flex;align-items:center;gap:10px;min-height:28px;cursor:pointer;list-style:none}
.source-line>summary::-webkit-details-marker{display:none}
.source-preview{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.source-chevron{flex:none;transition:transform .15s}
.source-line[open]>summary .source-chevron{transform:rotate(180deg)}
.source-details{padding:6px 0 2px}
footer{display:flex;justify-content:space-between;gap:30px;margin-top:44px;padding:28px 0 35px;border-top:1px solid var(--border);font-size:11px;color:var(--muted);line-height:1.7}
footer strong{font-family:Georgia,'Times New Roman',serif;color:var(--ink);font-size:16px;font-weight:600}
footer p{margin:8px 0 0}
footer>div:last-child{text-align:right;max-width:520px}
@media(max-width:1000px){.header-inner{padding:0 26px}.page-shell{padding:30px 26px 0}
.headline-strip{grid-template-columns:1fr 1fr}.metric{border-bottom:1px solid var(--border)}.metric:nth-child(2n){border-right:0}.metric:nth-child(odd){padding-left:0}}
@media(max-width:700px){.header-inner{height:auto;padding:20px 18px;flex-wrap:wrap;gap:12px}.brand{font-size:25px}
.page-shell{padding:24px 18px 0}.lead-sentence{font-size:18px}
.headline-strip{grid-template-columns:1fr}.metric{padding:18px 0;border-right:0}
.story-heading{gap:12px}.story-heading h2{font-size:21px}.takeaway{font-size:14px}
footer{display:block;font-size:10px}footer>div:last-child{text-align:left;margin-top:20px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""
