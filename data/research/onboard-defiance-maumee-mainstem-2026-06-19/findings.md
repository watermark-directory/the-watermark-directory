# Research run: onboard defiance (Defiance / Defiance County, OH): data-center activity + receiving-water screen for a new watershed-point site. The Defiance WWTP (NPDES OH0024899, ~12 MGD) discharges to the Maumee MAINSTEM right at the Maumee/Auglaize/Tiffin confluence — the cleanest test of whether Lima's small-tributary siting is what drives its effluent-dominance violation (here the mainstem carries far more flow, so the screen reads 'tight' ~6:1 rather than violation; cf. docs/bigger-picture.md). Investigate any Defiance-area data-center projects or land assembly, corpus gaps, reconciliation discrepancies, and GIS/connector leads worth tracking as issues.

- model: `claude-opus-4-8`
- generated: 2026-06-19T21:24:50+00:00
- turns: 21 (cap 30); cost: $1.5786
- tools: ToolSearch, Read, mcp__bosc__hydrology_balance, mcp__bosc__list_documents, Grep
- proposals: 5 (see `manifest.yaml`)

---

I have what I need. Here is the findings report.

---

# Findings — Onboard Defiance (Defiance / Defiance County, OH)

**Scope:** data-center activity + receiving-water screen for a candidate Maumee-mainstem watershed point. Read-only pass over the BOSC corpus + the committed reference/onboarding layer.

**Headline:** Defiance is **already scaffolded** (`SiteProfile` registered, `bosc onboard defiance` run for the hydrology + economics dimensions) and sits as a **coming-soon point** (`status: "open"`, `selectable: false`, issue #238). The receiving-water screen confirms the docs/bigger-picture.md thesis cleanly. The **data-center activity dimension is empty** and the **GIS / utility / SSURGO** review-gate items are open.

---

## 1. Site identity (verified)

- Defiance, OH; basin `maumee`; HUC-8 **04100009 (Lower Maumee)**. `[verified: src/bosc/sites.py _DEFIANCE; data/reference/echo/maumee-wwtp.potw.yaml:2462]`
- Receiving reach gages registered: **04192500 Maumee near Defiance** (mainstem, below the confluence) and **04191500 Auglaize near Defiance**. `[verified: sites.py:985-988]`
- County FIPS **39039**; design/centroid point 41.2868, −84.3621. `[verified]`
- Frontend registry: `status: "open"`, `selectable: false`, issue 238 — **not promoted**. `[verified: web/src/lib/sites.ts:63-72]`

---

## 2. Receiving-water screen — the mainstem-vs-tributary test

**The discharger (high confidence).** Defiance WWTP, **NPDES OH0024899**, POTW, design flow **12.0 MGD**, receiving water **MAUMEE RIVER**, at 41.28801, −84.31848. `[verified: data/reference/echo/maumee-wwtp.potw.yaml:2453-2467]`

**The screen.**
- Discharge: 12.0 MGD × 1.547 = **~18.6 cfs**. `[inference: unit conversion of the verified design flow]`
- Denominator: Maumee 7Q10 = **114.15 cfs**, derived LP3 at **USGS 04193500 (Maumee at Waterville)**, 44 climatic years 1980-2024, confidence *medium*. `[verified: data/reference/hydrology/low-flow-7q10.derived.yaml:9-19]`
- **Dilution ≈ 114.15 / 18.6 = ~6.2:1 — "tight," not a violation.** `[verified via the basin-screen reported in data/extracted/defiance/ONBOARDING.md:21 and docs/bigger-picture.md:78]`

**What this proves.** Set against Lima's plants on the same screen — American Bath → Pike Run **0.01:1 (violation)**, Shawnee II → Ottawa **0.04:1 (violation)**, American II → Dug Run **0.42:1 (violation)** `[verified: hydrology_balance]` — Defiance isolates the variable. Same model, same basin, a comparable mid-size plant; the only thing that changes is the **receiving water**. Discharging to the Maumee mainstem at the Auglaize/Tiffin confluence yields ~6:1 headroom; discharging to an intermittent tributary yields undiluted effluent. **Lima's effluent-dominance is driven by receiving-water choice, not plant size** — Defiance is the clean confirmation. `[inference, well-supported by the screen]`

**Important caveat on the denominator.** The 6.2:1 uses the **Waterville** 7Q10 (04193500), ~50 river-miles *downstream* of Defiance, which drains more area than the reach at the outfall. The derived file itself flags this value as a "screening proxy for the discharge reach," not the reach 7Q10. The true Defiance-reach dilution is therefore **likely tighter than 6.2:1**. The reach-specific gage **04192500 (Maumee near Defiance)** is registered on the profile but is **not** in the derived low-flow file. `[verified: derived YAML note lines 4-7; sites.py:986]` → **follow-up #1.**

**Compliance nuance (verified, under-characterized).** Even with ~6:1 headroom, ECHO records **informal_enf_count: 1** and **formal_enf_count: 1** for OH0024899 (`compliance_status: null`). `[verified: maumee-wwtp.potw.yaml:2469-2470]` This mirrors Fort Wayne — a mainstem plant that still runs against its permit (bigger-picture §2). Dilution headroom is not a clean record. The specific action is not characterized in this field → **follow-up #5.**

---

## 3. Data-center activity — nothing on the record

A full scan of `data/extracted/**` for "defiance" returns **only** the onboarding README and ONBOARDING.md — **no permits, no deeds, no entity-graph parties, no land assembly.** `[verified: Grep data/extracted]` The grid profile carries `load_share: null` because there is no disclosed facility. `[verified: data/reference/eia/defiance/grid-profile.yaml:72-77]` The ONBOARDING dimension box for "Data-center activity" is **unchecked.** `[verified: ONBOARDING.md:9]`

State this flatly: **there is no documented data-center project, application, or land assembly for Defiance in the BOSC corpus today.** That is a finding, not merely a gap — *but* the discovery work that would change it has not been run: no `--research` pass, and no per-jurisdiction GIS parcel scan (the connector isn't registered — see §5). The "no project" reading is therefore **provisional pending that discovery.** `[open]`

One adjacent infrastructure lead worth noting (not a data-center, but the kind of energy-corridor asset boom siting follows): **ANR Pipeline — Defiance Compressor Station (NPDES OH0079294)**, an interstate gas asset in the county. `[verified: maumee-wwtp.all-npdes.yaml:16983-16997]`

---

## 4. Economics & toxics backdrop (verified connector pulls)

- **County employment shrank:** 15,706 (2018) → 15,264 (2023) jobs; population ~38,258 (2023). Manufacturing-concentrated (**LQ 2.32**), near-absent Information sector (**LQ 0.55**, 162 jobs). `[verified: data/reference/economics/defiance/baseline.yaml]` Same "regulated-compute-onto-a-shrinking-industrial-base" shape as Lima.
- **Grid backdrop:** serving utility recorded as **The Toledo Edison Co (#18997, FirstEnergy / PJM ATSI)**, source-tagged `reference` — **see the verification flag in §5.** `[verified value, contested basis: grid-profile.yaml:1-33]`
- **RSEI toxics:** legacy-heavy — GM Defiance Casting, three Johns Manville fiberglass plants (formaldehyde), GT Technologies. **Every facility's `last_year` is 2014.** `[verified: data/reference/rsei/defiance/inventory.yaml]` That uniform 2014 ceiling is a **currency caveat** → follow-up #4. The profile's `toxic_corridor_bbox` is `(0,0,0,0)`, so no receiving-water toxics corridor is defined for Defiance yet. `[verified: sites.py:1043]`

---

## 5. Onboarding gate — what is open

| Item | Status | Evidence |
|---|---|---|
| Hydrology (low-flow, corridor DDF, climatology) | done, real values | `[verified: defiance/atlas14-corridor-ddf.yaml, nasa-power-climatology.yaml]` |
| Economics (baseline, RSEI, consumer-energy, grid) | done | `[verified: ONBOARDING.md:22-25]` |
| **SSURGO dominant HSG** | **skipped** — no footprint; `dominant_hsg="D"` is unconfirmed | `[verified: ONBOARDING.md:19; sites.py:1012 [inference]]` |
| **Data-center activity** | **empty** | §3 |
| **Per-jurisdiction GIS (parcels/zoning)** | **not registered** — `parcels_url/zoning_url="TODO"`, `gis_parcel/gis_zoning=None` | `[verified: sites.py:997-1003]` |
| Self-research pass | not run | `[verified: ONBOARDING.md:33]` |
| Promotion | not promoted (correct) | §1 |

---

## Follow-up investigations worth tracking as issues

1. **Derive a reach-specific Defiance 7Q10 (LP3 at USGS 04192500, Maumee near Defiance; + 04191500 Auglaize near Defiance).** Replace the Waterville (04193500) proxy in the dilution screen. Expected to tighten the 6.2:1; it's the honest reach denominator. Extend `derive-low-flows` to emit these gages. *(corpus/connector gap)*

2. **Verify the Defiance serving utility — Toledo Edison IOU vs. a municipal electric system.** The profile tags `eia861_utility_number=18997` `[reference]` as "largest IOU in Defiance County," and the citation itself cites a retail "electric-aggregation program" — which would *weakly* point to an IOU, but this is exactly the Bryan trap (muni utilities file EIA-861S and are home-rule-regulated, not PUCO). Confirm against the EIA-861 / EIA-861S service-territory file + PUCO map before promotion. If municipal, the grid path and `retail_regulator` are wrong. *(unverified claim)*

3. **Run the SSURGO HSG step against a Defiance footprint (or an area-weighted county read)** to confirm or correct `dominant_hsg="D"`. Currently `[inference]`, skipped for lack of geometry. *(review-gate / unverified value)*

4. **Audit RSEI inventory currency.** All 19 Defiance-County facilities terminate at `last_year: 2014`. Determine whether that is the RSEI v234 vintage ceiling or a truncated pull; a still-operating GM Defiance Casting means a 2014-capped toxics picture understates current corridor risk. Also define a `toxic_corridor_bbox` (currently `(0,0,0,0)`). *(data currency / reconciliation)*

5. **Pull the OH0024899 enforcement/DMR detail.** ECHO shows 1 informal + 1 formal action with `compliance_status: null`. Characterize the action — a mainstem plant with ~6:1 headroom still drawing a formal action is the documented Fort Wayne parallel. *(unverified claim / corpus extraction)*

6. **Stand up the Defiance County / City of Defiance GIS parcel + zoning connector, then run `bosc onboard defiance --research` + a parcel-assembly scan.** This is the only path to populate the data-center dimension. Note adjacent gas infrastructure (ANR Pipeline compressor station) as a siting indicator. Until done, "no data-center project" stays provisional. *(known lift / new extraction target)*

7. **Extract the Defiance WWTP NPDES fact sheet (OH0024899)** to populate `plant_receiving` (currently `{}`) with the outfall RM and any **fact-sheet-cited 7Q10** — the gold-standard denominator over the derived gage proxy. *(corpus gap)*

**No reconciliation discrepancies in the OPC/estimate program touch Defiance** (that program is Lima-specific); the discrepancies above are confined to the receiving-water denominator (#1) and the two reference-tagged guesses (#2 utility, #3 HSG).
