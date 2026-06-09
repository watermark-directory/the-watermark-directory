# CLAUDE.md — `bosc.poi`

The point-of-interest (place) research store. Defers to the root
[`CLAUDE.md`](../../../CLAUDE.md). Design + roadmap:
[`docs/poi-subsystem.md`](../../../docs/poi-subsystem.md).

- **A POI is the place peer of a person profile.** Same shape as `bosc.people`:
  `data/poi/<slug>.md` = a `---` YAML frontmatter header (validated by
  `POIFrontmatter`, `extra="forbid"`) + hand-written markdown body. `depth`/`kind` are
  `Literal` ladders — an out-of-vocabulary value is a loud validation error.
- **Depth is a cost gate** (`mention → located → characterized → watched`), human-set
  except the mechanical `mention → located` (geocode) advance. `watched` +
  `track.enabled` is the **single source of truth** for what gets imagery —
  `tracked_pois()` is the view `bosc.gis` consumes (replacing `gis_tracking_layers`).
- **Identity = the Allen County parcel number** where one exists (the dedup anchor);
  composites group member POIs/parcels by hand via `members`. Atomic resolution merges
  *within* a level; never auto-merge a parcel with the composite that contains it.
- **Chain of custody:** every POI carries `citations` (a POI with none is not evidence);
  geometry is `location.method`/`confidence`/`asof`-tagged, derived from a cited source,
  **never fabricated**. The `surface_forms` list is the dedup audit trail (record *why*
  aliases unified). Geocoding (P2) caches raw responses under git-ignored `data/cache/`.
- **`discover` (built):** `discover.py` scans the committed corpus text →
  `POICandidate`s (parcel ids + addresses) with citations + a store-`covered` flag.
  Read-only worklist; the uncovered parcel-ids are the leads. Its parcel regex mirrors
  `allen_gis._PARCEL_ID_RE` — a test cross-checks the two so they can't drift.
- **Not built yet:** `resolve` (the parcel-anchored funnel + merge) and the Census
  Geocoder / `parcel_at_point` / GNIS connectors. Promotion of a candidate to a curated
  `data/poi/` profile is a human step.
