---
topic: onboard van-wert
model: claude-opus-4-8
generated: 2026-06-28T20:28:47+00:00
turns: 26
turns_cap: 30
cost_usd: 1.6299
proposals: 5
tools:
  - ToolSearch
  - mcp__watermark__program_overview
  - mcp__watermark__list_documents
  - mcp__watermark__list_extractions
  - Bash
  - Read
  - mcp__watermark__retrieve_corpus
  - mcp__watermark__hydrology_balance
---

I now have a complete, directly-sourced picture. Note on method before the findings: the `retrieve_corpus` semantic index returned no results across four distinct query/filter combinations (oepa/npdes, legal/testimony, oepa/npdes_fact_sheet), consistent with the index not being built in this environment (the tool warns it "requires the index to be built first"). I therefore assessed van-wert against Lima by direct reads of the committed tree and the active-scope MCP tools, and I cite those throughout. Because `retrieve_corpus` surfaced no un-extracted source context, the `report_novel_finding` trigger never fired — and the genuine van-wert gaps are already filed as #375–#379, so filing duplicates would be wrong.

---

# Onboarding review — Van Wert (`van-wert`)

**Status:** registered + scaffolded, **not promoted**. `frontend/src/lib/sites.ts` carries `van-wert` as `status: "queued"`, `selectable: false`, `issue: 363`. The MCP analysis layer confirms emptiness on the gating side: `list_documents`, `list_extractions`, `program_overview`, and `hydrology_balance` all report *"No committed … for site 'van-wert' yet … serves the 'lima' reference build, … not substituted (#424)."* The substance that does exist lives in `data/reference/**/van-wert/` and `data/extracted/van-wert/`, read directly below.

Profile of record: `src/watermark/sites/_profiles.py` `_VAN_WERT` (lines 443–533). Self-research first pass already ran (`data/research/onboard-van-wert-…-2026-06-19/`, 27 turns, $1.28) and distilled 5 proposals → GH **#375–#379** (all **OPEN**), under tracking issue **#363** (`status:blocked`, `area:network`).

---

## 1. NPDES / permit profile

| | van-wert | Lima baseline |
|---|---|---|
| Ingested OEPA permits/fact sheets | **0** — `data/extracted/van-wert/` holds only `ONBOARDING.md` + `README.md` | 3 fact sheets (American II `2PH00006`, American Bath `2PH00007`, Lima Refining `2IG00001`) under `data/documents/oepa/` |
| Cited receiving-stream 7Q10 | **none** | Dug Run 0.78, Pike Run 0.03, Ottawa 0.2 cfs — each `source: document`, high confidence (`data/reference/hydrology/low-flow-7q10.yaml`) |

- The Van Wert WWTP **is** present in the basin-wide ECHO reference inventory — `OH0027910` (POTW, receiving water TOWN CREEK, HUC-8 `04100007`) and a second permit `OH0135569` (CITY OF VAN WERT) (`data/reference/echo/maumee-wwtp.all-npdes.yaml`). But that is a **reference dataset row, not an ingested fact sheet**, and the Town Creek discharge row carries **`design_flow_mgd: null`, `design_flow_missing: true`**. `[verified]` the permit exists in ECHO; `[open]` its design basis.
- The profile's `receiving_water_name` cites *"Ohio EPA NPDES 2PD00006/OH0027910 → Town Creek (RM 13.87)"* — that is `[reference]` to an external record, **not** corpus-`[verified]`. The *"~4.0 MGD plant"* in the profile comment (line 436) is **uncited in-corpus** `[open]`.
- **Gaps vs Lima:** no ingested permit, so no cited design flow and no cited 7Q10 — the single most load-bearing omission for the site whose entire rationale is effluent dominance on a tiny tributary. Filed: **#375** (ingest OH0027910 + Town Creek 7Q10; verify design flow), **#379** (disambiguate OH0135569).

## 2. Grid / utility profile

**The most complete dimension — connector-sourced, high-confidence, parity with Lima's structure.**

- **EIA-861 (serving utility + retail):** AEP Ohio / Ohio Power Co **#14006**, PJM, PUCO-regulated; retail 48,652.9 GWh, 1,533,265 customers, 18.61 ¢/kWh (`data/reference/eia/van-wert/grid-profile.yaml`, `source: connector`, high). The *"Bryan trap"* (muni short-form filer) was checked and cleared — no City of Van Wert EIA-861S filer; AEP distributes. `[verified]`
- **BA interchange:** `ba_profile` = PJM, EIA-930 daily-demand annual sum **815,056.2 GWh** (2024), high. `load_share: null` **by design** — no disclosed facility, so no campus load to express. There is no separate `ba-interchange` artifact in the van-wert tree, but the BA layer the connector populates is present.
- **LMP zone:** profile `lmp_usd_mwh = 45.81`, pnode **AEP (8445784)**, PJM Data Miner 2 da_hrl_lmps 2025 DA annual mean, *connector-sourced* (`_profiles.py` 520–526). (The 2026-06-19 research run flagged an older `$35/MWh [inference]` value; the current profile carries the connector-verified $45.81 — treat as resolved.)
- **Consumer energy:** OH residential 16.96 ¢/kWh, NG 13.85 $/Mcf, retail sales 161,933.98 M kWh (`consumer-energy.yaml`, EIA API v2, high).
- **Same Ohio/AEP/PUCO/PJM axis as Lima and Findlay**, so the cross-state connector axis is *not* re-exercised. **No blocking grid gap.**

## 3. Hydrology

- **NWIS gauges configured `[verified]`:** `04191000` Town Creek near Van Wert (the WWTP receiving reach) and `04191003` Stripe Creek (`_profiles.py` 448–451).
- **Reach connectors that landed:** NASA-POWER climatology (`nasa-power-climatology.yaml`, annual precip ~2.61 mm/day) and NOAA Atlas-14 corridor DDF (`atlas14-corridor-ddf.yaml`, 24-hr 100-yr 5.48 in) — both connector/`[reference]`, present.
- **7Q10 — the central hole.** `low-flow-7q10.derived.yaml` carries only USGS-gaged **mainstems** (Maumee 114.15, Auglaize 1.91, St. Marys 15.65, St. Joseph 29.69 cfs, plus Miami/Scioto reaches). **Town Creek appears in neither the cited nor the derived table**, and the receiving-reach gage `04191000` is not among the derived gages. So the discharger that defines the site is unscreened against its own water. `[open]`
- **Water-balance status: none.** Profile `plant_receiving = {}`, `supply_gage_primary/secondary = "TODO"`, `passby_*_cfs = 0.0` — the balance model is not designed for van-wert, and `hydrology_balance` confirms *"No committed hydrology_balance for site 'van-wert' yet."*
- **basin-screen:** ran 7/129 dischargers (1 violation, 2 tight; `ONBOARDING.md` line 22); `[inference]` OH0027910 was either not among the 7 or screened against a mainstem proxy that overstates dilution by orders of magnitude.
- **SSURGO HSG skipped** (no footprint to weight); `dominant_hsg = "D"` is `[inference]` (Black Swamp lake-plain clays), not SSURGO-confirmed.
- Filed: **#375** (Town Creek 7Q10), **#376** (re-screen + record dilution ratio).

## 4. GIS

- **Parcels / zoning: not wired.** `parcels_url = "TODO"`, `zoning_url = "TODO"`, `gis_parcel = None`, `gis_zoning = None` (`_profiles.py` 459–465). The Van Wert County PAT MapServer (`ags.bhamaps.com`, Bruce Harris & Assoc.) exists but its **TLS certificate is expired** — `cached_get`/httpx can't consume it, and *don't weaken TLS for it* (`ONBOARDING.md` GIS table). No City of Van Wert zoning REST catalog found.
- **Flood: wired** — shared national FEMA NFHL (layer 28), `gis_flood = NATIONAL_NFHL_FLOOD_SCHEMA` with `reference_dir: van-wert-gis`. `[verified]`
- **Footprint geometry: absent.** `footprint_relpath` → `extracted/van-wert/bosc-site-footprint.yaml` is **not present** (Lima has `data/extracted/plans/bosc-site-footprint.yaml`; Fort Wayne has `data/extracted/fort-wayne/bosc-site-footprint.yaml` — van-wert has neither footprint nor `parcels_relpath` geometry; `data/reference/van-wert/` holds only a README). `[open]` — pending an identified site.
- The footprint absence is also why SSURGO HSG (§3) was skipped — these are coupled.

## 5. Extracted corpus

- **Zero structured extractions and zero ingested source documents** for van-wert (`list_extractions` / `list_documents` empty; `data/extracted/van-wert/` = docs only; no `data/documents/van-wert/`). Contrast Lima's full corpus (aedg OPC estimates, recorder deeds, oepa, commissioners minutes, etc.).
- **Data-center activity is documented only secondhand, through Allen-County instruments** — there are **zero Van-Wert-jurisdiction primary documents** in the corpus:
  - **QTS** — $10B Van Wert County campus, up to 4,500 construction jobs, closed-loop cooling (~600,000 gal/yr office only): **proponent testimony**, `qts-2026-06-03.pdf` → `data/extracted/legal/select-committee-2026/witness-submissions.digest.yaml`. `[verified]` the claim is in the record; figures are proponent, BOSC-unverified.
  - **Thor Equities** — *"also doing a Van Wert data center; brought by AEP,"* 1-yr LOI 2025-03-27 @ $50K/ac on Perry Industrial Park (Allen County): `data/extracted/aedg/paac-board-minutes.minutes.yaml`. `[verified]` documented.
  - `[open]` whether QTS and Thor name the **same project** — the witness digest *flags* a tie (line 120) but no instrument establishes it. **Do not merge**, and **do not import the Allen-County Bistrozzi/Montfort/Ziance graph into van-wert** without a filed bridge — separate register.
- RSEI county-scale toxics did land (`rsei/van-wert/inventory.yaml`, EPA RSEI v234, FIPS 39161, 14 facilities) — useful industrial-corridor background (top scores Sonoco Fibre Drum, Kennedy Mfg, both TCE-driven, both closed series), but it is an EPA-modeled comparative index, **not** a discharge screen and **not** a substitute for the Town Creek gap. Profile `toxic_corridor_bbox` is still `(0,0,0,0)` `[open]`.
- Filed: **#377** (QTS primary instrument or formal negative-search record), **#378** (QTS↔Thor resolution).

## 6. Hypothesis assessments

Per-site cells live at `data/hypotheses/<hypothesis>/<slug>.yaml`:

- **H1 water:** `data/hypotheses/water/` carries **no per-site cells by design** — the water lens is rendered from the site registry + basin network by drainage, so van-wert participates without a cell. *Not a gap.*
- **H2 defense:** **no `defense/van-wert.yaml`** (present: columbus, lima, lordstown, new-albany, springfield, wpafb). **Open.**
- **H3 surveillance:** **no `surveillance/van-wert.yaml`** (present: columbus, hamilton-middletown, lima, new-albany). **Open.**

Both empty cells are authored by hand or promoted from `bosc research run --recipe hypothesis-assessment`. Non-blocking — but note a defensible H2/H3 cell requires ≥1 citation, which currently doesn't exist for van-wert beyond the secondhand QTS/Thor threads.

---

## Prioritized gap checklist

### Blocking — must clear before `selectable: true` (parity-gated manual edit)

1. **Ingest the OEPA NPDES permit/fact sheet for Van Wert WWTP `OH0027910` (`2PD00006`)** and extract a **cited Town Creek 7Q10** into `low-flow-7q10.yaml` (`source: document`); verify the **design flow** (ECHO shows `null`; profile's ~4.0 MGD is uncited). — **#375**
2. **Re-run `basin-screen`** so `OH0027910` is screened against Town Creek's *own* 7Q10, and record the dilution ratio. Until then any "effluent-dominated" statement is `[inference]`, not a finding. — **#376**
3. **Obtain ≥1 Van-Wert-jurisdiction primary document for the data-center activity** (a QTS county/city ED filing, CRA/PILOT, recorder instrument) to move the $10B claim from *testimony* to *documented instrument* — or commit a **formal negative-search record** to `ONBOARDING.md`. — **#377**
4. **Clear the `ONBOARDING.md` review gate** itself: every written reference value reviewed against a cited source; basin-screen coverage confirmed sane. (4 of the 6 gate boxes are unchecked.)

### Non-blocking — good follow-up leads

5. **Disambiguate `OH0135569` (City of Van Wert)** — permit type, receiving water, whether it belongs in the screen denominator. — **#379**
6. **Resolve the QTS↔Thor "same project?" question** with a primary document, not the digest flag or an aggregator profile. — **#378**
7. **GIS lift:** re-probe the County PAT MapServer once its TLS cert renews (or fall back to the Engineer's-office parcel shapefile) and register a `GisParcelSchema`; locate a City of Van Wert zoning layer or formally accept map-only. *(Tracked only in `ONBOARDING.md` today — no GH issue; recommend filing one.)*
8. **SSURGO HSG confirmation** once a footprint exists — upgrades `dominant_hsg D` from `[inference]` to a cited area-weighted value (coupled to the footprint/GIS work above).
9. **Author H2 (defense) and H3 (surveillance) hypothesis cells** for van-wert (hand or `--recipe hypothesis-assessment`), each with ≥1 citation; gated on item 3 producing a citable instrument.
10. **Set `toxic_corridor_bbox`** once an industrial corridor on Town Creek is identified.

**Bottom line:** van-wert is a cleanly-scaffolded *queued* site whose **grid dimension is parity-complete** and whose **hydrology reach data is present but missing the one denominator that matters** (Town Creek 7Q10). Promotion is correctly blocked: the receiving-water screen has a hole exactly where the site's thesis lives (#375/#376), and the data-center dimension rests entirely on secondhand Allen-County records with no Van-Wert-jurisdiction primary document (#377). No fabricated status was supplied for any absent value; absences are reported as "not found" / `[open]` with their tracking issues.
