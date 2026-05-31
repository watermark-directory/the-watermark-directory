# Periplus reference data (frozen import)

These files are **copied, unmodified, from the Periplus (`../gis`) repository at
its fork point** — the commit at which Project BOSC was spun out. They are kept
here as *independent, original-design research reference*, not as BOSC-produced
artifacts. Periplus is a separate GIS platform with a different goal; only raw
research data is imported (no platform code, schemas, or internal
representations).

| File | What it is |
|---|---|
| `defense-contractors.yaml` | Named local defense contractors / government-adjacent operators (Allen County). |
| `watch-items.geojson` | Watch-list features flagged during the Periplus investigation. |
| `corridor.geojson` | The North Cole Street corridor study area geometry. |
| `corridor-centerline.geojson` | Corridor centerline. |

Treat these as **external corroboration**: cross-check BOSC's own extractions
against them, but BOSC's `data/extracted/**` remains the system of record. Do not
edit these files in place — re-import from the frozen fork point if needed.
