# Onboarding — Fort Wayne (fort-wayne)

Living record for the Fort Wayne watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile
- [~] **Data-center activity** — self-research first pass run (#247); the inverse of every other point — a **confirmed** real-world facility (registry codename `GCP`) but **zero primary corpus documents** for it (`facility=None`). Open discovery: #360. See self-research summary below.
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

## Self-research (Phase 5; #247) — 2026-06-21

First automated-research pass (`bosc onboard --research`, 35 turns, $1.38, read-only over the corpus)
→ `data/research/onboard-fort-wayne-fort-wayne-data-center-activi-2026-06-19/` (`findings.md` +
`manifest.yaml`).

**Headline — the basin's largest discharger, the network's only confirmed data-center facility, and
the cross-state test, all at once.** Fort Wayne is the first **out-of-state** point (Allen County,
**Indiana**, FIPS 18003 — *not* Lima's Allen County, OH 39003; the cross-state trap the per-site axis
exists to catch). It carries the basin's **largest POTW** — Fort Wayne WWTP (IN0032191, **74 MGD ≈
114 cfs**) discharging to the Maumee at the headwaters under an active "Effluent – Monthly Average
Limit" ECHO flag (1 informal enforcement).

**The screen verdict — RESOLVED (#358/#359, 2026-06-23).** See the reviewed characterization
[`wwtp-receiving-water.md`](wwtp-receiving-water.md). Two corrections to
the hypothesis above: (1) the basin-screen **never** used the Waterville proxy for this plant — its
primary receiver is **Baldwin Ditch** (ungaged), so it is correctly left **unscreened** (omit-don't-
guess), and (2) the "~45 cfs / 2.5:1" figure used the *upstream* St. Joseph gage (Newville 04178000,
29.69 cfs). The correct near-Fort-Wayne gages give a derived **headwaters 7Q10 ≈ 69.7 cfs** (St.
Joseph nr FW 04180500 = 54.06 + St. Marys nr FW 04182000 = 15.65). Against it: design 74 MGD →
**0.61:1 (effluent-dominant)**; actual 43.9 MGD (2023 DMR mean, ≈ 59% of design) → **1.03:1 (tight)**.
The plant is effluent-balanced-to-dominant at low flow — significant, but milder than the hypothesis.
The DMR record shows **no monthly-average exceedance 2021–2025** (the ECHO SNC label is uncorroborated
by a recent exceedance — an open reconciliation item, likely historical).

**Data-center activity — the inverse of every other point.** The registry presents Fort Wayne as the
GCP/Google site (codename `GCP`, facility status *confirmed*) — the network's one **disclosed**
facility. But the **corpus holds zero primary Fort Wayne documents**: `facility=None`, no
permits/deeds/entity-graph, information-sector LQ 0.44 (not yet IT-oriented). So the facility is known
*from outside the record*, not yet *in* it — the open discovery (IURC large-load filings, permits,
economic-development records) is proposal #360. Honest register: a confirmed real-world campus, an
empty corpus dimension.

**Serving utility — VERIFIED across the state line.** Indiana Michigan Power (I&M, EIA #9324, an AEP
subsidiary), regulator **IURC** (Indiana — correctly *not* PUCO), RTO PJM — the cross-state grid path
(#356 fixed the Ohio-hardcoding the per-site axis had missed). **LMP resolved (#361, 2026-06-21):**
the $35 placeholder is replaced with the connector-sourced **AEP-zone** day-ahead annual mean
(**$45.81/MWh**, PJM Data Miner 2). I&M settles in the PJM **AEP zone** — the live Data Miner 2 zone
list carries no separate I&M zone — so Fort Wayne's zonal LMP is the AEP zone (pinned `lmp_pnode_id`,
same fixture as the OH AEP sites), `source=connector`.

**Read-side note.** The cross-document MCP tools (`entities`/`timeline`/`hydrology_balance`) are
**Lima-keyed** and return zero Fort Wayne content — the documented "read side stays Lima-keyed until
parity" deferral, not a corpus gap. All Fort Wayne findings come from the slug-scoped onboarding
outputs + the basin-shared ECHO inventory.

**Proposals — 5 filed as sub-issues of #235:** ~~#358 (resolve the headwaters 7Q10 denominator
mismatch)~~ **— resolved 2026-06-23: derived headwaters 7Q10 ≈ 69.7 cfs; FW correctly unscreened
(Baldwin Ditch); see [`wwtp-receiving-water.md`](wwtp-receiving-water.md)**,
~~#359 (extract the IN0032191 NPDES permit + DMR + ECHO detail)~~ **— resolved 2026-06-23: `bosc dmr`
connector + [`wwtp-in0032191.dmr.yaml`](wwtp-in0032191.dmr.yaml); actual ≈ 43.9 MGD vs 74 design, no
2021–2025 exceedance; the "1 violation" is American-Bath, not FW**, #360 (investigate the disclosed
Fort Wayne / NE-Indiana data-center facility), ~~#361 (verify the I&M LMP, replace the $35/MWh
placeholder)~~ **— resolved 2026-06-21: I&M is in the PJM AEP zone, LMP now connector-sourced
$45.81/MWh**, #362 (commit a site footprint to unblock SSURGO HSG + GIS discovery). The GIS
lift (Allen Co IN / City of Fort Wayne partial-CAMA parcel layers, no clean zoning catalog) is
tracked under GIS discovery above.

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [x] basin-screen coverage is sane for this site's receiving waters — IN0032191's primary receiver is the ungaged Baldwin Ditch, so it is correctly unscreened (omit-don't-guess); the receiving-water read is documented in [`wwtp-receiving-water.md`](wwtp-receiving-water.md) against the derived headwaters 7Q10 (#358/#359).
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [x] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/) — see self-research summary above; 5 proposals filed as sub-issues of #235 (#358–362).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'fort-wayne' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
