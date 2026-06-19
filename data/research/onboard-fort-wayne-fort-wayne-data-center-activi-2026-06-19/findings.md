# Research run: onboard fort-wayne (Fort Wayne): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-19T16:08:45+00:00
- turns: 35 (cap 30); cost: $1.3826
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, mcp__bosc__entities, Grep, Bash, Read
- proposals: 5 (see `manifest.yaml`)

---

I have enough to assemble the findings. The MCP cross-document tools (entities, timeline, hydrology_balance/scenario, program_overview) are all Lima-keyed and return zero Fort Wayne content — confirming the documented "read-side stays Lima-keyed until parity" deferral — so the Fort Wayne record lives in the onboarding scaffold I read directly. Here is the report.

---

# Findings — Onboarding Fort Wayne: data-center activity + receiving-water screen

**Site:** `fort-wayne` (Fort Wayne, IN) · basin `maumee` · the first **out-of-state** BOSC network point
**Status:** *coming-soon* / `onboarding` — scaffolded by `bosc onboard fort-wayne` (#326, #235). **Not promoted**; the review gate is open.
**Scope of this report:** what the committed corpus actually establishes for the two onboarding dimensions (hydrology, economics), the state of the third (data-center activity), and the receiving-water screen.

## 0. Method note / register boundaries

The read-side MCP tools (`entities`, `timeline`, `program_overview`, `hydrology_balance`, `hydrology_scenario`) are **Lima-keyed**: `hydrology_balance` returns the three Lima WWTPs → Ottawa/Pike/Dug Run and the BOSC campus, with **no Fort Wayne content**. This is the documented, deliberate deferral ("the read side stays Lima-keyed until a site reaches parity" — `docs/onboarding.md`), not a corpus gap. Accordingly, all Fort Wayne findings below come from the **slug-scoped onboarding outputs** and the **basin-shared** (Maumee-wide) reference data, read directly. `[verified]/[inference]/[reference]/[open]` tags follow the project vocabulary.

---

## 1. Site identity — confirmed and well-grounded

| Field | Value | Confidence |
|---|---|---|
| Place / basin | Fort Wayne, IN / Maumee (HUC-8 **04100005**, Upper Maumee) | `[verified]` — St. Joseph + St. Marys form the Maumee at Fort Wayne |
| County / FIPS | Allen County, **Indiana**, FIPS **18003** | `[verified]` (note: *not* Ohio's 39003 — the cross-state trap the per-site axis exists to catch) |
| Receiving reach gages | Maumee at Fort Wayne `04182900`; St. Joseph `04180500`; St. Marys `04182000` | `[verified]` NWIS |
| Projection / state | UTM 16N (EPSG 32616); GNIS state IN | `[verified]` |

This identity layer is the strongest part of the record — every geographic knob carries a citation. `src/bosc/sites.py:663-755`.

---

## 2. Receiving-water screen — the marquee finding

**The Fort Wayne WWTP is the largest single discharger in the Maumee basin inventory.**

From the basin-shared ECHO POTW inventory (`data/reference/echo/maumee-wwtp.potw.yaml:777-798`):

- **FORT WAYNE WWTP** — NPDES **IN0032191**, POTW, individual permit
- **Design flow: 74.0 MGD** `[verified, design_flow_missing: false]`
- Receiving water: **"BALDWIN DITCH, MAUMEE R TO ST MARYS RIVER, MAUMEE RIVER"** `[verified]`
- HUC-12 041000050102, Allen County; 41.079611, −85.104389
- **Compliance status: "Effluent – Monthly Average Limit"; informal enforcement count: 1** `[verified: ECHO]`

### The screen math

74.0 MGD × 1.547 = **~114.5 cfs** design-flow discharge `[derived]`.

Against the candidate low-flow denominators (`data/reference/hydrology/low-flow-7q10.derived.yaml`, all LP3-derived, confidence *medium*):

| Denominator (7Q10) | cfs | Discharge ÷ 7Q10 | Reading |
|---|---|---|---|
| Maumee R. @ Waterville (gage proxy) | 114.15 | **~1.0 : 1** | borderline / "tight" |
| St. Joseph + St. Marys at the FW confluence (29.69 + 15.65) | ~45.3 | **~2.5 : 1** `[inference]` | effluent-dominated |
| Baldwin Ditch (immediate receptor) | no cited 7Q10 | — | effluent-dominated by construction |

**Reconciliation flag — the denominator choice changes the verdict.** The committed derived Maumee 7Q10 (114.15 cfs) is measured at **Waterville, OH** — ~50 river-miles downstream of Fort Wayne and *below* the Auglaize and Tiffin confluences. The derived file itself warns this is "the 7Q10 AT THE GAGE, a proxy … a discharger on a tributary is screened only against that tributary's own 7Q10." Fort Wayne discharges at the **headwaters**, where the mainstem is only the St. Joseph + St. Marys sum (~45 cfs). Screening 74 MGD against the Waterville proxy understates the stress; against the headwaters flow the plant is effluent-dominant at design flow. This is geographic reasoning `[inference]`, but it is the single most important screening question for this site.

**Caveat (do not overstate):** 74.0 MGD is the **permitted design flow**, not the metered discharge — actual average flow is lower, so the design-flow screen is a conservative/worst-case denominator-stress test, not a statement of present-day loading. The ECHO "Effluent – Monthly Average Limit" status and 1 informal enforcement `[verified]` independently corroborate that this plant is on the regulator's radar.

**Recorded onboard screen result** (`data/extracted/fort-wayne/ONBOARDING.md:21`): *"basin-screen — 7/129 dischargers screened (1 violation, 2 tight)."* `[verified: onboard log]`. The per-discharger detail is **not committed** (basin-screen is a read-only coverage validation), so I cannot confirm which facility is the "1 violation" — though the FW WWTP's ECHO status makes it the obvious candidate `[inference]`.

---

## 3. Data-center activity dimension — empty, and that is the finding

- `facility=None` in the SiteProfile (`sites.py:738`); `grid-profile.yaml` `load_share: null` with the explicit note: *"This site has no documented data-center facility, so there is no campus load to express as a share."* `[verified]`
- `data/extracted/fort-wayne/` contains **only** `README.md` + `ONBOARDING.md` — no extracted permits, no deeds, no entity graph.
- No `data/research/fort-wayne-*` directory exists — the `--research` self-research pass has **not been run**.
- Dimension-coverage box for "Data-center activity" is **unchecked** (`ONBOARDING.md:9`).

**State it flatly: there is no documented data-center facility for Fort Wayne in the corpus.** The profile frames NE Indiana as "an active boom region — discovery work" `[inference, sites.py:662]`, but discovery has not occurred. The third dimension is genuinely unpopulated; "no data center here yet" is a finding, not a gap to paper over.

---

## 4. Economics + grid backdrop — connector-sourced, high confidence

**Serving utility / grid** (`grid-profile.yaml`): **Indiana Michigan Power Co (I&M, EIA #9324, AEP subsidiary)**, regulator **IURC**, RTO **PJM**. `[reference]` — EIA-861 territory file, *not* corpus-grounded.
- I&M retail: **14,997.9 GWh/yr**, **482,283 customers**, **11.62 ¢/kWh** (EIA-861 2024) `[verified: connector, high]`
- PJM annual load: **815,056.2 GWh/yr** (EIA-930 2024) `[verified: connector]`
- Indiana residential price **16.23 ¢/kWh**; retail sales 103,487 M kWh (EIA API v2, 2025) `[verified: connector]`
- LMP **$35/MWh** `[inference]` — "shared AEP-family value with Lima — verify via PJM Data Miner 2." **Unverified; flagged.**

**County baseline** (`baseline.yaml`, BLS QCEW 2023 / Census ACS5, all `[verified: connector, high]`): Allen County IN — **196,725 jobs**, 10,214 establishments, population **388,791** (2023, up from 351,332 in 2010). Sector LQs: Manufacturing **1.78**, Health Care 1.36; **Information sector LQ 0.44** (1,677 jobs) — i.e., the county is *not* currently data/IT-export-oriented, consistent with no disclosed campus.

---

## 5. Toxics / RSEI — legacy water dischargers, none current

Allen County IN RSEI (`inventory.yaml`, EPA RSEI v234): **128 facilities, 98 scored.** Top score: **VALBRUNA SLATER STAINLESS** (score 10.5M, 23.3M lbs, air/offsite — *not* a water discharger). Of **14 water-releasing facilities**, **every one has `last_year` ≤ 2014** (Dana Light Axle 59,577 lbs→2014; Essex/REA magnet-wire, BF Goodrich, etc.). `[verified]`

**Finding:** direct TRI water releases in Allen County IN are a **legacy** signal — the inventory shows no current (post-2014) toxic water discharger. `toxic_corridor_bbox` is `(0,0,0,0)` `[open]` — no industrial receiving-water corridor has been delineated for this site.

---

## 6. Hydrology design inputs — seeded, partly inferred

- NASA-POWER climatology + Atlas-14 corridor DDF written for the city centroid (41.0891, −85.1439) `[verified: connector]` — e.g., 24-hr depths 2.61″ (2-yr) → 5.73″ (100-yr).
- **`dominant_hsg="C"` is `[inference]`** (NRCS narrative, Blount/Glynwood till + Pewamo clays) — the SSURGO validation step was **skipped** (no footprint). Onboard log line 19: `ssurgo-hsg | skipped | footprint missing`.
- `pre_cover`/`post_cover`/`developed_pervious_cover` = `TODO` `[open]` — no stormwater development scenario, because no site footprint is identified.
- Supply-side water balance (`supply_gage_primary/secondary`, passby minimums) = `TODO`/0.0 `[open]` — the refill/water-supply model is not yet designed for Fort Wayne.

---

## 7. GIS — flood wired, parcels/zoning open

Floodzone = shared national FEMA NFHL layer 28 `[verified]`. **Parcels (`gis_parcel`) and zoning (`gis_zoning`) are both `None`/`TODO` `[open]`** — Allen County IN + City of Fort Wayne ArcGIS REST endpoints have not been discovered. Unlike Findlay, there is no committed district catalog. This is the documented "known lift."

---

## 8. Reconciliation discrepancies & unverified claims

1. **7Q10 denominator mismatch (highest priority).** Waterville-gage 7Q10 (114 cfs) is the wrong-scale proxy for the FW headwaters discharge point (~45 cfs). The screen verdict for the basin's largest plant turns on this. `[inference]`
2. **LMP $35/MWh** copied from the AEP/Lima family — `[inference]`, marked "verify." Indiana (IURC, I&M) is a different retail jurisdiction; do not let a Lima value masquerade as Fort Wayne's.
3. **`dominant_hsg="C"`** is narrative-derived, SSURGO-unconfirmed (step skipped).
4. **Onboard log records `econ-baseline/rsei/consumer-energy/grid-profile = ok`**, but the review-gate box "every written reference value reviewed against a cited source" is **unchecked** — these are onboarding *seeds*, not yet human-verified.
5. **"~4x Lima" framing** (`sites.py:657`) is an `[inference]` in the profile comment; by raw design flow FW (74 MGD) dwarfs Lima's three modeled sanitary-district plants combined (~5.7 MGD) by far more than 4×. The "4×" likely compares against Lima's main municipal WWTP (not in this corpus) — **do not publish the ratio without resolving the comparison basis.**

---

## 9. Recommended follow-up investigations (issue candidates)

1. **Resolve the Fort Wayne 7Q10 denominator.** Derive a headwaters Maumee 7Q10 at the St. Joseph/St. Marys confluence (or screen FW against the summed tributary 7Q10s) and re-run basin-screen; document Baldwin Ditch as the immediate receptor. *Reconciliation discrepancy → blocks a defensible receiving-water claim.*
2. **Pull FW WWTP IN0032191 NPDES permit + fact sheet + DMR/ECHO detail.** Get the actual average discharge vs. 74 MGD design, the effluent monthly-average exceedance behind the ECHO flag, and populate `plant_receiving`. *Corpus gap / new extraction target.*
3. **Run `bosc onboard fort-wayne --research`** to seed the data-center-activity dimension (corpus + entity graph); triage proposals. *Empty dimension.*
4. **Investigate whether a Fort Wayne / NE Indiana data-center facility is disclosed** (permits, IURC large-load filings, local zoning/economic-development records). Until found, keep `facility=None`. *Unverified thesis.*
5. **Discover Allen County IN + City of Fort Wayne parcel/zoning ArcGIS endpoints**; register `gis_parcel`/`gis_zoning` field-maps from live `?f=json`. *Known GIS lift.*
6. **Verify the I&M LMP** via PJM Data Miner 2 (AEP/I&M zone) and replace the inherited $35/MWh. *Unverified figure.*
7. **Commit a site footprint** (`extracted/fort-wayne/bosc-site-footprint.yaml`) to unblock the SSURGO HSG validation and the stormwater cover scenario. *Skipped onboard step.*
8. **Human-review every connector-written reference value** against its citation and check the review-gate boxes before any promotion. *Open review gate.*

**Bottom line:** Fort Wayne is correctly scaffolded across hydrology and economics with cited, regenerable connector data, and it surfaces a genuinely significant receiving-water fact — the basin's largest POTW (74 MGD, IN0032191) discharging to a ditch at the Maumee headwaters under an active effluent-limit compliance flag. But the receiving-water *verdict* is denominator-sensitive and unresolved, the data-center dimension is empty, and the whole record is unreviewed onboarding seed. It earns its coming-soon status; it is nowhere near promotion.
