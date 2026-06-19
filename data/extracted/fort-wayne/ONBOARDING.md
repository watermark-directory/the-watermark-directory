# Onboarding — Fort Wayne (fort-wayne)

Living record for the Fort Wayne watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [ ] **Data-center activity** — extracted permits/records + entity graph (corpus extraction; seed proposals via `bosc onboard --research`, #247)
- [~] **Per-jurisdiction GIS** — flood = shared national NFHL (wired). Parcels/zoning `[open]` — see GIS discovery below; no clean queryable district catalog like Findlay's, so nothing committed yet

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/fort-wayne/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/fort-wayne/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/fort-wayne/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/fort-wayne/baseline.yaml |
| rsei | ok | reference/rsei/fort-wayne/inventory.yaml |
| consumer-energy | ok | reference/eia/fort-wayne/consumer-energy.yaml |
| grid-profile | ok | reference/eia/fort-wayne/grid-profile.yaml |

## GIS discovery (2026-06-19; schema-driven GIS, #237)

Endpoints probed against the schema-driven GIS connector. Unlike Findlay (a clean City zoning
FeatureServer → a committed district catalog), Fort Wayne has **no clean queryable
district-catalog layer**, so nothing is committed yet; flood is the shared national NFHL.

| layer | finding | status |
|---|---|---|
| floodzone | FEMA NFHL (national, layer 28) — wired in the profile (`gis_flood`) | wired |
| parcels (county) | Allen County IN — `gis1.acimap.us/.../Accela/Accela_Production/MapServer/8` is queryable but **geometry + PIN only** (no CAMA owner/value/acres) | `[open]` |
| parcels (city) | City of Fort Wayne — `gis.acimap.us/.../CFW/Parcels_With_Ownership_Information/MapServer/0` carries **owner + addresses + transfer date** but no value/acres/land-use, and fully-qualified field names (`sde.CurrentOwner.OwnerofRecord`, …). Partial CAMA; wiring deferred (no corpus parcels to query yet) | `[open]` |
| zoning | county `Reference_Zoning` is a tiled basemap (`layers:[]`, not queryable); no City zoning REST district catalog found (the city interactive map renders zoning but not as a clean catalog service) | `[open]` |

Follow-up (a research/issue lead): wire the City of Fort Wayne partial-CAMA parcel layer behind
a `GisParcelSchema` once there are corpus parcels to resolve; locate a queryable Fort Wayne
zoning layer (or accept that zoning is map-only here).

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'fort-wayne' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
