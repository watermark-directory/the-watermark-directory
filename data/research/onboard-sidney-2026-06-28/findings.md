---
topic: onboard sidney
model: claude-opus-4-8
generated: 2026-06-28T20:14:44+00:00
turns: 22
turns_cap: 30
cost_usd: 0.9948
proposals: 5
tools:
  - ToolSearch
  - mcp__watermark__list_documents
  - mcp__watermark__list_extractions
  - mcp__watermark__entities
  - mcp__watermark__timeline
  - mcp__watermark__program_overview
  - mcp__watermark__hydrology_balance
  - mcp__watermark__hydrology_scenario
  - mcp__watermark__sanitary_basis
  - mcp__watermark__storm_plan_inventory
  - mcp__watermark__stormwater_runoff
  - mcp__watermark__tier1_swmm
  - mcp__watermark__retrieve_corpus
---

I now have a complete picture: sidney is greenfield across every subsystem, and I've established the Lima reference baseline for all six areas. 

A note on `report_novel_finding`: I did **not** fire it. The trigger is *unextracted source-document context for this site*. Every Lima retrieval above resolved to an already-extracted artifact (`data/extracted/...` provenance), and sidney has zero indexed source corpus, so there was no unextracted sidney source context to triage. Filing Lima's own documents as sidney "findings" would cross-contaminate two investigative threads — which the evidentiary discipline forbids absent an explicit bridge. I'm recording that decision rather than manufacturing a trigger.

---

# Onboarding Review — `sidney` watershed-point site

**Assessment date:** 2026-06-28 · **Reference build:** `lima` · **Method:** read-only BOSC tools + `retrieve_corpus(site="lima")` precedent pulls

## Status at a glance

`sidney` is **registered/queued but fully greenfield**. Every site-scoped BOSC tool returns the `#424` non-substitution message ("This tool serves the 'lima' reference build, which is not substituted for another site… onboard sidney's corpus/scenario to populate it"). No source documents, no extractions, no entities, no timeline, no hydrology cells.

- `list_documents` → no committed source documents for `sidney` `[verified]`
- `list_extractions` → "No extractions found under `data/extracted/sidney`" `[verified]`
- `entities`, `timeline` → site-scoped empty `[verified]`
- `hydrology_balance`, `hydrology_scenario`, `sanitary_basis`, `storm_plan_inventory`, `stormwater_runoff`, `tier1_swmm` → all site-scoped empty `[verified]`
- `program_overview` → "No `*.summary.opc.yaml` extraction found" `[verified]`

**Context** `[reference]`: sidney is the Great Miami / Mad River corridor site queued under the Miami-basin expansion epic **#440** (issue **#481**, alongside Darke **#482**) — not yet run through `watermark onboard`. Its receiving water is the Great Miami system, **not** Lima's Ottawa River; do not inherit Lima's hydrology constants.

---

## 1. NPDES / permit profile

**Lima baseline** `[verified]` — a multi-plant OEPA NPDES record under `data/extracted/oepa/`:
- American II WWTP — `2PH00006` / `OH0037338` (fact sheet + draft public notice 2025-04)
- American Bath WWTP — `2PH00007` / `OH0023841` (fact sheet + draft public notice 2024-03)
- Shawnee II WWTP — `2PK00002` / `OH0023850` (draft public notice 2026-03)
- ECHO DMR effluent record pattern (`watermark dmr <id>`), e.g. peer Fort Wayne `IN0032191`

**sidney status:** nothing pulled. No fact sheets, no public notices, no DMR. `[verified]`

**Gap:** sidney needs its WWTP NPDES inventory identified (OEPA permit IDs for the Sidney-area plant(s) discharging to the Great Miami), the fact-sheet/public-notice PDFs ingested under `oepa/` (Ohio jurisdiction), and `watermark dmr` run for the actual-vs-design flow record. Also the basin NPDES inventory (`watermark npdes --basin <miami>`) for the receiving reach.

## 2. Grid / utility profile

**Lima baseline** `[reference]`: per-site `SiteProfile` knobs — `eia861_utility_number` (EIA-861 sales / Short_Form fallback for muni/coop), BA interchange (PJM-930), and an LMP/pricing zone — plus the federal net-gen/price reference pulls. Grid reference data lives in `data/reference/`, not the document corpus, so `retrieve_corpus` surfaced only adjacent plan/permit text — expected, not a gap signal.

**sidney status:** no `SiteProfile` grid knobs verifiable as populated; no committed grid reference outputs for sidney. `[verified]` (inferred-empty from the universal `#424` scope wall and absence of any `sidney`-scoped output).

**Gap:** identify Sidney's serving utility and its EIA-861 number (watch the **muni short-form** case — Sidney is a home-rule municipal possibility; see the EIA-861S fallback precedent), confirm the **AEP/PJM** BA and the correct LMP zone, then run the grid/consumer-energy connectors. **Re-scan for Ohio-hardcoding is lower risk here** (sidney is Ohio, like Lima), but the demand-pressure facility leak noted for non-Lima sites still warrants a check.

## 3. Hydrology

**Lima baseline** `[verified]`: WWTP design-flow → receiving-water balance with cited **7Q10** low-flow screen (`hydrology_balance`), data-center consumptive-draw scenario vs the Ottawa 7Q10 (`hydrology_scenario`), document-cited `sanitary_basis` (consent-decree / I&I context), and the Tier-0/Tier-1 stormwater stack (`stormwater_runoff`, `tier1_swmm`) driven by live NOAA Atlas-14.

**sidney status:** every hydrology tool site-scoped empty. No NWIS gauges configured, no 7Q10, no water balance, no stormwater run. `[verified]`

**Gap:** configure `nwis_sites` for the Great Miami reach near Sidney, establish the receiving-water 7Q10, and run the portable reach connectors via `watermark onboard sidney`. The campus stormwater/sanitary tiers stay `[open]` until a sidney site footprint + civil plan exist (see §4–5).

## 4. GIS

**Lima baseline** `[verified]`: a transcribed developed/impervious **site footprint** from the stormwater permit, recorder deeds (`data/extracted/recorder/`), and an Allen County OGRIP parcel/zoning basis; the Fort Wayne peer demonstrates the fallback (recorded-ownership assemblage as boundary when the stormwater permit isn't yet in corpus).

**sidney status:** no parcel/zoning connectors wired, no footprint geometry, no deeds. `[verified]`

**Gap:** wire Sidney's county (Shelby County, OH) parcel/zoning GIS — **verify situs city + state from a live sample before wiring** (the same-name-county-wrong-state hazard); OGRIP `County='Shelby'` is the OH parcel substitute. Footprint `parcel_acres`/developed/impervious stay `[open]` pending a recorded assemblage or stormwater permit. If no project site is yet identified for Sidney, this is a candidate-siting task, not a transcription task.

## 5. Extracted corpus

**Lima baseline** `[verified]`: deep, multi-collection — `aedg/` (Tetra Tech OPC estimates + roadwork development agreement), `recorder/` deeds, `lacrpc/` zoning + meeting summaries, `commissioners/` resolution ledger, `regulatory/` wastewater-enforcement history, `legal/` (CRA agreement, PRR mandamus, select-committee hearings), `watershed/`, `permits/`.

**sidney status:** `data/extracted/sidney` does not exist; zero extractions. `[verified]`

**Gap:** there are no sidney source documents to extract yet — this is upstream of extraction. First obtain the Sidney project's primary instruments (any development agreement / OPC, deeds, local zoning, commissioners/council minutes) before the extract pipeline applies.

## 6. Hypothesis assessments

**Lima baseline** `[reference]`: the (site × hypothesis) join exists (`bosc.hypotheses` + `data/hypotheses/` + bundle feeds, contract ≥1.5.0); Lima's boom-origin cells are populated and evidence-linked (e.g. enforcement-history, hearing testimony, zoning-amendment causation).

**sidney status:** no populated hypothesis cells. `[verified]` All boom-origin hypothesis cells for sidney are **open**.

**Gap:** sidney's hypothesis row is empty by construction until §1–5 produce evidence to link. Expected for a queued site; not independently actionable yet.

---

## Prioritized checklist

### Blocking gaps — must resolve before promotion to `selectable`

The frontend readiness layer will (correctly) lock a thin sidney site; **do not fake values to make it look complete** — let sections lock and supply the source. Promotion is a manual, parity-gated edit to `frontend/src/lib/sites.ts`.

1. **Run `watermark onboard sidney`** — scaffold per-site data dirs, set `corpus_relpaths`, and execute the portable reach connectors. Without this, every bundle feed inherits Lima or falls empty (the documented onboarding gotcha). *(Blocks all of §1–6.)*
2. **NWIS gauges + receiving-water 7Q10** for the Great Miami reach (§3) — the hydrology spine; nothing downstream computes without it.
3. **Serving-utility + EIA-861 number** resolved and grid connectors run (§2), including the muni short-form check.
4. **WWTP NPDES identity** — OEPA permit ID(s) for the Sidney-area plant, fact sheet + public notice ingested under `oepa/`, and `watermark dmr` run (§1).
5. **County GIS wired + situs verified from a live sample** (Shelby County OGRIP), so parcel/zoning resolves (§4).
6. **At least one primary project instrument extracted** into `data/extracted/sidney/` (§5) so the site has a verifiable evidentiary anchor rather than connector-only scaffolding.

### Non-blocking gaps — good follow-up leads

- **Site footprint geometry** (developed/impervious acreage) — stays `[open]` until a stormwater permit or recorded assemblage exists; use the Fort Wayne ownership-assemblage fallback if a project is identified but the civil plan isn't in corpus.
- **Tier-1 SWMM / sanitary surcharge** (§3) — deferred until a footprint + civil/storm plan are in corpus.
- **Local legislative record** — Sidney/Shelby County council + commissioners minutes via the civic pipeline (the Lima `commissioners/` + `lacrpc/` analog).
- **Basin NPDES inventory** — `watermark npdes --basin <miami>` for the broader receiving reach (Miami-basin context, epic #440).
- **Hypothesis cells** (§6) — populate once §1–5 yield linkable evidence.

### Process note

No `report_novel_finding` issues were filed: no unextracted **sidney** source-document context surfaced (sidney's corpus is empty and all retrievals were Lima extractions). The leads above are onboarding gaps to be tracked under the queued-site issue **#481** / Miami-basin epic **#440**, not novel-finding triage tickets.

**Bottom line:** `sidney` is a registered-but-thin site at step zero — the correct next action is `watermark onboard sidney`, after which the connector-driven sections (hydrology, grid, NPDES) can populate and the document-driven sections (corpus, GIS footprint, hypotheses) can begin once primary instruments are obtained. It is **not** promotable to `selectable` today, and the readiness layer should lock it accordingly.
