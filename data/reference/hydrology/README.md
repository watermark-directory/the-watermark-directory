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

## Caveats

These are inputs, not measurements. The `cn-lookup` AMC formulas note which form is
actually applied in code. The 7Q10 here is the **cited regulatory** value — the USGS
NWIS connector only sanity-checks it against observed minimum discharge, it does not
replace it.
