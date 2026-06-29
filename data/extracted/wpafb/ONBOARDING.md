# Onboarding — Wright-Patterson AFB (wpafb)

Living record for the Wright-Patterson AFB watershed point (basin: great-miami), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`web/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

WPAFB is the **downstream terminus of the Mad River corridor** (Urbana → Springfield → **Dayton/WPAFB**) and the **richest node** of the Miami expansion — the SW-Ohio analog to Lima's JSMC / tank-plant defense nexus, and the **only Miami site that already carries a corpus thread**. Two distinctive choices are baked into the profile and both are correct: it is the network's **first UTM 16N site** (`hydro_utm_epsg=32616`; the base at ~84.05°W is *west* of the 84°W meridian, not in zone 17 like the other Miami sites), and its economic/toxics unit is **Montgomery County (Dayton metro, FIPS 39113)** even though the base straddles Greene + Montgomery (see the economics caveat below). The water story here is deliberately **groundwater** — the Great Miami / Mad River Buried Valley sole-source aquifer + a documented TCE/PFAS plume — **not** the surface-7Q10 dilution screen the other sites run.

## Dimension coverage

- [~] **Hydrology** — corridor-DDF + climatology connectors ran (WPAFB-specific, cited; Atlas-14 24h 2-yr 2.71 in → 100-yr 5.45 in). The surface receiving-water screen is **both blocked and the wrong screen**: blocked because there's no Great Miami / Mad River 7Q10 (the derived table is Maumee mainstems only — none of the three WPAFB gages 03270000/03270500/03263000 has a low flow; this run's `derive-low-flows` also hit a transient USGS 503, but the shared Maumee file is already committed and unchanged) and no WWTP ingested (`plant_receiving={}`); the *wrong* screen because the load-bearing risk is the **Buried Valley sole-source aquifer + the TCE/PFAS plume** (`[inference]`/`[reference]` in the profile — **to-verify**, not yet findings). SSURGO skipped (no footprint → HSG B stays `[inference]`).
- [x] **Economics** — Montgomery County baseline + consumer-energy ran (high-confidence: pop 535,528, 248,053 jobs). **CAVEAT (a real one):** the defense Professional/Scientific/Technical signature is **invisible in this unit** — Montgomery NAICS 54 LQ **0.81** (not elevated), NAICS 51 (Information) LQ **0.90** (near national). The defense-supplier concentration the WPAFB thesis rests on (NAICS 54 LQ **2.11**) lives in **adjacent Greene County**, which **Xenia (#444)** already covers. The straddle splits coherently — Greene/Xenia = the defense-employment cluster (the contractor bedroom communities), Montgomery/WPAFB = the well-field + plume + Dayton-metro toxics — but a reader of WPAFB's baseline alone would wrongly conclude "no defense concentration." A two-county treatment is filed as a follow-up. RSEI toxics ran (Montgomery Co, 141 facilities / 111 scored — the Dayton-metro toxics mass; top by modeled Score: EFTEC North America + Delphi Energy & Chassis Vandalia); grid-profile ran on the now-pinned serving utility **Dayton Power & Light** (AES Ohio, EIA-861 #4922; PJM/PUCO; verified from the EIA-861 2024 Service_Territory).
- [~] **Data-center activity** — self-research first pass run (#247); **the only Miami node with an existing corpus thread — but as published record, not a primary instrument.** The corpus carries the **regulated/air-gapped DoD cloud** variant: written testimony §8 "Ohio defense footprint" + `cloud-consumer-candidates.yaml` (Google Distributed Cloud air-gapped IL5/IL6, the **Air Force Rapid Sustainment Office** a named early customer, **GDIT + Google Public Sector** at Exercise Mobility Guardian 2025) — analyst-built from published record (Google Cloud blog, Breaking Defense, Defense One, GDIT) and explicitly **entity-level, not tied to a sited facility** (`docs/legal/mandamus-analysis.md:495`). `[verified]` there is **no primary deed, SOS shell, or permit** of a sited data-center facility here. **Method note:** this is the defense-cloud *customer* register (legitimately WPAFB's relevance), **not** the Lima Bistrozzi land-assembly graph, which is not bridged in.
- [ ] **Per-jurisdiction GIS** — Montgomery County parcels / City of Dayton zoning connector (the known lift), **plus the WPAFB federal enclave as its own register** (federal/military land won't appear in county CAMA — cf. Lima's `UNITED STATES` parcel-owner). Flood = national NFHL (wired).

## Last onboard run (2026-06-22, `--research`)

| step | status | output |
|---|---|---|
| scaffold | ok | per-site dirs + READMEs |
| derive-low-flows | error | transient USGS 503; shared `low-flow-7q10.derived.yaml` (Maumee mainstems) already committed, unchanged |
| corridor-ddf | ok | reference/hydrology/wpafb/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/wpafb/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/wpafb/nasa-power-climatology.yaml |
| basin-screen | ok (Maumee) | 7/129 dischargers — the Maumee inventory; **no Great-Miami coverage** |
| econ-baseline | ok | reference/economics/wpafb/baseline.yaml (Montgomery Co 39113) |
| rsei | ok | reference/rsei/wpafb/inventory.yaml — 141 facilities (111 scored) |
| consumer-energy | ok | reference/eia/wpafb/consumer-energy.yaml |
| grid-profile | ok | reference/eia/wpafb/grid-profile.yaml — Dayton Power & Light #4922, PJM |
| self-research | ok | research/onboard-wpafb-wright-patterson-afb-data-center-a-2026-06-22/ |

## Self-research (Phase 5; #247) — 2026-06-22

`bosc onboard wpafb --research` (claude-opus-4-8, 30 turns, $1.09). Findings + manifest in
`data/research/onboard-wpafb-wright-patterson-afb-data-center-a-2026-06-22/`.

**Bottom line.** WPAFB is registered + half-seeded but **not promotable**, and it is unusual on both
load-bearing dimensions: data-center activity is **documented (but only as published record, no sited
facility)**, and the receiving-water screen is **the wrong screen** until reframed to groundwater.

- **Receiving-water screen — reframe to groundwater (the defining WPAFB task).** The surface 7Q10
  screen is blocked (no Great Miami / Mad River low flow; no WWTP), but more importantly it is not
  WPAFB's water story. The load-bearing risk is the **Great Miami / Mad River Buried Valley Aquifer**
  (a US-EPA designated sole-source aquifer the Dayton municipal + WPAFB production well fields draw on)
  plus a documented **TCE / PFAS groundwater plume** on that same drinking-water aquifer. **Both are
  asserted in the profile as `[inference]`/`[reference]` with no primary cited source in the corpus —
  treat as to-verify, not findings** (likely sources: US-EPA SSA designation; the Air Force IRP/CERCLA
  record, ATSDR, OEPA).
- **Data-center activity — published-record DoD cloud, not a sited facility.** The distinctive variant
  is regulated/air-gapped **DoD cloud (IL5/IL6)**, documented in the corpus as published record and
  explicitly entity-level (not tied to a sited facility). The analytical frame is the testimony's
  **government-cloud premium** (~20-30% above commercial) and the **structurally-barred-local-tenants**
  argument (an IL5/IL6 enclave cannot host a local hospital, bank, or county). There is no primary
  instrument of a sited facility — the open work is to confirm/expand the published thread and, only if
  one is sited, pin a parcel; otherwise record a flat no-primary-record finding.
- **Economic-unit caveat.** Choosing Montgomery (39113) for the well-field/plume/metro-toxics context
  makes the defense Prof-Sci-Tech concentration (which lives in Greene, LQ 2.11 — Xenia #444) invisible
  in WPAFB's own baseline (Montgomery NAICS 54 LQ 0.81). Decide whether WPAFB needs a two-county
  (Greene + Montgomery) treatment so the defense signature the thesis depends on is visible.
- **Grid is unpinned at AES Ohio / DAY.** Montgomery County is AES Ohio (Dayton) territory — pin the
  EIA-861 utility + PJM zone (likely DAY) before publishing any grid figure (Ohio, so the cross-state
  connector axis isn't re-triggered).

**Proposals — all 5 filed** as sub-issues of #442 (none moot — the run knew the site was registered;
the missing-artifacts work is done by this PR): verify the sole-source aquifer + TCE/PFAS plume (the
groundwater screen); extend `derive-low-flows` to the Great Miami / Mad River + ingest the WPAFB/Dayton
WWTP NPDES; resolve the economic-unit scope (two-county Greene + Montgomery); complete the connector set
(RSEI 39113 + pin the utility/EIA-861/PJM zone — **DONE**: RSEI ran (141 fac/111 scored) + utility pinned
to DP&L #4922/PJM); and the data-center activity sweep (confirm the DoD-cloud
thread + scan for a sited facility).

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation. (HSG B is `[inference]`; footprint needed.)
- [ ] basin-screen coverage is sane for this site's receiving waters. (**Currently the Maumee inventory; and the real screen here is groundwater — the sole-source aquifer + plume — not surface 7Q10.**)
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md; + the federal-enclave register).
- [x] Self-research first pass reviewed (Phase 5, 2026-06-22; groundwater-reframe + published-record DoD-cloud + the economic-unit caveat; all 5 proposals filed as sub-issues of #442).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'wpafb' in web/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
