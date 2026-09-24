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
- Phase 2 (blocks C and D, verdict, policy path chart) — built 2026-09-24. r* is modelled (HLW-style, config/rstar.yaml) at the user's request, not a team-set range; it is fragile (−0.8% ± 1.1 by default, range −5.5 to −0.3 across calibrations) and currently makes the verdict "Room to ease". Gas = ONS SAP from 2018 (config σ); OECD euro-area CLI discontinued, DEU/FRA/ITA/ESP + USA weighted.
- Phases 3–4 — see `docs/SPEC.md` §8
