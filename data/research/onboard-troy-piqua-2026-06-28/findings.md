---
topic: onboard troy-piqua
model: claude-opus-4-8
generated: 2026-06-28T18:58:40+00:00
turns: 21
turns_cap: 30
cost_usd: 0.8378
proposals: 5
tools:
  - ToolSearch
  - mcp__watermark__program_overview
  - mcp__watermark__list_documents
  - mcp__watermark__list_extractions
  - mcp__watermark__entities
  - mcp__watermark__hydrology_balance
  - mcp__watermark__hydrology_scenario
  - mcp__watermark__sanitary_basis
  - mcp__watermark__storm_plan_inventory
  - mcp__watermark__timeline
  - mcp__watermark__retrieve_corpus
---

I now have a clear picture. Critically, my `site="troy-piqua"` probe returned **zero** indexed source context — so there is no troy-piqua source-document material lacking an extraction, and nothing to file via `report_novel_finding`. Every Lima result is an existing, already-extracted precedent, not unextracted troy-piqua context. I won't fabricate a finding.

Here is the structured onboarding review.

---

# Onboarding Review — `troy-piqua` watershed-point site

**Method.** Assessed via read-only BOSC tools on 2026-06-28. Every site-scoped surface was queried for `troy-piqua`; the Lima reference build was queried with focused `retrieve_corpus` semantic pulls to establish the baseline each area is measured against. Status registers below: `[verified]` = confirmed from a tool result; `[open]` = not determinable from these read-only tools and must be checked in the producer layer.

## Headline finding

`troy-piqua` is a **bare registered shell**. Every committed, reviewed artifact surface returns empty:

- `list_documents` → "No committed source documents for site 'troy-piqua' yet." `[verified]`
- `list_extractions` → "No extractions found under data/extracted/troy-piqua." `[verified]`
- `entities`, `timeline`, `hydrology_balance`, `hydrology_scenario`, `sanitary_basis`, `storm_plan_inventory` → all return the `[scope]` "not substituted for another site (#424)" stub. `[verified]`
- `program_overview` → no `*.summary.opc.yaml`. `[verified]`
- `retrieve_corpus(site="troy-piqua", …)` → "No results found." The corpus index holds **no** troy-piqua chunks. `[verified]`

Because the index surfaced no troy-piqua source context, the `report_novel_finding` triage path did not trigger — there is nothing extracted-vs-source to reconcile yet; there is simply nothing.

> Note on scope: these MCP tools serve *committed, reviewed* artifacts. They do **not** expose `watermark.sites.SITES` registration or slug-scoped reach-connector outputs under `data/site/`. So "empty here" confirms nothing is promoted; it does **not** by itself confirm the SiteProfile is unregistered. Per the Miami-basin expansion record (epic #440), troy-piqua was "onboarded" in the thin sense (profile + portable reach connectors). Each "verify in producer layer" item below flags that boundary honestly rather than asserting past it.

---

## 1. NPDES / permit profile

**Lima baseline** (`retrieve_corpus`): a fully-onboarded reach carries, per WWTP, an OEPA **fact sheet** + **draft public notice** extraction, plus an ECHO **DMR** connector pull:
- `extracted/oepa/oepa-2PH00006-american-ii-fact-sheet.npdes.yaml` and its draft PN `…-american-ii-draft-pn-2025-04` (App. OH0037338)
- `extracted/oepa/oepa-2PH00007-american-bath-fact-sheet.npdes.yaml` + draft PN `…-2024-03` (OH0023841)
- `extracted/oepa/oepa-2PK00002-shawnee-ii-draft-pn-2026-03.npdes.yaml` (OH0023850)
- ECHO DMR pattern: `extracted/fort-wayne/wwtp-in0032191.dmr.yaml`, regenerable via `watermark dmr <NPDES_ID> --start … --design-flow …`

**troy-piqua status:** `[verified]` none. No `oepa/` (or Ohio-equivalent) NPDES fact sheets/public notices, no DMR connector output. The receiving-water WWTP(s) for the Troy/Piqua reach are unidentified in any committed artifact.

**Gaps:** receiving-water WWTP NPDES ID(s) not established; no fact-sheet/PN ingest; no DMR pull. **Blocking** — sanitary basis and `hydrology_balance` both depend on a cited design flow + 7Q10 receptor.

## 2. Grid / utility profile

**Lima baseline:** the SiteProfile carries `eia861_utility_number`; the grid connector pulls EIA-861 sales + PJM-930 BA interchange + the LMP pricing zone (per repo conventions and the EIA-861 bulk connector, #94). Power basis is recorded per-site (Lima = disclosed ekW; Fort Wayne `idem/47378f.idem.yaml` = *derived* genset MW from heat input — a documented worked example of how to handle a non-disclosing permit).

**troy-piqua status:** `[verified]` no committed grid artifact reachable through these tools; `[open]` whether `eia861_utility_number` / `rsei_fips` / LMP zone are set on a registered SiteProfile (not exposed by MCP — verify in `watermark.sites`).

**Gaps:** confirm serving utility + EIA-861 number (watch the municipal **EIA-861S short-form** fallback — Troy and Piqua are both candidates for municipal/home-rule utilities, per the Bryan precedent); confirm PJM vs. correct RTO/LMP zone; no power basis recorded. **Mostly blocking** for a complete profile; the BA-interchange/LMP layer is **non-blocking** follow-up.

## 3. Hydrology

**Lima baseline:** SiteProfile `nwis_sites` drive live USGS NWIS pulls; `hydrology_balance` routes cited WWTP design flows to receiving waters and screens each against a cited **7Q10**; `hydrology_scenario` compares campus cooling draw to the river 7Q10.

**troy-piqua status:** `[verified]` `hydrology_balance` and `hydrology_scenario` both return the empty `[scope]` stub. No committed 7Q10, no water-balance, no scenario. `[open]` whether `nwis_sites` are configured on the profile and whether reach connectors have run (slug-scoped outputs not visible here).

**Gaps:** confirm Great Miami / Mad River NWIS gauge IDs on the profile; establish 7Q10 for the receiving reach; run the water balance once a WWTP receptor (§1) exists. **Blocking** for the assimilative-screen thesis that anchors the network.

## 4. GIS / footprint

**Lima baseline:** parcel + zoning connectors wired per county; a `bosc-site-footprint.yaml` records the geometry. Two documented patterns: Lima = stormwater-permit-transcribed developed/impervious acreage; Fort Wayne = **recorded ownership assemblage** (11 parcels) with `developed`/`impervious` left `[open]` pending the deed/stormwater extraction. Same-name-county hazard is on record (the "Williams County = North Dakota" miss) — verify situs city/state from a live sample before wiring any discovered parcel/zoning endpoint.

**troy-piqua status:** `[verified]` no committed footprint geometry, no parcel/zoning extraction. `[open]` whether Miami/Shelby-county (OH) parcel + zoning ArcGIS endpoints are wired on the profile.

**Gaps:** identify the candidate parcel assemblage; wire OH parcel/zoning GIS (OGRIP `County='Miami'`/`'Shelby'` substitute as needed); produce a footprint record (assemblage-based is acceptable, with `developed`/`impervious` `[open]`). **Blocking** for stormwater runoff; assemblage refinement is **non-blocking**.

## 5. Extracted corpus

**Lima baseline:** a deep reviewed tree — recorder deeds, commissioners resolution ledger + minutes, LACRPC zoning + collection index, the AEDG Tetra Tech OPC program, and a `legal/` PRR layer.

**troy-piqua status:** `[verified]` empty — `list_extractions` and `list_documents` both report nothing; the index holds no chunks. There are **no source documents** ingested yet, so there is nothing to extract against.

**Gaps:** no source corpus at all. Everything downstream (entities, timeline, program overview) is empty as a consequence. **Blocking** at the foundational level — needs source-document ingest before any extraction work.

## 6. Hypothesis assessments

**Lima baseline:** the (site × hypothesis) join (hypothesis store + bundle feeds, contract ≥1.5.0) is populated for Lima; assessments are grounded in primary instruments (e.g. the PRR `data-center-flows-treatment-evaluation` finding, the select-committee witness digest).

**troy-piqua status:** `[verified]` no hypothesis cells reachable through committed artifacts; the join is empty for this site. `[open]` whether placeholder hypothesis rows exist in the store (not exposed by these tools).

**Gaps:** every boom-origin hypothesis cell is **open** for troy-piqua. Non-blocking for promotion mechanics, but the page will (correctly) render `locked` until evidence exists.

---

## Prioritized gap checklist

### Blocking (must resolve before promotion to `selectable`)

1. **Source-document ingest (§5).** No corpus exists. Nothing else can be extracted or assessed until source documents are committed under a troy-piqua tree. *Foundational — gates 1, 5, 6.*
2. **Identify receiving-water WWTP + NPDES ID(s) (§1)** and ingest the OEPA fact sheet + public notice; pull ECHO DMR. *Gates hydrology balance and sanitary basis.*
3. **Establish 7Q10 + run `hydrology_balance` (§3)** for the receiving reach; configure `nwis_sites` on the profile. *Gates the core assimilative-screen thesis.*
4. **Confirm serving utility + EIA-861 number (§2)** — check the **EIA-861S short-form** path for municipal Troy/Piqua utilities; set the correct LMP/RTO zone and a power basis.
5. **Wire OH parcel/zoning GIS + produce a footprint record (§4)** — verify situs county/state from a live sample first; assemblage-based footprint acceptable with `developed`/`impervious` left `[open]`.
6. **Verify the SiteProfile is registered in `watermark.sites.SITES`** with `*_relpath`s, `nwis_sites`, `rsei_fips`, `eia861_utility_number`, GIS URLs. *Not visible to these read-only tools — confirm in the producer layer; if absent, this precedes all of the above.*

### Non-blocking (good follow-up leads)

- BA-interchange / PJM-930 interchange layer and full LMP-zone enrichment (§2) — useful but not promotion-gating.
- Parcel-assemblage refinement to a surveyed developed footprint once a stormwater permit exists (§4) — mirror the Fort Wayne `[open]`-acreage pattern in the interim.
- Boom-origin hypothesis-cell population (§6) — let the page render `locked` (per #781/#782 readiness layer); do **not** fake values to make the partial site look complete.
- `hydrology_scenario` (campus cooling draw vs. 7Q10) — depends on a footprint power/cooling basis; queue after §3 + §4.

### Process notes

- No `report_novel_finding` leads were filed: the index surfaced no troy-piqua source context that lacks an extraction. Once source documents are ingested, re-run the `retrieve_corpus(site="troy-piqua")` sweep — anything that surfaces without a `data/extracted/troy-piqua/` peer is then a legitimate triage lead.
- Cross-reference the **Miami basin expansion** record (epic #440) for the intended scope; Troy-Piqua is listed there as onboarded in the thin sense, consistent with the empty-but-registered state observed here.

I did **not** fabricate any figure, utility number, NPDES ID, or parcel — every troy-piqua line above is "not found," and every Lima baseline cites the specific extraction file the precedent comes from.
