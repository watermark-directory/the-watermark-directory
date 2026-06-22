# Research run: onboard sidney (Sidney): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T04:01:10+00:00
- turns: 33 (cap 30); cost: $1.1703
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__timeline, mcp__bosc__program_overview, mcp__bosc__hydrology_balance, Grep, mcp__bosc__hydrology_scenario, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I have what I need. Here is the findings report.

---

# Findings — Onboarding Sidney (`sidney`): data-center activity + receiving-water screen

## Scope and method

I queried the read-only BOSC corpus tools (`entities`, `timeline`, `program_overview`, `list_documents`, `list_extractions`, `hydrology_balance`, `hydrology_scenario`) and then read the Sidney scaffolding directly from the repo. **Key scoping fact up front:** the BOSC analysis tools (`entities`/`timeline`/`program_overview`/`hydrology_*`) read the *Lima/Allen County* extraction corpus only. The Sidney document index and entity graph returned **zero** matches for Sidney/Shelby/Great Miami/Loramie. Sidney's data lives as on-disk onboarding scaffolding, not in the queryable corpus. I distinguish below between connector-sourced figures (high confidence, cited) and the profile's `[inference]`/`[open]` placeholders.

## 1. Onboarding state — partially onboarded, not promoted `[verified]`

The memory note "Sidney #481 … queued, NOT yet onboarded" is **stale against the filesystem**. `bosc onboard sidney` (#326) has already run. Per `data/extracted/sidney/ONBOARDING.md`:

| Dimension | State |
|---|---|
| Hydrology (low-flows, corridor DDF, SSURGO HSG, climatology) | ✅ marked complete |
| Economics (county baseline, RSEI, consumer energy, grid) | ✅ marked complete |
| **Data-center activity** (permits/records + entity graph) | ☐ **not done** |
| **Per-jurisdiction GIS** (parcels/zoning) | ☐ **not done** |

Three onboard steps did **not** produce committed output (ONBOARDING.md "Last onboard run"):
- `ssurgo-hsg` — **skipped**, missing `extracted/sidney/bosc-site-footprint.yaml` (no identified site footprint).
- `rsei` — **skipped**, missing the RSEI v2.3.4 `elements.csv.gz` cache.
- `grid-profile` — **errored**: "EIA-861 2024: no Short-Form ('861S') row for utility **#0** in OH." This is the `eia861_utility_number=0` placeholder in the profile (`src/bosc/sites.py` L2166) — the Shelby County retail utility is unidentified.

Frontend status (`frontend/src/lib/sites.ts` L229–239): `status: "queued"`, `selectable: false`, issue 481. Promotion to live is a separate, parity-gated manual edit; only Lima (`/bosc`) is live today. This is the correct posture.

## 2. Verified site facts (from the `SiteProfile`, `src/bosc/sites.py` L2153–2224)

- **Basin / receiving water:** upper Great Miami River mainstem, HUC-8 05080001 → Ohio River. `receiving_water_name="Great Miami River"` `[verified]`.
- **Gages** `[verified]`: `03261500` Great Miami River at Sidney (at-site/abstraction/primary supply); `03262000` Loramie Creek at Lockington (major local tributary, Lockington dam; secondary supply); `03261950` Loramie Creek near Newport.
- **County:** Shelby County, OH, FIPS 39149. Sidney centroid 40.2842, −84.1558. **UTM 16N** (`hydro_utm_epsg=32616`; west of the 84°W meridian) `[verified]`.
- **Hydrologic soil group:** `dominant_hsg="B"` **`[inference]`** — upper Great Miami buried-valley outwash (US-EPA-designated sole-source aquifer the Sidney well field draws on), the inverse of Lima's HSG-D lake-plain clays. Pending SSURGO area-weighted confirmation, which is blocked on the missing footprint.

### Connector-sourced hydrology reference (high confidence)
- **NOAA Atlas-14 design storms** (`atlas14-corridor-ddf.yaml`): 24-hr depths 2.63 in (2-yr) → **5.66 in (100-yr)**; 60-min 1.30 → 2.74 in. HDSC point query, English depths. High confidence.
- **NASA POWER climatology** (`nasa-power-climatology.yaml`): annual precip 2.73 mm/day (~39 in/yr), annual mean temp 10.65 °C. Climatology normals, high confidence.

## 3. Data-center activity screen

**There are no in-corpus primary records for Sidney** — no deeds, EPA/NPDES permits, plans, or meeting minutes. `facility=None` `[open]` in the profile (the data-center dimension is explicitly the research target for #481). The entity graph contains no Shelby/Sidney party. **This dimension is empty.**

What *is* available is the Shelby County economic baseline (`data/reference/economics/sidney/baseline.yaml`, **BLS QCEW 2023**, high confidence) — and it argues *against* an existing data-center cluster, not for one:

- **Total employment 27,149 jobs; 1,123 establishments** (2023). Population **declining**: 49,350 (2010) → 48,007 (2023, ACS5).
- **Manufacturing (NAICS 31-33): 12,612 jobs, location quotient 5.53** — an extreme manufacturing concentration (~46% of county employment). Consistent with the profile's Emerson/Copeland compressor-/refrigeration-manufacturing characterization `[inference]`.
- **Information (NAICS 51): 73 jobs, 14 establishments, LQ 0.14.** Management of companies LQ 0.04; Professional/Scientific/Technical LQ 0.20. **No IT-hosting, corporate, or tech base.**

**Inference, clearly labeled:** Sidney's economic structure is that of a manufacturing town, not a data-center host. A hyperscale siting here would be a *greenfield* event with no existing-cluster signal — matching the network's standing finding that the data-center leg is the weakest for these Miami greenfields. This is an economic-structure read, **not** evidence about any specific proposed facility.

**Caveat on two figures:** Transportation & Warehousing (54 establishments) and Utilities (2 establishments) both report **0.0 jobs / LQ 0.0**. With establishments present and employment zero, these are **BLS QCEW confidentiality suppressions, not literal zeros** — do not read them as "no logistics/utility employment."

## 4. Receiving-water screen — the critical gap

**The committed receiving-water screen for Sidney is empty.** This is the most important finding, and it contradicts the ONBOARDING.md log line "`basin-screen ok | 7/129 dischargers screened (1 violations, 2 tight)`":

- **No Great Miami / Loramie Creek 7Q10 denominator exists in committed data.** `low-flow-7q10.derived.yaml` contains **only the four Maumee-basin mainstems** (Maumee 114.15, Auglaize 1.91, St. Marys 15.65, St. Joseph 29.69 cfs). `low-flow-7q10.yaml` (cited) has **no** Great Miami/Loramie entry. Grep for the Sidney gages, Shelby, Great Miami, and Loramie across both files: zero matches.
- **No Great Miami NPDES discharger inventory exists.** The only committed ECHO inventory is `data/reference/echo/maumee-wwtp.*` — Maumee basin. There is no Great Miami ECHO file.
- **`plant_receiving={}` `[open]`** — the Sidney WWTP and its NPDES fact sheet are not yet identified. **`passby_primary_cfs=0.0` / `passby_secondary_cfs=0.0` `[open]`** — no in-stream passby minimum is set.

So the basin-screen counts in the log are a **run artifact with no committed supporting denominators or discharger rows** — they cannot be reproduced or audited from committed data, and (given the only committed 7Q10s are Maumee) any screen that did run screened against the wrong basin or against transient cache. This exactly matches the network's own standing rule for the Great Miami branch: *"Receiving-water screen is empty until a Mad-River 7Q10 (#445) + a Great-Miami ECHO inventory (#446) exist."* Sidney inherits that gap.

**Methodological template (Lima, for reference only — do not transpose the numbers):** the Lima screen I ran (`hydrology_balance`, `hydrology_scenario`) shows the shape the Sidney screen must take once denominators exist — WWTP design discharge vs. receiving-stream 7Q10 dilution, then a data-center consumptive-cooling draw vs. 7Q10 (Lima: ~4.85 cfs net basin loss = 24.3× the Ottawa River's 0.20 cfs 7Q10). **Important distinction:** Lima is an *effluent-dominated tiny-7Q10* story (HSG-D lake plain). Sidney is the **inverse regime** — a buried-valley sole-source aquifer where the correct screen is *consumptive abstraction vs. baseflow on the supply gage*, not effluent-vs-7Q10. The Lima figures above are Allen County values and must not be attributed to Sidney.

## 5. Discrepancies and gaps (summary)

1. **Memory vs. filesystem:** memory says Sidney is "queued, not onboarded"; the filesystem shows a completed `bosc onboard sidney` run (#326). Reconcile the memory note.
2. **ONBOARDING log vs. committed data:** "basin-screen ok, 7/129 dischargers, 1 violation, 2 tight" is **not reproducible** — no Great Miami 7Q10 or ECHO inventory is committed.
3. **`grid-profile` errored** on `eia861_utility_number=0`; the Shelby County retail utility and PJM zone are unpinned (profile guesses AES Ohio / DAY `[inference]`).
4. **`rsei` skipped** (missing v2.3.4 cache); `rsei/sidney/inventory.yaml` and `grid-profile.yaml` are referenced by the profile but **do not exist on disk**.
5. **SSURGO skipped** — HSG "B" remains `[inference]`, blocked on a missing site footprint.

---

## Recommended follow-up issues to track

1. **Derive a Great Miami / Loramie Creek 7Q10** (LP3 over gages 03261500 / 03262000) and commit it to `low-flow-7q10.derived.yaml`; reconcile the orphaned "7/129" basin-screen claim or remove it. *(Sidney instance of #445.)*
2. **Build the Great Miami ECHO NPDES discharger inventory** under `data/reference/echo/`, mirroring the Maumee POTW file. *(Sidney instance of #446.)*
3. **Identify the Sidney WWTP and pull its NPDES permit + fact sheet** to populate `plant_receiving` and set the design discharge — the load-bearing input for the effluent screen.
4. **Set the in-stream passby minima** (`passby_primary_cfs`/`passby_secondary_cfs`) for the abstraction screen on the sole-source supply.
5. **Pin the Shelby County retail utility + EIA-861 number and PJM zone** (verify AES Ohio / DAY vs. a municipal system) to unblock `grid-profile`.
6. **Provision the RSEI v2.3.4 cache** and regenerate `rsei/sidney/inventory.yaml`; this is the only Miami site without a committed RSEI screen.
7. **Confirm dominant HSG via SSURGO** — requires an identified `bosc-site-footprint.yaml`; promotes HSG "B" from `[inference]` to `[verified]`.
8. **Data-center activity sweep (#481):** search Shelby County recorder deeds, Ohio SoS LLC filings, City of Sidney / county zoning and economic-development minutes, and Ohio EPA permit-to-install records for any greenfield large-load proposal. Until a real on-the-record fact exists, the Lima/Allen Bistrozzi graph must **not** be bridged in — there is no evidentiary link.
9. **Discover the Shelby County / City of Sidney parcel + zoning GIS endpoints** (`parcels_url`/`zoning_url` are `TODO`) — the known onboarding lift.
10. **Correct the memory note** for `miami-basin-expansion` to reflect Sidney's actual onboarded-but-unpromoted state.

**Promotion gate:** Sidney must remain `status: queued` / `selectable: false` until items 1–4 (the receiving-water screen) and item 8 (a real data-center fact or a documented absence) are resolved and reviewed against cited sources.
