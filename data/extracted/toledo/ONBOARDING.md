# Onboarding — Toledo (toledo)

Living record for the Toledo watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [ ] **Data-center activity** — extracted permits/records + entity graph (corpus extraction; seed proposals via `bosc onboard --research`, #247)
- [~] **Per-jurisdiction GIS** — flood = shared national NFHL (wired). Lucas County AREIS is a **full, queryable ArcGIS REST** (parcels + CAMA + a zoning catalog) — the richest in the network and genuinely wireable; see GIS discovery below. Schemas not committed yet (a reviewed follow-up), but this is the strongest wire-ready candidate.

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/toledo/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/toledo/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/toledo/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/toledo/baseline.yaml |
| rsei | ok | reference/rsei/toledo/inventory.yaml |
| consumer-energy | ok | reference/eia/toledo/consumer-energy.yaml |
| grid-profile | ok | reference/eia/toledo/grid-profile.yaml |

## GIS discovery (2026-06-19; schema-driven GIS, #237)

Unlike Fort Wayne/Van Wert (no clean catalog) — and even richer than Findlay's single zoning
FeatureServer — **Lucas County's AREIS is a full, valid-cert, queryable ArcGIS REST**
(`lcaudgis.co.lucas.oh.us/gisaudserver/rest/services`). It is the strongest wire-ready GIS
in the network; nothing is committed yet (registering the `GisParcelSchema`/`GisZoningSchema`
from the live field lists is a reviewed follow-up, not this discovery pass).

| layer | endpoint | finding | status |
|---|---|---|---|
| floodzone | FEMA NFHL (national, layer 28) | wired in the profile (`gis_flood`) | wired |
| parcels (geometry) | `Tyler/Parcels/MapServer/0` | polygon + tax-map numbering (`AREA_NUM`/`BLOCK_NUM`/`LOT_NUM`/`ASSESSOR_NUM`) + `ACREAGE` — no owner/value CAMA on this layer | wireable lead |
| parcels (CAMA) | `AREIS_Web_Map_MIL1/MapServer` layers 3 (Parcels), 38 (Parcels Land Use Classification), 83 (Land Values) | CAMA land-use + land-values exposed as AREIS layers (join target for owner/value) | wireable lead |
| zoning | `LandUse_Zoning/Parcel_Zoning/MapServer` | a parcel-level zoning catalog — directly registerable as a `GisZoningSchema` | wireable lead |

Follow-up (a strong issue lead): register Lucas County `gis_parcel` (Tyler/Parcels + AREIS
land-use/land-values join) and `gis_zoning` (Parcel_Zoning) field-maps from the live
`?f=json` — Toledo is the best candidate to be the network's second fully-wired GIS after Lima.

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'toledo' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
