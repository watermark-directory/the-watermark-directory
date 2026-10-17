# Onboarding — Wapakoneta (wapakoneta)

Living record for the Wapakoneta watershed point (basin: maumee), scaffolded by `watermark onboard`. Check items as you complete them; the site is **not** promoted (`web/packages/core/src/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [ ] **Data-center activity** — extracted permits/records + entity graph (corpus extraction; seed proposals via `watermark onboard --research`, #247)
- [ ] **Civic records** — per-site subdivisions registry + meeting minutes/agendas (feeds record; scaffolded empty, evidence-gated)
- [ ] **Per-jurisdiction GIS** — parcels/zoning connector (the known lift; see docs/onboarding.md)

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 5 README(s) |
| civic-registry | ok | reference/subdivisions/wapakoneta/subdivisions.yaml |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/wapakoneta/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | parcel geometry missing: reference/wapakoneta/bosc-parcels.geojson |
| climatology | ok | reference/hydrology/wapakoneta/nasa-power-climatology.yaml |
| basin-screen | ok | 10/130 dischargers screened (4 violations, 2 tight) |
| econ-baseline | ok | reference/economics/wapakoneta/baseline.yaml |
| rsei | ok | reference/rsei/wapakoneta/inventory.yaml |
| consumer-energy | ok | reference/eia/wapakoneta/consumer-energy.yaml |
| demand-pressure | skipped | no disclosed facility, or its IT load is entirely [open] |
| grid-profile | ok | reference/eia/wapakoneta/grid-profile.yaml |

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Civic registry: enumerate the county's meeting-holding bodies for 'wapakoneta' from a committed roster into data/reference/subdivisions/wapakoneta/subdivisions.yaml; run `watermark --site wapakoneta subdivisions discover` and fold confirmed platforms in BY HAND (discovery is read-only). An empty registry does not make record live.
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status: live + selectable: true for 'wapakoneta' in data/sites.yaml (the identity SSOT), then run `watermark sites sync` to regenerate the frontend registry. NOTHING under web/ is hand-edited to promote a site. Parity-gated; onboard never auto-promotes. Promotion is what publishes the site's inner pages at all — an un-promoted site serves only its landing page, however complete its bundle is.
