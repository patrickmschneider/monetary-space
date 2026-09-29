# monetary-space

A single-screen UK monetary policy dashboard: is policy tight enough for the inflation pressure?

A Python script fetches the data, scores it and renders one static HTML page. GitHub Actions rebuilds the page on a schedule and GitHub Pages hosts it. The full build spec is in [docs/SPEC.md](docs/SPEC.md).

**Status:** Phase 2 of 4, restructured around the Phillips curve. The layout pass, Compare-to, release log and embed view come in Phase 3.

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

## Estimated r\* (neutral real rate)

Stance compares the current policy setting with the neutral rate, the rate at which policy neither stimulates nor restrains the economy: Bank Rate minus year-ahead expected inflation (the MPR projection) against r\*. Nominal estimates of neutral (the survey) are converted with the same expected inflation, so the real gap equals the nominal gap. This departs from the spec's 2-year OIS (owner's decision, 29 Sep 2026); the market's expected path is shown in the policy path chart. No single r\* estimate is reliable for the UK, so, following central-bank practice (Bank of England, ECB, Bank of Canada), r\* is a suite of estimators (`analysis/rstar_suite.py`, method and evidence in [reports/UK neutral rate estimation methods.md](reports/UK%20neutral%20rate%20estimation%20methods.md)):

| Estimator | Horizon | Weight | Latest (real) |
| --- | --- | --- | --- |
| Trend-cycle model (after Del Negro, Giannone, Giannoni & Tambalotti): common random-walk trends in Bank Rate (missing at the lower bound 2009–21), CPI inflation and 10-year nominal and real gilt yields; trend-shock variances at DGGT's priors; cycle persistence capped at 0.9 | long run | 0.40 | 1.25% ± 0.3 |
| Repaired HLW-style model: λz = 0 (Buncic 2022), IS slope estimated, COVID and lower-bound variance scaling, households' expectations as the deflator | policy horizon | 0.25 if identified | excluded: the IS slope goes to its bound, so r\* is not identified (as the NY Fed found for the UK) |
| Bank of England Market Participants Survey: median neutral Bank Rate minus year-ahead expected inflation (scraped from each round since 2022) | policy horizon | 0.35 | 0.65% (3.25% − 2.6%) |
| Index-linked gilt 5y5y real forward | long run | shown only: includes term and liquidity premia | 2.6% |
| 10-year average real Bank Rate | benchmark | shown only | −0.5% |

Headline: the weighted mean of the estimators that pass diagnostics, rounded to 0.25pp: **1.0% real** (3.6% nominal at 2.6% expected inflation). The neutral zone is their range, rounded outward and at least ±0.5pp: 0.4–1.4%. It is consistent with published estimates (Alan Taylor 0.75%, Bank staff models up 25–75bp since 2018). An earlier single-model estimate (−0.8%) was an artefact of the HLW model failing on UK data; the report explains why.

## Phillips-curve structure

Inflation pressure is read as the terms of a hybrid New Keynesian Phillips curve, π = expectations + slack + cost-push, with slack split into demand and supply. This replaces the spec's demand / domestic inflation / global blocks (a design change agreed with the owner).

| Block | Question | Scored indicators |
| --- | --- | --- |
| Expectations | Are inflation expectations anchored at 2%? | Firms' expected own-price growth (DMP), households' 1-year expectations (BoE IAS) |
| Demand | Is demand running ahead of capacity? | Unemployment vs estimated u\*, vacancies per unemployed, payrolls, GDP growth vs estimated potential, Agents' capacity utilisation |
| Supply | Is capacity growing more slowly than normal? | Unit labour cost growth vs 2%, productivity growth vs its 5-year trend, change in inactivity |
| Cost-push | Are external costs pushing up prices? | Brent (US$), UK gas, sterling ERI, import prices |

Not scored, shown as momentum and context: services CPI, core CPI, private pay, 5y5y implied inflation, trading partners' leading indicators.

**Pressure weights.** Two weightings are computed; `pressure.method` in `config/weights.yaml` picks the one that drives the verdict, and the page shows both.
- *Config (literature-based):* Expectations 0.35, Demand 0.25, Supply 0.25, Cost-push 0.15. Look through first-round cost-push, respond fully to second-round channels ([reports/UK cost push pass through.md](reports/UK%20cost%20push%20pass%20through.md)).
- *Estimated:* each block's effect on CPI inflation 2–3 years out in a UK Bernanke–Blanchard wage–price model (`analysis/bb_uk.py`): Expectations 0.18, Demand 0.30, Supply 0.36, Cost-push 0.16. Energy adds 0.9pp to inflation in year one of a 1-SD shock but only about 0.2pp at the policy horizon: look-through, estimated rather than assumed.
- *State multiplier on cost-push:* 1 + (ratio − 1)·logistic((CPI − 3.1)/0.25), capped at 2.5. The ratio is the estimated high/low-inflation pass-through (headline CPI response to an oil supply shock when CPI is above vs below 3%, `analysis/passthrough_lp.py`): about 1.9.

**Estimations** (`analysis/`, re-run weekly by `.github/workflows/estimate.yml`; results in `analysis/results/`):

| Script | What it estimates |
| --- | --- |
| `passthrough_lp.py` | Local projections of UK prices and pay on Känzig's oil supply news shock, linear, LP-IV and state-dependent. A 10% oil shock raises headline CPI about 0.6% and core about 0.3% within two years; pay does not respond measurably |
| `bb_uk.py` | UK Bernanke–Blanchard four-equation model, 2001–2026; contributions of energy, food and labour-market tightness; block weights |
| `shapiro_uk.py` | Shapiro (2022) demand/supply split of household-spending inflation over 39 ONS categories |
| `svar_uk.py` | Sign-identified Bayesian VAR (oil, GDP, CPI, Bank Rate, sterling; 1993–), historical decomposition of CPI inflation. An illustration, not a forecast |

## Data notes

- Gas is the ONS System Average Price, from 2018; its σ is a config value (2010–19 SD of NBP gas price changes, 36pp).
- Unit labour costs and productivity use a σ sample from 1993 (inflation targeting); the full samples include the 1970s.
- The OECD no longer publishes a euro-area leading indicator: Germany, France, Italy and Spain stand in, weighted 65/35 with the US by UK export shares.

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
