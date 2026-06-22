# Research run: onboard greenville (Greenville · Darke Co): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T04:07:35+00:00
- turns: 24 (cap 30); cost: $0.8209
- tools: ToolSearch, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, mcp__bosc__timeline, Grep, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I have enough grounded material. Here is the findings report.

---

# Findings — Onboarding Greenville · Darke Co (`greenville`)
## Data-center activity + receiving-water screen for a new watershed-point site

## Bottom line

Greenville is a **registered but unpromoted** watershed-point site. A `bosc onboard greenville` run has already populated the portable reach connectors (hydrology climatology, design-storm DDF, county economics, consumer energy), and a `SiteProfile` exists in `bosc.sites`. But the two dimensions this task names are precisely the two that are **not** complete:

- **Data-center activity:** there is **zero** Greenville/Darke County content in the investigative corpus — no deeds, no NPDES permits, no entity-graph nodes, no meeting records. This is a flat no-data finding, not a weak one. `facility=None` in the profile; the data-center dimension is unchecked in the onboarding gate.
- **Receiving-water screen:** the receiving reach is identified and gaged, but the **at-site assimilative denominator (7Q10) for Greenville Creek is not committed** — the derived low-flow file still contains only Maumee-basin streams.

The site is correctly held at `status: "queued"`, `selectable: false` in `frontend/src/lib/sites.ts` (issue #482). Nothing below should be read as promotion-ready.

---

## 1. What the corpus actually contains for Greenville

**`[verified]` — the site is scaffolded, not investigated.** Every Greenville artifact in the repo is connector-generated reference data plus README/ONBOARDING scaffolding (`data/extracted/greenville/`, `data/reference/{hydrology,economics,eia,rsei}/greenville/`). The cross-document tools that drive the published record — `entities`, `timeline`, `program_overview` — return **only** Lima/Allen County content. A case-insensitive search of the full document inventory for "greenville"/"darke" returns no matches.

The onboarding run log (`data/extracted/greenville/ONBOARDING.md`) records the current state honestly:

| dimension | gate status |
|---|---|
| Hydrology (reach connectors) | ☑ done |
| Economics (county baseline, consumer energy) | ☑ done |
| **Data-center activity** (permits/records + entity graph) | ☐ **not started** |
| **Per-jurisdiction GIS** (parcels/zoning) | ☐ **not started** |

---

## 2. Data-center activity screen

**Finding: no documented data-center activity exists in the corpus for Greenville/Darke County.** State this without hedging — it is a finding.

- `_GREENVILLE.facility=None` with the comment "the data-center / ag-land-conversion dimension is the research target (#482)" (`src/bosc/sites.py:2291`).
- No Greenville entity appears in the entity graph; no Darke County deed, NPDES applicant, or shell-LLC node exists.
- The profile's framing of the angle is **`[inference]`, explicitly tagged as such**: Darke is "one of Ohio's top agricultural counties — the data-center angle is greenfield farmland conversion, and the likely utility is a rural electric co-op" (`sites.py:2227–2234`). This is a *hypothesis about why this node is interesting*, not evidence that a project exists. Do not let it read as a finding.

There is **no evidentiary bridge** from the Lima Bistrozzi/Amazon/Google data-center thread into Darke County. The Lima entity graph (Bistrozzi, Tilted Gate, Magenta Capital, Vorys/EMH&T counsel) must stay in its own register; nothing in the record links those actors to Greenville.

---

## 3. Receiving-water screen

### Receiving reach (high confidence)

**`[verified]`** The at-site receiving water is **Greenville Creek → Stillwater River → Great Miami River → Ohio River** (`sites.py:2238, 2284`). Gaging:

| role | USGS gage | name | tag |
|---|---|---|---|
| at-site / abstraction | **03264000** | Greenville Creek near Bradford OH | `[verified]` |
| downstream context | **03265000** | Stillwater River at Pleasant Hill OH | `[verified]` |

A genuinely notable geographic fact, **`[verified]`** in the profile: Darke County **straddles a drainage divide** — eastern Darke (Greenville Creek) drains to the Great Miami/Ohio, while **western Darke drains to the Wabash → Mississippi** (`sites.py:2229–2231`). The site is registered to the Great Miami side; any future site footprint must be confirmed to sit east of that divide before the receiving-water screen applies.

### Design-storm rainfall (high confidence)

**`[verified]`** NOAA Atlas-14 point depths at the Greenville centroid (40.1023, −84.633) are committed (`data/reference/hydrology/greenville/atlas14-corridor-ddf.yaml`): 24-hr depths of **2.66 / 3.74 / 4.40 / 4.92 / 5.47 in** for the 2/10/25/50/100-yr events. NASA-POWER climate normals are committed (annual precip 2.83 mm/day, annual T2M 10.94 °C; `nasa-power-climatology.yaml`).

### The screen denominator — **the gap**

**`[open] / reconciliation discrepancy.** The onboarding log reports `derive-low-flows → ok` and `basin-screen → ok (7/129 dischargers screened, 1 violation, 2 tight)`. But the committed derived low-flow file, `data/reference/hydrology/low-flow-7q10.derived.yaml`, contains **only the four Maumee-basin mainstems** (Maumee, Auglaize, St. Marys, St. Joseph) — **no Greenville Creek, no Stillwater, no Great Miami value**. The regulatory file `low-flow-7q10.yaml` likewise has no Stillwater/Greenville Creek entry.

So:
- The **assimilative-capacity denominator for the at-site reach is not present in the committed record.** The receiving-water screen cannot currently be reproduced from committed data.
- The "1 violation / 2 tight" basin-screen result is **logged but not committed** — there is no per-discharger output file to inspect, and it cannot be confirmed which receiving water the violation sits on. I am reporting it as *what the run logged*, not as an established finding.

This is the single most important thing to close before this screen can be cited.

---

## 4. County economic baseline (context, high confidence)

**`[verified]`** From `data/reference/economics/greenville/baseline.yaml` (BLS QCEW 2023, area 39037; Census ACS5):

- Population **51,655** (2023), gently declining from 52,945 (2010) — `confidence: high`.
- Total private employment **18,511** jobs across **1,361** establishments; essentially flat since 2018 (18,475).
- **Manufacturing-heavy and farm-economy**: Manufacturing is the top sector (4,348 jobs, **location quotient 2.8** — nearly 3× the national share). Transportation & Warehousing LQ 1.3.
- **`[verified]` and material to the data-center thesis:** the **Information** sector (NAICS 51, where data centers land) is **52 jobs / LQ 0.14**, and Professional/Scientific/Technical and Management of Companies both report **0 employment**. Darke is, today, a farm-and-factory county with effectively no information-economy footprint — which is exactly why a hyperscale load would be an outlier worth tracking, and exactly why none is yet in evidence.

Ohio consumer-energy reference is committed (residential electricity 16.96 ¢/kWh, 2025; `consumer-energy.yaml`) — note this is the **statewide** EIA series, not a Darke-specific rate.

---

## 5. High-confidence vs. inferred — explicit register

**Verified / cited (defensible):** receiving-water chain and gage IDs; the drainage divide; Atlas-14 and NASA-POWER values; all QCEW/Census/EIA figures (all carry `confidence: high` and a connector citation); county FIPS 39037; UTM 16N.

**Inference (tagged as such in-source, do not upgrade):**
- `dominant_hsg="C"` — "Darke till plain … `[inference]` pending an SSURGO area-weighted confirmation" (SSURGO step was **skipped**, no footprint).
- Serving utility = "likely a rural electric co-op (Darke REC / Pioneer) ± AES Ohio, DAY zone" — `[inference]`, utility number is `0` (unpinned).
- `lmp_usd_mwh=35.0` — explicit PJM **placeholder**.
- The greenfield-farmland-conversion data-center angle — `[inference]`, the research premise, not a record.

**Open / missing:** the data-center facility; parcel & zoning GIS endpoints (`parcels_url`/`zoning_url="TODO"`); the WWTP NPDES fact sheet (`plant_receiving={}`); in-stream passby minima (`0.0`); the at-site 7Q10.

No approximate (`~`) transcriptions are involved here — these are connector pulls, not scan transcriptions, so the int/float and `~` markers don't apply to this dataset.

---

## 6. Actionable follow-ups (track as issues, under epic #440 / #482)

1. **Commit the Greenville-basin 7Q10 denominator.** `derive-low-flows` reported success but the committed `low-flow-7q10.derived.yaml` is Maumee-only. Either the Great Miami / Greenville Creek (03264000) and Stillwater (03265000) LP3 7Q10s were computed and not written, or the basin-screen ran against a denominator that isn't in the repo. Reproduce, commit, and reconcile against the run log. **Blocks the receiving-water screen.**

2. **Commit the basin-screen output behind "7/129 dischargers, 1 violation, 2 tight."** The result is logged in ONBOARDING.md with no inspectable artifact. Persist the per-discharger screen so the violation can be attributed to a named outfall/receiving water and defended — or qualified.

3. **Data-center activity extraction (the dimension this task names).** Run `bosc onboard --research` (#247) to seed Darke County / City of Greenville record proposals; then targeted PRRs for any rezoning, CRA/TIF, port-authority, or large-load utility-interconnection activity. Until a primary instrument exists, the data-center angle stays `[inference]`.

4. **Per-jurisdiction parcel & zoning GIS connector** (`parcels_url`/`zoning_url` are `TODO`). Note the standing memory hazard: verify the discovered ArcGIS endpoint is **Darke County, *Ohio*** (FIPS 39037), not a same-named county elsewhere, from a live sample before wiring — and confirm any candidate footprint sits **east of the Wabash divide**.

5. **Resolve the three failed/skipped onboard steps:** (a) **RSEI** skipped — missing `data/cache/rsei/v234/.../elements.csv.gz`; (b) **grid-profile** errored — "no Short-Form ('861S') row for utility #0 in OH" (`eia861_utility_number=0` unset; expect a muni/co-op EIA-861S short-form per the known muni pattern); (c) **SSURGO HSG** skipped — needs `extracted/greenville/bosc-site-footprint.yaml`, which itself depends on identifying a candidate site (#3).

6. **Confirm the receiving-water passby minima and the Greenville WWTP NPDES fact sheet** (`plant_receiving={}`, `passby_*_cfs=0.0`) so the low-flow screen has a permitted design-flow numerator, mirroring the Lima `sanitary_basis` treatment.

A note on the published record: nothing here is parity-ready. The honest one-line status for the network page remains **"queued — reach connectors run; data-center and GIS dimensions open; at-site 7Q10 not yet committed."**
