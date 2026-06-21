# Research run: onboard urbana (Urbana): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-21T23:17:46+00:00
- turns: 27 (cap 30); cost: $1.0174
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, Grep, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I have everything I need across the onboarding scaffold, the reference data, the entity/timeline tools, and the two thin data-center threads. Here is the findings report.

---

# Findings — Onboarding `urbana` (Urbana): data-center activity + receiving-water screen

**Scope.** Whether the Urbana watershed point is ready to promote as a BOSC network site, assessed on its two load-bearing dimensions — documented data-center activity and a receiving-water (assimilative) screen. Read-only pass over the BOSC corpus (MCP `entities`/`timeline`/`list_*`) plus the committed onboarding scaffold under `data/**/urbana/` and `src/bosc/sites.py`.

## Bottom line up front

- **Urbana is scaffolded but not promoted.** `frontend/src/lib/sites.ts` carries it `status: "queued"`, `selectable: false`, issue 441 (lines 139–148); its facility lifecycle defaults to **`investigation`** (no entry in `FACILITY_STATUS`, line 200ff). The portable reach connectors ran and committed cited hydrology/economics/climatology reference data, but **three of the data-center-relevant steps failed or were skipped** (RSEI, grid-profile, self-research) and **both load-bearing dimensions — data-center activity and per-jurisdiction GIS — are unchecked** (`data/extracted/urbana/ONBOARDING.md` lines 9–10, 23–26).
- **Data-center activity is the weakest leg in the corpus — weaker than Van Wert's.** The only Urbana-specific signal is **Highland55**, and it exists *only* as a one-line entry in `docs/COURSE.md` (line 117) tagged **`[open]`; no in-corpus document yet** — there is no deed, NPDES, LLC, CRA, or zoning instrument. A second, adjacent signal — **Honda's announced "own Ohio data center" in the "Marysville / Clark / Champaign area"** (`data/entities/profiles/cloud-consumer-candidates.yaml` lines 282–290) — is an analytic **candidate profile, not a primary instrument**, and is not pinned to Urbana/Champaign. **`[verified]`** there are **zero Urbana/Champaign/Mad-River primary documents** in the ingested corpus (`list_documents` returns no match for urbana, champaign, mad river, great miami, 05080001, or 39021).
- **The receiving-water screen has no denominator for the Mad River at all.** Urbana's `receiving_water_name` is the **Mad River** `[verified]` (`sites.py` line 1667), but **neither 7Q10 table contains it** — the cited table holds only the three Lima/Maumee streams, and the derived table holds only the four Maumee mainstems. The `basin-screen` step that `ONBOARDING.md` reports as "7/129 dischargers screened" is **`[inference]` the Maumee ECHO inventory** (the only ECHO inventory committed; the count is identical to Van Wert's), which **does not cover the Great Miami / Ohio-River basin Urbana sits in.** The Urbana receiving-water screen is, in substance, **empty**.

---

## 1. Site provenance and onboarding status

The Urbana `SiteProfile` is registered (`src/bosc/sites.py` `_URBANA`, line 1613). Geography is sourced and tagged, and it is deliberately the network's **first Great-Miami / Mad-River site** — the geological *inverse* of the Maumee lake-plain points (header comment, lines 1603–1612):

- Basin `great-miami`; **Mad River → Great Miami River → Ohio River, HUC-8 `05080001`** `[verified]` (line 1616). Sink is the **Ohio River, not Lake Erie**; no Maumee-style basin TMDL.
- NWIS gages **03267000 (Mad River near Urbana)** and **03267900 (Mad River at Eagle City, downstream)** `[verified]` (lines 1617–1620) — these double as the **abstraction/supply gages** (lines 1669–1671).
- City centroid **40.1084, −83.7524** `[verified]`; county/RSEI/econ FIPS **`39021` (Champaign County)** `[verified]` (lines 1621–1624).
- Dominant HSG **B** is tagged **`[inference]`** (Mad River buried-valley outwash sand & gravel — a US-EPA **sole-source aquifer** feeding the Springfield/Dayton/Wright-Patterson corridor downstream), pending SSURGO confirmation (lines 1641–1646).

Last `bosc onboard` run (`data/extracted/urbana/ONBOARDING.md` lines 14–26):

| step | status |
|---|---|
| Hydrology — derive-low-flows, corridor-DDF, climatology | **ok** |
| Economics — baseline, consumer-energy | **ok** |
| SSURGO HSG | **skipped** — `footprint missing: extracted/urbana/bosc-site-footprint.yaml` |
| **RSEI** | **skipped** — cache input missing (`elements.csv.gz`) |
| **grid-profile** | **error** — `EIA-861 2024: no Short-Form ('861S') row for utility #0 in OH` |
| **self-research** (the #247 data-center seed proposals) | **error** — `1 validation error for ProposalDrafts` |
| Data-center activity / per-jurisdiction GIS | **`[ ]` not started** (lines 9–10) |

So the two dimensions this task is about — **data-center activity and the receiving-water screen — are exactly the two that did not complete**. The blocking review gate (lines 28–35) is entirely unchecked.

---

## 2. Data-center activity

### 2a. Highland55 — the only Urbana-specific signal `[open]`
`docs/COURSE.md` (lines 116–119) places Highland55 in the "parallel consumers (other counties)" thread:

> **Thor Equities / Thor Van Wert / Highland55** (Urbana, Van Wert); CyrusOne; Platon Investments / Dynamo Ventures … corridor **`[open]`; no in-corpus document yet**.

A repo-wide search confirms **Highland55 appears in exactly three places — `COURSE.md` and the prior Van Wert research run (`findings.md` + `manifest.yaml`)** — i.e., only in analysis/methodology text, **never in a primary instrument or an extraction**. It is an open lead, not a documented connection.

### 2b. Honda — geographically adjacent, analytically inferential `[inference]/[open]`
`data/entities/profiles/cloud-consumer-candidates.yaml` (lines 282–290): **Honda of America**, tier 4 candidate, location **"Marysville / Clark / Champaign area,"** `confirmed_cloud_relationship: own Ohio data center (announced/investing)`, basis "vehicle + manufacturing data at scale." This is a **candidate/inference profile** built for demand-fit screening — not a deed, permit, or filing — and its location string straddles three counties without pinning Urbana/Champaign. Treat it as corridor context, not a documented Urbana project.

### 2c. Downstream-adjacent thread (separate register)
`COURSE.md` (line 120) logs **Roshel / International Motors at the Springfield APA (2026-03-30)**. Springfield (Clark County) is immediately **downstream of Urbana on the Mad River**, so it is geographically relevant — but it is a **separate investigative register** and must not be bridged into Urbana absent a filed instrument.

### What the data-center record does and does not establish
- **`[verified]`** Zero Urbana/Champaign primary documents exist in the corpus. The profile's `facility` field is `None` `[open]` (line 1674); `facilityStatus("urbana") = "investigation"`.
- **`[open]`** Highland55 is an unsourced lead; the `self-research` seed-proposal step that would draft entity targets **errored**, so even the inferential entity layer is empty.
- **Do not import the Allen-County register.** The Bistrozzi / Tilted Gate / Magenta land-assembly graph and its shared organizers (Montfort/Ziance, EMH&T/Vorys) surfaced by `entities` are **Lima/Maumee** entities. There is **no evidentiary bridge** to Urbana; cross-referencing them in would be exactly the inference-as-finding error the method forbids.

---

## 3. Receiving-water screen — the central hole (and why Urbana's screen is a *different* screen)

### 3a. The receiving water is named; its design low flow is absent
`receiving_water_name: "Mad River"` `[verified]` (line 1667), but the discharge side is unpopulated: **`plant_receiving: {}` `[open]`** (line 1668) and **`passby_primary_cfs: 0.0` `[open]`** (lines 1672–1673). There is **no Urbana-area WWTP NPDES fact sheet in the corpus** — every `oepa/` extraction is a Lima plant (American II / American Bath / Shawnee II), and every ECHO inventory file is **Maumee-scoped** (`data/reference/echo/maumee-wwtp.*` — there is no Great-Miami inventory).

### 3b. The Mad River is in neither 7Q10 table
The screen's denominators (read directly):
- **Cited regulatory 7Q10s** (`low-flow-7q10.yaml`): only **Dug Run 0.78, Pike Run 0.03, Ottawa River 0.2 cfs** — all Lima fact-sheet-sourced, `source: document`, high confidence. **No Mad River.**
- **Derived 7Q10s** (`low-flow-7q10.derived.yaml`): only the four USGS-gaged **Maumee mainstems** — Maumee 114.15, Auglaize 1.91, St. Marys 15.65, St. Joseph 29.69 cfs (LP3, `source: derived`, confidence **medium**). **No Mad River.**

`ONBOARDING.md` reports `basin-screen` as **"7/129 dischargers screened (1 violations, 2 tight)."** Because (a) the only committed ECHO inventory is Maumee, and (b) the count is identical to Van Wert's run, this is **`[inference]` the Maumee inventory** — which **excludes the Great-Miami basin entirely**. (Stated as inference: I read the two denominator files and the ECHO file inventory, not the literal per-discharger screen output.) **No Mad-River / Champaign discharger was screened against its own receiving water.**

### 3c. Urbana's screen should not be a copy of Lima's — flag this for the methodology
Lima's screen is built around **effluent dominance** (a plant discharging more than a tiny tributary's entire 7Q10; American II's cited acute dilution is 1.3:1). Urbana is the **deliberate inverse**: a **groundwater-dominated, high-baseflow Mad River** fed by a permeable **sole-source buried-valley aquifer** (HSG B). The interesting assimilative question here is not effluent-vs-low-flow but **consumptive cooling abstraction vs. aquifer/baseflow on a designated sole-source supply** — which is precisely why the profile carries `abstraction_gage` / `supply_gage_primary` / `passby` fields (lines 1669–1673) that the Maumee sites don't lean on. The Mad River **near Urbana is gaged (03267000)**, so a derived 7Q10 *is* obtainable — the denominator is missing, not impossible.

### 3d. Supporting reach data that did land (connector / `[reference]`)
- **Climatology** (`reference/hydrology/urbana/nasa-power-climatology.yaml`): NASA POWER normals at 40.108/−83.752, elev 314.6 m, **annual precip 2.73 mm/day, mean T 10.86 °C** — connector-sourced.
- **Design-storm DDF** (`reference/hydrology/urbana/atlas14-corridor-ddf.yaml`): NOAA Atlas-14 point depths — **24-hr 100-yr 5.54 in, 24-hr 2-yr 2.67 in, 60-min 100-yr 2.78 in** — `[reference]` HDSC query.
- **Soils**: dominant HSG **B** is **`[inference]`**, SSURGO confirmation skipped for want of a site footprint. Do not promote as verified.
- **RSEI toxics**: **not generated** (cache miss) — there is no Champaign-County toxics inventory; `toxic_corridor_bbox` is `(0,0,0,0)` `[open]` (lines 1661–1666).

---

## 4. Economic / grid baseline

**Economics — high confidence** (`reference/economics/urbana/baseline.yaml`, BLS QCEW 2023 + Census ACS, all `confidence: high`):
- **10,471 jobs / 725 establishments** (2023); **manufacturing LQ 4.14** (a strongly export-oriented manufacturing county — consistent with the Honda/Marysville corridor).
- **Information sector: 36 jobs, LQ 0.18** — effectively no incumbent data-center/IT base, the expected greenfield signature.
- **Population 38,772 (2023)**, gently declining from 40,140 (2010).

**Grid — incomplete and likely a *different zone* than Lima.** The `grid-profile` step **errored** (no EIA-861 Short-Form row for **utility #0**) — `eia861_utility_number` is **`0` `[open]`** (line 1625). The profile flags **`lmp_usd_mwh: 35.0` as `[inference]`**, "likely the **DAY zone (Dayton / AES Ohio / DP&L)**" — **not** Lima's AEP/PUCO zone (lines 1677–1683, 1675). This is the actionable cross-utility note: Urbana is Ohio (so the cross-state connector axis from the Fort Wayne work is not re-triggered), but its **retail utility and PJM zone are unverified and probably AES Ohio, not AEP** — pin before any grid figure is published. `consumer-energy` did run (`ok`).

---

## 5. Reconciliation / data-quality notes

- **No OPC/estimate artifacts** exist for Urbana, so `program_overview` / `reconcile_*` are **not applicable** (they read the Lima Tetra Tech summary).
- The BOSC MCP analysis tools (`entities`, `timeline`, `list_extractions`) are **Lima-scoped** and do **not** surface the Urbana scaffold. An auditor working through the tool layer alone would wrongly conclude Urbana is empty; the data lives in `data/**/urbana/` and `src/bosc/sites.py` and must be read directly until an Urbana analysis scope exists.
- **Figure-confidence summary:** Champaign-County employment/population are connector **high-confidence**; climatology/DDF are connector/`[reference]`; **HSG B and LMP $35/MWh are `[inference]`**; **Highland55 and the Honda Champaign-area data center are `[open]`/proponent-candidate, not documented**; the **Mad-River 7Q10, the Urbana WWTP design flow, the serving utility, and the PJM zone are all `[open]`**. No `~`-marked figures appear in the Urbana scaffold.

---

## Recommended follow-up investigations (track as issues)

**Receiving-water — highest priority (the screen's central hole)**
1. **Derive a Mad-River 7Q10 at USGS 03267000** (`bosc derive-low-flows` already has the gage in-profile) and, in parallel, **ingest the Ohio EPA NPDES fact sheet for the Urbana-area WWTP** to add a *cited* receiving-water 7Q10 + design flow to `low-flow-7q10.yaml`. Right now `plant_receiving` and the 7Q10 are both empty — there is no screen.
2. **Build (or scope) a Great-Miami / Ohio-River-basin discharger inventory.** The `basin-screen` "7/129" result is the **Maumee** ECHO inventory and is meaningless for Urbana. Until a Great-Miami inventory exists, treat every Urbana receiving-water statement as `[open]`, not a finding.
3. **Reframe the Urbana screen as a source-water / abstraction screen**, not an effluent-dominance one: consumptive cooling draw vs. Mad River baseflow and the **sole-source buried-valley aquifer**. This is the site's actual thesis and the methodology should not copy Lima's denominator logic onto it.

**Data-center activity / entity graph**
4. **Source Highland55** — Champaign County / City of Urbana recorder, ODOD/JobsOhio, and any CRA/PILOT — to move it from a one-line `COURSE.md` lead to a documented instrument (or formally retire it). Keep any Urbana land assembly a **separate register** from the Allen-County Bistrozzi graph.
5. **Pin the Honda "Champaign-area" data center** to an actual parcel/filing or downgrade it to corridor context; it currently spans three counties on an inference profile.
6. **Re-run `bosc onboard urbana --research`** once the `ProposalDrafts` validation error is fixed, so the data-center seed-proposal pass actually produces triage targets.

**Hydrology / soils / grid completeness**
7. **Identify a candidate site footprint** to unblock the skipped **SSURGO** step and upgrade HSG from `[inference] B` to a cited area-weighted value.
8. **Resolve the EIA-861 utility number** (`utility #0` → the real Champaign-County retail utility, likely **AES Ohio**) and **pin the PJM zone (likely DAY)** so the grid-profile and LMP stop being placeholders.
9. **Regenerate RSEI** for FIPS 39021 (the run skipped on a missing `elements.csv.gz` cache) to get the Champaign-County toxics baseline.

**Promotion gate**
10. **Do not flip `status`→`live` / `selectable`→`true`** for `urbana` until items 1–2 (a cited/derived Mad-River 7Q10 + a basin-appropriate screen) and at least item 4 (a documented data-center instrument) clear the blocking checklist in `ONBOARDING.md`. Promotion remains a manual, parity-gated edit; onboarding never auto-promotes, and only the Lima `/bosc` build is live today.

---

Want me to write this up as a `data/research/onboard-urbana-…/findings.md` artifact (matching the Van Wert precedent), or open any of these as tracked issues?
