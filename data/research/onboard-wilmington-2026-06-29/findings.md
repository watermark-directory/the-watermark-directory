---
topic: onboard wilmington
model: claude-opus-4-8
generated: 2026-06-29T04:34:10+00:00
turns: 37
turns_cap: 30
cost_usd: 1.1742
proposals: 5
tools:
  - ToolSearch
  - mcp__watermark__list_documents
  - mcp__watermark__list_extractions
  - mcp__watermark__entities
  - mcp__watermark__timeline
  - mcp__watermark__program_overview
  - mcp__watermark__hydrology_balance
  - mcp__watermark__sanitary_basis
  - mcp__watermark__stormwater_runoff
  - mcp__watermark__hydrology_scenario
  - mcp__watermark__storm_plan_inventory
  - mcp__watermark__discover_oepa_permits
  - mcp__watermark__retrieve_corpus
  - mcp__watermark__fetch_oepa_permit
  - mcp__watermark__report_novel_finding
---

The lead is composed (it returned without a `GITHUB_TOKEN`, so it's drafted but not actually posted — I'll flag that). I now have everything needed for the structured review.

---

# Wilmington Watershed-Point — Onboarding Review

**Date:** 2026-06-29 · **Active site:** `wilmington` · **Reference build:** `lima`
**Method:** read-only BOSC tool sweep of every model surface + `discover_oepa_permits`; Lima parity established via `retrieve_corpus(site="lima")` precedents. All status below is tool-confirmed; no figures invented — "not found" is stated where a surface returned empty.

## Headline

Wilmington is a **bare registration**. Every active-site model surface returns the `[scope] No committed … for site 'wilmington' yet (#424)` sentinel: `list_documents`, `list_extractions`, `entities`, `timeline`, `program_overview`, `hydrology_balance`, `sanitary_basis`, `stormwater_runoff`, `hydrology_scenario`, `storm_plan_inventory` are all empty. The one thing I changed: pulled 6 OEPA permit PDFs to disk. Nothing is extracted, modeled, or connector-populated.

## 1. NPDES / permit profile

- **On the OEPA DAM** (`discover_oepa_permits`, term "Wilmington Ohio … data center"): **8 artifacts / 6 unique permit IDs, all `[new]`** — `8 new · 0 known · 0 committed`. So before this session, **0 committed and 0 in the site profile's `known` list**. `[verified]` (tool output).
- **Newly fetched** (6 primary PDFs → `data/documents/oepa/wilmington/`, SHA-256 recorded, `filename-map.yaml` updated):

  | DAM ID | type | size | prefix reading `[inference]` |
  |---|---|---|---|
  | `1PD00013` | permit (+ `.fs` fact sheet + DraftPN on DAM) | 1.9 MB | `1PD` municipal/POTW discharge |
  | `1PX00010` | permit | 0.35 MB | |
  | `1MP00060` | permit | **22 MB** (largest) | |
  | `1PV00089` | permit | 0.33 MB | |
  | `1IW00240` | permit | 0.90 MB | `1IW` industrial wastewater |
  | `1II00129` | permit | 1.24 MB | `1II` industrial discharge |

- **Still missing:** the **fact sheet (`1PD00013.fs.pdf`) and draft public notice (`1PD00013` DraftPN)** were *not* captured — `fetch_oepa_permit` is by-ID and pulled only the primary permit. Lima parity (`retrieve_corpus`: `oepa/oepa/oepa-2PH00006-american-ii-fact-sheet.npdes.yaml`, `…-draft-pn-…`, plus the permit) extracts **fact sheet + draft PN + permit separately**. And **all 6 fetched PDFs remain un-ingested/un-extracted** — no `data/extracted/wilmington/oepa/` exists.
- **Filed as a triage lead** via `report_novel_finding` (labels `type:gap, area:evidence, status:agent-proposed, site:wilmington`). ⚠️ Returned **"No GITHUB_TOKEN — issue not filed"**: the lead body is drafted but **not actually posted**; it must be filed manually or with a token present.

## 2. Grid / utility profile

- No active-site MCP surface exposes grid state, and **no connector output exists** to read. `[verified]`-empty by absence: nothing in `list_extractions`; hydrology/grid model tools all return the `#424` sentinel.
- Lima parity (`retrieve_corpus`): grid basis is carried on the `SiteProfile` (EIA-861 `eia861_utility_number`) and derived power basis (`extracted/idem/.../47378f.idem.yaml`, `extracted/permits/.../3859883.epa.yaml`). For wilmington: **EIA-861 utility number — not found; BA interchange — not found; LMP/LMP zone — not found.** `[open]`
- The `SiteProfile` registration (whether `wilmington` is even in `watermark.sites.SITES` with grid knobs) is **not introspectable via the read-only MCP tools available**; flag for direct code check.

## 3. Hydrology

- `hydrology_balance`, `sanitary_basis`, `stormwater_runoff`, `hydrology_scenario`, `storm_plan_inventory` — **all return the `#424` empty sentinel.** `[verified]`-empty.
- Implication: the **portable reach connectors that `watermark onboard <slug>` runs (NWIS gauges, NOAA Atlas-14, 7Q10, water balance) have not been run** for wilmington. NWIS gauges configured — **not found**; 7Q10 / water-balance — **not found**; WWTP sanitary design basis — **not found**.
- Lima parity (`retrieve_corpus`): receiving-water characterization + design flows + 7Q10 (`watershed/…`, `fort-wayne/bosc-site-footprint.yaml`, `legal/…bosc-site-permit-sequence.yaml`). This is connector work, not document extraction.

## 4. GIS

- No footprint, parcels, or zoning for wilmington — `entities` empty, no `extracted/wilmington` tree. `[verified]`-empty.
- Lima/FW parity (`retrieve_corpus`): footprint records (`fort-wayne/bosc-site-footprint.yaml` — recorded-ownership assemblage; Lima — document-transcribed developed/impervious acreage), zoning (`lacrpc/american-township-zoning.zoning.yaml`), land assembly (`aedg/seller-land-packets.land.yaml`), deeds via the recorder collection.
- For wilmington: parcel connector wired — **not verifiable / not found**; zoning connector — **not found**; footprint geometry — **not found**. GIS endpoint URLs live on the `SiteProfile` (not introspectable here).

## 5. Extracted corpus vs. source documents

- **Extracted: zero** (`list_extractions` → "No extractions found under `data/extracted/wilmington`").
- **Source documents: the 6 OEPA permit PDFs I just fetched** (now under `data/documents/oepa/wilmington/`), plus whatever was already staged outside the OEPA tree (`list_documents` still serves only Lima, so wilmington source beyond the OEPA fetch is **not found**).
- Net: source > extracted by exactly the 6 new permits; extraction backlog = **6 PDFs (+ 2 uncaptured DAM artifacts)**.

## 6. Hypothesis assessments

- No `hypotheses` content for wilmington (the `(site × hypothesis)` join has no populated cells; `retrieve_corpus(collection="hypotheses")` returned nothing, and the framework requires a registered site store).
- Lima parity (`retrieve_corpus`): boom-origin hypothesis evidence is assembled (`legal/select-committee-2026/witness-submissions.digest.yaml`, `legal/prr-mandamus/…response-index.yaml` — e.g. the "WWTP Data Center Flows Treatment Evaluation"). For wilmington: **every hypothesis cell is `[open]`.**

---

## Blocking gaps — must clear before `selectable` promotion

1. **Run `watermark onboard wilmington`** (scaffolds data dirs, runs portable reach connectors). This is the upstream unblock for hydrology + the per-site scaffolding — currently nothing has been run. *(Evidence: every hydrology/model surface empty.)*
2. **Confirm the `SiteProfile` is registered** in `watermark.sites.SITES` with the verifiable knobs (`nwis_sites`, `eia861_utility_number`, GIS URLs, `corpus_relpaths`). Per the bundle-per-site memo, a non-Lima site that omits `corpus_relpaths` silently inherits Lima feeds. *(Not introspectable via MCP — direct code check.)*
3. **Ingest + extract the 6 fetched OEPA permits** to `data/extracted/wilmington/oepa/*.npdes.yaml`, and identify each facility/receiving water from the document (do **not** assume the municipal WWTP). *(Triage lead drafted; see #6 below.)*
4. **EIA-861 utility number + grid basis** resolved and connector-run (BA interchange, LMP zone). *(Not found.)*
5. **NWIS gauge(s) + 7Q10 / water balance** populated for the receiving water. *(Not found.)*
6. **File the NPDES triage lead for real** — `report_novel_finding` could not post (no `GITHUB_TOKEN`). Re-file so the extraction backlog is tracked.

## Non-blocking gaps — good follow-up leads

- Pull the **two uncaptured DAM artifacts** (`1PD00013.fs.pdf` fact sheet, `1PD00013` draft PN) for fact-sheet/PN parity with Lima.
- **GIS footprint** — parcel/zoning connectors + recorded-ownership assemblage (FW-style) once a candidate site/owner is identified.
- **Land-assembly / zoning / commissioners** corpus — no Wilmington analog yet to Lima's `aedg/seller-land-packets`, `lacrpc` zoning, or commissioner resolution ledger.
- **Hypothesis cells** — populate the boom-origin `(site × hypothesis)` join once enough primary record exists.
- A non-`selectable` `/network/wilmington` page **degrades, not breaks** (readiness layer locks thin sections) — so promotion can wait on parity without harming the build.

**One caution on discipline:** grid/GIS/`SiteProfile` status above is "not found via the read-only tools available," not a positive finding of absence in the codebase — those knobs aren't introspectable through MCP. Treat them as open items to verify directly, not as confirmed-missing.
