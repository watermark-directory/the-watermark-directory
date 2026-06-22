# Onboarding — Greenville · Darke Co (greenville)

Living record for the Greenville · Darke Co watershed point (basin: great-miami), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [~] **Data-center activity** — self-research first pass run (#247, 2026-06-22). `[verified]` **zero** Greenville / Darke-County records in the corpus — a flat no-data finding, *not* evidence none is proposed. `facility=None`. `[open]` sweep target here is distinct: **greenfield farmland conversion** (Darke is a top-tier agricultural county, not an industrial mainstem), the basin-edge / ag end of the thesis. **Method note:** the Lima/Allen Bistrozzi land-assembly graph is **not** bridged in.
- [ ] **Per-jurisdiction GIS** — Darke County (FIPS 39037) parcels / City of Greenville zoning connector (the known lift). **Heed the same-name trap:** verify the situs is Darke County **OH** from a live `?f=json` sample before wiring any discovered service. Flood = national NFHL (wired).

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/greenville/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/greenville/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/greenville/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/greenville/baseline.yaml |
| rsei | skipped | input missing: [Errno 2] No such file or directory: '/Users/cparent/Code/goedelsoup/bosc/data/cache/rsei/v234/data_tables/elements.csv.gz' |
| consumer-energy | ok | reference/eia/greenville/consumer-energy.yaml |
| grid-profile | error | EIA-861 2024: no Short-Form ('861S') row for utility #0 in OH |

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [ ] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'greenville' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.

## Self-research (Phase 5; #247) — 2026-06-22

- [x] Self-research first pass reviewed (`bosc onboard greenville --research`; ~$0.8, 24 turns; 5 proposals in `data/research/onboard-greenville-…-2026-06-22/`). The **agricultural / basin-edge** node (Darke Co) — a deliberate contrast to the industrial mainstem nodes. Darke straddles a drainage divide: eastern Darke (Greenville Creek → Stillwater → Great Miami → Ohio R.) vs western Darke (→ Wabash → Mississippi); this site sits on the **Great Miami** reach. A **till-plain** county (not buried-valley) and likely a **rural electric co-op** utility — a third utility type for the network.
- `[verified]` **zero** Greenville/Darke-County records in the BOSC corpus as of 2026-06-22 — a flat no-data finding. The Greenville Creek / Stillwater **7Q10 is not yet committed** (the derived low-flow file remains Maumee-only), so the receiving-water screen can't run at-site.
- Proposals filed as sub-issues of **#482**: commit the Greenville Creek / Stillwater 7Q10; persist the per-discharger basin-screen artifact; run the Darke-County data-center / ag-land-conversion sweep; wire the Darke County GIS connector (situs-verified); resolve the skipped RSEI + grid-profile steps (co-op EIA-861).
