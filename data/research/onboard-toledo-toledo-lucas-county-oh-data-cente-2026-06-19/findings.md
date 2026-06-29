# Research run: onboard toledo (Toledo / Lucas County, OH): data-center activity + receiving-water screen for a new watershed-point site. Investigate Waterville, OH specifically (Lucas County, the Maumee-at-Waterville reach just upstream of Toledo) for any data-center activity or land assembly — there are rumblings of a project there — alongside the Toledo metro and the Lucas Co WRRF (OH0034223) discharge to the tidal lower Maumee.

- model: `claude-opus-4-8`
- generated: 2026-06-19T20:12:02+00:00
- turns: 28 (cap 30); cost: $1.3694
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__program_overview, Read, Grep, Glob, Bash
- proposals: 5 (see `manifest.yaml`)

---

# Findings — Toledo / Lucas County onboarding: data-center screen + Lower-Maumee receiving water

## Scope and method

I searched the committed corpus (`data/extracted/**`, `data/reference/**`), the Toledo `SiteProfile` (`src/bosc/sites.py`), the ECHO Maumee POTW inventory, the derived low-flow reference, and the self-research run directory. Registers below follow the repo tag vocabulary: `[verified]` = read from a cited corpus/connector file; `[inference]` = my labelled reading; `[open]` = explicit open question; `~` preserved for approximate figures. **The Allen County / Lima investigative thread is kept strictly separate** — I did not import any Lima entity, deed, or hypothesis into the Toledo register, and I flag the one place the two records touch.

---

## 1. Onboarding state — what's done, what's open

A prior `bosc onboard toledo` pass (#326) has scaffolded the **reach/economic dimensions**; the **investigative dimension is unstarted**. `[verified: data/extracted/toledo/ONBOARDING.md]`

| Dimension | Status | Source |
|---|---|---|
| Hydrology (low-flows, DDF, climatology) | done | `reference/hydrology/{low-flow-7q10.derived.yaml, toledo/*}` |
| Economics (county baseline, RSEI, energy, grid) | done | `reference/economics/toledo/baseline.yaml`, `reference/eia/toledo/*` |
| **Data-center activity (permits/records + entity graph)** | **`[ ]` not started** | ONBOARDING.md line 9 |
| Per-jurisdiction GIS (parcels/zoning) | partial — flood wired; parcels/zoning *discovered but not committed* | ONBOARDING.md GIS discovery |

The profile records `facility=None` and tags every facility-specific model input `[open]` "until a site is identified"; GIS `parcels_url`/`zoning_url` are `"TODO"`. `[verified: src/bosc/sites.py L871–950]`

---

## 2. Receiving-water screen — Lucas Co WRRF (OH0034223) and the Lower Maumee

The lower-Maumee POTW set (EPA ECHO, HUC-8 04100009) is in the committed inventory. The named facility and the screening denominator are both present:

- **LUCAS CO WRRF — NPDES OH0034223** — permitted **design flow 22.5 MGD** `[verified, high confidence: data/reference/echo/maumee-wwtp.potw.yaml L2628–2649]`. FRS `110000578036`; HUC-12 041000090903; at 41.535, −83.701. ECHO `compliance_status: null`, informal enforcement 1, **no formal enforcement** — clean per the connector. Caveat: ECHO's `receiving_water` is **null** for this permit; the "Maumee River" assignment comes from the SiteProfile/FacDerivedHuc, not the permit record itself.
- **Maumee River at Waterville (USGS 04193500)** — derived **7Q10 = 114.15 cfs** `[verified: reference/hydrology/low-flow-7q10.derived.yaml]`, but flagged **source=derived, confidence medium** — a screening proxy, *not* a cited regulatory 7Q10.

Screen result (my arithmetic, `[inference]`/derived, 1 MGD = 1.5472 cfs):

| Quantity | Value |
|---|---|
| WRRF effluent at design | ~34.8 cfs |
| Effluent fraction at 7Q10 | **~23%** |
| Stream:effluent dilution | **~3.3 : 1** |
| WRRF + Perrysburg WWTP (8.0 MGD, same HUC-12 reach) | ~47 cfs → **~29%** at 7Q10 |

**Reading `[inference]`:** This is the river-only, worst-case screen. Two facts make it a *conservative ceiling*, not the operating condition: (a) the WRRF sits **downstream of the Waterville gage in the tidal/lake-backwater reach** the profile calls "Lower Maumee / tidal corridor," where true dilution far exceeds the gage 7Q10; (b) Toledo's second mainstem gage, **Maumee at Anthony Wayne Bridge (04193990)**, is tidal and has no meaningful 7Q10. So even the harsh screen reads ~3.3:1 — and the tidal regime is far more dilute. This is exactly the **comparator the profile was built to test** (sites.py L862–870): "Where Lima discharges to tiny tributaries… the Lucas Co WRRF discharges to the tidal lower Maumee — a fundamentally different dilution regime (the 'is Lima's tributary siting the outlier?' contrast)." `[verified: src/bosc/sites.py]` The Toledo number empirically supports that framing.

**Coverage gap (important):** The **dominant Toledo metro POTW — the City of Toledo Bay View plant — is absent** from the committed slice (`grep` for "Bay View"/"City of Toledo" returns nothing in the 129-facility file). Bay View discharges to Maumee Bay / Lake Erie and is almost certainly coded to a Lake-Erie-shoreline HUC outside the 7-HUC Maumee query. The committed inventory's own caveat warns dischargers that "didn't geocode… can be missed." So the Lower-Maumee POTW picture here is missing the single largest plant in the metro. `[verified by absence + meta caveat: maumee-wwtp.potw.yaml L16–20]`

---

## 3. Waterville / data-center activity — the headline is an absence

**Finding, stated flatly:** The corpus contains **no primary-source evidence — no deed, parcel record, NPDES or air permit, zoning or rezoning action, development agreement, or named entity — of any data-center project or land assembly in Waterville, OH, or anywhere in Lucas County.** A full-tree search of `data/extracted/**` for Toledo/Lucas/Waterville returns only (a) the onboarding scaffolding above and (b) **one** investigative-content mention — and that one is a *Lima/Allen-County proponent talking point*, not a Toledo project:

> the AEDG data-center release quotes a proponent that "Toledo alone has 70 million gallons per day in excess water capacity." The corpus analyst already annotated it: *"the 'Toledo 70 MGD excess' point is about Toledo, not Lima."* `[verified: data/extracted/aedg/aedg-data-center-release.release.yaml L66–78]`

That is a generic water-capacity argument deployed in the Lima record; it is **not** corroboration of a Waterville project, and I am not treating it as such. The entity graph and timeline are built from the Allen County deeds/NPDES and carry **no Toledo/Lucas nodes**; the standing `corpus-completeness-audit.md` has no Toledo/Lucas/Waterville entry at all. `[verified by absence]`

The "data-center activity" dimension has **not been run** — `data/research/` holds research passes for **Findlay, Fort Wayne, and Van Wert, but no Toledo run** `[verified: data/research/ listing]`.

**Conclusion `[inference]`:** the "rumblings of a project at Waterville" is an **unverified tip with zero corpus corroboration**. It is an `[open]` lead to be worked, not a finding — and it should not be published as anything stronger until an instrument (a recorded deed, an OEPA permit application, a township/county rezoning, an economic-development agreement) names a site or a party.

The good news for working it: the onboarding GIS discovery found **Lucas County AREIS is a full, queryable ArcGIS REST** (parcels + CAMA land-use + land-values + a parcel-level zoning catalog) — described as "the strongest wire-ready GIS in the network." `[verified: ONBOARDING.md L27–44]` That is the right instrument for a land-assembly screen *once a candidate area near Waterville is identified* — a candidate set deserving a closer look, never a prediction (gis-and-siting discipline).

---

## 4. Backdrop (brief, for context)

- **Economy:** Lucas County 196,306 jobs (2023), **down from 209,708 in 2018**; population 428,748 and declining since 2010; Information-sector location quotient **0.49** (well below national). `[verified: reference/economics/toledo/baseline.yaml]` `[inference]` a shrinking, below-average tech-employment base — relevant to any benefit-export argument, consistent with the platform's pro-standards posture.
- **Grid:** First Ohio site **not on AEP** — **Toledo Edison (FirstEnergy, EIA #18997), PJM ATSI zone**. 2024 retail 11,412.9 GWh, 316,087 customers, 16.77¢/kWh `[verified, connector: reference/eia/toledo/grid-profile.yaml]`. The LMP ($35/MWh) is a profile **`[inference]` placeholder — verify via PJM Data Miner 2**, not the AEP value.

---

## 5. Follow-up investigations worth tracking as issues

1. **Work the Waterville tip from primary records (new extraction target).** Run `bosc onboard toledo --research` (the unstarted #247 dimension) and, in parallel, pull Lucas County recorder deeds + OEPA eDoc (air PTI / NPDES / SWP3) and township/county rezoning minutes for the Waterville/Maumee-mainstem reach. Goal: convert the `[open]` tip into either a documented site or a sourced no-link. *Until then it stays unpublished.*

2. **Wire the Lucas County AREIS parcel/zoning connector + run a land-assembly screen.** Register `gis_parcel` (Tyler/Parcels + AREIS land-use/land-values join) and `gis_zoning` (Parcel_Zoning) from the live `?f=json` (endpoints already discovered in ONBOARDING.md). Toledo is the network's best candidate for a second fully-wired GIS after Lima — and the only way to test assembly/ownership clustering near Waterville.

3. **Fix the Bay View / Toledo metro POTW coverage gap.** The dominant City of Toledo plant is missing from the HUC-04100009 ECHO slice (Maumee Bay / Lake Erie shoreline HUC). Re-query ECHO including the Western-Lake-Erie shoreline HUCs and confirm the basin screen captures Toledo's largest discharger before any "Lower Maumee receiving water" claim is published.

4. **Upgrade the WRRF screen denominator from derived to cited.** The 114.15 cfs Waterville 7Q10 is `source=derived, confidence medium`. Pull the OEPA-cited 7Q10 for the OH0034223 receiving reach (and confirm whether a *tidal* low-flow screen is even the right instrument). Also backfill the null `receiving_water` for OH0034223 from the permit fact sheet so the Maumee assignment is permit-sourced, not profile-sourced.

5. **Verify the PJM ATSI LMP.** Replace the `$35/MWh` `[inference]` placeholder with a Data Miner 2 `da_hrl_lmps` annual ATSI value before any cost-of-power figure ships for Toledo.

6. **SSURGO HSG confirmation.** `dominant_hsg="D"` is `[inference]` (Black Swamp lake-plain clays); the onboard SSURGO step skipped for lack of a footprint. Confirm area-weighted HSG once a candidate footprint exists — it materially changes any stormwater/detention result.

**Promotion remains correctly gated:** Toledo is a *coming-soon* point; flipping `status→live` / `selectable→true` in `web/src/lib/sites.ts` is a separate manual, parity-gated edit and should not happen until at least #1 and #3 close.

---

I did not write this to disk — say the word and I'll commit it as `data/research/onboard-toledo-…/findings.md` to match the Findlay/Fort Wayne/Van Wert pattern, and/or open the six follow-ups as issues.
