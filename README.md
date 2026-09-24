# monetary-space

A single-screen UK monetary policy dashboard: is policy tight enough for the inflation pressure?

A Python script fetches the data, scores it and renders one static HTML page. GitHub Actions rebuilds the page on a schedule and GitHub Pages hosts it. The full build spec is in [docs/SPEC.md](docs/SPEC.md).

**Status:** Phase 1 of 4. Blocks A (demand) and B (domestic inflation) are scored on a plain page. The global block, policy stance, verdict and final layout come in later phases.

## Run it locally

```sh
pip install -e ".[test]"
pytest -q
python -m monetary_space build          # fetch, store a vintage, score, render to site/
python -m monetary_space build --no-fetch   # rebuild from the latest stored vintage
open site/index.html
```

Local runs store vintages in `store/` (ignored by git). Put `FRED_API_KEY=...` in a `.env` file for sources that need it (from Phase 2).

## How it fits together

| Path | What it holds |
| --- | --- |
| `config/indicators.yaml` | Every series and scored indicator: source, code, transform, benchmark, σ, sign, lag, attribution |
| `config/weights.yaml` | Pressure weights, thresholds, z clip, r\* range, rule coefficients |
| `manual/` | Hand-maintained CSVs: MPR projections and u\*, MPC dates and votes, r\* estimates, fiscal events |
| `src/monetary_space/fetch/` | One module per publisher (ONS, Bank of England) |
| `src/monetary_space/transform.py`, `score.py` | Pure functions for transforms, benchmarks and the scoring rules |
| `src/monetary_space/store.py` | Dated vintages, one Parquet file per build day, on the `data` branch |
| `src/monetary_space/render.py` | The static page |
| `scripts/gate.py` | Lets the right UTC cron run through for 07:10 and 12:15 UK time |

Changing a benchmark, weight or threshold in `config/` changes the page with no code edits.

## Estimated u\* (NAIRU)

The unemployment indicator is scored against our own estimate of u\*, not the MPC's. It comes from a multivariate filter (`src/monetary_space/nairu.py`, settings in `config/nairu.yaml`), estimated by maximum likelihood with a Kalman filter and smoother:

- Unemployment is a slow-moving trend u\* (a random walk) plus a gap that mean-reverts (AR(2)): uₜ = u\*ₜ + gₜ.
- A wage Phillips curve says where the trend is: yₜ = c + a·yₜ₋₁ − β·gₜ + εₜ, where y is private-sector regular pay growth (q/q annualised) minus expected inflation minus trend productivity growth.
- Expected inflation is half households' 1-year expectations (re-centred so their pre-2020 average is 2%) and half last quarter's CPI inflation, so pay catching up with past inflation is not read as tightness. Trend productivity is the 5-year average of output-per-hour growth.
- Fixed in config: u\* may move by σ_η = 0.15pp a quarter; the gap's persistence ρ₁ + ρ₂ is capped at 0.9 (uncapped, the likelihood pushes the gap to a unit root and u\* stops tracking unemployment). The rest (c, a, β, ρ₁, ρ₂, σ_ε, σ_ν) is estimated.
- Sample 2001Q2 onward; 2020–21 pay data are excluded (furlough and composition effects). The z-score's σ is the pre-2020 SD of u − u\*. The tooltip shows the MPC's latest stated u\* for comparison.

A first version used the wage Phillips curve alone, without the gap equation. It put u\* above unemployment in every quarter since 2016, because nothing forced the gap to close. The table shows how the estimate depends on the choices (90% band for the latest quarter):

| Specification | 2007 Q4 | 2013 Q4 | 2016 Q4 | 2019 Q4 | 2023 Q4 | 2026 Q2 | 90% band | u\* > u since 2016 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Default** | 5.7 | 6.6 | 5.3 | 4.3 | 4.6 | 4.9 | ±0.5 | 79% |
| σ_η 0.10 | 5.6 | 6.0 | 5.3 | 4.6 | 4.6 | 4.7 | ±0.5 | 81% |
| Household expectations only | 5.7 | 6.5 | 5.1 | 4.3 | 4.9 | 4.9 | ±0.5 | 86% |
| Lagged CPI only | 5.8 | 6.7 | 5.3 | 4.3 | 4.2 | 4.7 | ±0.6 | 74% |
| Gap persistence uncapped | 5.1 | 5.8 | 5.4 | 4.8 | 5.0 | 5.1 | ±0.9 | 100% |
| Phillips curve only (first version) | 4.9 | 5.1 | 5.2 | 5.1 | 5.1 | 5.2 | ±0.9 | 95% |

For comparison, the February 2026 MPR put u\* at about 4¾%.

## Scheduled builds

`.github/workflows/build.yml` runs at 07:10 UK time every day (after the 07:00 ONS releases) and at 12:15 UK on MPC announcement days listed in `manual/mpc_dates.csv`. It also runs on every push to `main` and from **Actions → build → Run workflow**. Each run saves the day's raw data to the `data` branch, then deploys the page.

- **Late starts.** GitHub can start scheduled runs late when busy. On release days, use the manual trigger.
- **Failed sources.** If a source fails, the last good value is kept, marked on the page, and logged in `fetch_log.csv` on the `data` branch. The page still builds. GitHub emails the repository owner if a whole run fails.
- **Schedules switched off.** GitHub disables scheduled workflows in public repositories after 60 days without activity. To re-enable: **Actions → build → Enable workflow**. Whether the daily data commits count as activity is still to be confirmed.
- **Secret.** `FRED_API_KEY` is a repository secret (Settings → Secrets and variables → Actions).

## Data sources and attribution

Every series on the page shows its source. Series are republished for academic, non-commercial use with attribution.

- Office for National Statistics, licensed under the Open Government Licence v3.0.
- HMRC PAYE Real Time Information, published by the ONS under the Open Government Licence v3.0.
- Bank of England: Agents' scores; Inflation Attitudes Survey.
- Decision Maker Panel (Bank of England, Stanford University and University of Nottingham).
