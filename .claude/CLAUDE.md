# monetary-space — UK Monetary Policy Dashboard

Static, single-screen dashboard answering: is UK policy tight enough for the inflation pressure?
Full spec: `docs/SPEC.md` (authoritative; `original_prompt.md` is the untouched original).

## Architecture
Python build script: fetch → store (dated Parquet vintages on `data` branch) → score (pure functions) → render (one self-contained HTML, Observable Plot inline). GitHub Actions builds on a schedule; GitHub Pages hosts. No server.

- `config/indicators.yaml`, `config/weights.yaml` — every parameter lives here, never in code
- `manual/` — hand-maintained CSVs (r* table, MPR projections, u*, MPC dates/votes, fiscal events)
- `src/monetary_space/` — `fetch/` (one module per source), `store`, `score`, `render`
- `tests/` — unit tests on fixtures; golden test for all nine verdict cells

## Conventions
- Hard cap of 14 scored indicators. Positive z always means inflationary.
- Every on-screen number must be reproducible by hand from its tooltip (x, b, σ, s, z, date, source).
- A failed source keeps its last good value, marked stale; the build still completes.
- Colour = inflationary (orange) / disinflationary (blue) / neutral (grey) only. Never colour Stance. No red/green.
- Manual values pre-filled by Claude are marked `# confirm` with a cited source until the team reviews them.
- Secrets: `FRED_API_KEY` as a repo secret and in local `.env` (gitignored). Never commit or echo it.

## Automation
MPC calendar, decisions (vote, Bank Rate) and MPR central-projection CPI (1y/2y ahead) are scraped from bankofengland.co.uk (src/monetary_space/fetch/mpc.py) on every build and written to manual/*.csv by the weekly estimate job. Manual only: Känzig shock vintage, manual/rstar.csv.

## Look and feel
Match the Fiscal Space dashboard (../fiscal-space, editorial layer at the end of src/styles.css): #faf9f5 background, teal ink #153f46, Georgia serif wordmark only, uppercase teal eyebrows, sans lead sentence, headline strip between a 2px ink rule and 1px rules (no card boxes), numbered story sections, collapsible source lines. Teal is chrome only; data colour is copper (inflationary) / blue (disinflationary) / grey. Light and dark themes (fiscal-space has light only).

## Status
- Repo: github.com/patrickmschneider/monetary-space (public). Push over SSH (no gh CLI in use).
- Phase 1 (repo, workflow, Pages; config, fetchers, store, scoring for blocks A & B; plain score page) — built 2026-09-24
- Run locally: `pip install -e ".[test]"`, `pytest -q`, `python -m monetary_space build [--no-fetch]`
- ONS: old api.ons.gov.uk is retired; use www.ons.gov.uk{uri}/data. LFS/vacancy series are labelled by middle month; the parser re-stamps them on the end month.
- Latest MPR is July 2026 (BoE now publishes Feb/Apr/Jul/Nov). Apr 2026 MPR had scenarios only (Scenario B used). u* not stated since Feb 2026 (4.75).
- u* is estimated with a multivariate filter (u = u* + AR(2) gap; wage Phillips curve on the gap; config/nairu.yaml), not taken from the MPR; u* ≈ 4.9% in 2026Q2, ±0.5pp. A Phillips-curve-only version put u* above u for all of 2016–26, which the user rejected as unbelievable. Sensitivity table in README.
- Open for team: σ from full pre-2020 samples is large for services CPI (from 1989); config σ for payrolls, DMP, Agents marked confirm; IAS provider switched Ipsos→Savanta in 2026.
- Phase 2 (blocks C and D, verdict, policy path chart) — built 2026-09-24. r* (user wants it modelled, not team-set) is now a suite (analysis/rstar_suite.py, 2026-09-29, after a literature review): trend-cycle (DGGT-style) 0.40 + MaPS 0.35 + repaired HLW 0.25 (auto-excluded: IS slope at bound for the UK). Headline 1.0% real. The old single HLW gave −0.8% (artefact).
- Stance definition (owner, 2026-09-29): neutral = the rate at which policy neither stimulates nor restrains. Stance = Bank Rate (not the spec's 2y OIS) minus year-ahead expected inflation (MPR cpi_1y) vs r*; nominal neutral estimates converted with the same deflator (real gap = nominal gap). Owner's prior: policy is not strongly contractionary. Don't tune methods toward priors; present definitional choices instead. Gas = ONS SAP from 2018 (config σ); OECD euro-area CLI discontinued, DEU/FRA/ITA/ESP + USA weighted.
- Restructured 2026-09-29 (user request) around the Phillips curve: blocks E (expectations), D (demand), S (supply), C (cost-push) + P (policy stance). Two pressure weightings (config from literature review; estimated from UK Bernanke–Blanchard at the 2–3y horizon), cost-push state multiplier from state-dependent LPs. Analysis scripts in analysis/, re-estimated weekly (estimate.yml); results committed in analysis/results/. User wants to compare the two weightings and the two demand/supply splits before choosing.
- Phases 3–4 — see `docs/SPEC.md` §8
