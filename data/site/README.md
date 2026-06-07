# Site configuration

Committed configuration consumed by the site generator (`bosc.site`) when it stages
the browsable MkDocs tree. This is **input config**, not generated output — the
generated `web/` and `site/` trees are git-ignored and regenerable.

## Files

| File | What |
|---|---|
| `exhibits.yaml` | The curated **Exhibits** allowlist — which source PDFs (and page-range slices of large bundles) get published on the site. Edit here to add/remove an exhibit; page-range slices mean a full bundle is never republished wholesale. |
| `gis-findings.geojson` | The **GIS findings map** layers (WGS84): the campus footprint, the JSMC / Lima Army Tank Plant land, the nearby FEMA floodplain/floodway, and the `rsei` layer — Allen County RSEI toxic-release facility points sized by Score (a toggleable overlay, off by default). Copied to the site as an asset and drawn by `gis-map.md` (Leaflet). Corridor layers are regenerated from the county/FEMA GIS (server-generalized); the `rsei` points merge in from the committed `data/reference/rsei/inventory.yaml` via `bosc rsei --map`. |

See [`data/README.md`](../README.md) (Publishing) for the build/serve/deploy flow.
