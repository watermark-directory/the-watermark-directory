# Research run: onboard findlay (Findlay): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-19T14:51:14+00:00
- turns: 37 (cap 30); cost: $1.6754
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__timeline, Grep, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, Glob, Read
- proposals: 5 (see `manifest.yaml`)

---

I have a complete picture. Confirmed: **no Blanchard River 7Q10 exists anywhere in the corpus** — only a 2009 TMDL-approval row and the Atlas-14 corridor label reference the Blanchard. Here is the findings report.

---

# Findings — Onboarding Findlay: data-center activity + receiving-water screen

## Bottom line

Findlay is a **registered but un-promoted** watershed point. Its `SiteProfile` exists with sourced geography, and the connector-pull dimensions (hydrology reach data, county economics, toxics, grid backdrop, zoning catalog) are committed. But the **two dimensions named in this topic are the two that are not yet established**:

- **Data-center activity:** `[verified]` **nothing documented.** No Findlay/Hancock data-center permit, deed, record, or entity exists in the corpus. The profile carries `facility=None` deliberately. This is a *finding* ("no disclosed Findlay facility yet"), not merely a gap.
- **Receiving-water screen:** the inventory side is in place (the Findlay POTW and the Blanchard industrial dischargers are catalogued), but the **assimilative denominator is missing** — there is **no Blanchard River 7Q10** (cited or derived) anywhere in the corpus, so the Lima-style low-flow screen **cannot currently be run** for Findlay.

The corpus itself remains entirely Lima/Allen County: a search of the full document and timeline indices returns **zero** Findlay/Hancock/Blanchard hits.

---

## 1. Onboarding state (what is done, what gates promotion)

Source: `data/extracted/findlay/ONBOARDING.md`; `src/bosc/sites.py` L553–653; `frontend/src/lib/sites.ts` L73–83.

| Dimension | State | Evidence |
|---|---|---|
| Identity / registry | Done | Profile `_FINDLAY` registered; frontend `status:"open", selectable:false, issue:"237"` |
| Hydrology (reach) | Done | `findlay/atlas14-corridor-ddf.yaml`, `findlay/nasa-power-climatology.yaml` committed |
| Economics | Done | `economics/findlay/baseline.yaml`, `rsei/findlay/inventory.yaml`, `eia/findlay/*` committed |
| Per-jurisdiction GIS | Partial | Zoning catalog committed (15 districts, 2026-06-19); parcels `[open]`; flood = national NFHL (spatial, pending footprint) |
| **Data-center activity** | **Not started** | `facility=None`; `--research` pass never run (no `data/research/findlay-*`) |

**Review gate (blocking) — all four substantive boxes still unchecked** in `ONBOARDING.md`: reference-value review, SSURGO HSG confirmation, basin-screen sanity, and the self-research pass. Promotion (`status:"live"` + `selectable:true`) is a separate, parity-gated manual edit and is correctly **not** done.

**Profile placeholders still open** (`bosc onboard findlay --check` territory), each tagged in-source:
- `parcels_url="TODO"` / `gis_parcel=None` `[open]` — Hancock County publishes no ArcGIS-REST parcel layer (Beacon/Schneider only).
- `pre_cover`/`post_cover`/`developed_pervious_cover="TODO"` `[open]` — the development land-cover scenario, pending an identified site.
- `toxic_corridor_bbox=(0,0,0,0)` `[open]`; `plant_receiving={}` `[open]`; `supply_gage_primary/secondary="TODO"`, `passby_*=0.0` `[open]`.
- `dominant_hsg="D"` is `[inference]` (Great Black Swamp Hoytville/Pewamo clays) — the SSURGO validation step **skipped** (no footprint), so it is unconfirmed.

---

## 2. Receiving-water screen

### 2a. Inventory side — in place (high confidence, connector-sourced)

From the basin-wide ECHO inventory `data/reference/echo/maumee-wwtp.all-npdes.yaml` (Blanchard = HUC-8 `04100008`, **37 facility records** in the Blanchard HUC; 129 POTWs basin-wide):

- **City of Findlay Water Pollution Control Center** — NPDES `OH0025135`, FRS `110064593177`, POTW, **design flow 15.0 MGD** `[reference]` (ECHO ICIS, L19977–19998), Hancock County, at 41.048/−83.668. This is the anchor receiving-water datum and the single largest POTW in the basin after Lima's.
  - Caveat: ECHO `receiving_water: null` for this outfall. The profile asserts `receiving_water_name="Blanchard River" [verified]` for the *site*, but the WPCC's **specific outfall receiving water is not in the corpus** — it must come from the OH0025135 NPDES fact sheet before being stated as documented.
- Other Blanchard POTWs present (e.g. Mt. Blanchard WWTP `OH0095079`, Country Acres `OH0079057`); industrial NPDES dischargers present (National Lime & Stone–Findlay `OH0095320`; Intersil `OH0053627`).

### 2b. Denominator side — **missing (the headline gap)**

`[verified]` There is **no Blanchard River 7Q10** in the corpus:
- `low-flow-7q10.yaml` (cited fact-sheet 7Q10s) holds only Dug Run, Pike Run, Ottawa River — all Lima.
- `low-flow-7q10.derived.yaml` (LP3-derived mainstem proxies) holds only Maumee, Auglaize, St. Marys, St. Joseph — **no Blanchard**, despite the profile naming Blanchard gage `04189000` and Eagle Creek `04188496`.
- The only Blanchard hits in `data/reference/hydrology/` are a TMDL-approval row (Blanchard River Watershed TMDL approved **2009-07-02**, 15 TP TMDLs, 24 NPDES permits; `ottawa-lima-tmdl.yaml` L27) and the Atlas-14 corridor label.

**Consequence:** the Lima-style assimilative screen and the data-center buildout scenario (`hydrology_balance` / `hydrology_scenario`, which divide discharge or cooling consumptive draw by the receiving stream's 7Q10) **cannot be computed for Findlay**. The recorded onboard `basin-screen` result — "**7/129 dischargers screened (1 violation, 2 tight)**" (`ONBOARDING.md` L21) — is basin-wide and, given the absent Blanchard 7Q10, **almost certainly excludes the Findlay WPCC**. That 7-of-129 figure needs reconciliation (which 7 were screened, and confirmation the WPCC was unscreened for lack of a denominator).

---

## 3. Data-center activity

`[verified]` **No documented data-center activity for Findlay/Hancock in the corpus.** `facility=None`; no permit, deed, SOS filing, or meeting record references a Findlay data center. The entity graph and timeline are Lima-only.

This is consistent with the methodology: data-center activity is a **corpus-extraction + self-research** dimension that `bosc onboard` does **not** capture via connectors — and it is why the committed **grid profile is a backdrop only** (`eia/findlay/grid-profile.yaml`: AEP Ohio / Ohio Power #14006, PJM, PUCO — no campus load share fabricated). The `--research` self-research pass has not been run.

I will not assert anything about real-world Findlay-area development that is not in the corpus. Whether such projects exist is an `[open]` research question (item 3 below), not a finding.

---

## 4. Industrial / toxics context (relevant to any future receiving-water screen)

From `data/reference/rsei/findlay/inventory.yaml` (EPA RSEI v234, Hancock County `39063`: **29 facilities, 23 scored**, high-confidence connector data — figures are modeled RSEI scores, comparative only, **not** concentrations):

- **Water/POTW dischargers** (the cluster a Findlay receiving-water screen would intersect): **Cooper Tire** (701 Lima Ave, Findlay — `water_releases:true`), **Nissin Brake Ohio**, **Intersil Findlay Operations** (`OH0053627`, large POTW loadings), **Seneca Wire** (Fostoria), **Tower Automotive** (Bluffton).
- Highest RSEI score: **Cascade Corp** (Toyota Industries; chromium-driven) — but offsite/air, no water releases.

This is the empirical basis for eventually defining `toxic_corridor_bbox` (currently zeros) over the Findlay industrial corridor on the Blanchard.

**Economic baseline** (`economics/findlay/baseline.yaml`, BLS QCEW 2023, high confidence): Hancock County **44,290 jobs / 1,950 establishments**; **Manufacturing location quotient 2.92** (10,859 jobs) — a manufacturing-dense county, the relevant backdrop for siting/load arguments.

*Confidence note:* every figure in §2–§4 is connector/reference-sourced (ECHO ICIS, USGS, NOAA Atlas-14, BLS QCEW, EPA RSEI, EIA-861) and high-confidence — **none are hand-transcribed `~` approximations.** The hand-transcribed-figure discipline does not bear on this site yet because no scanned Findlay primary documents have been extracted.

---

## 5. Follow-up investigations worth tracking as issues

1. **Derive the Blanchard River 7Q10** (highest priority for the receiving-water screen). Run `bosc derive-low-flows` for USGS `04189000` (Blanchard nr Findlay, 346 sq mi, active since 1990) and add it to the curated `low-flow-7q10.derived.yaml`. Without it, no Findlay discharger — POTW or hypothetical data center — can be assimilatively screened.

2. **Pull the City of Findlay WPCC NPDES fact sheet (OH0025135)** and extract the *cited* 7Q10, design/peak flows, and stated dilution ratio; populate `plant_receiving` and confirm the WPCC's receiving water (ECHO has it `null`). This is the Findlay analogue of the Lima fact-sheet 7Q10s.

3. **Open the data-center-activity dimension.** Run `bosc onboard findlay --research`; triage proposals; search Ohio EPA eDoc / Hancock recorder / SOS for any Findlay data-center permits or land assembly. Until something surfaces, record "**no documented Findlay data center**" as an affirmative finding in `ONBOARDING.md`, not a blank.

4. **Resolve the SSURGO HSG `[inference]`.** Commit a Findlay footprint (or run area-weighted SSURGO over Hancock OH063) to confirm or correct `dominant_hsg="D"` — currently an unvalidated inference because the onboard SSURGO step skipped.

5. **Wire the parcel substitute.** Hancock publishes no ArcGIS-REST parcel layer; register the Ohio statewide parcel layer filtered to FIPS `39063` (geohio) and resolve `parcels_url`/`gis_parcel`.

6. **Reconcile the basin-screen "7/129 screened (1 violation, 2 tight)"** — enumerate which 7 dischargers were screened, confirm the Findlay WPCC was *excluded* for want of a Blanchard 7Q10, and document the unscreened Blanchard dischargers as a coverage gap (this ties directly to item 1).

7. **Define the Findlay toxics corridor** (`toxic_corridor_bbox`, currently zeros) over the Cooper Tire / Nissin / Intersil water-discharger cluster on the Blanchard, using the RSEI coordinates already committed.

8. **Verify the grid-market values copied from Lima.** `lmp_usd_mwh=35.0` is flagged `[inference]` (shared AEP-zone value); confirm against the PJM AEP-zone LMP and the EIA-861/PUCO service-territory record for Ohio Power #14006.

A note on registry hygiene: items 1, 4, 5, 7 correspond to live `TODO`/placeholder/`matches-lima` fields in `_FINDLAY` that `bosc onboard findlay --check` already flags — closing the investigations and clearing the lint are the same work.
