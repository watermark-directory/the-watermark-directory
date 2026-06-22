# CLAUDE.md — `bosc.site`

The site's **data tier**: turns the committed corpus into the typed **content bundle**
(`bosc export` → `data/site/bundle/`) that the Astro frontend (`frontend/`) reads at build
time. Defers to the root [`CLAUDE.md`](../../../CLAUDE.md).

- **`export.py` is the entry point** (`export_bundle`): loads the corpus once through the
  shared loaders (`load_corpus`, `build_timeline`, `build_entity_graph`, `load_people`,
  `load_pois`, …) + the per-section builders here, and writes versioned, schema-validated
  JSON feeds plus a `manifest.json` carrying a `CONTRACT_VERSION`. The contract (README,
  `schemas/`, `manifest.example.json`) is committed; the generated `manifest.json` + `feeds/`
  are regenerable and git-ignored.
- **The feed models live in `feeds.py`** — JSON Schemas are generated from them (serialization
  mode), so schema and code never drift. Add a feed by adding its Pydantic model there + a
  builder; never hand-write a schema.
- **Per-section builders** (`records`, `economics`, `candidates`, `documents`, `exhibits`,
  `gleif`, `graph`, `meetings`, `people`, `places`, `concepts`, `rsei`, `gismap`) each emit
  one or more typed feeds **from committed corpus data** — don't fabricate records or links.
- **`gismap.py`** lifts the committed `data/site/gis-findings.geojson` into typed per-layer
  `GeoFeatureCollection` feeds for the frontend's DeckGL map (`export_geo` /
  `export_watershed_geo` / `export_imagery_geo`); `merge_rsei_layer` / `merge_corridor_layer`
  fold the RSEI facility points + the frozen-Periplus corridor in first. Geometry is WGS84
  verbatim (display-only, no reprojection).
- **`objectstore.py`** backs the object-store CLI (serving real source bytes from R2), not the
  bundle.
- The legacy Python SSG (`build.py` / `render.py` / `nav` / `templates/` / `assets/`, the
  `bosc site build|serve` CLI, the generated `web/` + `site/` trees) was **removed at the
  parity cutover** — the Astro `frontend/` is now the sole presentation tier.
