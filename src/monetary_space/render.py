"""Render the static page, in the editorial style of the Fiscal Space dashboard.

Colour carries one meaning (spec Section 6): copper = inflationary, blue =
disinflationary, grey = neutral. The teal ink is chrome only (brand, links, labels).
"""
from __future__ import annotations

from html import escape

import pandas as pd

from . import charts, decomposition, policy_path
from .config import BLOCK_EXPLAIN, BLOCK_NAMES, BLOCK_TITLES, Config
from .indicators import Block, Indicator
from .score import DOWN, EASE, HAWKISH, UP

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


def summary(cfg: Config, inds: list[Indicator], blocks: dict[str, Block], problems: list[str], now,
            stance=None, verdict=None) -> dict:
    return {
        "built_at": now.isoformat(timespec="seconds"),
        "verdict": None if verdict is None else {
            "verdict": verdict.verdict, "driver": verdict.driver, "pressure": round(verdict.pressure, 3),
            "pressure_class": verdict.pressure_class, "stance_class": verdict.stance_class,
            "contributions": {k: round(v, 3) for k, v in verdict.contributions.items()},
            "method": verdict.method, "weights": {k: round(v, 3) for k, v in verdict.weights.items()},
            "cost_push_multiplier": round(verdict.multiplier, 3),
            "alternative": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in verdict.alternative.items()
                            if k in ("method", "pressure", "class", "verdict", "driver")}},
        "stance": None if stance is None else {
            "policy_rate": stance.rate, "policy_rate_name": stance.rate_name, "policy_rate_date": str(stance.rate_date.date()),
            "nominal_neutral": round(stance.nominal_neutral, 3),
            "expected_inflation": stance.expected_inflation, "expectation_source": stance.expectation_source,
            "real_rate": round(stance.real_rate, 3), "r_star": round(stance.r_star, 3),
            "r_star_se": round(stance.r_star_se, 3), "r_star_quarter": str(stance.r_star_quarter),
            "band": [round(b, 3) for b in stance.band], "gap": round(stance.gap, 3), "class": stance.cls},
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


def sparkline(hist: pd.Series, months: int, label: str, scale: float = SCALE) -> str:
    """Score over the last `months`, on a fixed ±scale, zero line shown."""
    h = hist.dropna().iloc[-months:]
    if len(h) < 2:
        return ""
    w, ht = 160, 36
    xs = [k * w / (len(h) - 1) for k in range(len(h))]
    ys = [ht / 2 - max(-scale, min(scale, v)) / scale * (ht / 2 - 2) for v in h]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    first, last = period_label(h.index[0]), period_label(h.index[-1])
    return (
        f'<figure class="spark"><svg viewBox="0 0 {w} {ht}" role="img" aria-label="{escape(label)}" preserveAspectRatio="none">'
        f'<line x1="0" y1="{ht / 2}" x2="{w}" y2="{ht / 2}" class="spark-zero"/>'
        f'<polyline points="{pts}" class="spark-line"/>'
        f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.2" class="spark-dot"/></svg>'
        f"<figcaption>{first} – {last}</figcaption></figure>"
    )


BLOCK_ROLE = {"E": "PHILLIPS CURVE: EXPECTED INFLATION", "D": "PHILLIPS CURVE: SLACK, DEMAND SIDE",
              "S": "PHILLIPS CURVE: SLACK, SUPPLY SIDE", "C": "PHILLIPS CURVE: COST-PUSH"}
STANCE_ANSWER = {"tight": "Restraining", "loose": "Stimulating", "neutral": "Neither: close to neutral"}
STANCE_SCALE = 4.0   # pp, fixed −4..+4 (spec Section 6)
STANCE_WORD = {"tight": "Tight", "loose": "Loose", "neutral": "Neutral"}
VERDICT_CLASS = {HAWKISH: "up", EASE: "down"}


def stance_bar(gap: float, half: float, label: str) -> str:
    """Greyscale: the r* band shaded around zero, a marker at the gap, clipped at ±4pp."""
    pos = lambda v: 50 + max(-STANCE_SCALE, min(STANCE_SCALE, v)) / STANCE_SCALE * 50
    clipped = abs(gap) > STANCE_SCALE
    return (
        f'<span class="sbar" role="img" aria-label="{escape(label)}">'
        f'<span class="sbar-band" style="left:{pos(-half):.2f}%;width:{pos(half) - pos(-half):.2f}%"></span>'
        f'<span class="zbar-zero"></span>'
        f'<span class="sbar-mark{" clipped" if clipped else ""}" style="left:{pos(gap):.2f}%"></span></span>'
        f'<span class="sbar-ends" aria-hidden="true"><span>← Loose</span><span>Tight →</span></span>'
    )


def term(label: str, explain: str, href: str | None = None) -> str:
    """A label with a plain-language explanation shown on hover or keyboard focus."""
    if not explain:
        return f'<a href="{href}">{escape(label)}</a>' if href else escape(label)
    tag = "a" if href else "span"
    attrs = f' href="{href}"' if href else ' tabindex="0"'
    return f'<{tag} class="term"{attrs} data-explain="{escape(explain)}">{escape(label)}</{tag}>'


def diffusion_dots(d: dict[str, int]) -> str:
    dots = "".join(f'<i class="dot {k}" aria-hidden="true"></i>' * d[k] for k in (UP, "neutral", DOWN))
    return f'<span class="dots">{dots}</span> {d[UP]} up · {d["neutral"]} neutral · {d[DOWN]} down'


# ------------------------------------------------------------------------- page
def in_sentence(name: str) -> str:
    """Lower-case a name's first word for mid-sentence use, unless it is an acronym."""
    first, _, rest = name.partition(" ")
    return name if first.isupper() else f"{first.lower()} {rest}".strip()


def lead_sentence(blocks: dict[str, Block], threshold: float, stance=None, verdict=None) -> str:
    """Plain-language reading of the four Phillips-curve terms and the stance."""
    phrases = {
        "E": {UP: "inflation expectations are above 2%-consistent levels", DOWN: "inflation expectations are below 2%-consistent levels",
              "neutral": "inflation expectations are close to 2%-consistent levels"},
        "D": {UP: "demand is running ahead of capacity", DOWN: "demand is running below capacity",
              "neutral": "demand is close to capacity"},
        "S": {UP: "supply capacity is weakening", DOWN: "supply capacity is strengthening", "neutral": "supply capacity is growing normally"},
        "C": {UP: "external costs are pushing prices up", DOWN: "external costs are pulling prices down",
              "neutral": "external costs are broadly neutral"},
    }
    parts = []
    for k in ("E", "D", "S", "C"):
        if k not in blocks:
            continue
        b = blocks[k]
        d = direction_of(b.score, threshold)
        movers = sorted((i for i in b.indicators if i.direction == d and d != "neutral"),
                        key=lambda i: -abs(i.latest.z))[:2]
        why = f", led by {' and '.join(i.phrase or in_sentence(i.name) for i in movers)}" if movers else ""
        parts.append(f"{phrases[k][d]} (<strong class=\"{d}\">{fmt(b.score)}</strong>){why}")
    if not parts:
        return "Scores are not yet available."
    text = "; ".join(parts)
    text = text[0].upper() + text[1:] + "."
    if stance is not None:
        s = {"tight": "tight", "loose": "loose", "neutral": "close to neutral"}[stance.cls]
        text += (f" Policy is {s}: a real {stance.rate_name} of {num(stance.real_rate)}% against an estimated "
                 f"neutral rate of {num(stance.r_star, 2)}%.")
    return text


def verdict_strip(cfg: Config, blocks: dict[str, Block], stance, verdict, data: dict, now) -> str:
    if verdict is None or stance is None:
        return ""
    thr = cfg.weights["pressure"]["threshold"]
    vcls = VERDICT_CLASS.get(verdict.verdict, "neutral")
    pcls = direction_of(verdict.pressure, thr)
    half = (stance.band[1] - stance.band[0]) / 2
    drv = verdict.driver
    facts = []
    if "D7G7" in data:
        cpi = data["D7G7"].dropna()
        facts.append(f"CPI inflation <strong>{num(cpi.iloc[-1])}%</strong> in {cpi.index[-1].strftime('%B')} (target 2%)")
    if "IUDBEDR" in data:
        facts.append(f"Bank Rate <strong>{data['IUDBEDR'].dropna().iloc[-1]:.2f}%</strong>")
    mpc = cfg.manual["mpc_dates"].copy()
    mpc["date"] = pd.to_datetime(mpc["date"])
    past = mpc[(mpc["date"] <= now.tz_localize(None)) & mpc["vote"].notna()]
    future = mpc[mpc["date"] > now.tz_localize(None)]
    if not past.empty:
        last = past.iloc[-1]
        facts.append(f"Last MPC {last['date']:%-d %b}: {escape(str(last['vote']).split(':')[0])}")
    if not future.empty:
        facts.append(f"Next MPC <strong>{future.iloc[0]['date']:%-d %B}</strong>")
    return f"""
<section class="verdict" aria-label="Verdict">
  <div class="verdict-main">
    <p class="verdict-label">Verdict</p>
    <p class="verdict-word {vcls}">{escape(verdict.verdict)}</p>
    <p class="verdict-driver">driven by <a href="#block-{drv}">{BLOCK_NAMES[drv].lower()}</a></p>
  </div>
  <div class="dial">
    <h2>Inflation pressure <span class="{pcls}">{fmt(verdict.pressure)} {ARROW[pcls]} {WORD[pcls]}</span></h2>
    <div class="dial-bar">{zbar(verdict.pressure, pcls, f"Pressure {fmt(verdict.pressure)} on a −3 to +3 scale")}<span class="sbar-ends" aria-hidden="true"><span>← Disinflationary</span><span>Inflationary →</span></span></div>

  </div>
  <div class="dial">
    <h2>Policy stance <span class="stance-word">{fmt(stance.gap)}pp · {STANCE_WORD[stance.cls]}</span></h2>
    <div class="dial-bar">{stance_bar(stance.gap, half, f"Real-rate gap {fmt(stance.gap)} percentage points, {stance.cls}")}</div>

  </div>
  <p class="verdict-facts">{" · ".join(facts)}</p>
</section>"""


def pressure_note(cfg: Config, verdict) -> str:
    """How the pressure score is built: weights, the alternative weighting and the cost-push multiplier."""
    if verdict is None:
        return ""
    contrib = ", ".join(f"{BLOCK_NAMES[k].lower()} {fmt(v, 2)}" for k, v in verdict.contributions.items())
    alt = verdict.alternative
    text = (f"Inflation pressure is {fmt(verdict.pressure, 2)}: {contrib}, using {verdict.method} weights "
            f"({', '.join(f'{BLOCK_NAMES[k].lower()} {w:.2f}' for k, w in verdict.weights.items())}). ")
    if alt:
        text += f"With {alt['method']} weights it is {fmt(alt['pressure'], 2)} and the verdict {alt['verdict']}. "
    text += (f"The cost-push weight is multiplied by {verdict.multiplier:.2f}, because second-round effects are about "
             f"{verdict.multiplier_ratio:.1f}× larger when CPI inflation is above "
             f"{cfg.weights['pressure']['cost_push_state']['cpi_threshold']:g}%.")
    return f'<div class="pressure-note">{charts.fig_note(text)}</div>'


def headline_strip(blocks: dict[str, Block], cfg: Config, stance=None) -> str:
    thr = cfg.weights["direction_threshold"]
    months = cfg.weights["history"]["sparkline_months"]
    cols = []
    for k in ("E", "D", "S", "C"):
        title = BLOCK_NAMES[k]
        if k == "P" and stance is not None:
            half = (stance.band[1] - stance.band[0]) / 2
            cols.append(
                f'<div class="metric"><h2><a href="#block-P">{title}</a></h2><p class="question">{escape(BLOCK_TITLES[k])}</p>'
                f'<p class="metric-value">{fmt(stance.gap)}<span class="metric-unit">pp</span> <span class="metric-word">{STANCE_WORD[stance.cls]}</span></p>'
                f'{stance_bar(stance.gap, half, f"Real-rate gap {fmt(stance.gap)}pp")}'
                f'<p class="metric-detail">{escape(stance.rate_name)} {num(stance.rate, 2)}% − expected inflation {num(stance.expected_inflation)}% − r* {num(stance.r_star, 2)}%</p>'
                f'{sparkline(stance.history, months, f"Real-rate gap, last {months} months", STANCE_SCALE)}</div>'
            )
            continue
        if k not in blocks:
            cols.append(
                f'<div class="metric pending"><h2>{title}</h2><p class="question">{escape(BLOCK_TITLES[k])}</p>'
                f'<p class="metric-value muted-value">—</p><span class="zbar-slot"></span><p class="metric-detail">Not available this run.</p><div class="spark-slot"></div></div>'
            )
            continue
        b = blocks[k]
        d = direction_of(b.score, thr)
        cols.append(
            f'<div class="metric"><h2>{term(title, BLOCK_EXPLAIN.get(k, ""), href=f"#block-{k}")}</h2><p class="question">{escape(BLOCK_TITLES[k])}</p>'
            f'<p class="metric-value {d}">{fmt(b.score)} <span class="metric-word">{ARROW[d]} {WORD[d]}</span></p>'
            f'{zbar(b.score, d, f"Block score {fmt(b.score)} on a −3 to +3 scale")}'
            f'<p class="metric-detail">{diffusion_dots(b.diffusion)}</p>'
            f'<div class="spark-slot">{sparkline(b.history, months, f"{BLOCK_NAMES[k]} score, last {months} months")}</div></div>'
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
            f'<th scope="row">{term(i.name, i.explain)}{_flags(i, sat)}</th>'
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
      <p class="eyebrow">{BLOCK_NAMES[b.id].upper()} · {BLOCK_ROLE[b.id]}</p>
      <h2 id="h-{b.id}">{escape(BLOCK_TITLES[b.id])}</h2>
      <p class="takeaway">Block score <strong class="{d}">{fmt(b.score)} {ARROW[d]} {WORD[d]}</strong>, the equal-weighted mean of {len(b.indicators)} indicators. {diffusion_dots(b.diffusion)}.</p>
    </div>
  </div>
  <div class="table-wrap"><table class="block-table">
    <colgroup><col style="width:28%"><col style="width:11%"><col style="width:10%"><col style="width:11%"><col style="width:9%"><col style="width:7%"><col style="width:24%"></colgroup>
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


def stance_rows(stance) -> str:
    rows = [
        (stance.rate_name, f"{num(stance.rate, 2)}%", f"{stance.rate_date:%-d %b %Y}", "Bank of England"),
        ("− Expected inflation", f"{num(stance.expected_inflation)}%", "", stance.expectation_source),
        ("= Real rate", f"{num(stance.real_rate, 2)}%", "", ""),
        ("r*, suite headline", f"{num(stance.r_star, 2)}%", "", "Weighted suite of estimators, rounded to 0.25pp"),
        ("Neutral zone", f"{num(stance.band[0])} to {num(stance.band[1])}%", "", "Range of the weighted estimators, at least 0.5pp wide"),
        ("Gap: real rate − r*", f"{fmt(stance.gap, 2)}pp", "", f"{STANCE_WORD[stance.cls]}"),
    ]
    body = "".join(f"<tr><th scope=\"row\">{escape(a)}</th><td class=\"num\">{b}</td><td>{escape(c)}</td><td>{escape(d)}</td></tr>"
                   for a, b, c, d in rows)
    return ('<div class="table-wrap"><table><thead><tr><th scope="col">Component</th><th scope="col" class="num">Value</th>'
            f'<th scope="col">Date</th><th scope="col">Basis</th></tr></thead><tbody>{body}</tbody></table></div>')


def stance_section(stance, estimates: dict, cfg: Config, number: int) -> str:
    """Overview: the stance itself. How r* is estimated is on its own tab."""
    if stance is None:
        return ""
    return f"""
<section class="story-section" id="block-P" aria-labelledby="h-P">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">POLICY STANCE</p>
      <h2 id="h-P">{escape(BLOCK_TITLES['P'])}</h2>
      <p class="takeaway">{escape(stance.rate_name)} against the neutral rate, the rate at which policy neither stimulates nor restrains the economy. Both are in real terms with the same expected inflation, so the gap is the same as in nominal terms.</p>
    </div>
  </div>
  <div class="stance-answer">
    <p class="stance-verdict">{STANCE_ANSWER[stance.cls]}</p>
    <p class="stance-gap">{escape(stance.rate_name)} {num(stance.rate, 2)}% against a neutral rate of {num(stance.nominal_neutral, 2)}%:
      <strong>{fmt(stance.gap, 2)}pp</strong> {"above" if stance.gap >= 0 else "below"} neutral in real terms (neutral zone {num(stance.band[0], 2)} to {num(stance.band[1], 2)}% real)</p>
    <div class="stance-answer-bar">{stance_bar(stance.gap, (stance.band[1] - stance.band[0]) / 2, f"Real-rate gap {fmt(stance.gap)} percentage points, {stance.cls}")}</div>
  </div>
  {stance_rows(stance)}
  <p class="more-link"><a href="stance.html">How r* is estimated →</a></p>
</section>"""


def stance_workings_section(stance, estimates: dict, cfg: Config, number: int) -> str:
    """Stance working tab: the r* suite, its history and published estimates."""
    if stance is None:
        return ""
    suite = estimates["rstar"]
    rows = [
        (stance.rate_name, f"{num(stance.rate, 2)}%", f"{stance.rate_date:%-d %b %Y}", "Bank of England"),
        ("− Expected inflation", f"{num(stance.expected_inflation)}%", "", stance.expectation_source),
        ("= Real rate", f"{num(stance.real_rate, 2)}%", "", ""),
        ("r*, suite headline", f"{num(stance.r_star, 2)}%", "", "Weighted estimators below, rounded to 0.25pp"),
        ("Neutral zone", f"{num(stance.band[0])} to {num(stance.band[1])}%", "", "Range of the weighted estimators, at least 0.5pp wide"),
        ("Gap: real rate − r*", f"{fmt(stance.gap, 2)}pp", "", f"{STANCE_WORD[stance.cls]}"),
    ]
    body = "".join(f"<tr><th scope=\"row\">{escape(a)}</th><td class=\"num\">{b}</td><td>{escape(c)}</td><td>{escape(d)}</td></tr>"
                   for a, b, c, d in rows)
    est_rows = ""
    if hasattr(suite, "estimators"):
        for k, v in suite.estimators.items():
            if not v:
                continue
            w = v.get("weight", 0)
            est_rows += (f"<tr class=\"{'' if w else 'muted-row'}\"><th scope=\"row\">{escape(v['name'])}</th>"
                         f"<td class=\"num\">{num(v['value'], 2)}%</td><td class=\"num\">{num(v['value'] + 2, 2)}%</td>"
                         f"<td>{escape(v['date'])}</td><td>{escape(v['role'])}</td><td class=\"num\">{w:.2f}</td>"
                         f"<td>{escape(v['basis'])}. <em>{escape(v['status'])}</em></td></tr>")
    est_table = (f'<h3 class="sub-h">The r* suite</h3><div class="table-wrap"><table><thead><tr><th scope="col">Estimator</th>'
                 f'<th scope="col" class="num">Real</th><th scope="col" class="num">Nominal</th><th scope="col">Date</th>'
                 f'<th scope="col">Horizon</th><th scope="col" class="num">Weight</th><th scope="col">Basis and status</th></tr></thead>'
                 f'<tbody>{est_rows}</tbody></table></div>' if est_rows else "")
    chart = rstar_chart(suite, cfg)
    published = cfg.manual.get("rstar")
    pub_rows = ""
    if published is not None:
        pub = published.dropna(subset=["low"]).copy()
        pub["date"] = pd.to_datetime(pub["date"])
        for _, r in pub.sort_values("date", ascending=False).iterrows():
            rng = f"{r['low']:.2f}" if r["low"] == r["high"] else f"{r['low']:.2f} to {r['high']:.2f}"
            pub_rows += (f"<tr><th scope=\"row\">{escape(str(r['author']))}</th><td class=\"num\">{rng}%</td>"
                         f"<td>{r['date']:%b %Y}</td><td><a href=\"{escape(str(r['url']))}\">{escape(str(r['source']))}</a></td></tr>")
    pub_html = (f'<details class="disclosure-plain"><summary>Published estimates of r* for comparison (real, %)</summary>'
                f'<div class="table-wrap"><table><thead><tr><th scope="col">Who</th><th scope="col" class="num">r*</th>'
                f'<th scope="col">Date</th><th scope="col">Source</th></tr></thead><tbody>{pub_rows}</tbody></table></div>'
                f'<p class="chart-note">Hand-maintained in manual/rstar.csv. Nominal figures are converted to real by subtracting 2.</p></details>'
                if pub_rows else "")
    return f"""
<section class="story-section" id="rstar" aria-labelledby="h-rstar">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">THE NEUTRAL RATE</p>
      <h2 id="h-rstar">How r* is estimated</h2>
      <p class="takeaway">No single estimate of the neutral rate is reliable, so r* is a weighted suite of estimators, following central-bank practice, and the neutral zone is their range. Stance is in percentage points and never coloured, because "up" means tight, not inflationary.</p>
    </div>
  </div>
  {stance_rows(stance)}
  {est_table}
  {chart}
  {pub_html}
  {charts.fig_note("The suite is re-estimated weekly; method and evidence are in reports/UK neutral rate estimation methods.md. The Market Participants Survey reports the neutral Bank Rate in nominal terms; it is converted to real with the same year-ahead expected inflation as Bank Rate. The gilt forward includes term and liquidity premia and is shown only.", "Bank of England (yield curves, Market Participants Survey, Inflation Attitudes Survey); Office for National Statistics; Monetary Space estimates")}
</section>"""


def momentum_section(data: dict, number: int) -> str:
    """Unscored: where inflation already is, and slower-moving context."""
    rows = []

    def add(name, s, unit, note, dp=1):
        s = s.dropna() if s is not None else None
        if s is None or s.empty:
            return
        p = s.index[-1]
        year_ago = s.get(p - (12 if p.freqstr == "M" else 4))
        prev = f"{num(year_ago, dp)}{unit}" if year_ago is not None and pd.notna(year_ago) else "–"
        rows.append(f"<tr><th scope=\"row\">{escape(name)}</th><td class=\"num\">{num(s.iloc[-1], dp)}{unit}</td>"
                    f"<td>{period_label(p)}</td><td class=\"num\">{prev}</td><td>{escape(note)}</td></tr>")

    add("Services CPI inflation", data.get("D7NN"), "%", "Mostly domestic costs; about 3¼% is consistent with 2% overall")
    add("Core CPI inflation", data.get("DKO8"), "%", "Excluding energy, food, alcohol and tobacco")
    add("Private-sector regular pay growth", data.get("KAJ4"), "%", "3-month average, y/y; about 3¼% is target-consistent")
    if "IUDSIZC" in data and "IUDMIZC" in data:
        f = (10 * data["IUDMIZC"] - 5 * data["IUDSIZC"]) / 5
        f = f.groupby(f.index.asfreq("M")).mean()
        add("5y5y implied inflation", f, "%", "Market-implied, 5–10 years ahead. RPI basis until 2030, CPIH after: not comparable with history", 2)
    cli = [data.get(f"OECD_CLI:{c}") for c in ("DEU", "FRA", "ITA", "ESP", "USA")]
    if all(c is not None for c in cli):
        w = [0.25, 0.18, 0.13, 0.09, 0.35]
        comb = sum(wi * ci for wi, ci in zip(w, cli)) / sum(w)
        add("Trading partners' leading indicator", comb, "", "OECD CLI, 100 = trend; euro area proxy and US weighted by UK exports")
    if not rows:
        return ""
    return f"""
<section class="story-section" id="momentum" aria-labelledby="h-momentum">
  <div class="story-heading">
    <span class="section-number">{number:02d}</span>
    <div>
      <p class="eyebrow">MOMENTUM AND CONTEXT · NOT SCORED</p>
      <h2 id="h-momentum">Where inflation already is</h2>
      <p class="takeaway">These are outcomes or slow-moving context rather than drivers, so they are shown but not scored. Services inflation and pay are what second-round effects would show up in.</p>
    </div>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th scope="col">Measure</th><th scope="col" class="num">Latest</th><th scope="col">Date</th><th scope="col" class="num">A year earlier</th><th scope="col">Note</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</section>"""


def rstar_chart(suite, cfg: Config) -> str:
    """Trend-cycle r̄ (with ±1 s.e.), the suite headline and the gilt forward, since 2000."""
    from .transform import to_monthly
    if not hasattr(suite, "history"):
        return ""
    h = suite.history
    tc = pd.Series({pd.Period(k, "Q"): v[0] for k, v in h["trend_cycle"].items()}).sort_index()
    se = pd.Series({pd.Period(k, "Q"): v[1] for k, v in h["trend_cycle"].items()}).sort_index()
    fwd = pd.Series({pd.Period(k, "Q"): v for k, v in h["market_5y5y"].items()}).sort_index()
    since = pd.Period("2000Q1", "Q")
    tc, se, fwd = tc[tc.index >= since], se[se.index >= since], fwd[fwd.index >= since]
    path = [to_monthly(s) for s in (tc, tc - se, tc + se)]
    c = charts.ChartData(
        id="rstar", title="r*: the trend-cycle estimate and the gilt market",
        subtitle="Real, %. Line: index-linked gilt 5y5y real forward (includes term premia). Dashed with band: trend-cycle r̄ ± 1 s.e.",
        unit="%", decimals=1, step=False, x=to_monthly(fwd), reference=None,
        ref_path=(path[0], path[1], path[2], f"r̄ {path[0].iloc[-1]:.1f}"), ylim=(-3.0, 5.0),
        source="Bank of England; Monetary Space estimates", attribution="")
    markup, note = charts.svg(c, width=760)
    return (f'<figure class="chart-panel wide" tabindex="0" aria-describedby="tip-rstar">'
            f'<figcaption class="panel-heading"><h3>{escape(c.title)}</h3><p>{escape(c.subtitle)}</p></figcaption>'
            f'<div class="chart-frame">{markup}<div class="chart-tip" id="tip-rstar" aria-live="polite"></div></div>{charts.fig_note(note)}</figure>')


def part(number: int, title: str, intro: str) -> str:
    return (f'<header class="part-heading" id="part-{number}"><p class="part-number">Part {number}</p>'
            f'<h2>{escape(title)}</h2><p>{escape(intro)}</p></header>')


TERM_SCRIPT = """
(()=>{const tip=document.getElementById('term-tip');if(!tip)return;let cur=null;
const show=el=>{cur=el;tip.textContent=el.dataset.explain;tip.hidden=false;el.setAttribute('aria-describedby','term-tip');
const r=el.getBoundingClientRect(),w=Math.min(340,window.innerWidth-24);tip.style.width=w+'px';
let x=Math.min(Math.max(12,r.left),window.innerWidth-w-12);tip.style.left=(x+window.scrollX)+'px';
const below=r.bottom+8+tip.offsetHeight<window.innerHeight;
tip.style.top=((below?r.bottom+8:r.top-8-tip.offsetHeight)+window.scrollY)+'px';};
const hide=()=>{if(cur)cur.removeAttribute('aria-describedby');cur=null;tip.hidden=true;};
for(const el of document.querySelectorAll('.term')){el.addEventListener('mouseenter',()=>show(el));el.addEventListener('mouseleave',hide);
el.addEventListener('focus',()=>show(el));el.addEventListener('blur',hide);}
document.addEventListener('keydown',e=>{if(e.key==='Escape')hide();});window.addEventListener('scroll',hide,{passive:true});})();
"""


TABS = [("index.html", "Overview"), ("drivers.html", "Inflation drivers"), ("stance.html", "Stance working")]


def shell(title: str, active: str, body: str, now, script: bool = True) -> str:
    nav = "".join(f'<a href="{f}"{" aria-current=\"page\" class=\"active\"" if f == active else ""}>{escape(n)}</a>' for f, n in TABS)
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#153f46">
<meta name="description" content="Monetary Space: a guide to UK monetary policy">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Monetary Space">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="Monetary Space: a guide to UK monetary policy">
<meta property="og:url" content="https://patrickmschneider.github.io/monetary-space/{active if active != 'index.html' else ''}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="Monetary Space: a guide to UK monetary policy">
<title>{escape(title)}</title>
<style>{CSS}{charts.CSS}{policy_path.CSS}{decomposition.CSS}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="index.html"><span><strong>Monetary Space</strong><small>A GUIDE TO UK MONETARY POLICY</small></span></a>
    <nav class="tabs" aria-label="Pages">{nav}</nav>
    <p class="release-stamp"><span class="status-dot" aria-hidden="true"></span>Data as of <strong>{now:%-d %B %Y}</strong></p>
  </div>
</header>
<main id="main" class="page-shell editorial">
{body}
  <footer>
    <div><strong>Monetary Space</strong><p>AI augmented by Patrick Schneider</p></div>
    <div><p>Built {now:%-d %B %Y, %H:%M} UK time</p></div>
  </footer>
</main>
<div id="term-tip" class="term-tip" role="tooltip" hidden></div>
<script>{charts.SCRIPT}{TERM_SCRIPT}</script>
</body>
</html>
"""


def pages(cfg: Config, inds: list[Indicator], blocks: dict[str, Block], problems: list[str], now,
          failed: list[str], context: list | None = None, stance=None, verdict=None,
          estimates: dict | None = None, data: dict | None = None) -> dict[str, str]:
    """Overview (index.html), Inflation drivers (drivers.html) and Stance working (stance.html)."""
    thr = cfg.weights["direction_threshold"]
    estimates, data = estimates or {}, data or {}
    notice = ""
    if problems or failed:
        items = [f"Source failed this run, last good value kept: {escape(s)}." for s in failed]
        items += [f"Not scored: {escape(p)}." for p in problems]
        notice = '<div class="notice" role="status">' + " ".join(items) + "</div>"

    # Overview: the answer; where the economy is; the pressure ahead; policy and where markets expect it to go.
    n = 1
    context_html = charts.section(context or [], n)
    n += bool(context_html)
    blocks_html = ""
    for b in blocks.values():
        blocks_html += block_section(b, cfg, n)
        n += 1
    stance_html = stance_section(stance, estimates, cfg, n)
    n += bool(stance_html)
    path_html = policy_path.section(
        policy_path.prepare(cfg, data, estimates, stance, now.tz_localize(None).normalize()), n, stance)
    overview = f"""
  <section class="briefing-lead">
    <p class="eyebrow">UK MONETARY POLICY · {now:%B %Y}</p>
    {verdict_strip(cfg, blocks, stance, verdict, data, now)}
    <h1 class="lead-sentence">{lead_sentence(blocks, thr, stance, verdict)}</h1>
    <nav class="reading-guide" aria-label="Sections"><span>On this page</span>
      <a href="#part-1">1. Where the economy is</a><a href="#part-2">2. Inflation pressure ahead</a>
      <a href="#part-3">3. Monetary policy</a></nav>
  </section>
  {notice}
  {part(1, "Where the economy is", "Headline data, for orientation.")}
  {context_html}
  {part(2, "Inflation pressure ahead", "The terms of the Phillips curve: expectations, slack on the demand and supply sides, and external cost-push. Together they give the inflation-pressure score.")}
  {headline_strip(blocks, cfg, stance)}
  {pressure_note(cfg, verdict)}
  <p class="legend"><span><i class="swatch up"></i>Inflationary (z above +{thr:g})</span><span><i class="swatch neutral"></i>Neutral</span><span><i class="swatch down"></i>Disinflationary (z below −{thr:g})</span><span><i class="swatch band"></i>Neutral band ±{thr:g}</span></p>
  <p class="basis-note">Scores are z-scores on a fixed −3 to +3 scale: z = s·(x − b)/σ, clipped at ±{cfg.weights['z_clip']:g}. Positive always means inflationary; beyond ±{thr:g} an indicator points up or down. Hover or focus any z for its calculation.</p>
  {blocks_html}
  {part(3, "Monetary policy", "Whether policy is stimulating or restraining the economy, and where markets expect it to go.")}
  {stance_html}
  {path_html}"""

    drivers = f"""
  <section class="briefing-lead tab-lead">
    <p class="eyebrow">INFLATION DRIVERS · {now:%B %Y}</p>
    <h1 class="tab-title">Where inflation is, and what has driven it</h1>
    <p class="basis-note">Not scored. Outcomes and slow-moving context, then three model-based ways to split inflation into its sources, looking back.</p>
  </section>
  {momentum_section(data, 1)}
  {decomposition.section(cfg.analysis, 2)}"""

    workings = f"""
  <section class="briefing-lead tab-lead">
    <p class="eyebrow">STANCE WORKING · {now:%B %Y}</p>
    <h1 class="tab-title">How the policy stance is measured</h1>
    <p class="basis-note">The neutral rate r*, the estimators behind it, and how they compare with published estimates.</p>
  </section>
  {stance_workings_section(stance, estimates, cfg, 1)}"""

    return {
        "index.html": shell("Monetary Space", "index.html", overview, now),
        "drivers.html": shell("Inflation drivers · Monetary Space", "drivers.html", drivers, now),
        "stance.html": shell("Stance working · Monetary Space", "stance.html", workings, now),
    }


def page(*args, **kwargs) -> str:
    """The overview page (kept for callers that want a single page)."""
    return pages(*args, **kwargs)["index.html"]


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
.headline-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:repeat(6,auto);border-top:2px solid var(--ink);border-bottom:1px solid var(--border);margin-top:24px}
.metric{padding:20px 20px 18px;border-right:1px solid var(--border);min-width:0;display:grid;grid-template-rows:subgrid;grid-row:span 6;row-gap:0}
.metric>.question{align-self:start}
.metric>.metric-value{align-self:end}
.zbar-slot{display:block;height:8px}
.spark-slot:empty{min-height:0}
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
.verdict{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr) minmax(0,1fr);grid-template-rows:auto auto auto;column-gap:36px;row-gap:0;border-top:2px solid var(--ink);padding:20px 0 16px;margin:6px 0 18px}
.verdict-main{grid-row:1 / span 2;align-self:end}
.dial{display:grid;grid-template-rows:subgrid;grid-row:1 / span 2;align-self:end}
.dial-bar{align-self:start}
.dial-notes{align-self:start}
.verdict-label{font-size:10px;font-weight:700;letter-spacing:1.65px;color:var(--muted);text-transform:uppercase;margin:0 0 4px}
.verdict-word{font-size:clamp(34px,4.2vw,50px);font-weight:650;letter-spacing:-1.5px;line-height:1.05;margin:0}
.verdict-word.neutral{color:var(--fg)}
.verdict-driver{font-size:14px;color:var(--muted);margin:6px 0 0}
.verdict-driver a{color:var(--accent)}
.dial h2{font-size:12px;font-weight:600;color:var(--muted);margin:0 0 8px;display:flex;justify-content:space-between;gap:10px}
.dial h2 span{color:var(--fg);white-space:nowrap}
.dial h2 span.up{color:var(--up)}.dial h2 span.down{color:var(--down)}
.dial-note{font-size:11px;color:var(--muted);margin:8px 0 0;line-height:1.5}
.verdict-facts{grid-column:1/-1;grid-row:3;margin-top:14px!important;font-size:12px;color:var(--muted);margin:4px 0 0;border-top:1px solid var(--border);padding-top:12px}
.verdict-facts strong{color:var(--fg);font-weight:600}
.sbar{position:relative;display:block;height:8px;background:var(--track);min-width:90px}
.sbar-band{position:absolute;top:0;bottom:0;background:var(--band)}
.sbar-mark{position:absolute;top:-4px;bottom:-4px;width:3px;margin-left:-1.5px;background:var(--ink)}
.sbar-mark.clipped{width:6px;margin-left:-3px}
.sbar-ends{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-top:4px}
.metric-unit{font-size:16px;font-weight:600;margin-left:1px}
.chart-panel.wide{max-width:760px;margin:6px 0 18px;border-top:0;padding-top:0}
.disclosure-plain{margin:10px 0 14px;font-size:13px}
.sub-h{font-size:16px;font-weight:650;color:var(--ink);margin:22px 0 8px}
.muted-row th,.muted-row td{color:var(--muted)}
.disclosure-plain summary{cursor:pointer;color:var(--accent);margin-bottom:10px}
.table-wrap a{color:var(--accent)}
.part-heading{margin:56px 0 0;padding-top:18px;border-top:2px solid var(--ink)}
.part-number{font-size:10px;font-weight:700;letter-spacing:1.65px;text-transform:uppercase;color:var(--accent);margin:0 0 6px}
.part-heading h2{font-family:Georgia,'Times New Roman',serif;font-weight:400;font-size:clamp(26px,3vw,34px);letter-spacing:-.6px;color:var(--ink);margin:0 0 8px}
.part-heading>p:last-child{font-size:14px;color:var(--muted);margin:0 0 8px;max-width:760px}
.reading-guide{display:flex;flex-wrap:wrap;gap:8px 22px;padding:12px 0 4px;font-size:12px;border-top:1px solid var(--border);margin-top:6px}
.reading-guide>span{font-weight:700;color:var(--muted)}
.reading-guide a{color:var(--accent);text-decoration:none}
.reading-guide a:hover{text-decoration:underline}
.tabs{display:flex;align-self:stretch;gap:24px;margin-left:auto;margin-right:8px}
.tabs a{display:flex;align-items:center;position:relative;font-size:13px;color:var(--muted);text-decoration:none;padding:0 2px}
.tabs a:hover{color:var(--accent)}
.tabs a.active{color:var(--accent);font-weight:700}
.tabs a.active::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:var(--accent)}
.tab-title{font-family:Georgia,'Times New Roman',serif;font-weight:400;font-size:clamp(28px,3.4vw,40px);letter-spacing:-.8px;color:var(--ink);margin:0 0 10px}
.tab-lead{padding-bottom:0}
.more-link{font-size:13px;margin:10px 0 0}
.stance-answer{border-top:2px solid var(--ink);border-bottom:1px solid var(--border);padding:18px 0 20px;margin:0 0 18px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6px 36px;align-items:end}
.stance-verdict{grid-column:1;font-size:clamp(28px,3.2vw,40px);font-weight:650;letter-spacing:-1px;line-height:1.1;color:var(--ink);margin:0}
.stance-gap{grid-column:1;font-size:14px;color:var(--muted);margin:4px 0 0}
.stance-gap strong{color:var(--fg);font-weight:650}
.stance-answer-bar{grid-column:2;grid-row:1 / span 2;align-self:center}
@media(max-width:700px){.stance-answer{grid-template-columns:1fr}.stance-answer-bar{grid-column:1;grid-row:auto}}
.more-link a{color:var(--accent)}
.term{text-decoration:underline dotted var(--muted);text-underline-offset:3px;cursor:help;color:inherit}
a.term:hover{color:var(--accent)}
.term-tip{position:absolute;z-index:50;background:var(--ink);color:var(--bg);font-size:12px;font-weight:400;line-height:1.5;padding:10px 12px;border-radius:6px;box-shadow:0 4px 14px #0002;pointer-events:none;text-align:left;white-space:normal;letter-spacing:0}
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
.block-table{table-layout:fixed;min-width:760px}
.block-table tbody th{min-width:0}
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
footer>div:last-child{text-align:right;align-self:flex-end}
@media(max-width:900px){.verdict{grid-template-columns:1fr;grid-template-rows:none;row-gap:18px}.verdict-main,.dial{grid-row:auto}.dial{display:block}.verdict-facts{grid-row:auto}}
@media(max-width:1000px){.header-inner{padding:0 26px}.page-shell{padding:30px 26px 0}
.headline-strip{grid-template-columns:1fr 1fr}.metric{border-bottom:1px solid var(--border)}.metric:nth-child(2n){border-right:0}.metric:nth-child(2n+1){padding-left:0}}
@media(max-width:700px){.tabs{order:3;width:100%;height:44px;margin:0;gap:18px;overflow-x:auto}.header-inner{height:auto;padding:20px 18px 0;flex-wrap:wrap;gap:12px}.brand{font-size:25px}
.page-shell{padding:24px 18px 0}.lead-sentence{font-size:18px}
.headline-strip{grid-template-columns:1fr}.metric{padding:18px 0;border-right:0}
.story-heading{gap:12px}.story-heading h2{font-size:21px}.takeaway{font-size:14px}
footer{display:block;font-size:10px}footer>div:last-child{text-align:left;margin-top:20px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""
