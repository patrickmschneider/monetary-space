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

The unemployment indicator is scored against our own estimate of u\*, not the MPC's. It comes from a wage Phillips curve with a time-varying u\*, estimated by Kalman filter and smoother (`src/monetary_space/nairu.py`, settings in `config/nairu.yaml`):

- y = private-sector regular pay growth (q/q annualised) − expected inflation − trend productivity growth
- yₜ = a·yₜ₋₁ − β(uₜ − u\*ₜ) + εₜ, with u\*ₜ = u\*ₜ₋₁ + ηₜ
- Expected inflation is half households' 1-year expectations (re-centred so their pre-2020 average is 2%) and half last quarter's CPI inflation. The CPI half captures pay catching up with past inflation, which household expectations alone miss (with them alone, the 2022–24 pay surge reads as extreme tightness).
- Trend productivity is the 5-year average of output-per-hour growth. There is no constant, so u\* is the unemployment rate at which real pay grows in line with productivity.
- σ_η, how fast u\* may move, is fixed at 0.10pp a quarter; a, β and σ_ε are estimated by maximum likelihood. 2020–21 is excluded (furlough and composition effects).
- Sample 2001Q2 onward. The z-score's σ is the pre-2020 SD of the gap u − u\*. The tooltip shows the MPC's latest stated u\* for comparison.

u\* is weakly identified in UK data and the result depends on the specification (all q/q pay growth with a lag term; 90% band for the latest quarter):

| Specification | 2007 Q4 | 2013 Q4 | 2019 Q4 | 2026 Q2 | 90% band |
| --- | --- | --- | --- | --- | --- |
| **Default: half household expectations, half lagged CPI, σ_η 0.10** | 4.9 | 5.1 | 5.1 | 5.2 | ±0.9 |
| Same, σ_η 0.15 | 4.8 | 5.2 | 5.1 | 5.2 | ±1.1 |
| Household expectations only | 5.2 | 5.5 | 5.7 | 6.0 | ±0.9 |
| Lagged CPI only | 4.2 | 4.2 | 4.2 | 4.1 | ±1.5 |
| Year-on-year pay growth, household expectations | 5.4 | 5.5 | 5.5 | 5.6 | ±1.4 |

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
