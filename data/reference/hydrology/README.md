# Hydrology reference parameters

Committed reference inputs for the water-balance / stormwater model
(`bosc.hydrology`). These are **published reference values / standing assumptions**,
not document-derived figures — each is consumed as a tagged hydrology input
(`assumption`/`reference`), distinct from live connector pulls (USGS, NOAA, ECHO)
which are cached, not committed here.

## Files

| File | What | Source |
|---|---|---|
| `cn-lookup.yaml` | SCS Curve Numbers by NLCD land-cover class × hydrologic soil group (AMC-II), plus the dry/wet AMC adjustment forms. | USDA NRCS TR-55 Table 2-2, mapped to NLCD 2021 classes (same mapping Periplus used). |
| `low-flow-7q10.yaml` | Cited 7Q10 (7-day, 10-year) low-flow statistics for the receiving waters. | As cited; the regulatory statistic used by `bosc.hydrology.lowflow`. |
| `sanitary-basis.yaml` | Sanitary-flow basis parameters for the loop. | Reference basis. |
| `maumee-tmdl-wla.yaml` | Individual NPDES total-phosphorus wasteload allocations (spring-season + daily) for the Lima-loop facilities. | Transcribed verbatim from the final Maumee Watershed Nutrient TMDL, Appendix 4 (`data/documents/maumee-tmdl/`); `source: document`. |
| `campus-floodzone.yaml` | Whether the recorded campus parcels sit in — or near — the FEMA Special Flood Hazard Area. | Spatial intersect of the Bistrozzi footprint with the FEMA DFIRM (panel 39003C) via the City of Lima GIS floodzone layer (`bosc floodzone --footprint`); `source: connector`. |
| `wwtp-floodzone.yaml` | FEMA flood exposure of the three county WWTP discharge points (point-in-polygon + 50/150/400 m buffers). | Facility coordinates from EPA ECHO (`data/reference/echo/`) tested against the FEMA DFIRM (panel 39003C); `source: connector`. ECHO coords are a proxy for the outfall. |
| `nasa-power-climatology.yaml` | Monthly + annual climate normals (corrected precip, temperature, humidity, wind, solar) at the Lima loop point — the long-run water-budget context for the design-storm analysis. | NASA POWER climatology point API (AWS Open Data `s3://nasa-power`), pulled via `bosc nasa-power --write`; `source: connector`. Climate *normals*, distinct from the NOAA Atlas-14 design-storm *extremes*. |
| `atlas14-corridor-ddf.yaml` | NOAA Atlas-14 depth-duration-frequency table (depths in inches) for the Cole St / Bluelick corridor centroid — the 60-min through 24-hr design storms at the 2/10/25/50/100-yr return periods. The regulatory design rainfall the OPC drainage scope must meet (`bosc drainage-audit`). | NOAA Atlas-14 PDS point query, pulled via `bosc drainage-audit --write-ddf`; `source: connector`. Design-storm *extremes*, distinct from the NASA POWER *normals*. |

## Caveats

These are inputs, not measurements. The `cn-lookup` AMC formulas note which form is
actually applied in code. The 7Q10 here is the **cited regulatory** value — the USGS
NWIS connector only sanity-checks it against observed minimum discharge, it does not
replace it.
