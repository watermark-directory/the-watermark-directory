# Research run: onboard wpafb (Wright-Patterson AFB): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T00:16:45+00:00
- turns: 30 (cap 30); cost: $1.0921
- tools: ToolSearch, Skill, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__program_overview, mcp__bosc__timeline, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, Grep, Glob, Read, Bash
- proposals: 5 (see `manifest.yaml`)

---

I have a complete picture. Here is the findings report.

---

# Findings — Onboarding screen: Wright-Patterson AFB (Dayton, Montgomery County, OH) as a BOSC watershed-point site

**Task:** assess data-center activity + a receiving-water screen for the candidate site "wpafb," over the BOSC corpus, using read-only tools.
**Tools used:** `program_overview`, `entities`, `timeline`, `list_documents`, `list_extractions`, `hydrology_balance`, `hydrology_scenario`; plus text search over the committed reference tree, `watermark.sites`, the frontend registry, the defense-footprint testimony, and the cloud-consumer profile.

**Headline:** Like the other Miami sites, WPAFB is **registered and partly seeded, not promoted** — its `SiteProfile` exists and the portable hydrometeorology + economics connectors have run. But it is the **one Miami node that already carries a corpus thread** (the defense-footprint testimony + the cloud-consumer candidate entry), and its water story is deliberately **not** the surface-7Q10 dilution screen the bound tools run — it is the **buried-valley sole-source aquifer + a TCE/PFAS plume**. Both named dimensions of this task are therefore in an unusual state: data-center activity is *documented but only as published record* (no primary instrument), and the receiving-water screen is *the wrong screen* unless reframed to groundwater.

---

## 1. Onboarding state: registered, half-seeded, not promoted `[verified]`

Registered in both registries:
- `src/bosc/sites.py` — `_WPAFB` profile (sites.py:1887–1963), basin `great-miami`, `Montgomery County, OH` / FIPS `39113`, slug-scoped output relpaths. Two distinctive choices, both flagged in-profile: it is the network's **first UTM 16N site** (`hydro_utm_epsg=32616`, base at ~84.05°W, west of the 84° meridian) and its economic/toxics unit is **Montgomery County (39113)**, deliberately distinct from the Greene-County (Xenia #444) unit even though the base straddles both counties.
- `frontend/src/lib/sites.ts` (sites.ts:178–192) — `slug:"wpafb"`, `status:"queued"`, `selectable:false`, `issue:"442"`, `place:"Dayton · WPAFB"`, basin "Mad River · Great Miami".

Connector outputs present, with **live data** `[verified-connector]`:

| Output | File | Status |
|---|---|---|
| NASA-POWER climatology | `reference/hydrology/wpafb/nasa-power-climatology.yaml` | **present** |
| Atlas-14 corridor DDF | `reference/hydrology/wpafb/atlas14-corridor-ddf.yaml` | **present** |
| Census+QCEW county baseline | `reference/economics/wpafb/baseline.yaml` | **present** |
| EIA consumer energy (OH) | `reference/eia/wpafb/consumer-energy.yaml` | **present** |

**Missing / not yet run** (each a concrete gap, not a hedge) `[verified]`:
- **RSEI county toxics inventory** — `reference/rsei/wpafb/inventory.yaml` absent (only README).
- **EIA-861 grid profile** — `reference/eia/wpafb/grid-profile.yaml` absent; `eia861_utility_number=0 [open]`.
- **Basin 7Q10 for the Great Miami / Mad River** — see §3; the derived file is Maumee-only.
- **The blocking review gate** — `data/extracted/wpafb/ONBOARDING.md` does **not** exist (only `README.md`).
- **The self-research first pass** — no `data/research/onboard-wpafb-*/findings.md` (all 10 onboarded siblings have one). *This report is effectively that missing pass, run by hand.*
- **GIS field-maps + geometry** — `gis_parcel=None`, `gis_zoning=None`, `parcels_url`/`zoning_url="TODO"`; no `bosc-parcels.geojson`, no `bosc-site-footprint.yaml`. (Flood is free via national NFHL layer 28 `[verified]`.)
- Minor: `noaa_fallback_24h_depth_in={} [open]` even though the full corridor-DDF file is populated (the fallback dict is just unfilled — not a data gap).

## 2. The corpus holds zero WPAFB *primary* records; the bound tools are Lima-only `[verified]`

The `entities` graph and the 1,485-line `list_documents` inventory are **entirely Lima / Allen County**: every deed, NPDES permit, WWTP (Shawnee II → Ottawa River; American Bath → Pike Run; American II → Dug Run), and shell entity is the Lima reference build. There is **no Montgomery/Greene County deed, NPDES permit, SOS shell filing, or meeting record.**

The MCP hydrology tools take **no site parameter** — they read the active site (`lima`):
- `hydrology_balance` returned only the three Lima WWTPs, each a low-flow violation (e.g. Shawnee II → Ottawa River, 7Q10 0.20 cfs vs 4.64 cfs discharge `[doc]`).
- `hydrology_scenario` returned only the Lima/BOSC campus draw (4.85 cfs net = 24.3× the cited Ottawa 7Q10).

So a WPAFB screen is **not blocked by analysis capacity — it is blocked by the absence of committed Great Miami reference data**, and the read side stays Lima-keyed until a site reaches parity. State it flatly.

## 3. Receiving-water screen: the *surface* screen is blocked **and** is the wrong screen `[open]` / `[inference]`

Two findings, in order of importance:

**(a) The surface dilution screen is blocked.** A Tier-0 screen needs, per outfall, a cited design flow, the receiving stream, and that stream's 7Q10. None exist for WPAFB: `low-flow-7q10.derived.yaml` covers only the **Maumee-basin mainstems** (Maumee, Auglaize, St. Marys, St. Joseph) — none of WPAFB's gages (`03270000` Mad River nr Dayton, `03270500` Great Miami at Dayton, `03263000` Great Miami at Taylorsville) has a derived low flow; `plant_receiving={}` and both passby minimums are `0.0 [open]` (no WWTP fact sheet ingested). `[verified]`

**(b) The profile is explicit that surface 7Q10 is *not* WPAFB's water story.** The hsg_citation and header comment state the load-bearing risk is the **Great Miami / Mad River Buried Valley Aquifer** — a US-EPA designated **sole-source aquifer** that the Dayton municipal and WPAFB production well fields draw on — plus a documented **TCE / PFAS groundwater plume** on that same drinking-water aquifer. This is a genuinely different screen from every Maumee/dilution site: the denominator is groundwater supply, not in-stream low flow. **Caveat:** the sole-source-aquifer designation and the plume are asserted in the profile as `[inference]`/`[reference]`; I did **not** see a primary cited source for either in the corpus. Treat both as **to-verify**, not as findings.

The stormwater side *is* ready: the Atlas-14 24-hr depths are in hand `[verified-connector]` — 2-yr 2.71 in, 10-yr 3.79 in, 25-yr 4.43 in, 50-yr 4.94 in, 100-yr 5.45 in — so a pre/post-development runoff screen is feasible **once a footprint exists** (`pre_cover`/`post_cover` still `"TODO"`).

## 4. Data-center activity: documented as published record, **not** as a primary instrument `[verified]` / `[inference]`

This is WPAFB's distinguishing feature versus the greenfield Miami sites — the corpus already carries the thread, but be precise about its register:

- **Written testimony §8** ("Ohio defense footprint," `bosc-written-testimony-2026-06-01.md:183`): *"Google Distributed Cloud air-gapped appliance holds DoD IL5, MIL-STD-810H; Air Force Rapid Sustainment Office a named early customer; GDIT + Google Public Sector demoed at Exercise Mobility Guardian 2025."* This is a **secondary/published-record** assertion (the cited sources are Google Cloud blog, Breaking Defense, Defense One, GDIT) inside a relator's own testimony — defensible as published record, **not** a primary land or permit instrument.
- **Cloud-consumer profile** (`cloud-consumer-candidates.yaml:220–228`): Tier-3 entry "Wright-Patterson AFB-adjacent suppliers (corridor)," `confirmed_cloud_relationship: GDIT (WPAFB Rapid Sustainment Office hub, per published record)`. Again analyst-built from published record.

So the accurate statement is: **the distinctive data-center variant here is regulated/air-gapped DoD cloud (IL5/IL6), documented in the corpus as published record; there is no primary deed, SOS shell, or permit record of any sited data-center facility in this corpus.** The economic frame is the testimony's "government-cloud premium" (≈20–30% above commercial) and the "structurally barred local tenants" argument — an IL5/IL6 enclave cannot host a local hospital, bank, or county (`bosc-written-testimony-2026-06-01.md:73–97`).

The committed Montgomery County economics (BLS QCEW 2023 / Census ACS, connector `confidence:high`) give defensible context — but with a **caution about the geography choice**:
- Population **535,528** (2023); total employment **248,053** jobs; 13,083 establishments.
- **Information (NAICS 51): 4,354 jobs, LQ 0.90** — near/below national share; no existing data/IT-hosting concentration by employment.
- **Professional, Scientific & Technical Services (NAICS 54): 14,018 jobs, LQ 0.81** — *not* elevated. The defense Prof-Sci-Tech signature lives in **Greene County** (Xenia profile reports LQ 2.11), not in the Montgomery unit chosen here. `[inference]` Because the economic unit was set to Montgomery (39113) for the well-field/plume/metro context, **the WPAFB baseline does not show the defense-supplier employment concentration that the WPAFB thesis rests on** — that concentration is in the adjacent county.

## 5. Profile field audit — verified vs. open `[verified]` / `[open]`

Sound and citable: `basin=great-miami` (HUC-8 05080001/2), the three NWIS gages, county/FIPS 39113, design & met lat/lon (39.8261, −84.0494), **UTM 16N** (correctly zone 16, not 17), NFHL flood schema. Still **open**, explicitly flagged — do not treat as findings: `eia861_utility_number=0`, `lmp_usd_mwh=35.0` placeholder + `lmp_pnode_id=0` (PJM DAY zone not pinned), `dominant_hsg="B" [inference]` (footprint-dependent), `parcels_url`/`zoning_url="TODO"`, `toxic_corridor_bbox=(0,0,0,0)`, `plant_receiving={}`, `passby_*=0.0`, `facility=None`.

## 6. Actionable follow-ups (track as issues, under #442 / epic #440)

1. **Reframe the screen to groundwater — the defining WPAFB task.** Verify, with cited sources, (a) the US-EPA **sole-source aquifer** designation for the Great Miami / Mad River Buried Valley Aquifer and (b) the WPAFB **TCE/PFAS plume** (likely Air Force IRP/CERCLA record, ATSDR, or OEPA). Define a buried-valley + plume overlay; this is a **new analysis dimension** the surface Tier-0 tools do not cover. Currently `[inference]`/`[reference]` in the profile only.
2. **Extend `derive-low-flows` to the Great Miami / Mad River basin** — gages `03270000`, `03270500`, `03263000` into a basin-scoped 7Q10 file. Necessary for completeness, but secondary to #1 given the aquifer is the water story. `[open]`
3. **Ingest the WPAFB / Dayton-area WWTP NPDES permit + fact sheet** to populate `plant_receiving` (cited design flow, receiving reach) and the in-stream passby minimum.
4. **Finish the connector set** — run RSEI for Montgomery County 39113 (`reference/rsei/wpafb/inventory.yaml`, only README now) and EIA-861 grid-profile; verify the retail utility / EIA number (likely AES Ohio / DP&L, PJM **DAY** zone). **Re-scan grid/econ connectors for non-Lima Ohio-hardcoding** per the known cross-state-leak pattern — it surfaced even for in-state OH siblings.
5. **GIS lift** — discover + register Montgomery County parcel + City of Dayton/Montgomery zoning ArcGIS REST endpoints from a live `?f=json` (never fabricate field names); **verify the situs is Montgomery County OH** (recorded same-name-county trap). Handle the **WPAFB federal enclave** as its own register — federal/military land won't appear in county CAMA (cf. the `UNITED STATES` parcel_owner entity already in Lima's graph). Floodzone is free national NFHL.
6. **Data-center activity sweep, two distinct tasks** — (a) expand/confirm the published DoD-cloud thread (GDIT / Google Distributed Cloud IL5 / RSO) and pin an actual facility/parcel *if one is sited*; (b) parcel/SOS/permit scan for any new data-center land assembly in the Dayton/WPAFB corridor — **record a flat no-primary-record finding if none.** Keep the regulated/air-gapped variant and the government-cloud-premium thesis as the analytical frame, not as evidence of a sited facility.
7. **Resolve the economic-unit caveat** — decide whether WPAFB needs a **two-county (Greene + Montgomery)** economic treatment so the defense Prof-Sci-Tech concentration (which lives in Greene) is visible in the baseline the WPAFB thesis depends on; otherwise document why Montgomery-only is the right unit.
8. **Generate the missing onboarding artifacts** — persist `data/extracted/wpafb/ONBOARDING.md` (the blocking review gate) and the `data/research/onboard-wpafb-*/findings.md` self-research pass. Promotion to `live`/`selectable` stays a separate, parity-gated edit.

**Bottom line:** WPAFB is a registered, half-seeded site with good hydrometeorology and Montgomery-County economics scaffolding but **no surface 7Q10, no local WWTP, no GIS, and no primary data-center record** in the corpus. It is the only Miami node with an existing corpus thread — but that thread is **published-record DoD-cloud context, not a sited facility** — and its real receiving-water risk is **groundwater (sole-source aquifer + plume), which the bound surface tools do not screen.** The two decisive next steps are #1 (verify and build the aquifer/plume overlay) and #7 (fix the economic-unit so the defense signature isn't invisible); everything else can proceed in parallel.

---

Want me to persist this as `data/research/onboard-wpafb-*/findings.md` (matching the sibling artifact format) and seed `data/extracted/wpafb/ONBOARDING.md` with the review-gate checklist?
