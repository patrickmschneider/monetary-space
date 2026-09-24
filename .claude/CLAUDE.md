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

## Status
- Repo: github.com/patrickmschneider/monetary-space (public). Push over SSH (no gh CLI in use).
- Phase 1 (repo, workflow, Pages; config, fetchers, store, scoring for blocks A & B; plain score page) — not started
- Phases 2–4 — see `docs/SPEC.md` §8
