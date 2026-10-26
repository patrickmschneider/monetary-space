# Plan: Australia and US editions

Status: phase 0 built 2026-10-26 (the UK runs through the country layer); phases 1–3 not started. Facts marked *confirm* were written from memory and need checking against the source before they go into config.

## 1. Goal

Answer the same question for three economies: is policy tight enough for the inflation pressure? The scoring, blocks (E, D, S, C, P), verdict grid and page layout stay the same. What changes per country is the data, the parameters, the institutional wording and the model estimates (u*, r*, pressure weights, cost-push multiplier).

Out of scope for now: a page comparing countries side by side, and any countries beyond these three.

## 2. How Fiscal Space does it, and what we copy

Fiscal Space (`../uk-fiscal`) builds a **separate edition for each country** from the same code:

- `src/country.ts` holds one object per country with every country-specific word and setting (agency names, currency, time zone, financial year, measure names, feature flags such as `realCurves`). The rest of the code reads `C.<field>`. Where only a sentence differs, `local(ukText, auText)` keeps both versions next to each other.
- The edition is chosen at build time (`vite --mode au`). The UK edition is served at the site root and Australia at `au/`. Data goes to separate folders (`public/data`, `public-au/data`) and Python code (`pipeline/`, `pipeline/au/`), and the workflow runs `refresh --country au`.
- `EditionSwitch` (App.tsx:116) is a pill group (`.edition-switch`, styles.css:69–73) in the brand block under the wordmark. Each country is a link to the other edition that keeps the current page (`?page=…&section=…&view=…`). The current country has `aria-current="page"` and a filled pill. The group is hidden when the header shrinks on scroll.

**We copy:** one edition per country, UK at the root with `au/` and `us/` beneath it, a country settings file that the code reads, and a pill switch in the same place with the same behaviour. This dashboard has separate HTML files rather than query parameters, so "keep the current page" means linking to the same file name in the other edition (`drivers.html` → `au/drivers.html`).

**We change:** the pill uses colour tokens, not a hard-coded `#fff`, so it works in dark mode (Fiscal Space has no dark mode). Its active colour is teal, because the pill is chrome. Tab order: **UK · Australia · US**.

## 3. Architecture changes

### 3.1 Country settings (`config/<country>/country.yaml`)

This replaces the UK wording that is currently hard-coded. Grep finds UK-specific strings or series IDs in `render.py`, `stance.py`, `policy_path.py`, `build.py`, `config.py`, `rstar.py`, `trend_cycle.py` and `decomposition.py`. They include `D7G7` and `IUDBEDR` in `build.assess`/`render`, `Europe/London` in `build.run`, `BLOCK_EXPLAIN` text, "A GUIDE TO UK MONETARY POLICY", "Bank Rate", "MPC", "MPR" and "gilt". Fields:

```yaml
id: au
name: Australia            # tab label
adjective: Australian
tagline: A GUIDE TO AUSTRALIAN MONETARY POLICY
central_bank: Reserve Bank of Australia
committee: Monetary Policy Board       # MPC / FOMC
committee_short: the Board
policy_rate_name: cash rate target
forecast_doc: Statement on Monetary Policy   # MPR / SEP
forecast_short: SMP
currency_name: Australian dollar
time_zone: Australia/Sydney
target: {measure: CPI, point: 2.5, band: [2, 3]}   # UK {CPI, 2.0}; US {PCE, 2.0}
headline_series: <id>      # replaces D7G7 (cost-push state, context)
policy_rate_series: <id>   # replaces IUDBEDR
bond_word: bond            # gilt / Treasury
```

`config.py` gains `Config.country`. `BLOCK_TITLES` and `BLOCK_EXPLAIN` stay in code but take `{target}` and `{currency}` placeholders, so the UK text comes out unchanged.

### 3.2 Folder layout

```
config/{uk,au,us}/   indicators.yaml weights.yaml nairu.yaml rstar.yaml charts.yaml country.yaml
manual/{uk,au,us}/   one CSV per type, same schema in every country (the UK names mpc_dates.csv and mpr.csv are kept for every country)
analysis/results/{uk,au,us}/
src/monetary_space/fetch/   add abs.py, rba.py; add US scrapers to fred.py or a new fed.py
store (data branch): {uk,au,us}/vintages/YYYY-MM-DD.parquet, {uk,au,us}/fetch_log.csv
site/  index.html …   site/au/ …   site/us/ …
```

Sources that more than one country uses (Brent from FRED, the OECD leading indicators) are listed in each country's config. Their fetches are cached once per run so they are not downloaded twice.

**Store migration** (built). The next build moves the existing UK vintages and `fetch_log.csv` into `uk/` (`store.migrate_to_country`), and the workflow's `git add -A` commits the move to the data branch. Release dates are worked out from the fetch log, so the log moves whole; a test checks this.

### 3.3 Build and workflow

- `python -m monetary_space build --country uk|au|us|all` (built; `all` is the default). Each country builds into its own subfolder. If one country throws an error, its edition is rebuilt from its last vintage (`--no-fetch`). If that also fails, the other editions still build, then the run fails. Pages deploys the whole site at once, so failing the run keeps the live site's last good pages for every edition; a "temporarily unavailable" page would have replaced a working one. A failed *source* still never stops the build.
- **Scheduling.** `scripts/gate.py` currently checks for UK times only. It becomes a table of slots, each tied to a country's own time zone:
  - UK: 07:10 and 12:15 on MPC days (unchanged).
  - US: 08:45 ET for data, and 14:15 ET on FOMC days (statement plus SEP).
  - AU: 11:45 AEST/AEDT for ABS releases, and 14:45 on Board decision days.

  Every slot builds every country. This is simple, costs a few minutes of runner time, and improves the release-date resolution for all three.
- `estimate.yml` runs the analysis scripts once per country.

### 3.4 Switch component

Add `EDITIONS` and a `switch(current, page)` helper to `render.py`, placed in the `site-header` brand block under the wordmark. A country appears in the switch only once its edition passes its acceptance tests (section 6). Until then the UK page looks exactly as it does today.

## 4. Country content

Every country keeps **≤14 scored indicators**, the same four pressure blocks, and the rule that a positive z is inflationary. The indicators **do not have to match across countries** (decided). Each list picks the series that drive inflation in that economy. Energy is the clearest example: UK gas, US oil and natural gas, Australian oil and wholesale electricity. Ids are shared where the concept is the same (`unemployment`, `ulc`, `brent` …) and differ where it is not (`gas`, `electricity`). The page is generated from config, so it does not need the same slots in each country. Tests check each country's own list.

### 4.1 United States (first: almost all of it is on FRED, and the key is already set up)

| Block | Indicator | Series (FRED unless noted) |
|---|---|---|
| E | Firms' expectations | Atlanta Fed Business Inflation Expectations, 1y (*confirm* FRED availability) |
| E | Household expectations | Michigan 1y (`MICH`); NY Fed SCE 3y as an alternative |
| E | Market inflation compensation | 5y5y forward (`T5YIFR`) |
| D | Unemployment vs u* | `UNRATE` |
| D | Vacancies per unemployed | `JTSJOL` / `UNEMPLOY` |
| D | Payrolls | `PAYEMS` |
| D | GDP | `GDPC1` (quarterly; there is no monthly GDP) |
| D | Capacity | Capacity utilisation `TCU` |
| S | Unit labour costs | `ULCNFB` |
| S | Productivity | `OPHNFB` |
| C | Oil | Brent `DCOILBRENTEU` (shared); oil reaches US prices mainly through gasoline |
| C | Natural gas | Henry Hub `DHHNGSP`; gas is the largest fuel for US power, so it feeds electricity and utility-gas prices |
| C | Exchange rate | Broad dollar index `DTWEXBGS`, sign reversed |
| C | Import prices | `IR` (ex-fuel; *confirm*) |

- **Target and headline** (decided). The dashboard scores against what the Fed targets: 2% headline PCE inflation (`PCEPI`). Core PCE (`PCEPILFE`) and CPI are shown as context.
- **Decisions and projections.** Scrape the FOMC calendar, statements (vote, dissents, target range) and the SEP medians for PCE inflation one and two years ahead from federalreserve.gov. The SEP comes out quarterly (Mar/Jun/Sep/Dec), not with every meeting.
- **Policy rate.** Use the midpoint of the target range (`DFEDTARU`/`DFEDTARL`). `EFFR` is shown as context.
- **r\*.** Use the same three methods as the UK suite:
  - trend-cycle;
  - a survey measure, standing in for MaPS: the NY Fed Survey of Market Expectations longer-run fed funds rate (*confirm* how long the series runs). The SEP longer-run median is shown as a cross-check;
  - our repaired HLW.

  The NY Fed's own published HLW is shown **as a cross-check only**, because you want r* estimated, not taken from someone else.
- **Weights.** Bernanke–Blanchard was built on US data, so the estimated weights are close to a replication of the original paper. The Shapiro supply/demand split also comes from the US: use the SF Fed's published series or replicate it on PCE components.

### 4.2 Australia (second: needs new fetchers)

**Sources:**
- the ABS Data API (SDMX, `data.api.abs.gov.au`, *confirm* the current host);
- RBA statistical tables as CSV. The RBA parsing in `../uk-fiscal/pipeline/au/rba.py` can be reused.

| Block | Indicator | Series |
|---|---|---|
| E | Firms' expectations | NAB survey price expectations (via RBA G3 if present; *confirm*) |
| E | Household expectations | Melbourne Institute consumer 1y (RBA G3; *confirm* licence) |
| E | Market inflation compensation | 10y breakeven (RBA G3, or F2 nominal minus indexed) |
| D | Unemployment vs u* | ABS Labour Force (6202), monthly |
| D | Vacancies per unemployed | ABS Job Vacancies (6354), quarterly |
| D | Payrolls | ABS payroll jobs |
| D | GDP | ABS National Accounts (5206), quarterly |
| D | Capacity | NAB capacity utilisation (*confirm* public source) |
| S | Unit labour costs | ABS nominal ULC, non-farm (5206) |
| S | Productivity | GDP per hour worked (5206) |
| C | Oil | Brent (shared); reaches prices through automotive fuel |
| C | Electricity | AEMO National Electricity Market wholesale price, volume-weighted across regions (east-coast gas feeds into it). Electricity has been the big energy driver of Australian CPI. *Confirm* the AEMO aggregated-price download |
| C | Exchange rate | Trade-weighted index (RBA F11), sign reversed |
| C | Import prices | ABS International Trade Price Indexes (6457) |

- **Target and headline** (decided). Score against what the RBA targets: headline CPI at the 2.5% midpoint of the 2–3% band. Show the band on charts and trimmed-mean CPI as context. Government electricity rebates moved headline CPI in 2023–26, so the electricity tooltip says so. The ABS switched to a complete monthly CPI in late 2025 (*confirm*), so the monthly series is short. σ needs ≥10 years before 2020, so it comes from the quarterly CPI history.
- **Decisions and projections.** Scrape the Monetary Policy Board calendar (8 meetings a year), decisions and published vote counts (*confirm* format) from rba.gov.au. Take headline and trimmed-mean CPI forecasts from the SMP forecast table (Feb/May/Aug/Nov).
- **r\*.**
  - Trend-cycle and repaired HLW run as in the UK. HLW may hit the IS-slope bound here as well, and the suite already drops it automatically when that happens.
  - Survey measure (decided): **market economists'** long-run cash-rate expectations take the place of MaPS. *Confirm* a free source; the candidates are any long-horizon cash-rate question in a published economists' survey, and news-reported polls (Reuters, Bloomberg). If the only source is press reports, keep it as a hand-entered `manual/au/rstar_survey.csv` with each row cited and marked `# confirm`. The economists' nominal rates are converted to real with the same deflator as the stance. The RBA's own published range is shown as a cross-check only.
- **u\*.** The filter's wage equation uses the Wage Price Index (ABS 6345) instead of AWE.

### 4.3 Shared work for each new country

Each of the steps below is a separate commit, in this order:

1. Fetchers, with parser tests on saved fixtures.
2. `indicators.yaml` with benchmark and σ for each indicator. Config values are marked `# confirm` with a cited source.
3. Scrapers for decisions and projections, plus seed CSVs in `manual/<country>/`.
4. u* filter (`nairu.yaml`), with a sensitivity table in the README. The published NAIRU (CBO for the US, RBA for Australia) is shown for comparison only and **not tuned towards**.
5. r* suite.
6. Bernanke–Blanchard estimated weights and the state-dependent local-projection cost-push multiplier. `cpi_threshold` is set per country: the UK's 3.1 is a BoE staff number and does not carry over.
7. Context charts and the policy-path chart.
8. Wording review in `country.yaml`.

## 5. Order of work

| Phase | Work | Done when |
|---|---|---|
| 0 ✓ | Restructure so the UK runs through the country layer: `country.yaml`, folders, store migration, `--country`, gate table, switch helper (hidden) | Done 2026-10-26. UK pages identical to the previous build from the same vintage apart from the build time, the switch CSS and three file paths in notes (`config/uk/…`, `manual/uk/…`); 92 tests pass |
| 1 (in progress) | US edition, steps 1–8 | Built and published 2026-10-26 at `us/` (switch shows UK · US): fetchers, indicators, SEP/FOMC scraper, r* suite, policy path, wording, tests (105 pass). US u*: the UK filter is not identified on US data, so the FOMC longer-run median is used (owner, 2026-10-26). Open: Bernanke–Blanchard weights, cost-push LPs, decompositions, review of `confirm` items. Then switch shows UK · US |
| 2 (in progress) | Australia edition, steps 1–8 | Built 2026-10-26, unpublished at `au/`: RBA tables, ABS API, AEMO electricity, Board/SMP scraper, u* (filter identified), r* suite with the RBA survey of market economists, F17 policy path. Open as for the US: BB weights, cost-push LPs, decompositions. Then switch shows UK · Australia · US |
| 3 | Shared polish: dark-mode pill, scheduling check over a full week of releases, README and SPEC update, CLAUDE.md status | One week of scheduled builds with no edition falling back |

Phase 0 has no visible effect on the site and carries most of the risk, so it ships and runs for a few days before phase 1 starts.

**Still UK-specific after phase 0**, to be moved into config when the US edition needs it (phase 1): the policy-path chart (OIS series, "sterling OIS", SONIA note), the r* notes on the Stance working tab (gilt forward, Market Participants Survey), the decomposition notes (ONS categories, Bank Rate, sterling), the release-log note ("07:00 ONS releases"), the trading-partner CLI label, the MPC calendar scraper (`build.CALENDARS`) and the analysis scripts, which still write UK results only. The no-UK-words test (section 6) is what catches anything missed.

## 6. Tests and acceptance (per country)

- **Golden test** for all nine verdict cells, using fixtures for that country (the same test as the UK one, run once per country).
- **Parser tests** for every new source on saved fixtures. Live fetches never run in `pytest`.
- **Config validation:** at most 14 indicators, the sign is ±1, every config σ has a rationale, the weights sum to 1, and `country.yaml` has every field the templates use. A missing field fails the build, not the page.
- **No UK words outside the UK edition:** after rendering AU and US, check the HTML for "Bank Rate", "MPC", "MPR", "gilt", "ONS" and "sterling" (with an allow-list for the Brent/FRED attributions).
- **Switch:** every edition links to the same file name in every other edition, and the current edition has `aria-current`.
- **Falling back:** a test that makes one country's build fail, then checks that the other two editions and the deploy still complete.
- **Reproducibility:** every tooltip still gives x, b, σ, s, z, date and source, so each number can be recomputed by hand.

## 7. Decisions (2026-10-26)

1. **Target measure:** whatever each central bank targets. The Fed: 2% headline PCE. The RBA: headline CPI, 2.5% midpoint of the 2–3% band. The UK is unchanged (2% CPI).
2. **Stance deflator:** the central bank's own year-ahead inflation forecast in every country, for now.
   - US: SEP median PCE. The SEP is given by calendar year (Q4 on Q4), so the year-ahead figure is interpolated between this year's and next year's projections according to the date.
   - AU: SMP headline CPI. The SMP gives year-ended forecasts at half-year points, so the value one year ahead is read off or interpolated.

   The tooltip shows how the number is interpolated.
3. **Survey part of Australian r\*:** market economists (section 4.2).
4. **Market-implied policy path:** from each country's yield curve (section 7.1).
5. **Indicators:** country-specific where the drivers differ. Energy is chosen per country (section 4).
6. **Order and URLs:** no preference. The default is US first, then Australia, at `/us/` and `/au/`.

### 7.1 Policy path from the yield curve

The UK chart uses the Bank of England's OIS instantaneous forward curve (`OIS_FWD`), which is effectively a curve of expected Bank Rate. There is no free daily OIS curve for the US or Australia, so the path comes from government-bond forward rates instead:

| | Short end (to 1 year) | 1 year onward | Frequency |
|---|---|---|---|
| US | Treasury bill and constant-maturity yields 1m, 3m, 6m, 1y (FRED `DGS1MO`…`DGS1`), turned into forwards | Fed staff fitted curve (Gürkaynak–Sack–Wright, `feds200628.csv`), instantaneous forwards worked out from the published Svensson parameters | daily |
| AU | RBA F1 overnight indexed swaps 1m, 3m, 6m (*confirm* table columns) | RBA F17 zero-coupon forward rates | F1 daily; F17 monthly, so the long end may be up to five weeks old (the chart says so) |

Bond forwards are not the same thing as OIS forwards:
- They carry a **term premium**. The chart would show it unadjusted and say so. For the US, the NY Fed's ACM term-premium estimates could take it out later, as an option.
- Bill yields can sit below the policy rate (**convenience yield**). The gap between the short end and the policy rate in the past month is shown in the tooltip, not silently removed.

The chart labels the line "implied by the government bond forward curve" rather than "OIS". The stance never uses this path (as in the UK).
