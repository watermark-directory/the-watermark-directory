# satellite imagery subsystem — design

*Design + roadmap. **P0 (scaffold) and P1 (STAC search) have shipped**; the
raster-materialization layer (P2+) is not built yet. The working code is the
`bosc.gis` package (`sites.py`, `imagery.py`) with `bosc imagery sites` /
`bosc imagery search`; steady-state guidance lives in
[`src/bosc/gis/CLAUDE.md`](../src/bosc/gis/CLAUDE.md). This file is the plan and the
record of decisions/deviations.*

**Shipped in P1 (two deviations from the original plan, by design):**
- **`_cache` was not physically lifted.** `civic` and `economics` already reuse
  `bosc.hydrology.connectors._cache.cached_get` cross-subsystem (a documented
  pattern), and ~26 files reference `HydroOfflineError`. So imagery follows that
  precedent — reuse `cached_get` with a GIS-specific cache root — and the lift to a
  neutral `bosc.connectors` is deferred to its own focused refactor.
- **Search needs no heavy deps.** A direct `httpx` POST to STAC `/search` (cached +
  fixtured) replaces `pystac-client` for P1, so **no `pystac-client`/`rasterio`/GDAL
  yet** — those arrive with P2 (asset signing + COG reads). Consequently the offline
  miss raises `HydroOfflineError` for now; `ImageryOfflineError` lands with the lift.

*Note: `bosc site build` mirrors every `.md` under `docs/` into the published site
([`build.py`](../src/bosc/site/build.py)). This is an internal engineering plan — keep
it out of a public deploy unless that's intended (deploy is manual `workflow_dispatch`,
so it never ships automatically).*

## Executive summary / decisions

Build a `bosc.gis.imagery` subsystem that, given a **tracking site** (an AOI drawn
from the GIS layer), searches a public STAC catalog, clips the matching scenes to the
AOI, and writes dated, provenance-stamped GeoTIFFs — a regenerable image time series
per site.

Locked decisions (chosen 2026-06-09):

- **Purpose — all three:** (1) land disturbance & water (NDVI disturbance, NDWI
  reservoir water-extent), (2) construction / site-change timeline (high-res
  before/after), (3) long historical baseline. *Not* map-context-only.
- **Sources — free & open only.** Public-domain (NAIP, Landsat) and open-license
  (Sentinel-2, attribution) so the imagery is **publishable as evidence**. No Planet /
  Maxar; Esri Wayback view-only at most.
- **Architecture — raster-capable.** STAC search + `rasterio` windowed-read of
  cloud-optimized GeoTIFFs (COGs) clipped to each site AOI → dated GeoTIFF + provenance
  sidecar. *Not* the raster-light "processing API returns a rendered PNG" path.

**Spine:** Microsoft **Planetary Computer** STAC fronts all three free/open sources
behind one access pattern (search → sign asset hrefs → windowed COG read), with
anonymous asset signing (no API key).

## 1. Goal & scope

A "tracking site" is a named area of interest — the data-center campus, the Amazon
warehouse parcel, the off-stream reservoir, the WWTP receivers — already present as
features in the GIS layer. The subsystem turns each AOI into a **dated image series**
that supports: change detection (date vs. date), vegetation/disturbance indices,
water-extent measurement, and a pre-development baseline. Everything is regenerable
from committed scene identifiers, which is what makes it defensible evidence.

Out of scope for the core: commercial near-daily imagery (Planet/Maxar), live tile
overlays as the *only* artifact, and in-browser raster processing.

## 2. Source review

One STAC endpoint, three collections — all free/open, all COG-backed:

| Goal | Collection (Planetary Computer id) | Resolution | Cadence / history | License |
|---|---|---|---|---|
| Land disturbance & water | `sentinel-2-l2a` | 10 m (multispectral) | ~5-day; 2015→ | ESA Copernicus, open (attribution) |
| Construction timeline | `naip` | 0.3–0.6 m | every ~2–3 yr (OH, leaf-on); ~2003→ | USDA, **US public domain** |
| Historical baseline | `landsat-c2-l2` | 30 m (15 m pan) | ~8-day combined; surface-reflectance archive 1982→ | USGS/NASA, **public domain** |

Considered and deferred (different access pattern and/or licensing):

| Source | Why deferred |
|---|---|
| USGS EarthExplorer historical aerials | Sub-meter single-frame archive back decades, but the M2M API needs a login and a different fetch flow — a later phase for the deep baseline. |
| Esri World Imagery **Wayback** | Dated high-res snapshots of the basemap the site map already uses; free to *view* but redistribution is license-restricted, so view-only supplement, never a committed artifact. |
| Planet PlanetScope (~3 m, near-daily) / Maxar (<0.5 m) | Excluded by the free/open decision — paid, and redistribution restricted, which conflicts with publishing imagery as evidence. |

**Why Planetary Computer as the spine:** it exposes Sentinel-2, NAIP, and Landsat
through one STAC API (`https://planetarycomputer.microsoft.com/api/stac/v1`) returning
COG asset hrefs, with anonymous SAS signing — so a single `search → sign → windowed
read` code path serves all three collections. Copernicus Data Space and the AWS open
buckets are equivalent fallbacks if PC access ever changes.

## 3. Architecture

The work splits cleanly along the existing connector cache contract:

### Layer A — STAC search (JSON; reuses the connector pattern)

A pure sync connector, exactly like the hydrology connectors:

```
search_scenes(aoi, collection, dt_range, max_cloud, *, settings) -> list[Scene]
```

- Network call wrapped in the `fetch` callable handed to `_cache.cached_get`
  (fresh on-disk cache → committed fixture → live). Tests never hit the network.
- A new collection/AOI needs a committed STAC-response fixture under
  `tests/fixtures/gis/imagery/<key>.json`; an offline miss raises an
  `ImageryOfflineError` naming the exact key to record (mirrors `HydroOfflineError`).
- STAC item fields are selected **by name** (`properties.datetime`,
  `eo:cloud_cover`, `assets.<band>.href`, …), never by index.

### Layer B — raster materialization (binary; separate path)

```
pull_capture(scene, aoi, bands, *, settings) -> Capture
```

- Sign the item's asset hrefs (Planetary Computer SAS), then `rasterio` windowed-read
  each band's COG restricted to the AOI window, reproject/clip to the AOI, and write a
  dated GeoTIFF.
- Output: `data/reference/imagery/<site>/<collection>/<acq-date>.tif` plus a provenance
  sidecar (see §4). Raw scene bytes cache under git-ignored `data/cache/`.
- Offline/tests read a **committed tiny fixture COG** (AOI-sized, a few KB) instead of
  the network — same "never trust the network in tests" discipline as the JSON layer.

This two-layer split keeps the JSON search inside the proven `cached_get` machinery
while giving the binary read its own committed-fixture path; the existing
[`geo.py`](../src/bosc/hydrology/geo.py) note that the subsystem stays "no rasterio"
is superseded *only* for this new package — `rasterio` is an imagery dependency, not a
hydrology one.

### Package placement

Promote a small **`bosc.gis`** package (`bosc.gis.imagery`, `bosc.gis.sites`) rather
than wedging satellites under `bosc.hydrology`. The shared `_cache` currently lives at
[`bosc.hydrology.connectors._cache`](../src/bosc/hydrology/connectors/_cache.py); lift
it to a common location (e.g. `bosc.connectors._cache`) and re-export from hydrology so
nothing breaks. The vector helpers in `geo.py` (`bbox_of`, area math) are also natural
candidates to migrate into `bosc.gis` over time.

### Data models (Pydantic, `bosc.models` style)

- `TrackingSite` — `id`, `name`, `geometry`, `bbox`, `notes`.
- `Scene` — STAC search result: `collection`, `scene_id` (granule/scene id),
  `acquired` (sensing datetime), `platform`, `cloud_cover`, `level`, `assets`
  (band → href), `bbox`. Verbatim from STAC properties; `None` for absent fields.
- `Capture` — the materialized artifact: `path`, `source`, `scene_id`, `collection`,
  `acq_date`, processing `level`, `aoi` + `crs`, `retrieved_at`, `sha256`.

### Sites come from the POI store

> **Superseded.** Tracking sites are now **watched POIs** in `data/poi/`, not a
> `gis-findings.geojson` layer. `bosc.gis.load_tracking_sites` / `get_site` read
> `bosc.poi.tracked_pois()` and project each to a `TrackingSite` (id = the POI slug,
> `bbox` = the AOI). The `track` flag in a `data/poi/<slug>.md` profile is the single
> source of truth. See [`poi-subsystem.md`](poi-subsystem.md) (decision #7). The original
> group-by-layer sketch is kept below for history.

A tracking site is just a feature with an AOI. Reuse
[`geo.bbox_of(path, pad_deg=...)`](../src/bosc/hydrology/geo.py) for the search
envelope and parse sites the way
[`wwtp_nodes_from_watch_items`](../src/bosc/hydrology/geo.py) parses receivers.
Two options for the source-of-truth (decide at P0):

- tag features `track: true` in the existing `data/site/gis-findings.geojson`, or
- add a dedicated `data/site/tracking-sites.geojson`.

Either way, the campus parcels / footprints / reservoir already mapped *are* the
sites — no new geometry authored, no fabrication.

## 4. Chain of custody (this is litigation evidence)

- **Artifacts** under `data/reference/imagery/<site>/...`, each with a per-folder
  `README.md` naming source and gaps — the discipline modeled by
  [`data/reference/echo/README.md`](../data/reference/echo/README.md).
- **Sidecar** (one per GeoTIFF) records: source + source URL, STAC collection,
  scene/granule id, **sensing datetime vs. retrieval timestamp** (kept distinct),
  processing level, cloud cover, AOI geometry + CRS, the exact clip/reproject applied,
  tool version, and the **sha256** of the GeoTIFF.
- Keep the **scene id** so anyone can re-pull the identical scene from the
  authoritative archive — the artifact is regenerable, not a one-off screenshot.
- Public-domain (NAIP, Landsat) + open (Sentinel-2) only, so the imagery is
  **publishable**. Never alter pixels beyond the logged clip/reproject; never fabricate
  or backfill a missing date.

## 5. Dependencies & tooling impact

New deps (the real cost of "raster-capable"): `pystac-client`, `planetary-computer`
(asset signing), `rasterio` (bundles GDAL in the wheel), `numpy` (indices).
`shapely` / `pyproj` are already present.

- **mypy strict:** `rasterio` is only partially typed — expect a per-module override
  in `pyproject.toml` (same treatment any GDAL-adjacent lib needs).
- **Tooling:** `rasterio`/`pystac-client` install from wheels under `uv`; no system
  GDAL required. Confirm the wheel resolves under the pinned Python (3.11) via `mise`.
- **CLI option discipline:** any `typer.Option` whose param is a `Path` must be typed
  `str` and converted in the body (ruff `B008`) — applies to `--out`, `--sites`.

## 6. CLI surface (`bosc imagery`)

- `bosc imagery sites` — list tracking sites + AOIs.
- `bosc imagery search <site> --collection sentinel-2-l2a --from … --to … --max-cloud …`
  — STAC search; print matching scenes.
- `bosc imagery pull <site> --collection … (--date … | --from/--to …) [--bands …]`
  — materialize clipped GeoTIFF(s) + sidecar.
- `bosc imagery timeline <site>` — build/refresh the dated series.
- `--index ndvi|ndwi` — compute a derived raster (tagged `derived`).

## 7. Testing / fixtures

- Commit a **STAC search JSON fixture** per (collection, AOI) key so `search_scenes`
  runs offline through `cached_get`.
- Commit a **tiny fixture COG** (AOI-sized) so `pull_capture` exercises the
  windowed-read → GeoTIFF → sidecar path offline.
- An offline miss raises `ImageryOfflineError` naming the missing key, so adding a new
  site/collection tells you exactly which fixture to record.
- `mise run check` (ruff + mypy strict + pytest) stays green with zero network.

## 8. Roadmap

Each phase is a shippable slice.

- **P0 — scaffold. ✅ done.** Created `bosc.gis`; added `gis_*` settings; defined
  `TrackingSite` + the sites source (group-by-layer over `gis-findings.geojson`).
  `_cache` lift + `ImageryOfflineError` deferred (see the deviations note up top).
- **P1 — search. ✅ done.** Sentinel-2 STAC search via `httpx` + `cached_get` +
  committed real fixture + `bosc imagery sites` / `bosc imagery search`. The
  "Data-center campus" site (10 Bistrozzi parcels, ~339 ac) resolves and returns
  scenes offline.
- **P2 — pull. ✅ done.** `rasterio` + `planetary-computer` (no `pystac-client` —
  signing only); sign assets → windowed COG clip to AOI → GeoTIFF + sidecar + sha256;
  committed fixture COG; `bosc imagery pull`. `ImageryOfflineError` added for the
  raster path (the `_cache` lift remains deferred).
- **P3 — NAIP + Landsat. ✅ done.** Same `pull` path, per-collection default asset
  (`raster._DEFAULT_ASSET`: sentinel-2→`visual`, naip→`image`, landsat→`red`).
  Real search + small COG fixtures for both; NAIP (0.3 m) pull-fixtures use a small
  sub-AOI. NAIP has no `eo:cloud_cover` (don't `--max-cloud` it). Gives the high-res
  before/after (NAIP) and the decadal baseline (Landsat).
- **P4 — analysis. ✅ done.** `bosc.gis.analysis.compute_index` clips the band COGs
  (shared `raster.clip_asset`) and computes **NDVI** (vegetation/disturbance) or **NDWI**
  (open water) → a `derived` float32 GeoTIFF + a sidecar with mean + **water fraction**.
  `bosc imagery index <site> --index ndvi|ndwi`. The campus reads NDVI ≈ 0.31 (vegetated),
  NDWI water-fraction 0 (no water). Wiring the NDWI water-extent series into the
  sequent-peak reservoir budget, and date-to-date change detection, await the off-stream
  reservoir becoming a tracked POI (a diff of two index rasters is a thin follow-on).
- **P5 — map. ✅ done.** The site GIS map ([`gismap.py`](../src/bosc/site/gismap.py))
  gains a curated ladder of **dated Esri *Wayback* aerials** (2014 → 2024, real release
  numbers) in the layer control — flip the AOI between years to watch the data-center
  land change. View-only (tiles load from Esri, no redistribution). EarthExplorer
  historical aerials (M2M login — a different access pattern) and a scrubbing timeline
  slider remain follow-ons.

## 9. Open decisions

- **Sites source — decided (P0):** group `gis-findings.geojson` features by `layer`
  (`settings.gis_tracking_layers`, default `["campus"]`). No new `track:` tag or
  separate file; geometry stays sourced from committed findings.
- **First sites in scope:** the **data-center campus** is live (layer `campus`). The
  **Amazon warehouse parcel** and **off-stream reservoir** still need committed
  geometry in `gis-findings.geojson` (pull the warehouse parcel via `bosc parcels`;
  add the reservoir footprint) before they can be tracked — not fabricated here.
- **`_cache` lift target:** still open — `bosc.connectors._cache` vs. `bosc.net._cache`.
  Deferred to its own refactor (P1 followed the civic/economics reuse precedent).

## Sources

- [Microsoft Planetary Computer — STAC API](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/)
- [Planetary Computer — data catalog (Sentinel-2 L2A, NAIP, Landsat C2 L2)](https://planetarycomputer.microsoft.com/catalog)
- [pystac-client docs](https://pystac-client.readthedocs.io/)
- [rasterio — windowed reads / COG](https://rasterio.readthedocs.io/en/stable/topics/windowed-rw.html)
- [USDA NAIP](https://naip-usdaonline.hub.arcgis.com/)
- [ESA Copernicus Sentinel-2](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2)
- [USGS Landsat Collection 2](https://www.usgs.gov/landsat-missions/landsat-collection-2)
- [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- [Esri World Imagery Wayback](https://livingatlas.arcgis.com/wayback/)
