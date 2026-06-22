# Research run: onboard wilmington (Wilmington): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T04:11:29+00:00
- turns: 30 (cap 30); cost: $1.0079
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, Grep, Glob, Read, Bash
- proposals: 5 (see `manifest.yaml`)

---

I now have a complete, evidence-grounded picture. Here is the findings report.

---

# Findings — Onboarding Wilmington (OH): data-center activity + receiving-water screen

**Scope note.** The read-only BOSC MCP corpus tools (`entities`, `timeline`, `program_overview`, the `hydrology_*` family) are scoped to the **active site — Lima/Allen County, Ohio**. They return zero Wilmington content: `entities` resolves only Lima parties and three Lima receiving waters (Dug Run, Pike Run, Ottawa River); the ingested document list has **0** "wilmington" mentions. Everything below about Wilmington therefore comes from the **repo's per-site onboarding artifacts** (the `wilmington` `SiteProfile` in `src/bosc/sites.py` and the `data/reference/**/wilmington/` + `data/extracted/wilmington/` trees), which is where `bosc onboard wilmington` (#326 / #492, epic #440) writes. I read every committed Wilmington reference file.

## 1. Onboarding status — partially complete, not promoted `[verified]`

Per `data/extracted/wilmington/ONBOARDING.md`, two of four dimensions are auto-populated and two are open:

| Dimension | Status | Evidence |
|---|---|---|
| Hydrology (low-flows, corridor DDF, climatology) | **done** | DDF + climatology committed; SSURGO **skipped** (no footprint) |
| Economics (county baseline, consumer energy) | **done** | baseline + consumer-energy committed |
| **Data-center activity** (permits/records + entity graph) | **open** | nothing extracted; `facility=None` |
| **Per-jurisdiction GIS** (parcels/zoning) | **open** | `parcels_url`/`zoning_url` = `TODO` |

The last onboard run log (ONBOARDING.md lines 14–25) records four steps that did **not** fully succeed and are load-bearing for any screen:
- `ssurgo-hsg` **skipped** — `extracted/wilmington/bosc-site-footprint.yaml` missing.
- `rsei` **skipped** — input `data/cache/rsei/v234/.../elements.csv.gz` absent (only `rsei/wilmington/README.md` exists; no `inventory.yaml`).
- `grid-profile` **errored** — "EIA-861 2024: no Short-Form ('861S') row for utility #0 in OH" (the profile's `eia861_utility_number=0` placeholder).
- `corridor-ddf`, `climatology`, `econ-baseline`, `consumer-energy`, `derive-low-flows`, `basin-screen` all **ok**.

Promotion (`frontend/src/lib/sites.ts` `status→live`/`selectable→true`) is a separate, parity-gated manual edit and has **not** happened. The blocking review gate (ONBOARDING.md lines 27–34) is entirely unchecked.

## 2. Site definition `[verified]` in the profile

The `_WILMINGTON` SiteProfile (sites.py lines 2317–2387) is well-tagged and internally disciplined:
- **Basin:** Little Miami — Todd Fork → Little Miami River → Ohio River, HUC-8 **05090202** `[verified]`.
- **County:** Clinton County, OH, FIPS **39027** `[verified]`.
- **Receiving water:** **Todd Fork** `[verified]`, draining to the Little Miami, a **National & State Scenic River** (same anti-degradation overlay as Xenia).
- **The site thesis:** a "place shaped by one tenant" — the **Wilmington Air Park (ILN)**, former DHL/Airborne super-hub (2008 DHL pullout = landmark company-town collapse), now an **Amazon Air cargo hub + ATSG base**. Framed as the comparator to Lima's Amazon data-center tenant. This framing is tagged `[reference]`/contextual in the profile comment, **not** a documented data-center record.

## 3. Receiving-water screen — what the evidence supports, and three hard caveats

**Design-storm rainfall (high confidence).** `data/reference/hydrology/wilmington/atlas14-corridor-ddf.yaml` holds a NOAA Atlas-14 HDSC point query at the Wilmington centroid (39.4453, −83.8285). 24-hr depths: **2-yr 2.79 in, 10-yr 3.91 in, 25-yr 4.58 in, 50-yr 5.12 in, 100-yr 5.67 in** — all source-tagged "NOAA Atlas-14 PDS, English depths." These are clean, citable, and suitable as a runoff driver.

**Climatology (high confidence).** `nasa-power-climatology.yaml` (NASA POWER, point 39.445/−83.829, elev 299.2 m) gives monthly normals — annual precip 2.83 mm/day, T2M 11.39 °C, etc. Fine for context; not a screen denominator.

**The dilution denominator is the problem.** Three caveats, all flagged in the profile and confirmed against the committed files:

1. **Todd Fork is ungaged `[verified caveat]`.** The profile (line 2315, 2366–2370) states the old gage 03244000 is discontinued and Clinton County has no active gage. `abstraction_gage`/`supply_gage_primary` are set to **03245500 (Little Miami at Milford)**, a *downstream mainstem integrator* that the profile itself flags **"overstates at-site dilution."** Any at-site assimilative result for Todd Fork using the Milford gage is optimistic by construction.

2. **No committed 7Q10 denominator exists for this basin `[verified gap]`.** The cited low-flow file (`low-flow-7q10.yaml`) is **Lima-only** (Dug Run 0.78, Pike Run 0.03, Ottawa River 0.2 cfs — all `source: document` from OEPA fact sheets). The derived file (`low-flow-7q10.derived.yaml`) is **Maumee-basin mainstems only** (Maumee, Auglaize, St. Marys, St. Joseph). **Neither contains Little Miami or Todd Fork.** So there is no reviewable 7Q10 — cited or derived — backing a Wilmington screen.

3. **The basin-screen result is a log line, not an artifact `[verified gap]`.** ONBOARDING.md line 21 records `basin-screen ok | 7/129 dischargers screened (1 violations, 2 tight)`. No screen output file is committed anywhere under `data/reference/hydrology/` (Glob for `*screen*` → none). Given caveat #2, the denominator that produced "1 violation, 2 tight" is **not verifiable from the committed corpus** and should not be cited until the Little Miami/Todd Fork 7Q10 is derived and committed.

**Net:** the rainfall side of the receiving-water screen is solid and citable; the **streamflow/dilution side is unestablished** for this basin. No effluent-dominance or assimilative-capacity finding for Wilmington can be stated yet.

Worth noting the structural parallel (an `[inference]`, not a finding): Lima's thesis is that tiny tributaries (Dug Run, Pike Run) receive effluent exceeding their entire 7Q10. Todd Fork is a small tributary to a *protected Scenic River*; the profile notes scenic-river protection "likely raises" the in-stream passby minimum (passby fields currently 0.0, `[open]`). Whether Wilmington reproduces or breaks the Lima pattern is exactly what the missing denominator would decide.

## 4. Data-center activity — empty in the corpus, and a no-link to flag

**There are no extracted Wilmington data-center records.** No deeds, NPDES permits, township minutes, or entity-graph parties for Clinton County exist in either the MCP corpus or `data/extracted/wilmington/` (which holds only README + ONBOARDING.md). `facility=None` in the profile (line 2373), and the data-center-activity dimension is explicitly open pending corpus extraction + `bosc onboard --research` (#247/#492).

**No-link finding (to prevent cross-thread contamination):** the 44 repo files matching "wilmington" include Lima permit and deed extractions (e.g., `permits/4081910.epa.yaml`, `recorder/202508130008300.deed.yaml`). These matches are the **Delaware registered-agent / shell-company mailing addresses** — "2801 Centerville Road, … Wilmington, Delaware 19808" (Tilted Gate LLC; Bistrozzi grantee address). They are **Wilmington, *Delaware***, part of the Lima Bistrozzi/Amazon thread, and have **no connection** to the Wilmington, Ohio watershed point. They must not be read as Wilmington-OH activity.

The Air Park "Amazon Air / ATSG" tenant claim (profile line 2310–2316, 2345) is `[reference]`/`[inference]` context, not yet backed by an extracted instrument.

## 5. Economics baseline (high confidence, connector-sourced)

`data/reference/economics/wilmington/baseline.yaml` (BLS QCEW 2023, area 39027; Census ACS5) — all `confidence: high`:
- Total employment **18,883 jobs** (2023; up from 17,848 in 2018); **959 establishments**.
- **Transportation & Warehousing dominates: 4,570 jobs, location quotient 5.75** — i.e. ~5.75× the national share, the quantitative fingerprint of the single-tenant air-cargo hub. Manufacturing LQ 2.04; Information LQ 1.57.
- Clinton County population **~42,014** (2023 ACS5), essentially flat since 2010 (42,416).

`data/reference/eia/wilmington/consumer-energy.yaml` (EIA API v2, 2025, OH statewide): residential electricity **16.96 ¢/kWh**, residential gas **$13.85/Mcf**, OH retail sales 161,933.98 million kWh — all `confidence: high`. Note these are **state-level**, not Clinton-County-specific; the site-specific grid profile (PJM zone/LMP) is **not** populated (§6).

## 6. Reconciliation discrepancies & open items

- **No Little Miami 7Q10 anywhere** — `derive-low-flows` reportedly ran "ok," yet the committed `low-flow-7q10.derived.yaml` contains only Maumee mainstems. Either the derive step didn't write the Little Miami gages (03245500/03240000) or the basin file wasn't regenerated. The "7/129 … 1 violation/2 tight" screen has no committed, reviewable denominator behind it.
- **Grid profile missing/errored** — `eia861_utility_number=0` is a placeholder; no `grid-profile.yaml` was produced. Clinton County's retail utility is `[open]` (profile guesses AES Ohio / PJM **DAY** zone, `[inference]`). This is the same muni/short-form pattern as Bryan (EIA-861S) noted in repo memory.
- **RSEI inventory missing** — step skipped on absent `elements.csv.gz`; no toxics screen for Clinton County.
- **SSURGO unconfirmed** — `dominant_hsg="C"` is `[inference]` (glaciated till-plain reasoning), never confirmed against an area-weighted SSURGO pull because no site footprint exists. `pre_cover`/`post_cover`/`developed_pervious_cover` = `TODO`, so no stormwater runoff scenario can run.
- **GIS lift outstanding** — `parcels_url`/`zoning_url`/`gis_parcel`/`gis_zoning` = `TODO`/`None`; only the national FEMA NFHL flood layer is wired. Per repo memory, **verify county+state from a live parcel sample before wiring any discovered Clinton County GIS** (the "same-name county, wrong state" trap that bit Williams County → North Dakota).

## 7. Recommended follow-up investigations (issue candidates)

1. **Derive & commit the Little Miami / Todd Fork 7Q10.** Run `derive-low-flows` for gages 03245500 (Milford) and 03240000 (Oldtown), commit them to `low-flow-7q10.derived.yaml`, and **re-run basin-screen committing the output as a reviewable artifact.** Until then, treat the "1 violation / 2 tight" result as unverified. *(Blocks the receiving-water screen.)*
2. **Resolve the ungaged-Todd-Fork dilution honestly.** Document a drainage-area-ratio adjustment from the Milford gage to Todd Fork (the profile concedes Milford overstates dilution), and pin the scenic-river passby minimum (`passby_primary_cfs` currently 0.0). *(Receiving-water accuracy.)*
3. **Open the data-center-activity dimension.** Run `bosc onboard wilmington --research` (#247/#492) to seed Air Park / Amazon Air / ATSG proposals; extract any Clinton County / City of Wilmington records into `data/extracted/wilmington/`. The "single-tenant" thesis is currently `[reference]`, not sourced.
4. **Pin the retail utility + PJM zone.** Find Clinton County's EIA-861 (likely 861S Short-Form) utility number, set `eia861_utility_number`, confirm the PJM zone (verify DAY vs. other) and LMP pnode; re-run grid-profile.
5. **Stand up the Clinton County GIS connector** (parcels + zoning), **verifying situs city/state against a live sample first** (county-name/state trap). Then capture a site footprint to unblock SSURGO HSG confirmation and the stormwater runoff scenario.
6. **Regenerate RSEI** (stage `elements.csv.gz`) to populate the Clinton County toxics inventory.
7. **Do not promote** to `live`/`selectable` until items 1–6 clear the blocking review gate; today only the `/bosc` Lima build is live.

**Confidence summary:** Atlas-14 DDF, NASA-POWER climatology, QCEW/ACS economics, and EIA state energy prices are **high-confidence, connector-cited**. The site definition (basin, county, gages, receiving water) is **verified** in the profile. The **receiving-water screen result, the HSG, the data-center tenancy, and the grid/utility profile are not yet established** — they are `[open]`/`[inference]` and must be sourced before any Wilmington claim is published. No figures were invented; gaps are reported as gaps.
