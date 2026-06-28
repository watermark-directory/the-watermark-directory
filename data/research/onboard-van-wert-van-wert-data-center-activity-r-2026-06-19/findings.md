# Research run: onboard van-wert (Van Wert): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-19T19:49:10+00:00
- turns: 27 (cap 30); cost: $1.2770
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__timeline, Grep, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I now have what I need across the onboarding artifacts, the reference data, and the two primary-source document threads. Here is the findings report.

---

# Findings — Onboarding `van-wert`: data-center activity + receiving-water screen

**Scope.** Whether the Van Wert watershed point is ready to promote as a BOSC network site, assessed on its two load-bearing dimensions: documented data-center activity, and a receiving-water (assimilative) screen. Read-only pass over the BOSC corpus + the committed onboarding scaffold.

## Bottom line up front

- Van Wert is **scaffolded but not promoted** (`status`/`selectable` still gated in `frontend/src/lib/sites.ts`). The portable reach connectors (hydrology, economics, RSEI, grid) ran and committed cited reference data; the **data-center activity dimension and the per-jurisdiction GIS dimension are unchecked** (`data/extracted/van-wert/ONBOARDING.md`).
- **Data-center activity is real and documented in the record — but only secondhand, through Allen-County documents.** Two distinct proponent threads name Van Wert: **QTS** (a $10B campus, sworn-equivalent committee testimony) and **Thor Equities** (a developer "also doing a Van Wert data center," PAAC board minutes). **`[verified]`** that both threads exist in the corpus; **`[open]`** whether they are the same project, and **`[open]`** at the parcel/entity level entirely — there are **zero Van-Wert-jurisdiction primary documents** in the ingested corpus (a `list_documents` search returns no Van Wert match).
- **The receiving-water screen has a hole exactly where this site is most interesting.** Van Wert was chosen as the basin's *effluent-dominance* end-member — a ~4.0 MGD plant on a tiny tributary (Town Creek). But **Town Creek has no cited or derived 7Q10 in the corpus**, so the very discharger that motivates the site is **not actually screened against its own receiving water**. The "4.0 MGD" plant size is itself **uncited** in-corpus.

---

## 1. Site provenance and onboarding status

The Van Wert `SiteProfile` is registered (`src/bosc/sites.py` `_VAN_WERT`, lines 767–857) with geography sourced and tagged: basin `maumee`, Town Creek → Little Auglaize → Auglaize → Maumee, HUC-8 `04100007` **`[verified]`**; city centroid 40.8696, −84.5829 **`[verified]`**; RSEI/econ FIPS `39161` (Van Wert County) **`[verified]`**; serving utility AEP Ohio / Ohio Power Co #14006, PJM AEP zone **`[verified]`** — so the cross-state connector axis is *not* re-exercised (Van Wert is an Ohio/AEP/PUCO site, like Lima and Findlay).

Last `bosc onboard` run (`data/extracted/van-wert/ONBOARDING.md`):

| dimension | status |
|---|---|
| Hydrology (low-flows, corridor DDF, climatology) | **done** |
| Economics (baseline, RSEI, consumer-energy, grid) | **done** |
| Data-center activity (permits/records + entity graph) | **`[ ]` not started** |
| Per-jurisdiction GIS (parcels/zoning) | **`[~]` partial** — flood = shared national NFHL; parcels/zoning `[open]` |
| SSURGO HSG | **skipped** — no site footprint to weight against |

Two GIS blockers are documented and concrete: the Van Wert County PAT MapServer (Bruce Harris & Assoc.) **exists but its TLS certificate is expired**, so `cached_get`/httpx can't consume it; no City of Van Wert zoning REST catalog was found (`ONBOARDING.md` GIS-discovery table).

---

## 2. Data-center activity

### 2a. QTS — $10B Van Wert County campus `[verified that the claim is in the record]`

Source: **`qts-2026-06-03.pdf`**, witness **John Smith, J.D. (Government Relations, QTS)**, testimony dated **2026-06-03** to the Ohio Select/Joint Committee on Data Centers (`data/extracted/legal/select-committee-2026/witness-submissions.digest.yaml`, lines 112–120). The witness's own claims:

- **"$10B QTS data-center campus announced in Van Wert County"**, up to **4,500 construction jobs**; 90+ facilities nationally.
- Closed-loop cooling → "does not require additional water" in operation; **~600,000 gal/yr** domestic (office) only; pays interconnection + upgrade costs (BYONG).

These are **proponent figures, not BOSC-verified** — the neutral assessment in `docs/legal/proponent-analysis.md` (QTS section, lines 81–108) treats the $10B capital claim as `solid`, the closed-loop water claim as **`solid but design-specific`** (a closed-loop design ≠ the evaporative 36-cooling-tower design the Lima air permit shows), and notes QTS, like Google, **does not address beneficial-ownership / per-site end use**. The digest explicitly flags the cross-thread tie: *"Van Wert ties to PAAC minutes' Thor Equities (a data-center developer 'working with Van Wert')"* (line 120).

### 2b. Thor Equities — a second, separate thread `[verified that it is documented]`

Source: **PAAC (Port Authority of Allen County) board minutes** (`data/extracted/aedg/paac-board-minutes.minutes.yaml`, line 77), provenance `data/documents/aedg/PRR-01-bundle.ocr.pdf`:

> **Thor Equities** — Perry Industrial Park (remainder, N of power line); real party "**data-center developer (also doing a Van Wert data center; brought by AEP)**"; **1-yr LOI 2025-03-27 @ $50K/ac**.

`docs/COURSE.md` (lines 116–118) gathers this as a "parallel consumers (other counties)" thread: **"Thor Equities / Thor Van Wert / Highland55 (Urbana, Van Wert); CyrusOne; Platon Investments / Dynamo Ventures"** — and states the status plainly: corridor **`[open]`; no in-corpus document yet** (the Platon/Dynamo leg rests on a third-party aggregator profile, not a primary instrument).

### What the data-center record does and does not establish

- **`[verified]`** Two named proponents (QTS, Thor Equities) are tied to Van Wert County in the corpus, via two independent Allen-County primary documents (committee testimony; PAAC minutes).
- **`[inference]`** The corpus itself *flags* a QTS↔Thor tie (witness digest line 120), but the documents do not establish that the QTS $10B campus and the Thor "Van Wert data center" are the **same project**. Do not merge them. The Thor entry is the only one with a dated instrument (an LOI at $50K/ac); the QTS entry is an announcement figure in testimony.
- **`[open]` — the whole entity/parcel layer.** There is **no Van Wert deed, NPDES applicant, shell-LLC, CRA, or zoning record** in the corpus. The Allen-County pattern (Bistrozzi/Tilted Gate/Magenta land assembly, shared organizers Montfort/Ziance, EMH&T/Vorys) is **a separate register** and must not be cross-referenced into Van Wert without an evidentiary bridge. `COURSE.md` notes only a *shared-organizer overlap with Montfort* on the unrelated Platon/Dynamo thread — an inference resting on an aggregator profile, not a filed instrument.

---

## 3. Receiving-water screen

### 3a. The receiving water is identified; its design low flow is not

The Van Wert WWTP is in the corpus's ECHO inventory: **VAN WERT WWTP, NPDES `OH0027910`, FRS `110006645176`, POTW**, HUC-8 `04100007` (Auglaize), receiving water **TOWN CREEK** (`data/reference/echo/maumee-wwtp.all-npdes.yaml`, the OH0027910 record ~line 19714, and a Town Creek discharge row ~line 18576). A separate **CITY OF VAN WERT `OH0135569`** permit also appears (line 18216) — likely a distinct MS4/industrial coverage worth disambiguating.

Two figures that the profile carries are **not grounded in the corpus**:

- **Design flow ~4.0 MGD.** The profile comment (`sites.py` line 760) describes "a 4.0 MGD plant," but the ECHO record for the Town Creek discharge shows **`design_flow_mgd: null`, `design_flow_missing: true`** (`maumee-wwtp.all-npdes.yaml` line 18574). **`[open]`** — the 4.0 MGD is uncited; it needs the actual Ohio EPA NPDES permit/fact sheet, which is **not in the corpus** (every `oepa/` extraction is a Lima plant — American II/American Bath/Shawnee II).
- **RM 13.87 / permit `2PD00006`.** Cited in the profile's `receiving_water_name` field as `[verified]` against "Ohio EPA NPDES 2PD00006/OH0027910 → Town Creek (RM 13.87)," but the **underlying fact sheet is not an ingested document** — the citation is to an external record, so it reads as `[reference]`, not corpus-`[verified]`.

### 3b. Town Creek is missing from both 7Q10 tables — the screen's central gap

This is the load-bearing finding. The receiving-water screen denominators live in two files:

- **Cited regulatory 7Q10s** (`data/reference/hydrology/low-flow-7q10.yaml`): only **Dug Run (0.78 cfs), Pike Run (0.03 cfs), Ottawa River (0.2 cfs)** — all Lima fact-sheet-sourced (`source: document`, high confidence). **No Town Creek.**
- **Derived basin 7Q10s** (`low-flow-7q10.derived.yaml`): only the four USGS-gaged **mainstems** — Maumee 114.15, Auglaize 1.91, St. Marys 15.65, St. Joseph 29.69 cfs (LP3, `source: derived`, confidence **medium**, gage-proxy not discharge-reach). **No Town Creek.**

The onboard `basin-screen` step reports **"7/129 dischargers screened (1 violation, 2 tight)"** (`ONBOARDING.md` line 21). Because Town Creek appears in **neither** 7Q10 table, the Van Wert WWTP — a small-tributary discharger that is the *entire rationale* for picking this site as the basin's effluent-dominance end-member — **`[inference]` was almost certainly not among the 7 screened**, or was screened only against a mainstem proxy that overstates available dilution by orders of magnitude. (Stated as an inference: I read the two denominator files and the screen's coverage count, not the literal per-discharger output rows.) The Lima precedent shows why this matters — American II's stated acute dilution ratio is 1.3:1 and Pike Run's 7Q10 is 0.03 cfs (effluent effectively undiluted). A ~4 MGD (~6.2 cfs) discharge to a headwater creek is squarely in that regime, and the corpus currently cannot quantify it.

### 3c. Supporting reach data that *did* land (high confidence where tagged)

- **Climatology** (`reference/hydrology/van-wert/nasa-power-climatology.yaml`): NASA POWER normals at 40.87/−84.583, annual precip 2.61 mm/day, mean T 10.48 °C — connector-sourced.
- **Design-storm DDF** (`reference/hydrology/van-wert/atlas14-corridor-ddf.yaml`): NOAA Atlas-14 point depths, e.g. 24-hr 100-yr **5.48 in**, 24-hr 2-yr 2.56 in — `[reference]` HDSC query.
- **Soils**: dominant HSG **D** is tagged **`[inference]`** (Black Swamp lake-plain clays), *pending an SSURGO area-weighted confirmation that the onboard step skipped for want of a footprint* (`sites.py` lines 799–804). Do not promote the HSG as verified.

### 3d. RSEI toxics context (county-scale, EPA-modeled — not a discharge screen)

`reference/rsei/van-wert/inventory.yaml` (EPA RSEI v234, county FIPS 39161, 14 facilities/13 scored). Highest modeled Risk-Screening Scores: **Sonoco Fibre Drum (399,575)** and **Kennedy Manufacturing (187,191)**, both TCE-driven, both **closed reporting series (1988–1994 / 1988–2000)**. Only three facilities report any water/POTW pathway (**Eaton Aeroquip** `water_releases: true`, potw 256,383 lb cumulative; **GKN Sinter Metals**, NPDES OHR000003; **Bunge NA / Delphos**). Caveats per the file: Score is EPA's modeled, population-weighted, **comparative-only** index — not a risk or concentration, and not an effluent screen. Useful as industrial-corridor background; it does **not** substitute for the Town Creek assimilative gap. Note the profile's `toxic_corridor_bbox` is still `(0,0,0,0)` `[open]`.

---

## 4. Economic / grid baseline (brief, high confidence)

`reference/economics/van-wert/baseline.yaml` — BLS QCEW 2023 + Census ACS, all `confidence: high`: **11,586 jobs / 660 establishments**; manufacturing LQ **3.14** (an export-oriented manufacturing county); **Information sector 21 jobs, LQ 0.09** (i.e., effectively no incumbent data-center/IT base — consistent with a greenfield announcement). County population **28,824 (2023)**, gently declining since 2010. Grid (`reference/eia/van-wert/grid-profile.yaml`): AEP Ohio / PJM, EIA-861/930 connector values high-confidence; the file correctly notes **no documented data-center facility → no campus load share** can yet be expressed. The LMP $35/MWh in the profile is `[inference]` (shared AEP-zone value with Lima, flagged "verify").

---

## 5. Reconciliation / data-quality notes

- **No OPC/estimate artifacts** exist for Van Wert, so `program_overview`/`reconcile_*` are not applicable here (those read the Lima Tetra Tech summary).
- The BOSC MCP analysis tools (`entities`, `timeline`, `list_extractions`) are **Lima-scoped** (`WATERMARK_SITE=lima`); they do not surface the Van Wert scaffold at all. Anyone auditing Van Wert through the tool layer alone would wrongly conclude the site is empty. The data lives in `data/reference/**/van-wert/` and `data/extracted/van-wert/` and must be read directly until a Van Wert analysis scope exists.

---

## Recommended follow-up investigations (track as issues)

**Receiving-water (highest priority — closes the screen's central hole)**
1. **Ingest the Ohio EPA NPDES record for Van Wert WWTP `OH0027910` / permit `2PD00006`** (permit + fact sheet) and extract the **Stream Flows table** to add a **cited Town Creek 7Q10** to `low-flow-7q10.yaml`. This is the single change that makes the site's headline thesis (effluent-dominated tributary) defensible. Verify the **~4.0 MGD design flow** at the same time — it is currently uncited.
2. **Re-run `basin-screen` after (1)** and confirm OH0027910 is screened against Town Creek's own 7Q10; record the dilution ratio. Until then, treat any "Van Wert is effluent-dominated" statement as `[inference]`, not a finding.
3. **Disambiguate `OH0135569` (CITY OF VAN WERT)** from the WWTP — identify whether it's an MS4/stormwater or industrial permit; map both outfalls to receiving reaches.
4. **Run SSURGO with a real footprint** once a candidate parcel exists, to upgrade dominant HSG from `[inference] D` to a cited area-weighted value.

**Data-center activity / entity graph**
5. **Obtain the QTS Van Wert primary record** — the actual project announcement / Van Wert County or City economic-development filing / any CRA or PILOT — to move the $10B campus from *testimony claim* to *documented instrument*, and to fix its location (parcel/site).
6. **Trace the Thor Equities "Van Wert data center"** independently of the Perry-Industrial-Park LOI: Van Wert County recorder + ODOD/CRA records. Resolve the **`[open]` QTS↔Thor "same project?" question** with a document, not the digest's flag.
7. **Open a Van Wert deed/shell-LLC pull** (Van Wert County recorder) for any data-center land assembly; keep it a **separate register** from the Allen-County Bistrozzi graph unless a filed instrument bridges them. Do not import the Montfort/Ziance/EMH&T overlap (it rests on an aggregator profile per `COURSE.md`).

**GIS / infrastructure**
8. **Re-probe the Van Wert County PAT MapServer once its TLS cert renews** (or fall back to the Engineer's-office parcel shapefile), then register a `GisParcelSchema`; locate a City of Van Wert zoning layer or formally accept map-only. (`parcels_url`/`zoning_url`/`gis_parcel`/`gis_zoning` are all `TODO/None`.)

**Promotion gate**
9. **Do not flip `status`→`live`/`selectable`→`true`** until items 1–2 (cited Town Creek 7Q10 + real screen) and at least item 5 (a documented data-center instrument) clear the blocking review checklist. Promotion remains a manual, parity-gated edit; onboarding never auto-promotes.

**Note on figures:** county employment/population/grid values are connector-sourced **high-confidence**; the QTS **$10B / 4,500 jobs / ~600,000 gal-yr** are **proponent claims** (witness's own, unverified); the Lima cooling-basis **~3–10 MGD** consumptive figure carries its `~` approximate marker and belongs to the *Lima* site, not Van Wert; RSEI scores are **EPA-modeled comparative indices**, not concentrations. The **4.0 MGD** plant size and **HSG D** are currently **uncited/`[inference]`** and should not be published as verified.
