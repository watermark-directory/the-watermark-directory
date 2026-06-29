# Research run: onboard bryan (Bryan): data-center activity + receiving-water screen for a new watershed-point site (the basin's first municipal electric utility, Bryan Municipal Utilities / AMP / PJM)

- model: `claude-opus-4-8`
- generated: 2026-06-21T13:13:47+00:00
- turns: 24 (cap 30); cost: $1.2654
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__hydrology_balance, mcp__bosc__sanitary_basis, mcp__bosc__timeline, Grep, Glob, Read
- proposals: 5 (see `manifest.yaml`)

---

I now have a complete, sourced picture. Here is the findings report.

---

# Findings — Onboarding Bryan (Williams County, OH) as a BOSC watershed point

## Bottom line

Bryan is **registered but not yet built** — a `status: "queued"`, `selectable: false` "coming-soon" point (`web/src/lib/sites.ts:112–120`, issue #380). Its **geography and grid identity are sourced and verified**; its **receiving-water assimilative screen cannot yet be run** (no 7Q10 low flow for Prairie Creek); and there is **no documented data-center activity** — but that last finding rests on a screening layer that, for Bryan, lacks the parcel/recorder/permit infrastructure that surfaced the data-center thread in Lima. The distinguishing reason to onboard Bryan is the **grid**: it is the network's **first municipal electric utility** (Bryan Municipal Utilities, an AMP member scheduled into PJM), which exercises code paths no IOU site does.

---

## 1. Site identity and geography — `[verified]`

From the registered `SiteProfile` (`src/bosc/sites.py:1157–1258`) and the ECHO Maumee inventory (`data/reference/echo/maumee-wwtp.all-npdes.yaml:17026–17041`):

| Field | Value | Confidence |
|---|---|---|
| Place / county | Bryan, **Williams County, OH** (FIPS 39171) | `[verified]` |
| Basin / HUC-8 | Maumee → **Tiffin subbasin, 04100006** | `[verified]` |
| Receiving water | Prairie Creek → Tiffin River → Maumee → Lake Erie | `[verified]` (NPDES fact) |
| City centroid | 41.4748, −84.5525 (NOAA Atlas-14 design point) | `[verified]` |
| Gages | 04185000 Tiffin R. at Stryker; 04184500 Bean Cr. at Powers | `[verified]` |
| Dominant HSG | **C** (Blount/Glynwood/Pewamo till-plain) | `[inference]` — pending SSURGO area-weighting |

This is a **small-tributary headwaters point** in the Tiffin subbasin — geographically analogous to Van Wert, but Tiffin rather than Auglaize. It sits **upstream of Defiance** in the basin network (`data/reference/network/basin-network.yaml:189`).

---

## 2. Receiving-water screen — the WWTP is identified; the screen is **unrun** `[open]`

**Documented discharger** (ECHO, `maumee-wwtp.all-npdes.yaml:17026–17047`):

- **Bryan WWTP**, NPDES **OH0020532**, FRS 110000573175, POTW, **design flow 3.1 MGD** → **Prairie Creek** (HUC-12 041000060403). `informal_enf_count: 0`. — all `[verified]`, high confidence.
- 3.1 MGD ≈ **4.80 cfs** (arithmetic conversion). For scale, this is *larger* than Lima's Shawnee II (3.0 MGD / 4.64 cfs), discharged into a far smaller headwaters creek.

**The screen cannot be computed.** The profile's `plant_receiving={}` is `[open]` "pending Bryan-area WWTP NPDES fact sheets," and the network synthesis records `screen.status: no_7q10`, `dilution_ratio: null` (`basin-network.yaml:191–199`). The `mcp__bosc__hydrology_balance` / `hydrology_scenario` tools are **Lima-rooted** (Ottawa River / BOSC campus) and return nothing for Bryan.

**Evidentiary caution:** the synthesis pre-labels Bryan `regime: effluent_dominated_tributary` (`basin-network.yaml:190`). On the Lima pattern — Pike Run (0.01:1) and Dug Run (0.42:1) both fail the 7Q10 screen — a 4.8-cfs discharge into a headwaters creek is *plausibly* effluent-dominated. **But that label is an `[inference]`, not a finding**: no Prairie Creek 7Q10 is in the corpus, so the assimilative classification is unverified.

**Other Williams County NPDES on Prairie Creek** (same file): City of Bryan Utilities **Water** Treatment Plant (OH0030481, NON-POTW, flow uncited); an unnamed NON-POTW on "Prairie Creek, un. trib" (OH...; `informal_enf_count: 3`); Thiel Oil – Bryan Bulk Plant (OH0122661). These are catalogued but not screened.

---

## 3. Grid / utility — the distinguishing feature, **verified** `[reference]`/connector

This is *why* Bryan is worth onboarding. From `data/reference/eia/bryan/grid-profile.yaml`:

- **Serving utility: City of Bryan – (OH)**, EIA **#2439**, **Municipal** ownership, EIA-861**S** short-form filer. High confidence.
- **Retail: 160.5 GWh/yr, 5,814 customers, 10.75 ¢/kWh** (EIA-861 2024 861S short form) — connector-sourced, high confidence.
- **Balancing authority / RTO: PJM Interconnection**; wholesale power and PJM scheduling **through American Municipal Power (AMP)**, not an IOU holding company.
- **Retail regulator: municipal home rule (OH)** — *not* PUCO rate-regulated.

This is the **network's first municipal/short-form/PJM/AMP utility** — every other registered site is an AEP/IOU, PJM-or-MISO. It exercises the grid connector's EIA-861S fallback path and the ownership-aware regulator logic (cf. MEMORY: EIA-861 municipal short-form, #2439 / PR #388).

**One flagged placeholder:** `lmp_usd_mwh = 35.0` is an **`[inference]` placeholder** — the profile explicitly states the AMP/PJM transmission zone "is not yet pinned; verify via PJM Data Miner 2" (`sites.py:1246–1251`). Do not treat the LMP as sourced.

---

## 4. Data-center activity — **no documented facility** (with a scope caveat)

- The profile carries `facility=None` `[open]` — "the data-center dimension onboarding doesn't capture (no disclosed facility)" (`sites.py:1237`). Grid `load_share: null`.
- Network synthesis: `activity.has_disclosed_facility: false`, `it_load_mw: null`, `summary: no disclosed data-center facility` (`basin-network.yaml:218–221`).
- Economy corroborates the absence indirectly: **Information-sector employment LQ 0.19** (~60 jobs; `data/reference/economics/bryan/baseline.yaml:275–296`) — no IT/data-center concentration.

**State it flatly:** *As of this corpus, there is no documented data-center facility at Bryan.* **But scope the claim honestly** — this is an absence at the *screening* layer, not a deed-level no-link. In Lima, the data-center thread is documented through recorder deeds (Bistrozzi/Amazon land assembly), NPDES applications, and site plans; **Bryan has none of that layer in the corpus** (`parcels_url`/`zoning_url` = `TODO`; no Williams County recorder or permit extractions exist). So Bryan's "no activity" is *evidence not yet gathered*, not *land assembly ruled out*. The honest register is: **no evidence of data-center activity, and the parcel/recorder tripwire that would detect quiet assembly is not yet installed.**

---

## 5. Economy and toxics context — `[verified]`, connector-sourced

**Economy** (`economics/bryan/baseline.yaml`, BLS QCEW 2023 / Census ACS): 16,635 jobs (−5.1% vs 2018), population **36,862** (declining from 38,172 in 2010), **Manufacturing LQ 4.54** (6,352 jobs) — a heavily industrial, export-oriented small county, not a growth/IT economy.

**Toxics** (`data/reference/rsei/bryan/inventory.yaml`, EPA RSEI v234, FIPS 39171): **35 facilities (29 scored), county-wide**. Top emitter **NEW ERA OHIO LLC** (Bryan; metal-finishing, water + POTW releases, score-dominant on cobalt/chromium/nickel) — but **last reporting year 2010**; the county's RSEI vintage tails off by **2014** (`basin-network.yaml:217`). Other water-relevant legacy dischargers: Titan Tire of Bryan (POTW), Hayes-Albion/Trim Trends, A-Stamp, Chase Brass (Montpelier).

Two caveats, faithfully: the RSEI set is **county-wide** (includes Stryker, Montpelier, Pioneer, Edgerton — *not* all on Prairie Creek), and it is **historical/legacy** (largely pre-2014). The profile's `toxic_corridor_bbox` is `[0,0,0,0]` `[open]` — no Prairie Creek toxic corridor has been delineated.

---

## 6. Onboarding / parity status

- **Committed reference artifacts exist**: grid-profile, economics baseline, RSEI inventory, NASA-POWER climatology, Atlas-14 corridor DDF (all under `data/reference/**/bryan/`).
- **Not promoted**: `status: "queued"`, `selectable: false` (`web/src/lib/sites.ts`) — the parity gate is correctly still closed.
- **No onboarding research manifest / review checklist** exists for Bryan (`data/research/*bryan*` → none found), unlike Defiance and Fort Wayne, which have `onboard-…/manifest.yaml`. Bryan appears to have been hand-assembled from the profile rather than run through `bosc onboard bryan`.

---

## 7. Recommended follow-up investigations (issue candidates)

1. **Acquire a Prairie Creek 7Q10 and run the assimilative screen.** This is the single highest-value gap: it converts `regime: effluent_dominated_tributary` from `[inference]` to a finding (or refutes it). Source a USGS/OEPA low-flow statistic for Prairie Creek at the Bryan WWTP outfall; populate `plant_receiving` and re-run the balance. *(corpus gap / unverified claim)*

2. **Ingest the Bryan WWTP NPDES fact sheet (OH0020532).** Confirm the 3.1 MGD design/permitted flows, peak hydraulic capacity (wet-weather headroom), and any I/I or bypass history — the Tiffin-headwaters analogue to the Lima sanitary-basis work. *(new extraction target)*

3. **Install the parcel/recorder tripwire for Williams County.** Discover the Williams County GIS parcel REST endpoint and City of Bryan zoning layer (both `parcels_url`/`zoning_url` = `TODO`), and a recorder-deed feed. Until this exists, "no data-center activity" is untestable against land assembly. *(corpus gap — the load-bearing one for the data-center thesis)*

4. **Pin the AMP/PJM transmission zone and replace the LMP placeholder.** `lmp_usd_mwh = 35.0` is an unverified `[inference]`; resolve Bryan's AMP/PJM zone via PJM Data Miner 2 and substitute a sourced annual LMP. *(unverified figure)*

5. **Confirm the dominant HSG by SSURGO.** `dominant_hsg = "C"` is an `[inference]` pending an SSURGO area-weighted read — which itself needs a site footprint. *(unverified parameter)*

6. **Run `bosc onboard bryan` to generate the missing review manifest.** Produce the slug-scoped reach connectors and the blocking review checklist that Defiance/Fort Wayne have, so promotion is auditable rather than hand-curated. *(process gap)*

7. **Refresh and corridor-scope the RSEI/toxics layer.** The committed inventory is county-wide and tails out ~2014; delineate a Prairie Creek `toxic_corridor_bbox` and confirm whether NEW ERA OHIO / Titan Tire remain active POTW contributors to the Bryan WWTP load. *(stale data / scope refinement)*

---

**Method notes.** Every figure above is from connector-sourced or reference YAML (high confidence); none derives from degraded OCR. I have preserved the `[verified]`/`[inference]`/`[reference]`/`[open]` registers as the artifacts carry them, and have **not** upgraded the `effluent_dominated_tributary` regime or the "no data-center activity" screen beyond what the evidence supports. No line items or sources were invented; where the corpus is silent (Prairie Creek 7Q10, Williams County parcels, AMP/PJM zone), I have said so rather than filled the gap.
