# Onboarding — Bryan (bryan)

Living record for the Bryan watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile (**municipal** — see grid note)
- [ ] **Data-center activity** — extracted permits/records + entity graph (corpus extraction; seed proposals via `bosc onboard --research`, #247)
- [~] **Per-jurisdiction GIS** — flood = shared national NFHL (wired). Williams County has a **full, valid-cert, queryable ArcGIS** — `ParcelsWeb` (owner **and** CAMA values on one layer, no join) **and** a `Zoning_OD` district catalog — the best-equipped small-county GIS in the network and genuinely wireable; see GIS discovery below. Schemas not committed yet (a reviewed follow-up), but this is a strong wire-ready candidate.

## Grid — the network's first MUNICIPAL utility (notable)

Bryan is served by **Bryan Municipal Utilities** (City of Bryan, EIA **#2439**), not an IOU — the
network's first municipal electric point. It files the **EIA-861 *short form* (861S)**, so it is
absent from the full Sales-to-Ultimate-Customers sheet the grid connector reads; this onboarding
added a **short-form fallback** + an **ownership-aware retail regulator** to `bosc.grid.eia861` /
`bosc.grid.utility`. The generated `grid-profile.yaml` correctly shows: ownership Municipal,
~160 GWh / 5,814 customers (861S 2024), avg price ~10.75¢/kWh; holding company = **American
Municipal Power (AMP)** member (no IOU parent); BA/RTO = PJM (AMP-scheduled); retail regulator =
**municipal home rule** (NOT PUCO rate-regulated). The PJM transmission **zone** is not yet pinned
(LMP is a placeholder) — a verification follow-up.

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/bryan/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/bryan/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/bryan/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/bryan/baseline.yaml |
| rsei | ok | reference/rsei/bryan/inventory.yaml |
| consumer-energy | ok | reference/eia/bryan/consumer-energy.yaml |
| grid-profile | ok | reference/eia/bryan/grid-profile.yaml |

## GIS discovery (2026-06-19; schema-driven GIS, #237)

Unlike Van Wert (county PAT MapServer with an **expired** TLS cert) and Fort Wayne (no clean
catalog), **Williams County publishes a full, valid-cert, queryable ArcGIS** across two AGOL orgs —
the county GIS opendata site (`services1.arcgis.com/D85sDZoJyameepNh`) and the county engineer
(`services8.arcgis.com/KG1citvUsI75VegT`). It is the best-equipped small-county GIS in the network:
the parcel layer carries owner **and** CAMA values together (no separate land-values join, unlike
Lucas AREIS). Nothing is committed yet — registering the field-maps from the live `?f=json` is a
reviewed follow-up, not this discovery pass.

| layer | endpoint | finding | status |
|---|---|---|---|
| floodzone | FEMA NFHL (national, layer 28) | wired in the profile (`gis_flood`) | wired |
| parcels (CAMA) | `D85sDZoJyameepNh/ParcelsWeb/FeatureServer/0` (`Parcels_WC`, polygon, 58 fields) | `p_ParcelID`, `p_OwnerName` + owner address, `p_PrimaryParcelUse`, `p_DeededAcres`, `p_Residential/Commercial/Agriculture*LandValue` + `p_*StructureValue`, `p_TotalValue`, `p_TaxingDistrict` — owner **and** values on one layer | wireable lead |
| parcels (engineer) | `KG1citvUsI75VegT/Williams_County_Parcels/FeatureServer/0` + `Auditor_Landcover/FeatureServer/0` | county-engineer parcels + auditor land-cover (alternate/derived source) | wireable lead |
| zoning | `D85sDZoJyameepNh/Zoning_OD/FeatureServer/0` (polygon; fields `Zoning`, `Updated_Zo`) | a parcel-area zoning catalog — directly registerable as a `GisZoningSchema` (polygon-only, like Findlay: district catalog, no parcel-id join) | wireable lead |
| taxing districts | `D85sDZoJyameepNh/TaxingDistricts/FeatureServer/0` | tax/school/fire/ambulance districts | reference |

Follow-up (a strong issue lead): register Williams County `gis_parcel` (`ParcelsWeb` `p_*` field-map —
the network's most complete single-layer parcel GIS, owner+value, no join) and `gis_zoning`
(`Zoning_OD`) from the live `?f=json` — Bryan is a strong candidate to be the network's second
fully-wired GIS after Lima.

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'bryan' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
