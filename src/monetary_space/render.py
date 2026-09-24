"""Render the static page. Phase 1: a plain, self-contained list of scores."""
from __future__ import annotations

from html import escape

import pandas as pd

from .config import BLOCK_NAMES, BLOCK_TITLES, Config
from .indicators import Block, Indicator

ARROW = {"up": "▲ up", "down": "▼ down", "neutral": "● neutral"}


def fmt(v: float, dp: int = 1) -> str:
    return f"{v:+.{dp}f}".replace("-", "−") if v else f"{0:.{dp}f}"


def num(v: float, dp: int = 1) -> str:
    return f"{v:.{dp}f}".replace("-", "−")


def period_label(p: pd.Period) -> str:
    return f"{p.year} Q{p.quarter}" if p.freqstr.startswith("Q") else p.strftime("%b %Y")


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


CSS = """
:root{--bg:#fff;--fg:#1b1b1b;--muted:#5f5f5f;--rule:#d9d9d9;--up:#b35806;--down:#2166ac;--neutral:#6b6b6b;--stale:#8a8a8a}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#ececec;--muted:#a8a8a8;--rule:#3a3a3a;--up:#f1a340;--down:#8fb8e0;--neutral:#a8a8a8;--stale:#7d7d7d}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-variant-numeric:tabular-nums}
main{max-width:1100px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;margin:0 0 4px}
h2{font-size:17px;margin:32px 0 2px}
.sub{color:var(--muted);margin:0 0 8px}
.score{font-size:22px;font-weight:600}
.up{color:var(--up)}.down{color:var(--down)}.neutral{color:var(--neutral)}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;margin-top:8px}
th,td{text-align:right;padding:6px 10px;border-bottom:1px solid var(--rule);white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal}
th{font-weight:600;color:var(--muted);font-size:13px}
td[title]{cursor:help}
td:focus{outline:2px solid var(--down);outline-offset:-2px}
.stale td{color:var(--stale)}
.flag{font-size:12px;color:var(--muted)}
.notice{border-left:3px solid var(--rule);padding:4px 12px;color:var(--muted)}
footer{margin-top:40px;padding-top:12px;border-top:1px solid var(--rule);color:var(--muted);font-size:13px}
"""


def _block_html(b: Block, saturation_share: float) -> str:
    d = b.diffusion
    cls = "up" if b.score > 0.5 else "down" if b.score < -0.5 else "neutral"
    rows = []
    for i in b.indicators:
        flags = []
        if i.stale:
            flags.append(f"stale, next release was due {i.next_due:%d %b %Y}")
        if i.failed_series:
            flags.append("fetch failed, last good value shown")
        if i.clip_share_recent > saturation_share:
            flags.append(f"z clipped in {i.clip_share_recent:.0%} of periods since 2021")
        flag = f'<div class="flag">{escape("; ".join(flags))}</div>' if flags else ""
        rows.append(
            f'<tr class="{"stale" if i.stale else ""}">'
            f"<td>{escape(i.name)}{flag}</td>"
            f"<td>{num(i.latest.x)} {escape(i.unit)}</td>"
            f"<td>{period_label(i.period)}</td>"
            f"<td>{num(i.b, 2)}</td>"
            f"<td>{num(i.sigma, 2)}</td>"
            f"<td>{i.sign:+d}</td>"
            f'<td tabindex="0" title="{escape(tooltip(i))}"><span class="{i.direction}">{fmt(i.latest.z)} {ARROW[i.direction]}</span></td>'
            "</tr>"
        )
    return f"""
<section aria-labelledby="block-{b.id}">
  <h2 id="block-{b.id}">{b.id}. {BLOCK_NAMES[b.id]}: {escape(BLOCK_TITLES[b.id])}</h2>
  <p class="sub">Block score <span class="score {cls}">{fmt(b.score)}</span>
    &nbsp;·&nbsp; {d['up']} up, {d['neutral']} neutral, {d['down']} down</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Indicator</th><th>Value</th><th>Date</th><th>Benchmark b</th><th>Scale σ</th><th>Sign s</th><th>z</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</section>"""


def page(cfg: Config, inds: list[Indicator], blocks: dict[str, Block], problems: list[str], now, failed: list[str]) -> str:
    sat = cfg.weights["history"]["saturation_note_share"]
    sections = "".join(_block_html(b, sat) for b in blocks.values())
    attributions = sorted({i.attribution for i in inds})
    notices = ""
    if problems or failed:
        items = [f"Source failed this run, last good value kept: {escape(s)}" for s in failed]
        items += [f"Not scored: {escape(p)}" for p in problems]
        notices = '<div class="notice"><p>' + "</p><p>".join(items) + "</p></div>"
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UK Monetary Policy Dashboard</title>
<style>{CSS}</style>
</head>
<body>
<main>
  <h1>UK monetary policy dashboard</h1>
  <p class="sub">Phase 1 preview: demand and domestic inflation scores. Data as of {now:%d %B %Y, %H:%M} UK time.</p>
  <p class="sub">z = s·(x − b)/σ, clipped at ±{cfg.weights['z_clip']:g}; positive means inflationary. Above +{cfg.weights['direction_threshold']:g} points up, below −{cfg.weights['direction_threshold']:g} down. Hover or focus a z-score for its calculation.</p>
  {notices}
  {sections}
  <footer>
    <p>{'<br>'.join(escape(a) for a in attributions)}</p>
    <p>Built {now:%d %B %Y %H:%M} UK time. Not investment advice.</p>
  </footer>
</main>
</body>
</html>
"""
