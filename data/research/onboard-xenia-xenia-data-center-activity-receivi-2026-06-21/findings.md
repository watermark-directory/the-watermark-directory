# Research run: onboard xenia (Xenia): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-21T23:58:20+00:00
- turns: 33 (cap 30); cost: $1.0716
- tools: ToolSearch, Skill, mcp__bosc__program_overview, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__entities, Grep, Read, Glob, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario
- proposals: 5 (see `manifest.yaml`)

---

I have a complete picture. Here is the findings report.

---

# Findings — Onboarding screen: Xenia (Greene County, OH) as a BOSC watershed-point site

**Task:** assess data-center activity + a receiving-water screen for the candidate site "Xenia," over the BOSC corpus, using read-only tools.
**Tools used:** `program_overview`, `entities`, `timeline`, `list_documents`, `list_extractions`, `hydrology_balance`, `hydrology_scenario`, `read_extraction`; plus text search over the committed reference tree, `watermark.sites`, the frontend registry, and the saved `list_documents` dump.

**Headline:** Unlike a greenfield onboarding, **Xenia is already mid-chain** — its `SiteProfile` is registered and the portable reach/economics connectors have partly run. But the two dimensions this task names — a **receiving-water screen** and **data-center activity** — are both **unbuilt**, and the corpus contains **zero** Xenia primary-source records. This is a clean status report on a half-onboarded site, not a discovery.

---

## 1. Onboarding state: registered and partly seeded, not promoted `[verified]`

Xenia is registered in both registries:
- `src/bosc/sites.py` — `_XENIA` profile (basin `little-miami`), slug-scoped output relpaths, county `Greene County, OH` / FIPS `39057`. (sites.py:1791)
- `web/src/lib/sites.ts` — `slug: "xenia"`, `status: "queued"`, `selectable: false`, `issue: "444"`, watershed "Little Miami". (sites.ts:168–177)

`onboard` has clearly run at least partially — the per-site dirs and house-style READMEs exist, and these connector outputs are **populated with live data**:

| Output | File | Status |
|---|---|---|
| NASA-POWER climatology | `reference/hydrology/xenia/nasa-power-climatology.yaml` | **present** `[verified-connector]` |
| Atlas-14 corridor DDF | `reference/hydrology/xenia/atlas14-corridor-ddf.yaml` | **present** `[verified-connector]` |
| Census+QCEW county baseline | `reference/economics/xenia/baseline.yaml` | **present** `[verified-connector]` |
| EIA consumer energy (OH) | `reference/eia/xenia/consumer-energy.yaml` | **present** `[verified-connector]` |

**Missing / not yet run** (each is a concrete gap, not a hedge):
- **RSEI county toxics inventory** — `reference/rsei/xenia/inventory.yaml` absent (only README).
- **EIA-861 grid profile** — `reference/eia/xenia/grid-profile.yaml` absent (expected: it aggregates a facility load that doesn't exist yet).
- **Basin 7Q10 low-flows for the Little Miami** — see §3; the derived file is Maumee-only.
- **The persisted review gate** — `data/extracted/xenia/ONBOARDING.md` does **not** exist (Urbana and Springfield both have one). Only `data/extracted/xenia/README.md` is present.
- **The self-research first pass** — no `data/research/onboard-xenia-*/findings.md` (Urbana and Springfield each have one dated 2026-06-21). *This report is effectively that missing pass, run by hand.*
- **GIS field-maps** — `gis_parcel=None`, `gis_zoning=None`; `parcels_url`/`zoning_url` are `"TODO"`. Flood is free (national NFHL).
- **Site geometry** — no `bosc-parcels.geojson`, no footprint (`bosc-site-footprint.yaml`) — both pending an identified site.

## 2. The corpus holds zero Xenia records; the bound tools are Lima-only `[verified]`

A case-insensitive search for `xenia | greene | little miami | beavercreek` returns **no matches** in the 1,485-line `list_documents` inventory. The `entities` graph is **entirely Lima / Allen County** — every party, WWTP, and receiving water (Ottawa River, Dug Run, Pike Run) is the Lima reference build. There is no Greene County deed, NPDES permit, meeting, or shell entity.

The MCP hydrology tools take **no site parameter** — they read the active site, which is `lima`:
- `hydrology_balance` returns only the three Lima loop WWTPs (Shawnee II → Ottawa River 4.64 cfs `[doc]`; American Bath → Pike Run 2.32 cfs `[doc]`; American II → Dug Run 1.86 cfs `[doc]`), each a low-flow violation.
- `hydrology_scenario` returns only the Lima/BOSC campus draw (4.85 cfs net = 24.3× the cited Ottawa River 7Q10).

So a Xenia screen is **not blocked by analysis capacity — it's blocked by the absence of committed Little Miami reference data.** This matches the documented model: the read side stays Lima-keyed until a site reaches parity.

## 3. Receiving-water screen: blocked, with one distinguishing constraint `[open]` / `[reference]`

A Tier-0 receiving-water screen needs, per outfall: a cited permitted design flow, the receiving stream, and that stream's **7Q10**. For Xenia, the inputs do not exist:

- **No Little Miami 7Q10.** `low-flow-7q10.derived.yaml` covers only the **Maumee-basin mainstems** (Maumee at Waterville, Auglaize, St. Marys, St. Joseph). None of the Little Miami gages on the Xenia profile — `03240000` (Little Miami nr Oldtown), `03241500` (Massies Creek at Wilberforce), `03242050` (Little Miami nr Spring Valley) — has a derived low flow. `bosc derive-low-flows` has not been extended to this basin. `[verified]`
- **No Xenia-area WWTP.** Profile `plant_receiving={}` and both passby minimums are `0.0 [open]` — no NPDES fact sheet has been ingested for the Xenia/Beavercreek treatment plant(s).
- **The Little Miami is a National & State Scenic River** (NPS Wild & Scenic + Ohio Scenic River) `[reference]`. Per the profile comment, this is Xenia's *distinguishing* feature versus every Maumee and Great-Miami site: a protected receiving water whose anti-degradation / scenic-river status materially constrains a large new discharger or withdrawal, and likely raises the in-stream passby minimum above a routine value. This is the single most important thing to verify and quantify before the site is screened.

The Atlas-14 storm depths *are* in hand for the stormwater side (24-hr depths: 2-yr 2.73 in → 100-yr 5.51 in `[verified-connector]`), so a pre/post-development runoff screen is feasible **once a footprint exists** (`pre_cover`/`post_cover` are still `"TODO"`).

## 4. Data-center activity: none documented; the economic context cuts against an existing cluster `[verified-connector]` / `[inference]`

There is **no documented data-center activity for Xenia in BOSC** — no deeds, shell-LLC SOS filings, stormwater/air permits, or meeting records (profile `facility=None [open]`; the WPAFB-corridor data-center/contamination overlay is the named research target for #444). State this flatly: *as of this corpus, there is no Xenia data-center land assembly or permit record.* That is a finding, not a gap.

The committed county economics baseline (BLS QCEW 2023 / Census ACS, connector `confidence: high`) gives defensible context:
- Greene County population **168,531** (2023); total employment **78,410** jobs.
- **Professional, Scientific & Technical Services (NAICS 54): 11,617 jobs, location quotient 2.11** — roughly twice the national share. `[inference]` this is the Wright-Patterson AFB / defense-contractor signature, consistent with the profile's WPAFB-adjacency note; it is **not** evidence of data-center activity.
- **Information (NAICS 51): 435 jobs, LQ 0.29** — well below the national share. By employment, Greene County shows **no existing data/IT-hosting concentration**, which is consistent with "no data-center cluster here yet."

## 5. Profile field audit — verified vs. open `[verified]` / `[open]`

Sound and citable: `basin=little-miami` (HUC-8 05090202), the three NWIS gages, county/FIPS, design & met lat/lon, UTM 17N, NFHL flood schema. Still **open** and explicitly flagged as such in the profile — do not treat as findings:
- `eia861_utility_number=0` `[open]` (profile guesses AES Ohio/DAY — unverified).
- `lmp_usd_mwh=35.0` is a **placeholder** `[inference]`; PJM zone not pinned (likely DAY).
- `dominant_hsg="B"` is `[inference]`, footprint-dependent (valley outwash A/B vs. till-upland C/D), pending SSURGO over a real footprint.
- `parcels_url`/`zoning_url="TODO"`, `toxic_corridor_bbox=(0,0,0,0)`.

## 6. Actionable follow-ups (track as issues, under #444 / epic #440)

1. **Extend `derive-low-flows` to the Little Miami basin** — pull/curate 7Q10s for gages `03240000`, `03241500`, `03242050` into `low-flow-7q10.derived.yaml` (or a basin-scoped peer). *Blocks the receiving-water screen.* `[open]`
2. **Quantify the Scenic-River overlay** — confirm the Little Miami's NPS Wild & Scenic + Ohio Scenic River designation through the Xenia reach, and capture the anti-degradation status and any elevated in-stream passby minimum into the profile (`passby_primary_cfs`/`passby_secondary_cfs`). This is the site's defining constraint. `[reference → verify]`
3. **Ingest the Xenia/Beavercreek WWTP NPDES permit + fact sheet** — populate `plant_receiving` with cited design flow and receiving reach so `hydrology_balance` has real inputs.
4. **Finish the connector set** — run RSEI (`reference/rsei/xenia/inventory.yaml`) and verify the Greene County retail utility + EIA-861 number (test for non-Lima/cross-state Ohio-hardcoding per the known connector-leak pattern, even though Greene is in-state).
5. **GIS lift** — discover and register Greene County parcel + City of Xenia/Greene zoning ArcGIS layers from a live `?f=json` (field names never fabricated); verify the situs is Greene County **OH**, not a same-name county elsewhere (recorded prior trap). Floodzone is free via national NFHL.
6. **Data-center activity sweep** — open-records/parcel scan for any data-center land assembly, rezoning, or large utility-tap near Xenia/Beavercreek and the WPAFB defense-supplier corridor; ingest deeds/SOS/permits if found, **or record a flat no-activity finding** if not. Include the WPAFB groundwater plume as the `[open]` contamination overlay.
7. **Generate the missing onboarding artifacts** — persist `data/extracted/xenia/ONBOARDING.md` (the blocking review gate) and run `bosc onboard xenia --research`, then triage. Promotion to `live`/`selectable` stays a separate, parity-gated edit.

**Bottom line:** Xenia is a registered, half-seeded site with good hydrometeorology and economics scaffolding but **no receiving-water screen inputs (no Little Miami 7Q10, no local WWTP), no GIS, and no data-center record** in the corpus. Its differentiator — a Scenic-River receiving water — is exactly what is still unquantified. The next decisive step is item #1 (Little Miami low-flows); everything else can proceed in parallel.

---

Want me to write this up as the missing `data/research/onboard-xenia-*/findings.md` (matching the Springfield/Urbana artifact format) and seed `data/extracted/xenia/ONBOARDING.md` with the review-gate checklist?
