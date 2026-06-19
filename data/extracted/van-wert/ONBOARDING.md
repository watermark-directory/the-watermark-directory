# Onboarding — Van Wert (van-wert)

Living record for the Van Wert watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

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
| corridor-ddf | ok | reference/hydrology/van-wert/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/van-wert/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/van-wert/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/van-wert/baseline.yaml |
| rsei | ok | reference/rsei/van-wert/inventory.yaml |
| consumer-energy | ok | reference/eia/van-wert/consumer-energy.yaml |
| grid-profile | ok | reference/eia/van-wert/grid-profile.yaml |

## GIS discovery (2026-06-19; schema-driven GIS, #237)

Endpoints probed against the schema-driven GIS connector. Like Fort Wayne (and unlike
Findlay's clean City zoning FeatureServer), Van Wert has **no cleanly-consumable queryable
district catalog**, so nothing is committed yet; flood is the shared national NFHL.

| layer | finding | status |
|---|---|---|
| floodzone | FEMA NFHL (national, layer 28) — wired in the profile (`gis_flood`) | wired |
| parcels (county) | Van Wert County PAT MapServer (`ags.bhamaps.com/.../VanWertOH/VanWertOH_PAT_Search/MapServer`, Bruce Harris & Assoc) exists but its **TLS certificate is expired** — `cached_get`/httpx can't consume it without disabling verification; parcels are otherwise distributed as Engineer's-office shapefiles + a Beacon-style auditor parcel app | `[open]` |
| zoning | no separate City of Van Wert zoning REST catalog found (small city; zoning appears map-only) | `[open]` |

Follow-up (a research/issue lead): re-probe the county PAT MapServer once its TLS cert is
renewed (then register a `GisParcelSchema` from the live field list), or fall back to the
Engineer's-office parcel shapefile; locate a Van Wert zoning layer (or accept map-only here).

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'van-wert' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
