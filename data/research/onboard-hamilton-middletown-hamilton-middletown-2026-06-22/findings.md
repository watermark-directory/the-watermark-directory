# Research run: onboard hamilton-middletown (Hamilton · Middletown): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T01:26:18+00:00
- turns: 26 (cap 30); cost: $1.0916
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__program_overview, mcp__bosc__entities, mcp__bosc__timeline, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, Grep, Read, Glob
- proposals: 5 (see `manifest.yaml`)

---

I now have a complete, grounded picture. Here is the findings report.

---

# Findings — Onboarding screen: Hamilton · Middletown (Butler County, OH) as a BOSC watershed-point site

**Task:** assess data-center activity + a receiving-water screen for the candidate site "hamilton-middletown," over the BOSC corpus, using the read-only BOSC tools.
**Tools used:** `list_documents`, `list_extractions`, `entities`, `timeline`, `program_overview`, `hydrology_balance`, `hydrology_scenario`; plus text/Glob/Read over the committed site-registry (`watermark.sites`, `web/src/lib/sites.ts`), the per-site reference tree, and the Xenia/Springfield/Urbana onboarding precedents.

**Headline:** Hamilton–Middletown is **registered and partly seeded**, like Xenia — its `SiteProfile` exists and the portable hydrometeorology + economics connectors have run. But the two dimensions this task names — a **receiving-water screen** and **data-center activity** — are both **unbuilt**, and the corpus holds **zero** Hamilton/Middletown/Butler County primary-source records. This is a clean status report on a half-onboarded site, not a discovery. Its distinguishing trait is the inverse of every other Miami-basin point: it is the **established-heavy-industry comparator** (Cleveland-Cliffs Middletown Works / former AK Steel) on a **large mainstem** receiving water, not a greenfield on a low-flow tributary.

---

## 1. Onboarding state: registered, hydromet+economics seeded, not promoted `[verified]`

Registered in both registries:
- `src/bosc/sites.py` — `_HAMILTON_MIDDLETOWN` profile, `basin="great-miami"` (lower Great Miami → Ohio River, **HUC-8 05080002**), Butler County **FIPS 39017**, **UTM 16N** (EPSG 32616), with the explicit guard that this is Butler County (seat = City of Hamilton), **not** Hamilton County / Cincinnati (sites.py:1977–2051).
- `web/src/lib/sites.ts` — `slug: "hamilton-middletown"`, `mono: "HAM"`, `status: "queued"`, `selectable: false`, `issue: "443"`, watershed "Great Miami (lower)" (sites.ts:198–207, 315).

Connector outputs **populated with live data** `[verified-connector]`:

| Output | File | Status |
|---|---|---|
| NASA-POWER climatology | `reference/hydrology/hamilton-middletown/nasa-power-climatology.yaml` | **present** |
| Atlas-14 corridor DDF | `reference/hydrology/hamilton-middletown/atlas14-corridor-ddf.yaml` | **present** |
| Census+QCEW county baseline | `reference/economics/hamilton-middletown/baseline.yaml` | **present** |
| EIA consumer energy (OH) | `reference/eia/hamilton-middletown/consumer-energy.yaml` | **present** |

**Missing / not yet run** (each a concrete gap, not a hedge):
- **RSEI county toxics inventory** — `reference/rsei/hamilton-middletown/inventory.yaml` absent (only README). *This is the most consequential omission for this particular site — see §4.*
- **EIA-861 grid profile** — `reference/eia/hamilton-middletown/grid-profile.yaml` absent.
- **Great Miami 7Q10 low-flows** — see §3; the derived file is Maumee-only.
- **The blocking review gate** — `data/extracted/hamilton-middletown/ONBOARDING.md` does **not** exist (Urbana, Springfield, WPAFB each have one). Only `README.md` is present.
- **The self-research first pass** — no `data/research/onboard-hamilton-middletown-*/findings.md`. *This report is that missing pass, run by hand.*
- **GIS field-maps** — `gis_parcel=None`, `gis_zoning=None`; `parcels_url`/`zoning_url="TODO"`. Flood is free (national NFHL layer 28, wired).
- **Site geometry** — no `bosc-parcels.geojson`, no `bosc-site-footprint.yaml` (pending an identified site).

## 2. The corpus holds zero Hamilton/Middletown records; the bound tools are Lima-only `[verified]`

A search for `hamilton | middletown | great miami | butler` returns **no matches** in the 1,485-line `list_documents` inventory. The `entities` graph is **entirely Lima / Allen County** — every party, WWTP, and receiving water (Ottawa River, Dug Run, Pike Run) is the Lima reference build. There is no Butler County deed, NPDES permit, SOS filing, meeting, or shell entity.

The MCP hydrology tools take **no site parameter** — they read the active site, `lima`:
- `hydrology_balance` returns only the three Lima loop WWTPs (Shawnee II → Ottawa River 4.64 cfs `[doc]`; American Bath → Pike Run 2.32 cfs `[doc]`; American II → Dug Run 1.86 cfs `[doc]`), each a low-flow **violation** (dilution 0.04:1 to 0.42:1).
- `hydrology_scenario` returns only the Lima/BOSC campus draw (4.85 cfs = 24.3× the cited Ottawa River 7Q10).

So a Hamilton–Middletown screen is **not blocked by analysis capacity — it's blocked by absent committed Great Miami reference data.** Consistent with the documented model: the read side stays Lima-keyed until a site reaches parity.

## 3. Receiving-water screen: blocked, but with the opposite structural posture from Lima `[open]` / `[inference]`

A Tier-0 screen needs, per outfall: a cited permitted design flow, the receiving stream, and that stream's **7Q10**. For Hamilton–Middletown the inputs do not exist:

- **No Great Miami 7Q10.** A grep of `low-flow-7q10.derived.yaml` for the two profile gages — `03274000` (Great Miami River at Hamilton) and `03272100` (Great Miami River at Middletown) — and for "great miami" returns **nothing**. `bosc derive-low-flows` has not been extended to this basin. `[verified]`
- **No Hamilton/Middletown WWTP or industrial outfall.** Profile `plant_receiving={}`, both passby minimums `0.0 [open]` — no NPDES fact sheet ingested for the municipal plants or the Middletown Works industrial discharge.
- **Structural contrast worth stating up front `[inference]`:** the Lima loop's violations come from small *effluent-dominated headwater tributaries* (Dug Run, Pike Run — 7Q10 of 0.78 and 0.03 cfs). Hamilton and Middletown sit on the **lower Great Miami mainstem**, an order-of-magnitude-larger river near the Ohio confluence. The assimilative-capacity question here is therefore qualitatively different — a new discharge or consumptive draw screens against a real river, not a ditch. **Do not pre-judge the direction:** that is an inference about hydrology, and the actual 7Q10 must be derived from the two cited gages and the result cited before any screen statement is published.

The Atlas-14 storm depths **are** in hand for the stormwater side (24-hr: 2-yr **2.82 in** → 10-yr 3.93 → 25-yr 4.57 → 50-yr 5.07 → 100-yr **5.58 in**, NOAA Atlas-14 PDS at the Hamilton centroid 39.3994/−84.5613) `[verified-connector]`, so a pre/post-development runoff screen is feasible **once a footprint exists** (`pre_cover`/`post_cover` are `"TODO"`). Note the profile's `dominant_hsg="B"` is an **`[inference]`** — lower Great Miami buried-valley outwash, the *inverse* of the Maumee lake-plain HSG-D clays — pending SSURGO over a real footprint.

## 4. Data-center activity: none documented; the economics say "heavy-industry node," not "data cluster" `[verified-connector]` / `[inference]`

There is **no documented data-center activity for Hamilton–Middletown in BOSC** — no deeds, shell-LLC SOS filings, stormwater/air permits, or meeting records (profile `facility=None [open]`; the I-75-corridor data-center dimension is the named research target for #443). State it flatly: *as of this corpus, there is no Hamilton–Middletown data-center land assembly or permit record.* That is a finding, not a gap.

The committed county economics baseline (BLS QCEW 2023 / Census ACS, connector `confidence: high`) gives defensible context — Butler County, FIPS 39017:
- Population **389,910** (2023, ACS5); total employment **160,057** jobs (QCEW 2023; up from 155,213 in 2018).
- **Manufacturing (NAICS 31-33): 24,558 jobs, location quotient 1.83** — the heavy-industry signature, consistent with the registry's framing of this site as the Cleveland-Cliffs Middletown Works / former AK Steel comparator. `[inference]`
- **Wholesale Trade (42): LQ 2.06** and **Transportation & Warehousing (48-49): 9,972 jobs, LQ 1.48** — the I-75 Cincinnati–Dayton logistics-corridor signature. `[inference]`
- **Information (NAICS 51): 895 jobs, LQ 0.29** and **Professional/Scientific/Technical (54): LQ 0.40** — both well below national share. By employment, Butler County shows **no existing data/IT-hosting concentration** — consistent with "no data-center cluster here yet," and a sharp contrast to Greene County/WPAFB's NAICS-54 LQ of 2.11.

**The site's real differentiator is toxics, and it is unmeasured.** RSEI `fips=39017` is set but `inventory.yaml` was never pulled, and `toxic_corridor_bbox=(0,0,0,0) [open]`. Of all the Miami-basin points, this is the one with a large *active* heavy-industrial discharger on the mainstem — so the RSEI inventory is likely to be material here in a way it is not for the greenfield siblings. Running it is the highest-value connector still outstanding.

## 5. Profile field audit — verified vs. open `[verified]` / `[open]`

Sound and citable: `basin=great-miami` (HUC-8 05080002), the two NWIS gages (`03274000`, `03272100`), county/FIPS 39017, the Butler-vs-Hamilton-County guard, design & met lat/lon (39.3994/−84.5613), **UTM 16N** (correctly distinguished from zone 17), NFHL flood schema, LSC GA 136. Still **open** and flagged as such — do not treat as findings:
- `eia861_utility_number=0` `[open]` — the split-utility question (City of Hamilton on its own **municipal** system / AMP, EIA-861S short-form; Middletown on **Duke Energy Ohio**) is unresolved.
- `lmp_usd_mwh=35.0` is a **placeholder** `[inference]`; PJM zone not pinned (**DEOK** — Duke Energy Ohio/Kentucky — is the likely zone, a *third* PJM zone for the network after the Maumee and Mad-River points). `lmp_pnode_id=0 [open]`.
- `dominant_hsg="B"` is `[inference]`, footprint-dependent.
- `parcels_url`/`zoning_url="TODO"`; `gis_parcel`/`gis_zoning=None`.
- The Great Miami Buried Valley Aquifer is described in `hsg_citation` as a **US-EPA designated sole-source aquifer** — flagged `[inference] pending SSURGO`; the sole-source designation itself should be promoted to `[reference]` once verified against the EPA designation record (see follow-up #2).

## 6. Actionable follow-ups (track as issues, under #443 / epic #440)

1. **Extend `derive-low-flows` to the Great Miami basin** — derive/curate 7Q10s for gages `03274000` (Hamilton) and `03272100` (Middletown) into `low-flow-7q10.derived.yaml` (or a basin-scoped peer). **Blocks the receiving-water screen.** `[open]`
2. **Verify the sole-source-aquifer overlay** — confirm the Great Miami Buried Valley Aquifer's US-EPA Sole-Source Aquifer designation through the Hamilton/Middletown reach and promote `hsg_citation`'s claim from `[inference]` to `[reference]`; this is the groundwater analogue of Xenia's Scenic-River constraint and bears on any large groundwater withdrawal or contamination pathway. `[reference → verify]`
3. **Run the RSEI inventory** — populate `reference/rsei/hamilton-middletown/inventory.yaml` and the `toxic_corridor_bbox` for the Middletown Works + Hamilton industrial reach. **Highest-value outstanding connector for this site** (§4); the established discharger is the differentiator. `[open]`
4. **Ingest the Hamilton/Middletown WWTP + industrial NPDES permit(s) + fact sheet(s)** — populate `plant_receiving` with cited design flow and receiving reach so a real `hydrology_balance` input exists. `[open]`
5. **Pin the split utility + PJM zone** — resolve City of Hamilton (municipal/AMP, EIA-861S short-form) vs. Middletown (Duke Energy Ohio); set `eia861_utility_number`, the **DEOK** PJM zone, and a cited `lmp_usd_mwh`. **Re-scan grid + consumer-energy connectors for any non-Lima/cross-state Ohio-hardcoding** per the known connector-leak pattern (Butler is in-state, but the muni/short-form path is the same one that bit Bryan). `[open]`
6. **GIS lift** — discover and register **Butler County, OH** parcel + City of Hamilton / Middletown zoning ArcGIS layers from a live `?f=json` (field names never fabricated). **Verify the situs is Butler County OH** — the same-name-county trap is acute here (Hamilton County ≠ City of Hamilton); the profile already guards it, but confirm from a live sample. Floodzone is free via national NFHL. `[open]`
7. **Data-center activity sweep** — open-records/parcel scan for any data-center land assembly, rezoning, or large utility-tap along the I-75 corridor near Hamilton/Middletown; ingest deeds/SOS/permits if found, **or record a flat no-activity finding** if not. `[open]`
8. **Generate the missing onboarding artifacts** — persist `data/extracted/hamilton-middletown/ONBOARDING.md` (the blocking review gate, matching Urbana/Springfield/WPAFB) and the `data/research/onboard-hamilton-middletown-*/findings.md` artifact. Promotion to `live`/`selectable` in `sites.ts` stays a separate, parity-gated edit. `[open]`

**Bottom line:** Hamilton–Middletown is a registered, half-seeded site with solid hydrometeorology and county economics but **no receiving-water screen inputs (no Great Miami 7Q10, no WWTP/industrial NPDES), no RSEI inventory, no GIS, and no data-center record** in the corpus. Unlike its greenfield siblings, its defining features are an *established* heavy-industrial discharger on a *large mainstem* river over a *sole-source aquifer* — which makes the **RSEI inventory (item #3)** and the **Great Miami 7Q10 (item #1)** the two decisive next steps. Everything else can proceed in parallel.

---

I can persist this as the missing `data/research/onboard-hamilton-middletown-*/findings.md` artifact and seed `data/extracted/hamilton-middletown/ONBOARDING.md` with the review-gate checklist (matching the Urbana/Springfield/WPAFB format) if you'd like — say the word and I'll write them.
