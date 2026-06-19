# CLAUDE.md — `bosc.hydrology.connectors`

Live public-data connectors (USGS NWIS, NOAA Atlas-14, EPA ECHO, USDA SSURGO/SDA, County/City
GIS, FEMA NFHL, ORC, LSC). Defers to the root [`CLAUDE.md`](../../../../CLAUDE.md).

- **GIS is schema-driven, not jurisdiction-hardcoded (#237).** `allen_gis.py` (parcel/CAMA)
  and `lima_gis.py` (zoning + floodzone) read their ArcGIS **field names + encodings** from the
  active site's `GisParcelSchema`/`GisZoningSchema`/`GisFloodSchema`
  (`bosc.connectors.gis_schema`), carried on `SiteProfile.gis_parcel`/`gis_zoning`/`gis_flood`
  (the *instances* live in `bosc.sites`). A new jurisdiction is config — register a schema; do
  **not** copy a connector or hardcode a field. A `None` schema makes the connector/CLI refuse
  cleanly (no fabricated cross-jurisdiction query). The endpoint URL is the per-site
  `parcels_url`/`zoning_url`/`floodzone_url`. The FEMA NFHL is the *shared national* flood
  field-map (`NATIONAL_NFHL_FLOOD_SCHEMA`), so any US site's floodzone is one connector.

- **A connector is a pure sync `fn(..., settings) -> pydantic`.** Keep the network
  call inside the `fetch` callable you hand to `_cache.cached_get` — never call
  `httpx` directly past the cache, and never read `os.environ` (use `settings`).
- **`cached_get` resolves: fresh on-disk cache → committed fixture (offline) → live
  fetch.** So tests never hit the network. A fresh connector/key needs a committed
  fixture under [`tests/fixtures/hydrology/<connector>/<key>.json`](../../../../tests/fixtures/hydrology/);
  an offline miss raises `HydroOfflineError` naming the exact key to record.
- **Select API columns/fields by name, never by index** (ECHO by **ObjectName**;
  same discipline for the GIS/portal connectors). Column order is not stable.
- **Never fabricate or backfill.** A `null` from the API stays `null`; a derived
  flag is tagged `derived`. The headline-count and caveat discipline in
  [`data/reference/echo/README.md`](../../../../data/reference/echo/README.md) is the
  model to follow.
- Committed reference datasets a connector regenerates live under
  `data/reference/<source>/` (each with a README naming its source and gaps); raw
  responses cache under the git-ignored `data/cache/`.
