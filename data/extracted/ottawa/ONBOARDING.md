# Onboarding — Ottawa (ottawa)

Living record for the Ottawa watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile (AEP Ohio IOU; standard path)
- [ ] **Data-center activity** — extracted permits/records + entity graph (corpus extraction; seed proposals via `bosc onboard --research`, #247)
- [~] **Per-jurisdiction GIS** — flood = shared national NFHL (wired). Putnam County self-hosts a **valid-cert, queryable ArcGIS** — `Parcels` (owner + values) **and** a `Land Use` CAMA layer (land/improvement/total value + soil type) — a strong wireable lead; no standalone zoning REST (village zoning is class-coded / map-only). See GIS discovery below. Schemas not committed yet (a reviewed follow-up).

## Same-river sibling of Findlay (#237) — the intra-tributary control

Ottawa and **Findlay** sit on the **same receiving river** (the Blanchard), ~40 river-mi apart — the
network's only *along-one-river* pair (every other comparison is across tributaries). This makes
Findlay↔Ottawa a clean control on watershed identity: same river chemistry/regime, two discharge
points. Both are **AEP Ohio** (PJM AEP zone), so the grid story is identical — the comparison
isolates the hydrology/siting variables. (Disambiguation confirmed: this is the **Village of
Ottawa, Putnam County** on the **Blanchard**, gage 04189260 — *not* Ottawa County / Port Clinton,
*not* the Ottawa River of Lima or Toledo.)

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/ottawa/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/ottawa/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/ottawa/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/ottawa/baseline.yaml |
| rsei | ok | reference/rsei/ottawa/inventory.yaml |
| consumer-energy | ok | reference/eia/ottawa/consumer-energy.yaml |
| grid-profile | ok | reference/eia/ottawa/grid-profile.yaml |

## GIS discovery (2026-06-19; schema-driven GIS, #237)

Putnam County **self-hosts** an ArcGIS Server (`putnamcountygis.com/arcgis/rest/services`, valid
TLS, `?f=json` queryable) — discovered via the county GIS hub (`new-pcohio.hub.arcgis.com`). Like
Williams/Lucas it carries owner **and** CAMA values; the `Land Use` layer adds soil type and the
full appraisal split. No standalone zoning FeatureServer (the village's zoning is class-coded /
map-only). Nothing is committed yet — registering the field-maps from the live `?f=json` is a
reviewed follow-up, not this discovery pass.

| layer | endpoint | finding | status |
|---|---|---|---|
| floodzone | FEMA NFHL (national, layer 28) | wired in the profile (`gis_flood`) | wired |
| parcels | `putnamcountygis.com/.../Parcels/Parcels/MapServer/0` (polygon) | `PIN`/`PARCELNUM`, `OWNER` + mailing address, `Class`, `SALEDATE`/`PURPRI`, `ACRESOWNED`, `LANDVALUE`, `BLDGVALUE` — owner **and** values on one layer | wireable lead |
| land use (CAMA) | `putnamcountygis.com/.../Land_Features/LandUseParcels/MapServer/0` (polygon) | full CAMA join: `PPClassCod` (use class), `PPAcres`, `PPLandValu`/`PPImprValu`/`PPTotalVal`, `PPOnCauv`, `PPSaleDate`/`ValidSale`, `SOIL_TYPE` | wireable lead |
| villages | `putnamcountygis.com/.../Boundaries/Villages/MapServer/0` | village boundaries (incl. Ottawa) | reference |
| zoning | — | no standalone zoning REST found (village zoning is parcel-class-coded / map-only) | `[open]` |

Follow-up (a research/issue lead): register Putnam County `gis_parcel` (the `Parcels` or
`LandUseParcels` field-map — owner + value, no join) from the live `?f=json`; accept zoning as
class-coded/map-only here (or locate a Village of Ottawa zoning layer).

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'ottawa' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
