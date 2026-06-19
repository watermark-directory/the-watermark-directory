# Onboarding — Findlay (findlay)

Living record for the Findlay watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [ ] **Data-center activity** — extracted permits/records + entity graph (corpus extraction; seed proposals via `bosc onboard --research`, #247)
- [x] **Per-jurisdiction GIS** — schema-driven connector wired (#237 / PR #348); zoning-district catalog committed (`reference/findlay-gis/`). Parcels `[open]` (Hancock publishes no ArcGIS-REST layer); floodzone = shared national FEMA NFHL (spatial — pending a site footprint)

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/findlay/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/findlay/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/findlay/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/findlay/baseline.yaml |
| rsei | ok | reference/rsei/findlay/inventory.yaml |
| consumer-energy | ok | reference/eia/findlay/consumer-energy.yaml |
| grid-profile | ok | reference/eia/findlay/grid-profile.yaml |

## GIS pulls (manual; not part of `bosc onboard`)

| layer | status | output |
|---|---|---|
| zoning catalog | ok (2026-06-19) | reference/findlay-gis/zoning-districts.yaml — 15 districts (dissolved layer, 1 polygon each) |
| parcels | `[open]` | Hancock County publishes no ArcGIS-REST parcel layer (Beacon/Schneider only) |
| floodzone | n/a | shared national FEMA NFHL — spatial query; needs an identified site footprint |

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [x] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md). Schema-driven (#237); Findlay zoning field-map registered + catalog committed; parcels `[open]`.
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'findlay' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
