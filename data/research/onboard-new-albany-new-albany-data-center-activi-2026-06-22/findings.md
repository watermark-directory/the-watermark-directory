# Research run: onboard new-albany (New Albany): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T17:27:20+00:00
- turns: 25 (cap 30); cost: $1.0542
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__timeline, Grep, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I now have a complete, grounded picture. Here is the findings report.

---

# Findings — Onboarding `new-albany` (New Albany): data-center activity + receiving-water screen

## 0. Scope note / threshold finding

The read-only BOSC corpus tools (`entities`, `timeline`, `program_overview`, and the entire hydrology tool family — `hydrology_balance`, `hydrology_scenario`, `sanitary_basis`, `stormwater_runoff`, `storm_plan_inventory`, `tier1_swmm`) are **bound to the Lima / Allen County reference build.** Every entity, dated event, WWTP, and receiving water they return is Lima's (American II→Dug Run, American Bath→Pike Run, Shawnee II→Ottawa River; the Bistrozzi/Amazon/Google land assemblage). `hydrology_scenario` screens against the *Ottawa River* 7Q10; `sanitary_basis` returns the Lima WWTPs and the 1996 federal consent decree. **None of these tools screen New Albany.** `[verified]` — confirmed by inspecting all five graph tools and the hydrology tool contracts.

New Albany therefore has **zero primary-source documents in the extraction corpus.** Its state is not "investigated record" but "**partially onboarded site profile.**" The findings below report that state precisely, separating what the reach connectors have verified from what remains `[open]`.

One string-collision to retire before anyone trips on it: the corpus timeline contains a "**Scioto County**" reference (a ~914-acre Section-404/wetland permit, Green Township) — that is Scioto *County* (Portsmouth, far southern Ohio), **not** the Scioto *basin* New Albany site. `[verified]` no-link: it is unrelated to this onboarding and must not be cross-referenced into it.

## 1. Onboarding state (what exists)

New Albany is registered as `_NEW_ALBANY` in `src/bosc/sites.py` (slug `new-albany`, `basin="scioto"`, Scioto epic #484 / onboarding #485) and was last onboarded **2026-06-22** (today). In the frontend (`web/src/lib/sites.ts`) it is `status: "tracking"`, `selectable: false` — **not promoted; not live.** Promotion is a separate, parity-gated manual edit. `[verified]`

**Reach connectors that ran (committed, citable):**

| Dimension | Output | Status |
|---|---|---|
| Hydrology — climatology | `data/reference/hydrology/new-albany/nasa-power-climatology.yaml` (NASA POWER, 40.09/−82.776) | ✅ |
| Hydrology — corridor DDF | `data/reference/hydrology/new-albany/atlas14-corridor-ddf.yaml` | ✅ |
| Hydrology — low-flow 7Q10s | `data/reference/hydrology/low-flow-7q10.derived.yaml` (Scioto mainstems) | ✅ derived |
| Economics — county baseline | `data/reference/economics/new-albany/baseline.yaml` (Licking 39089) | ✅ |
| Economics — consumer energy | `data/reference/eia/new-albany/consumer-energy.yaml` | ✅ |
| Economics — grid profile | `data/reference/eia/new-albany/grid-profile.yaml` (AEP Ohio #14006, pinned) | ✅ |

**Connectors skipped (from `data/extracted/new-albany/ONBOARDING.md`):**
- **SSURGO HSG** — skipped, no footprint. Dominant HSG = **C is `[inference]`**, not soil-survey confirmed.
- **basin-screen** — skipped, **0/0**: the Scioto ECHO NPDES inventory was never pulled (ECHO 300/hr throttle, HTTP 429 at onboard time).
- **RSEI toxics** — skipped (v234 `elements.csv.gz` cache miss); no Licking-County toxics inventory.

## 2. Data-center activity

**Finding: no New Albany data-center facility is documented anywhere in the corpus or entity graph.** `facility=None` in the profile; the entity graph holds only Lima/RSEI parties. `[verified]`

The profile comments and `ONBOARDING.md` name the research *target* — Intel "Ohio One" plus Google/Meta/AWS/Microsoft/QTS in the New Albany International Business Park — but these are **`[open]` targets, not findings.** No instrument pins any of them. The self-research first pass (`bosc onboard new-albany --research`, #247) and a discover-and-pin sweep **have not been run.** Until a facility is pinned to a primary instrument, there is no campus load, no consumptive draw, and therefore **no numerator for the receiving-water screen.** `grid-profile.yaml` states this explicitly: "no documented data-center facility, so there is no campus load to express as a share."

What *is* verified is the **grid backdrop** the campus would land in (connector-sourced, **high confidence**):
- Serving utility **AEP Ohio (Ohio Power Co #14006)**, investor-owned, PJM/PUCO; **no municipal electric utility.** `[verified]`
- AEP Ohio retail: **48,652.9 GWh/yr**, **1,533,265 customers**, blended **18.61 ¢/kWh** (EIA-861 2024). `[verified, high]` — note the file's own caveat: a blended price *understates* all-in cost because delivery-only rows exclude generation.
- PJM annual load **815,056.2 GWh** (EIA-930 2024). `[verified, high]`
- Wholesale price proxy **LMP 45.81 $/MWh** (PJM AEP-zone day-ahead annual mean). `[reference]`

County economic backdrop (Licking 39089, BLS QCEW 2023 / Census ACS, **high confidence**): **70,045 jobs** (up from 59,960 in 2018), **3,892 establishments**, population **180,311** (2023). Transportation & Warehousing carries the highest export orientation (location quotient **2.95**), Manufacturing **1.6** — consistent with a logistics/industrial-park economy, *not yet* a measured data-center signal. `[verified, high]`

## 3. Receiving-water screen

**Finding: the screen is scaffolded on the denominator side and empty on the numerator side — it cannot yet run (0/0).** `[verified]`

**Denominators present (DERIVED, medium confidence — explicitly NOT cited regulatory 7Q10s):** from `low-flow-7q10.derived.yaml` (USGS NWIS → log-Pearson III, gage-value screening proxies, 1980–2024):
- **Big Walnut Creek = 35.43 cfs** 7Q10 (gage 03229500, Big Walnut Creek at Rees OH; 44 climatic yrs) — the Scioto-side receiving water.
- Scioto River mainstem = 515.73 cfs (03234500 at Higby); Olentangy = 13.53 (31 yrs); Big Darby = 11.24.
- At-reach abstraction/supply gage = **Big Walnut Creek at Central College (03228500)**. `[verified]` these are the profile's pinned gages.

These are **medium-confidence derived screening denominators**, flagged in the file header as *not* the cited regulatory 7Q10s (those would live in `low-flow-7q10.yaml`). Do not present them as regulatory low flows.

**Numerators absent (`[open]`):**
- `plant_receiving={}` — no WWTP NPDES fact sheet; no permitted design flow. The basin-screen file `scioto-wwtp.potw.yaml` **does not exist** (only `echo/maumee-wwtp.potw.yaml` and `echo/great-miami-wwtp.potw.yaml` are committed). `[verified]`
- `facility=None` — no data-center consumptive draw to screen. `[verified]`
- `passby_primary_cfs / passby_secondary_cfs = 0.0` `[open]`.

**The divide caveat (load-bearing, do not paper over):** New Albany **straddles the Scioto↔Muskingum divide.** The profile frames the **Scioto/Big-Walnut side** (HUC 05060001), but the **Intel/business-park epicenter is on the Licking side** (Jersey Twp, Licking Co) → South Fork Licking → Muskingum (HUC 05040006), which a Scioto ECHO inventory would **not** cover. `receiving_water_name="Big Walnut Creek"` flips to South Fork Licking if the pinned footprint lands Licking-side. Separately, the onboarding record notes Intel's *process* wastewater is routed to **Columbus' sanitary sewer**, not a surface stream — a material nuance for any effluent-dominance argument. `[verified]` from profile/`ONBOARDING.md`; the Licking-side receiving water itself is `[open]`.

## 4. Review-gate status (blocking, from `ONBOARDING.md`)

All five gate items are **unchecked**: source-review of written values; SSURGO-vs-HSG; basin-screen coverage; per-jurisdiction GIS connector; self-research first pass. Parcels run via an **OGRIP-Licking substitute** (Licking County's own ArcGIS REST returns HTTP 500; `SitusAddressAll` is null for Licking — a thin catalog); zoning is `[open]` (no confirmed New Albany/Jersey Twp REST). `[verified]`

---

## Recommended follow-up investigations (issue candidates)

1. **Pull the Scioto ECHO NPDES inventory** — `bosc npdes --basin scioto`, deferred on a 429 at onboard. Commit `scioto-wwtp.potw.yaml` and re-run the basin-screen so Big Walnut Creek (HUC 05060001) gets a real numerator. *Gap: basin-screen is 0/0.*
2. **Resolve the Scioto↔Muskingum divide** — pin the operative footprint (Franklin/Scioto vs Licking/Muskingum); flip `receiving_water_name` to South Fork Licking if Licking-side. A Muskingum-basin ECHO inventory is required to screen the Licking side; the Scioto pull will not cover it. *Gap: receiving water is divide-ambiguous.*
3. **Data-center discover-and-pin first pass** — run `bosc onboard new-albany --research` (#247) + the Springfield #454 discover-and-pin pattern. Pin Intel "Ohio One" and each hyperscaler to a **primary instrument** (deed/NPDES/air PTI/SOS), with **no Bistrozzi-graph bridging** across sites. *Gap: `facility=None`; named targets are `[open]`, uncited.*
4. **Identify and commit the site footprint** — `extracted/new-albany/bosc-site-footprint.yaml` + `reference/new-albany/bosc-parcels.geojson`. Unblocks SSURGO HSG (currently `[inference] C`), the stormwater pre/post runoff scenario, and the divide resolution. *Gap: footprint missing.*
5. **Verify the derived Big Walnut 7Q10 against a cited regulatory value** — promote from medium-confidence derived to a cited Ohio EPA WQS/Total-Available-Flow figure if one exists for the actual discharge reach. *Discrepancy risk: derived gage proxy ≠ regulatory 7Q10 at the reach.*
6. **Stand up a Licking/New Albany parcel+zoning GIS connector** — Licking's REST is down (HTTP 500), zoning `[open]`; evaluate the Franklin County Auditor native owner+CAMA layer for the city-core side. *Gap: GIS gate unmet.*
7. **Retry RSEI for Licking 39089** — resolve the `elements.csv.gz` cache miss to give the data-center toxics/receiving-water context an industrial baseline. *Gap: no toxics inventory.*

**Caveats on this report:** I did not exhaustively read the full `list_documents` (1,485 lines) or `timeline` (328 lines) dumps line-by-line; I searched both for New Albany / Scioto / Licking / Blacklick / Rocky Fork terms and found only the unrelated Scioto-County wetland permit. The conclusion that no New Albany primary documents exist rests on that targeted search plus the Lima-only entity graph, not a full read of every line.
