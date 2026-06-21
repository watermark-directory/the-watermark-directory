# Onboarding — Van Wert (van-wert)

Living record for the Van Wert watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [~] **Data-center activity** — self-research first pass run (`bosc onboard --research`, #247); the QTS $10B campus + Thor Equities threads are documented **secondhand** (Allen-County records), `[open]` at the parcel/entity level (#377/#378). See self-research summary below.
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

## Self-research (Phase 5; #247) — 2026-06-21

First automated-research pass (`bosc onboard --research`, 27 turns, $1.28, read-only over the corpus) →
`data/research/onboard-van-wert-van-wert-data-center-activity-r-2026-06-19/` (`findings.md` + `manifest.yaml`).

**Headline — the effluent-dominance end-member, with the screen hole exactly where it matters.** Van
Wert is the basin's small-stream end-member: a ~4.0 MGD plant (Van Wert WWTP, OH0027910) on a tiny
tributary (Town Creek). But **Town Creek has no cited or derived 7Q10 in the corpus**, so the very
discharger that motivates the site is **unscreened** (`bosc basin-network` status `no_receiving_water`,
dilution `null`) — the data gap *is* the finding, and any QTS/Thor load would land on the
least-buffered receiving water in the network. The "4.0 MGD" plant size is itself uncited in-corpus
(the #363 issue text only). Proposals #375 (ingest the OH0027910 NPDES permit + Town Creek 7Q10) and
#376 (re-screen once it lands) close this.

**Data-center activity — documented, but only secondhand through Allen-County records.** Unlike the
other comparators (no disclosed facility), Van Wert carries **two** proponent threads, both
`[verified]` as present in the corpus, both `[open]` at the parcel/entity level:

- **QTS** — a **$10B Van Wert County campus**, up to 4,500 construction jobs, in sworn-equivalent
  Select-Committee testimony (`qts-2026-06-03.pdf`; `select-committee-2026/witness-submissions.digest.yaml`).
  Proponent figures, not BOSC-verified; the closed-loop "no additional water" claim is design-specific
  (cf. `docs/legal/proponent-analysis.md`).
- **Thor Equities** — a developer "also doing a Van Wert data center; brought by AEP," a 1-yr LOI at
  $50K/ac on Perry Industrial Park (PAAC board minutes, `paac-board-minutes.minutes.yaml`).
- `[open]`: whether QTS and Thor name the **same** project, and the whole thread at the parcel level —
  there are **zero Van-Wert-jurisdiction primary documents** in the ingested corpus (proposals #377/#378).

**The economic shape is the basin's most extreme.** Van Wert County: manufacturing LQ **3.14**,
information LQ **0.09** — the strongest "load onto a shrinking industrial base, not jobs" signature in
the network (cf. the cross-site scorecard on `/directory/basin`).

**Serving utility — VERIFIED (the "Bryan trap" checked & cleared).** Van Wert is **not** a municipal:
the grid connector's EIA-861S short-form fallback found no City of Van Wert filer, and the EIA-861
service-territory file + PUCO certified-territory confirm **AEP Ohio (Ohio Power Co #14006, PJM AEP
zone)** distributes (`data/reference/eia/van-wert/grid-profile.yaml`). The profile's
`eia861_utility_number=14006` + the PUCO/PJM grid path are correct — the same Ohio/AEP/PUCO axis as
Lima and Findlay, so the cross-state connector axis is not re-exercised.

**Proposals — all 5 distilled proposals are filed as sub-issues of #363:** #375 (ingest the OH0027910
NPDES permit + Town Creek 7Q10), #376 (re-screen once the 7Q10 lands), #377 (obtain a primary QTS
instrument), #378 (resolve QTS-vs-Thor), #379 (disambiguate OH0135569 vs OH0027910). The GIS lift
(the Van Wert County PAT MapServer on `ags.bhamaps.com` with an expired TLS cert) is the shared-host
case tracked under GIS discovery above — re-probe once the cert is renewed; **don't weaken TLS** for it.

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [x] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/) — see self-research summary above; 5 proposals filed as sub-issues of #363 (#375–379).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'van-wert' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
