# Ohio principal streams & drainage areas (ODNR Division of Water)

`principal-streams-and-drainage-areas.pdf` — a statewide map of Ohio's principal streams and
their drainage basins, used here as a **basin-distribution orientation + corroboration** reference
for the network's `basin` axis (`watermark.sites` / `web/src/lib/sites.ts`). It is **not** a
quantitative data source.

## Source

- **Publisher:** State of Ohio, Department of Natural Resources, **Division of Water** —
  "DIVISION OF WATER · PRINCIPAL STREAMS AND THEIR DRAINAGE AREAS."
- **Basis:** "based on the map of Ohio showing principal streams and their drainage areas by
  **C. E. Sherman, C. E., dated July, 1925**."
- **Edition:** **Reprinted 1999** (legend credits Bob Taft, Governor; Samuel W. Speck, Director).
- **Rights:** Ohio state-government work — public domain.
- **As-received filename:** `ohio-watershed-catchments.pdf` (renamed to a canonical name here;
  this is `data/reference/`, not the chain-of-custody `data/documents/` tree).

## What it shows

- Drainage **basins enclosed by red lines**; **drainage areas in square miles** as red figures
  (some are *areas above an indicated gage point*, marked by arrows — i.e. sub-basin, not always
  whole-basin totals).
- The Lake Erie ↔ Ohio River **continental divide** across the state, low-water elevations,
  navigation locks/dams, and reservoirs.
- Stated land area of Ohio: **41,249 mi²** (excluding Lake Erie and the Ohio River).

## How the network uses it (and how it must not)

The BOSC network is organized by **watershed point**; the `basin` axis today carries `maumee`,
`great-miami`, and `little-miami`, and this map is the menu + sanity check for that axis and for
expansion targeting. Reading it macro-scale:

| Basin (sink) | ~drainage area (map) | network |
|---|---|---|
| Maumee → Lake Erie | ~6,562 mi² | covered (8 sites) |
| Great Miami → Ohio R. | ~5,371 mi² | covered (Miami branch, #440) |
| Little Miami → Ohio R. | ~1,757 mi² | covered (Xenia) |
| **Scioto → Ohio R.** | ~6,517 mi² | **Scioto branch opened (Columbus / New Albany)** |
| Muskingum → Ohio R. | ~8,051 mi² (largest) | open |
| Sandusky → Lake Erie | ~1,420 mi² | open |
| Cuyahoga → Lake Erie | ~809 mi² | open |

**Discipline:** this is a **1925-vintage orientation map**. Do **not** transcribe its red sq-mi
figures into committed `SiteProfile`/reference data as `[verified]` — the authoritative sources for
the network's basin/gage/HUC values remain **USGS NWIS, NHD, and the HUC-8 catalog** (what the
connectors use). The map is `[reference]` context for *where the basins are and roughly how big*,
nothing finer.
