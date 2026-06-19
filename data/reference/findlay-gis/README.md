# Findlay GIS — committed reference data

City of Findlay (Hancock County, OH) GIS layers for the Findlay watershed point
(`bosc.sites` `findlay`). Schema-driven via the per-site `gis_*` field-maps (#237); see
[`docs/onboarding.md`](../../../docs/onboarding.md) and
[`src/bosc/connectors/gis_schema.py`](../../../src/bosc/connectors/gis_schema.py).

## `zoning-districts.yaml` — zoning-district catalog

- **Source:** City of Findlay GIS — ArcGIS Online hosted FeatureServer `FindlayZoning`
  (org `XMr9uonP553LyU3o`), layer 0. Pulled 2026-06-19; values verbatim from the service.
  `source_url`: <https://services6.arcgis.com/XMr9uonP553LyU3o/arcgis/rest/services/FindlayZoning/FeatureServer/0>
- **What it is:** the 15 named zoning districts of the City of Findlay, by `Zoning` label.

### Known gaps & caveats

- **Dissolved layer — `polygon_count` is 1 for every district.** The FeatureServer holds
  16 polygons total: one dissolved polygon per district plus one polygon with a null
  `Zoning` value (dropped). So `polygon_count: 1` means "one dissolved district polygon,"
  **not** "one parcel" — it is not a parcel/area measure. (Contrast Lima, whose layer carries
  many per-parcel polygons.)
- **Polygon-only — no parcel join.** The layer has no parcel-id field, so per-parcel zoning
  lookups (`zoning_for_parcel` / `bosc zoning --parcel`) are not supported for Findlay; the
  district catalog is the available read.
- **Parcels are `[open]`:** Hancock County publishes no ArcGIS-REST parcel layer
  (Beacon/Schneider only); `SiteProfile.gis_parcel` is `None`. A future substitute is the
  Ohio statewide parcel layer filtered to FIPS 39063.
- **Floodzone** is served by the shared national FEMA NFHL layer (no committed catalog: a
  national `1=1` catalog is not meaningful — flood is a spatial query against an identified
  footprint, which Findlay does not have yet).

### Regenerate

```sh
bosc --site findlay zoning --districts        # live; writes this file
```

Raw API responses cache under the git-ignored `data/cache/`; the offline replay fixture is
[`tests/fixtures/hydrology/findlay_gis/`](../../../tests/fixtures/hydrology/findlay_gis/).
