# Research run: onboard ottawa (Village of Ottawa, Putnam County): data-center activity + receiving-water screen for a new watershed-point site, and the Findlay-Ottawa same-river (Blanchard) intra-tributary control

- model: `claude-opus-4-8`
- generated: 2026-06-21T13:17:59+00:00
- turns: 28 (cap 30); cost: $1.5739
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__timeline, mcp__bosc__entities, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, mcp__bosc__sanitary_basis, Read, Grep, Glob
- proposals: 5 (see `manifest.yaml`)

---

I now have everything needed. Confirmed in the committed corpus: **OTTAWA WASTEWATER TREATMENT PLANT, NPDES OH0026921, POTW, 3.0 MGD design flow** (FRS 110000760668), with ECHO `receiving_water: null`. Here is the findings report.

---

# Findings — Onboarding Ottawa (Village of Ottawa, Putnam County): data-center activity + receiving-water screen, and the Findlay↔Ottawa Blanchard intra-tributary control

## Bottom line

Ottawa is a **registered but un-promoted** watershed point (profile `_OTTAWA`, `src/bosc/sites.py` L1271–1369; marked a "coming-soon" point, issue #381). It is further along than Findlay was: the connector dimensions (hydrology reach, economics, toxics, grid) are committed, **and** the per-jurisdiction GIS discovery already found a queryable county ArcGIS (a stronger posture than Findlay). But the two dimensions named in this topic carry the same structural gaps as every other un-promoted point:

- **Receiving-water screen:** the inventory side is **corpus-grounded and verified** — the Ottawa WWTP and the Blanchard dischargers are catalogued — but the **assimilative denominator is missing.** `[verified]` There is **no Blanchard River 7Q10** (cited or derived) anywhere in the corpus, so the Lima-style low-flow screen and the data-center buildout scenario **cannot currently be computed for Ottawa.** This is identical to the Findlay headline gap (`data/research/onboard-findlay-.../findings.md` §2b) — and it is the *shared* gap that makes or breaks the intra-tributary control.
- **Data-center activity:** `[verified]` **nothing documented.** `facility=None` (L1350). No Putnam/Ottawa data-center permit, deed, SOS filing, or meeting record exists in the corpus; the entity graph and timeline are entirely Lima/Allen County. The `--research` self-research pass has **not** been run (no `data/research/*ottawa*` directory). This is an affirmative "no disclosed Ottawa facility yet," not merely an empty cell.

The intra-tributary control is **structurally sound and well-scaffolded, but not yet computable** — both endpoints lack the same Blanchard 7Q10.

---

## 1. Disambiguation (load-bearing — three different "Ottawas")

`[verified]` This site is the **Village of Ottawa, Putnam County, OH**, on the **Blanchard River** (centroid 41.0192/−84.0472; OSM relation 182178, `sites.py` L1280). It is **not**:
- the **Ottawa River** of Lima/Allen County — the Lima site's receiving water (Shawnee II WWTP → Ottawa River, 7Q10 0.2 cfs, `low-flow-7q10.yaml` L45–56). Every "Ottawa River" reference in `mcp__bosc__entities`, `hydrology_balance`, and `network.yaml` is the Lima river, a different watershed.
- **Ottawa County / Port Clinton** (Lake Erie).

The profile, ONBOARDING, and TMDL records keep this distinction clean (`sites.py` L1268; `data/extracted/ottawa/ONBOARDING.md` L18–20). Any prose that screens "Ottawa" against the cited 0.2 cfs 7Q10 would be **wrong** — that denominator belongs to Lima's Ottawa River, not the Village's Blanchard.

---

## 2. The Findlay↔Ottawa intra-tributary (same-river) control

`[verified]` Findlay and Ottawa sit on the **same receiving river (the Blanchard)**, ~40 river-mi apart — the network's only *along-one-river* pair (`ONBOARDING.md` L12–20; `sites.py` L1261–1266). The design value: every other network comparison is *across* tributaries (different chemistry, regime, gage); Findlay↔Ottawa holds watershed identity constant and varies only the discharge point. Both are AEP Ohio / PJM AEP zone (`grid-profile.yaml`), so the grid story is identical too — the control isolates the hydrology/siting variables.

| | Findlay (upstream) | Ottawa (downstream) |
|---|---|---|
| County | Hancock (39063) | Putnam (39137) |
| POTW | City of Findlay WPCC `OH0025135`, **15.0 MGD** `[reference]` (ECHO) | **Ottawa WWTP `OH0026921`, 3.0 MGD** `[verified]` (ECHO, FRS 110000760668) |
| Receiving gage(s) | `04189000` Blanchard nr Findlay | `04189260` Blanchard at Ottawa; `04189500` Blanchard at Glandorf (long-record, just downstream) |
| Grid | AEP Ohio / PJM | AEP Ohio / PJM |
| Watershed TMDL | Blanchard River Watershed TMDL, **approved 2009-07-02**, 15 TP TMDLs, 24 NPDES permits (`ottawa-lima-tmdl.yaml` L27) | same |

**The shared blocker:** the control needs a Blanchard 7Q10 at (or near) each end. `[verified]` Neither exists in the corpus — see §3. Until a Blanchard 7Q10 is derived, the "two discharge points on one river" comparison is a clean *design* with **no computable assimilative result at either node.** A useful framing for tracking: the single derivation that unblocks Findlay (item F-1 in its findings) is the same one that unblocks Ottawa — one piece of work clears both ends of the control.

---

## 3. Receiving-water screen

### 3a. Inventory side — verified, connector-sourced

From the committed basin ECHO inventory `data/reference/echo/maumee-wwtp.all-npdes.yaml` (Blanchard = HUC-8 `04100008`):
- `[verified]` **OTTAWA WASTEWATER TREATMENT PLANT**, `OH0026921`, POTW, **design flow 3.0 MGD**, FRS 110000760668 (L20395–20403). This is the site's anchor receiving-water datum.
  - **Caveat (evidentiary):** ECHO carries `receiving_water: null` for this outfall (L20404). The profile asserts `receiving_water_name="Blanchard River"` (L1340) — defensible at the *village* level (the village is on the Blanchard), but the **specific OH0026921 outfall receiving water and its design flows/dilution are not in the corpus.** They must come from the OH0026921 NPDES fact sheet before being stated as documented. This is exactly the Findlay-WPCC caveat repeated.
- Other Blanchard dischargers present in Putnam/adjacent counties: **National Lime & Stone Co Ottawa Plant** `OH0038482` (L20330); smaller POTWs and IUs across Hancock/Hardin/Allen/Putnam in the same HUC-8.

### 3b. Denominator side — **missing (the headline gap)**

`[verified]` **No Blanchard River 7Q10 anywhere in the corpus:**
- `low-flow-7q10.yaml` (cited fact-sheet 7Q10s) holds only **Dug Run, Pike Run, Ottawa River** — all Lima (L20–56).
- `low-flow-7q10.derived.yaml` (LP3-derived mainstem proxies) holds only **Maumee, Auglaize, St. Marys, St. Joseph** — **no Blanchard** (full file read; L8–62), despite the profile naming the Blanchard gages `04189260`/`04189500`.
- The only Blanchard hits in `data/reference/hydrology/` are the 2009 TMDL-approval row and the Atlas-14 corridor label.

**Reconciliation discrepancy worth an issue:** the recorded onboard run (`ONBOARDING.md` L21, L31) reports `derive-low-flows: ok → low-flow-7q10.derived.yaml` and `basin-screen: ok — 7/129 dischargers screened (1 violation, 2 tight)`. Yet that derived file contains **no Blanchard value** — so the "ok" derive step produced nothing for this site's own receiving water, and the "7/129" figure is **identical** to Findlay's basin-screen result. The strong `[inference]` is that basin-screen covers only the 7 streams that *have* a denominator (4 derived mainstems + 3 cited Lima tributaries) and that the **Ottawa WWTP is among the unscreened** Blanchard dischargers. That needs enumerating (which 7, and confirmation OH0026921 was excluded for want of a denominator), not assuming.

**Consequence:** `hydrology_balance` / `hydrology_scenario` (which divide discharge or cooling consumptive draw by the receiving stream's 7Q10) **cannot be run for Ottawa today.** Both tools currently return the Lima loop only — their "Ottawa River 7Q10 0.2 cfs" is Lima's river (§1), not the Village's Blanchard.

---

## 4. Data-center activity

`[verified]` **No documented data-center activity for Ottawa/Putnam.** `facility=None` (L1350); no permit, deed, SOS filing, or meeting record references it. Consistent with methodology: data-center activity is a **corpus-extraction + self-research** dimension that `bosc onboard` does not capture via connectors — which is why the committed **grid profile is a backdrop only** (`grid-profile.yaml` L72–77: AEP Ohio / Ohio Power #14006, PJM, PUCO, `load_share: null` — no campus load fabricated). The `--research` pass has not been run. Whether any real-world Putnam-area development exists is an `[open]` research question (item 3 below), **not** a finding — I will not assert it from outside the corpus.

---

## 5. Industrial / toxics + economic context (the future screen's intersect)

From `data/reference/rsei/ottawa/inventory.yaml` (EPA RSEI v234, Putnam County `39137`: **14 facilities, 12 scored**; figures are modeled, comparative RSEI scores — **not** concentrations; high-confidence connector data, all years ≤2014):
- **Water dischargers** (the cluster a Blanchard screen would intersect): `water_releases:true` for **LG.Philips Displays USA** (700 N. Pratt St, Ottawa; NPDES `2IN00028ED`) and **Unverferth Manufacturing** (Kalida; chromium/nickel).
- The dominant *legacy* toxics signal is **LG.Philips Displays** — RSEI score 513,121, **trichloroethylene-driven** (carcinogen), 1.48M lb TCE — but the facility is **defunct (last reporting year 2002)**, and its mass was overwhelmingly offsite/air/POTW (water 460 lb). So it is a candidate *corridor anchor* for `toxic_corridor_bbox` (currently zeros, `[open]`, L1334–1339), with the explicit caveat that it is not an active surface-water discharger.

Economic backdrop (`economics/ottawa/baseline.yaml`, BLS QCEW 2023 / Census ACS, high confidence): Putnam County **12,320 jobs / 857 establishments**; **Manufacturing location quotient 3.72** (3,853 jobs) — *more* manufacturing-dense than Hancock/Findlay (LQ 2.92); population **34,352** (2023), gently declining from 34,647 (2010). A manufacturing-heavy, slow/negative-growth rural county — the relevant siting/load backdrop.

*Confidence note:* every figure in §3–§5 is connector/reference-sourced (ECHO ICIS, USGS, NOAA Atlas-14, BLS QCEW, EPA RSEI, EIA-861) and high-confidence. **None are hand-transcribed `~` approximations** — no scanned Ottawa primary documents have been extracted yet, so the approximate-figure discipline does not bear on this site.

## 6. GIS posture (better than Findlay)

`[verified, per live discovery]` Putnam County **self-hosts a valid-cert, queryable ArcGIS** (`putnamcountygis.com/arcgis/rest/services`) carrying owner **and** CAMA values on the `Parcels` layer, plus a `Land Use`/CAMA layer with the full appraisal split and soil type (`ONBOARDING.md` L37–56). This is a wireable lead — stronger than Findlay (Hancock publishes no ArcGIS-REST parcel layer). No standalone village zoning REST (zoning is parcel-class-coded / map-only) → `gis_zoning=None` `[open]`. Field-maps are **not committed yet** (a reviewed follow-up), so `parcels_url`/`gis_parcel` remain `TODO`/`None` (L1288, L1293).

---

## 7. Follow-up investigations worth tracking as issues

1. **Derive the Blanchard River 7Q10 (highest priority; unblocks BOTH ends of the control).** Run `bosc derive-low-flows` for the **long-record Glandorf gage `04189500`** (and/or `04189000` Findlay, `04189260` Ottawa) and add it to `low-flow-7q10.derived.yaml`. Without it, neither the Ottawa WWTP nor any hypothetical Putnam data center — nor the Findlay end — can be assimilatively screened, and the intra-tributary control is non-computable.

2. **Pull the Ottawa WWTP NPDES fact sheet (OH0026921)** and extract the *cited* receiving water (ECHO has it `null`), 7Q10, design/peak flows, and stated dilution ratio; populate `plant_receiving` (currently `{}`, L1342) and convert `receiving_water_name="Blanchard River"` from site-level to outfall-level documented. This is the Ottawa analogue of the Lima fact-sheet 7Q10s and the Findlay WPCC pull.

3. **Open the data-center-activity dimension.** Run `bosc onboard ottawa --research`; triage `data/research/ottawa-<date>/`; search Ohio EPA eDoc / Putnam recorder / Ohio SOS for any Ottawa/Putnam data-center permits or land assembly. Until something surfaces, record "**no documented Ottawa data center**" as an affirmative finding in `ONBOARDING.md`, not a blank.

4. **Reconcile the onboard `derive-low-flows`/`basin-screen` "ok" against the empty Blanchard result.** Enumerate which 7 of 129 dischargers were screened, confirm OH0026921 was **excluded** for want of a Blanchard 7Q10, and document the unscreened Blanchard dischargers as a coverage gap. (The "7/129 (1 violation, 2 tight)" figure being identical to Findlay's strongly suggests the step never touched Blanchard data — verify, don't assume.) Ties directly to item 1.

5. **Resolve the SSURGO HSG `[inference]`.** `dominant_hsg="D"` (Black Swamp clays, L1303–1308) is unvalidated — the onboard SSURGO step **skipped** (no footprint, `ONBOARDING.md` L29). Commit an Ottawa footprint or run area-weighted SSURGO over Putnam OH137 to confirm/correct.

6. **Wire the Putnam County parcel connector.** Register `gis_parcel` from the live `putnamcountygis.com` `Parcels`/`LandUseParcels` field-map (owner + value); accept zoning as class-coded/map-only or locate a Village of Ottawa zoning layer. Closes `parcels_url`/`gis_parcel`/`zoning_url` (L1288–1294).

7. **Define the Ottawa toxics corridor** (`toxic_corridor_bbox`, currently zeros) over the Ottawa/Kalida water-discharger cluster on the Blanchard, anchored on the RSEI coordinates already committed — flagging that the dominant signal (LG.Philips/TCE) is a **defunct legacy** source, not an active surface-water discharger.

8. **Verify the grid-market value copied from Lima/Findlay.** `lmp_usd_mwh=35.0` is flagged `[inference]` (shared AEP-zone value, L1358–1362); confirm against PJM Data Miner 2 AEP-zone LMP. (Registry hygiene: items 1, 2, 5, 6, 7, 8 each correspond to live `TODO`/`{}`/zero/`[inference]` fields in `_OTTAWA` that `bosc onboard ottawa --check` already flags — closing the investigations and clearing the lint are the same work.)

9. **Build the network-level intra-tributary comparison artifact.** Once item 1 lands, wire a Findlay↔Ottawa same-river comparison (upstream WPCC 15 MGD vs downstream Ottawa WWTP 3 MGD against a common Blanchard 7Q10) into the basin/network layer — this is the analytical payoff the whole control was scaffolded for, and the network's only along-one-river case.

**Promotion remains correctly gated:** all four substantive review-gate boxes in `ONBOARDING.md` (L58–65) are unchecked, and `status:"live"`/`selectable:true` in `frontend/src/lib/sites.ts` is a separate, parity-gated manual edit — `onboard` never auto-promotes.

A note on scope: I did not open the full `mcp__bosc__list_documents` index (109k chars) line-by-line; the document/extraction/entity/timeline indices I did read are uniformly Lima/Allen County, and the targeted Blanchard/Putnam/Ottawa greps across `data/` returned only the connector-reference scaffolding reported above — consistent with "no Ottawa primary documents extracted yet."
