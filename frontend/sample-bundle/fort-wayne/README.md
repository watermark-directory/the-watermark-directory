# `sample-bundle/fort-wayne/` — Fort Wayne offline fixture

A **minimal, trimmed snapshot** of the real Fort Wayne content bundle
(`bosc --site fort-wayne export` → `data/site/bundles/fort-wayne/`), committed so
`npm run build` and offline UI work need zero Python or Git-LFS. It's the sibling of
`../lima/` — the first non-Lima site fixture (Epic #741), keyed by registry slug like
every other site (`bundleFor("fort-wayne")` in `src/lib/bundle.ts`).

Production regenerates the real bundle (`bosc export` in `.github/workflows/pages.yml`),
so this fixture is the **offline/CI stand-in only** — a few authentic rows per feed (real
shapes, not mocks). Schemas are **not** duplicated here (the manifest keeps its schema refs;
the canonical `schemas/*.schema.json` live under `data/site/bundle/`).

## Strictly Fort Wayne's own record

This fixture is the proof of the per-site bundle scope (#762): every feed is **only Fort
Wayne's** data — none of Lima's Allen-County-Ohio corpus. Several feeds are empty because
the site is early and the platform doesn't fabricate:

- `timeline`, `meetings`, `people`, `exhibits`, `hydrology-scenarios`, `hypothesis-assessments`
  are **0 rows** — Fort Wayne has no committed dated civic record, curated people/exhibits,
  per-site scenarios, or assessed hypothesis cells yet. On-thesis opacity, not a trim artifact.
- `entities` / `relationships` are the corridor's own graph (no Allen-County townships, no
  JSMC defense node — those are Lima's).
- `catalog` carries Fort Wayne's `slug-scoped` datasets + genuinely `basin-shared` ones, never
  Lima's `lima-legacy` rows.
- `geo/campus` is the Project Zodiac assemblage (the Hatchworks parcels); `places` is the
  campus POI; `rsei` is Allen County **Indiana** (FIPS 18003).

`concepts` (the wiki glossary) and `network` (the basin synthesis) are network-global by
design and legitimately mention other sites — they are the same in every site's bundle.

## Refresh this fixture

After a contract change or new Fort Wayne data (run from the repo root):

```sh
bosc --site fort-wayne export --out /tmp/fw-bundle
# then re-trim /tmp/fw-bundle into this directory — a handful of rows per feed, dropping the
# generated schemas/ dir (catalog → ~6 rows, rsei.facilities → ~6, geo/campus → ~2 features).
```

The drift guard `tests/test_site_bundle.py::test_frontend_sample_bundle_tracks_the_export_contract`
(parametrized over every committed fixture) fails if this drifts from `bosc export`.
