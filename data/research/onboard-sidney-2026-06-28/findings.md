# Research run: onboard sidney

- model: `claude-opus-4-8`
- generated: 2026-06-28T17:28:35+00:00
- turns: 17 (cap 30); cost: $0.7827
- tools: ToolSearch, mcp__watermark__list_documents, mcp__watermark__list_extractions, mcp__watermark__entities, mcp__watermark__program_overview, mcp__watermark__timeline, mcp__watermark__hydrology_balance, mcp__watermark__retrieve_corpus
- proposals: 5 (see `manifest.yaml`)

---

I have enough to complete the assessment. One important methodological finding first: the semantic retrieval index is not responsive in this environment.

I probed `retrieve_corpus` with `site="lima"` across six filter combinations — including two known to exist in the Lima build (`recorder/deed`, `aedg/opc`) — and every call returned "No results found." The tool itself warns it "Requires the index to be built first (`watermark index`)." So the Lima-precedent retrieval step could not be executed, and the `report_novel_finding` trigger (retrieve_corpus surfacing un-extracted source context) never fired. I will **not** fabricate retrieved context or file leads citing sources I did not actually retrieve. The assessment below rests on the structured, site-scoped tools, which all responded.

---

# Onboarding Review — `sidney` watershed-point site

## Headline status `[verified]`

`sidney` is a **recognized but un-onboarded** site. Every site-scoped BOSC tool resolves the slug (so a profile is registered) but returns **zero committed artifacts**, explicitly deferring to the Lima reference build under the #424 non-substitution rule:

| Tool | Result for `sidney` |
|---|---|
| `list_documents` | "No committed source documents for site 'sidney' yet" |
| `list_extractions` | "No extractions found under data/extracted/sidney" |
| `entities` | "No committed entities for site 'sidney' yet" |
| `timeline` | "No committed timeline for site 'sidney' yet" |
| `hydrology_balance` | "No committed hydrology_balance for site 'sidney' yet" |
| `program_overview` | "No *.summary.opc.yaml extraction found" |
| `retrieve_corpus` (site=sidney) | "No results found" |

**Identity `[inference]`:** consistent with project memory, `sidney` is Sidney, Ohio, queued on the Great Miami / Mad River corridor (Miami-basin expansion epic **#440**, queued as **#481**) — registered/queued, not yet onboarded. The tools recognizing the slug confirms a `SITES` profile exists; the empty artifacts confirm onboarding has not run.

## Methodology caveat `[verified]`

The Lima-vs-sidney precedent comparison via `retrieve_corpus(site="lima")` **could not be performed** — the corpus index is unbuilt/unresponsive (6/6 probes empty, including known-good filters). The Lima baseline below is drawn from the **structured tool contracts** (what each Lima-serving tool exercises), not from invented figures. No `report_novel_finding` leads were filed: with no retrievable source context, any citation would be fabricated.

---

## 1. NPDES / permit profile

- **Lima baseline:** `oepa/npdes` extractions feed `hydrology_balance` (WWTP cited design flows → receiving waters → 7Q10 assimilative screen) and `sanitary_basis` (per-plant avg design + peak hydraulic capacity, I/I + consent-decree context).
- **sidney:** no `oepa`/`npdes` documents (`list_documents`), no extractions (`list_extractions`), no entities. **Gap: total** — no permit corpus, no receiving-water identification, no design flows.

## 2. Grid / utility profile

- **Lima baseline:** `reference/grid` — EIA-861 utility, BA interchange, LMP/pricing zone (per platform grid connectors).
- **sidney:** no `reference` grid artifacts committed; profile knobs (`eia861_utility_number`, BA, LMP zone) not verifiable as populated from any tool output. **Gap: unverified/absent.** Note `[reference]`: per project memory, non-Ohio leaks don't apply (Sidney is OH), but EIA-861S municipal short-form fallback should be checked if Sidney is muni-served.

## 3. Hydrology

- **Lima baseline:** NWIS gauges (`nwis_sites`) + cited 7Q10 drive `hydrology_balance`, `hydrology_scenario` (campus consumptive draw vs river 7Q10), `sanitary_basis`, `stormwater_runoff`, `tier1_swmm`.
- **sidney:** `hydrology_balance` returns empty/not-substituted; no NWIS configuration or 7Q10 evidenced. **Gap: total** — no gauges, no water balance, no low-flow screen.

## 4. GIS

- **Lima baseline:** parcel/zoning connectors + footprint geometry underpin `entities` (parcels) and the storm/grading plan inventory.
- **sidney:** no `recorder`/`gis` documents, no parcels in `entities`, no footprint geometry. **Gap: total.**

## 5. Extracted corpus

- **sidney:** `list_extractions` → nothing under `data/extracted/sidney`. With zero source documents ingested, there is nothing to extract or reconcile (`program_overview` empty). **Gap: total** — and correctly so, since extraction follows ingest.

## 6. Hypothesis assessments

- **Lima baseline:** the (site × hypothesis) join populates hypothesis cells for the reference build.
- **sidney:** no hypothesis artifacts surfaced; with an empty corpus every cell is **open**. **Gap: total.**

---

## Prioritized checklist

### Blocking (must clear before `selectable` promotion in `frontend/src/lib/sites.ts`)

1. **Run `watermark onboard sidney`** (runbook `docs/onboarding.md`) — scaffolds per-site data dirs and runs portable reach connectors. Nothing downstream is possible until this runs. `[verified: tools show zero artifacts]`
2. **Ingest the NPDES/permit corpus** (`data/documents/oepa/` or sidney-scoped equivalent) and extract → without it `hydrology_balance` and `sanitary_basis` have no design flows.
3. **Configure hydrology inputs** — `nwis_sites` + cited 7Q10 for Sidney's Great Miami receiving water; produce a committed `hydrology_balance`.
4. **Set `corpus_relpaths` and commit curated stores under a `sidney/` subdir.** Per project memory this is the documented onboarding trap: omit it and feeds silently inherit Lima or fall empty.
5. **Populate grid profile knobs** (`eia861_utility_number`, BA, LMP zone), verifying EIA-861 vs 861S short-form for Sidney's utility.
6. **Wire GIS** parcel/zoning connectors and commit footprint geometry — required for `entities` parcels.

### Non-blocking (good follow-up leads)

- Rebuild the **corpus index** (`watermark index`) — currently unresponsive, blocking all semantic retrieval / Lima-precedent comparison and the `report_novel_finding` workflow. Recommend resolving before the next onboarding pass.
- Seed hypothesis cells once corpus exists (Miami-basin buried-valley-vs-lake-plain thesis, epic #440).
- Confirm the Sidney #481 GH issue reflects "registered, pre-onboarding" status.
- Until parity, rely on the readiness layer to lock thin sections (`available|locked`) — **do not fake values to make the page look complete**; let sections lock and request the source.

---

**Bottom line:** `sidney` is a clean pre-onboarding profile — no fabricated status, just an empty registered slug. The single unblocking action is running the onboarding pass; promotion to `selectable` stays a manual, parity-gated edit and is far off. Separately, the retrieval index needs rebuilding before the Lima-comparison method this task prescribes can actually run.
