# Research run: onboard troy-piqua (Troy · Piqua): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T01:45:35+00:00
- turns: 31 (cap 30); cost: $1.2255
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__timeline, mcp__bosc__entities, Grep, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, mcp__bosc__sanitary_basis, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I have enough to produce the findings report. Let me compile it.

---

# Findings — Onboarding `troy-piqua` (Troy · Piqua): data-center activity + receiving-water screen

## Bottom line

`troy-piqua` is a **registered but not-yet-extracted onboarding seed** — a "queued" watershed point in the network's Great Miami basin branch, tracking issue **#475**. The repo carries a `SiteProfile` and a partially-populated per-site data tree, but **zero primary-source documents and zero extractions** exist for Troy, Piqua, or Miami County. Both target dimensions you named are, at this stage, gaps rather than findings:

- **Data-center activity:** no documented activity in the corpus. `facility=None` by design. `[open]`
- **Receiving-water screen:** the geography is sourced, but the screen has **no low-flow denominator and no discharger inventory** yet — it cannot be run. `[open]`

The in-app BOSC hydrology tools (`hydrology_balance`, `hydrology_scenario`, `sanitary_basis`, `stormwater_runoff`, `tier1_swmm`) are **Lima-bound**: they returned the Ottawa River / three-Allen-County-WWTP model with no Troy/Piqua content. None of them is parameterized by `WATERMARK_SITE` in a way that reflects this seed.

---

## 1. What the corpus actually contains for Troy/Piqua

**No documents, no extractions.** `list_documents` (1,485 lines) and `list_extractions` contain **no** Troy, Piqua, or Miami County entries; a case-insensitive search for `troy|piqua|miami` against the full document inventory returned **no matches**. The entity graph (`entities`) is entirely Lima/Allen-County (Bistrozzi, Amazon, the three WWTPs, the JSMC defense cluster); no Miami-County party, parcel, or receiving water appears.

What *does* exist is **onboarding scaffolding** (`bosc onboard troy-piqua`, #326), committed under slug-scoped paths:

| File | Status | Confidence |
|---|---|---|
| `src/bosc/sites.py` `_TROY_PIQUA` profile (lines 2068–2145) | registered | mixed (see §3) |
| `frontend/src/lib/sites.ts` (lines 208–222) — `status: "queued"`, `selectable: false`, `issue: "475"` | registered | n/a |
| `data/reference/hydrology/troy-piqua/nasa-power-climatology.yaml` | populated | **high** (NASA-POWER connector) |
| `data/reference/hydrology/troy-piqua/atlas14-corridor-ddf.yaml` | populated | **high** (NOAA Atlas-14 HDSC) |
| `data/reference/economics/troy-piqua/baseline.yaml` | populated | **high** (BLS QCEW 2023 / Census ACS5) |
| `data/reference/eia/troy-piqua/consumer-energy.yaml` | populated | **high** (EIA API v2, OH state) |
| `data/reference/rsei/troy-piqua/` | **README only — no `inventory.yaml`** | `[open]` |
| `data/reference/eia/troy-piqua/` | **no `grid-profile.yaml`** | `[open]` |
| `data/extracted/troy-piqua/` | **README only — no extractions, no `ONBOARDING.md`** | `[open]` |

So onboarding's **hydrology** and **economics** dimensions are partially seeded; the **data-center** dimension (corpus extraction + entity graph) is entirely absent — exactly the dimension `docs/onboarding.md` says `onboard` does *not* capture (§"Two dimensions captured, one not").

---

## 2. Data-center activity dimension

**Finding: no data-center activity is documented in the BOSC corpus for Troy/Piqua, and none is asserted.** This is recorded honestly in the profile, not papered over:

- `facility=None` with the comment *"the I-75-corridor data-center dimension is the research target (#475)"* (`sites.py:2130`).
- `grid_relpath` points at `reference/eia/troy-piqua/grid-profile.yaml`, which **does not exist** — consistent with the documented rule that the grid profile stays sparse "until the site has a documented facility load" (`docs/onboarding.md` §"Two dimensions captured, one not").
- `eia861_utility_number=0` `[open]`; serving utility unverified `[open]`.

**Discipline note — this is a no-data finding, not a no-thing finding.** Absence in the corpus means no *extracted record* exists; it is **not** evidence that no data-center is proposed or operating in Miami County. Establishing either way requires the corpus-extraction + self-research pass (`bosc onboard troy-piqua --research`), which has not been run (no `data/research/troy-piqua-*/` artifact exists). Until then, the defensible statement is: *"the BOSC corpus contains no Troy/Piqua data-center records as of 2026-06-21."*

The structural rationale for the site is documented and reasonable as a hypothesis, not a finding: the profile and `sites.ts` frame Troy/Piqua as the **upper Great Miami / I-75 mid-size-manufacturing node** (Hobart food-equipment HQ, auto parts) over the **Great Miami Buried Valley sole-source aquifer**, with a distinctive **municipal-power angle (Piqua runs its own AMP-member electric utility)** (`sites.py:2060–2067, 2098–2104, 2131–2138`). All of that is `[inference]`/context, not evidence of a specific project.

---

## 3. Receiving-water screen

### 3a. What is sourced (verified geography)

From `_TROY_PIQUA` (`sites.py`), tagged `[verified]` in-code:
- **Basin:** upper Great Miami River → Ohio River, HUC-8 05080001 (`:2071`). This is a **different basin sink than the rest of the network's Maumee/Lake-Erie sites** — a genuinely new receiving-water context.
- **Receiving water:** Great Miami River (`:2123`).
- **Gages:** `03262700` Great Miami at Troy (abstraction + primary supply), `03262500` Great Miami at Piqua (secondary supply), `03265000` Stillwater River at Pleasant Hill (second supply water) (`:2072–2076, 2125–2127`).
- **Design/met point:** Troy centroid 40.0392, −84.2033 (`:2077–2078, 2094–2095`); **UTM 16N** (zone 32616), correctly *not* zone 17 (`:2089`).
- **County:** Miami County, OH, FIPS 39109 (`:2079, 2141`).

**Design-storm depths are populated and high-confidence** (`atlas14-corridor-ddf.yaml`): 24-hr depths 2.67 / 3.80 / 4.51 / 5.10 / 5.71 in for the 2/10/25/50/100-yr events at the Troy point (NOAA Atlas-14 PDS). Climatology is populated (`nasa-power-climatology.yaml`: annual precip 2.83 mm/day, annual T2M 10.94 °C at 40.039/−84.203).

### 3b. What is missing (the screen cannot run)

- **No 7Q10 low-flow denominator for the Great Miami or Stillwater.** `low-flow-7q10.derived.yaml` is explicitly **"DERIVED … for the major Maumee-basin mainstems"** and contains only Maumee/Auglaize/St. Marys/St. Joseph. There is **no Ohio-River-basin 7Q10** committed. Without it, the assimilative-dilution screen that flagged all three Lima WWTPs (`hydrology_balance`) has no basis to run for Troy/Piqua. `[open]`
- **`plant_receiving={}`** — empty `[open]` (`:2124`): no Troy/Piqua WWTP, NPDES permit, design flow, or outfall receiving-water is identified. Lima's screen is built on three NPDES fact sheets (2PH00006/2PH00007/2PK00002); the Troy/Piqua equivalents are not in the corpus.
- **`toxic_corridor_bbox=(0,0,0,0)`** placeholder `[open]` (`:2117–2122`): the toxics-corridor inference has no geographic extent, so no RSEI receiving-water toxics screen is possible. The RSEI county inventory (`rsei/troy-piqua/inventory.yaml`) was also never generated.
- **`passby_primary_cfs=0.0` / `passby_secondary_cfs=0.0`** `[open]` (`:2128–2129`): no in-stream passby minimums for the refill-adequacy model.
- **`noaa_fallback_24h_depth_in={}`** empty in the profile (`:2108`) **even though** the corridor-DDF file carries the 24-hr depths — a populate-from-committed-data inconsistency worth closing.

### 3c. Inferences that need confirmation before promotion

- **`dominant_hsg="B"`** is `[inference]` (well-drained buried-valley outwash), the *inverse* of the Maumee Black-Swamp HSG-D pattern (`:2097–2104`). The citation itself flags it "pending an SSURGO area-weighted confirmation" — and SSURGO needs a footprint, which doesn't exist (`footprint_relpath` is `[open]`, `:2110`).
- **`lmp_usd_mwh=35.0`** is a `[inference]` PJM placeholder; zone unpinned (likely DAY/AES Ohio, with Piqua on AMP) `[open]` (`:2133–2140`).
- **`pre_cover`/`post_cover`/`developed_pervious_cover="TODO"`** `[open]` — no development land-cover scenario, because no site is identified (`:2105–2107`).

---

## 4. Reconciliation / tool-scope discrepancies

- **The hydrology MCP tools do not honor this seed.** `hydrology_balance`, `hydrology_scenario`, and `sanitary_basis` returned Lima-only output (Ottawa River 7Q10 0.20 cfs; the three Allen County plants; the BOSC campus 3.87 cfs). There is no Troy/Piqua path through them. For the screen to run on this site, the receiving-water/7Q10/plant-receiving data above must be committed **and** the hydrology read-side made site-aware (today the read side stays Lima-keyed until a site reaches parity — `docs/onboarding.md` §"What's shared vs. per-site").
- **Profile claims `[verified]` on gage IDs that I could not independently confirm this session.** The three NWIS IDs are asserted `[verified]` in-code but the onboarding README is explicit that *every* seeded value must be reviewed against a cited source before promotion. Treat the gage→reach mapping as profile-asserted, not yet corpus-verified.
- **Frontend/Python registries agree** (both carry `troy-piqua`, basin "Great Miami (upper)", issue #475), satisfying the CI cross-registry invariant — no drift there.

---

## 5. Recommended follow-up investigations (trackable issues)

**Receiving-water screen (highest leverage — unblocks the site's core thesis):**
1. **Derive Ohio-River-basin 7Q10s** for `03262700` (Great Miami at Troy), `03262500` (Piqua), and `03265000` (Stillwater at Pleasant Hill) via `bosc derive-low-flows`; commit to a Great-Miami-scoped derived file (the existing one is Maumee-only). Without this the assimilative screen has no denominator.
2. **Acquire and extract the Troy and Piqua WWTP NPDES permits + fact sheets** (Ohio EPA eDocs / ECHO), populate `plant_receiving`, and confirm each outfall's receiving reach. This is the corpus gap that most directly mirrors Lima's screen.
3. **Set `toxic_corridor_bbox` and generate `rsei/troy-piqua/inventory.yaml`** so the receiving-water toxics screen exists; pair with an ECHO NPDES inventory for the upper Great Miami HUC-8 (the Maumee ECHO inventory does not cover this basin).
4. **Confirm `dominant_hsg`** with an SSURGO area-weighted read once a footprint exists; the HSG-B "inverse of Black Swamp" claim is currently inference.
5. **Populate `noaa_fallback_24h_depth_in`** in the profile from the already-committed `atlas14-corridor-ddf.yaml` (closes a trivial internal inconsistency).
6. **Set `passby_primary_cfs`/`passby_secondary_cfs`** for the refill-adequacy model.

**Data-center activity dimension:**
7. **Run `bosc onboard troy-piqua --research`** to produce the first-pass findings/manifest proposal over the corpus (currently absent), then triage. "No data-center here yet" is itself a publishable finding if that's what the record shows.
8. **Pin the retail utility + EIA-861 number + PJM zone** — resolve Piqua-municipal (AMP) vs Troy/Miami-County (AES Ohio / DAY zone). The muni-power split is the site's distinctive angle and is wholly `[open]`. (Cf. the prior EIA-861S municipal short-form lesson — a muni utility files the short form.)
9. **Identify/verify any specific data-center proposal** (Miami County commissioners, Troy/Piqua city councils, Ohio EPA air PTI, Miami County recorder deed activity). Until a site is identified, `facility=None` is correct — do not fabricate a campus load.

**GIS / jurisdiction layer (the known lift):**
10. **Discover Miami County parcel + City of Troy/Piqua zoning ArcGIS REST endpoints** (`parcels_url`/`zoning_url` are `TODO`); register field-maps from a live `?f=json`, or fall back to the OGRIP statewide layer scoped `County='Miami'`. **Heed the prior burn:** verify the situs city/state from a live sample before wiring any discovered "Miami County" service (there are multiple Miami Counties nationally). Flood is already free via the national NFHL schema.

**Promotion gate:**
11. Generate the persisted `data/extracted/troy-piqua/ONBOARDING.md` checklist (not yet created) and keep `status: "queued"`/`selectable: false` until items 1–10 clear — promotion is the manual, parity-gated edit, and per `docs/onboarding.md` a *second* live build is a separate cutover beyond routine onboarding.

---

**Sourcing note:** All figures above are connector-sourced and self-tagged high-confidence (BLS QCEW 2023, Census ACS5, EIA API v2, NASA-POWER, NOAA Atlas-14); none carry the `~` approximate marker. Geographic identity values are `[verified]` in the profile but, per the onboarding discipline, remain onboarding seeds until reviewed against a cited source. I have not asserted any Troy/Piqua data-center, discharger, or low-flow value that the committed data does not contain.
