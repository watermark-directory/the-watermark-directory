# Onboarding — Bryan (bryan)

Living record for the Bryan watershed point (basin: maumee), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

## Dimension coverage

- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)
- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile (**municipal** — see grid note)
- [~] **Data-center activity** — self-research first pass run (#247); **no documented facility**, scoped honestly (no Williams County parcel/recorder layer in the corpus yet — the tripwire isn't installed, #410). See self-research summary below.
- [~] **Per-jurisdiction GIS** — flood = shared national NFHL (wired). Williams County has a **full, valid-cert, queryable ArcGIS** — `ParcelsWeb` (owner **and** CAMA values on one layer, no join) **and** a `Zoning_OD` district catalog — the best-equipped small-county GIS in the network and genuinely wireable; see GIS discovery below. Schemas not committed yet (a reviewed follow-up), but this is a strong wire-ready candidate.

## Grid — the network's first MUNICIPAL utility (notable)

Bryan is served by **Bryan Municipal Utilities** (City of Bryan, EIA **#2439**), not an IOU — the
network's first municipal electric point. It files the **EIA-861 *short form* (861S)**, so it is
absent from the full Sales-to-Ultimate-Customers sheet the grid connector reads; this onboarding
added a **short-form fallback** + an **ownership-aware retail regulator** to `bosc.grid.eia861` /
`bosc.grid.utility`. The generated `grid-profile.yaml` correctly shows: ownership Municipal,
~160 GWh / 5,814 customers (861S 2024), avg price ~10.75¢/kWh; holding company = **American
Municipal Power (AMP)** member (no IOU parent); BA/RTO = PJM (AMP-scheduled); retail regulator =
**municipal home rule** (NOT PUCO rate-regulated). The PJM transmission **zone** is not yet pinned
(LMP is a placeholder) — a verification follow-up.

## Last onboard run

| step | status | output |
|---|---|---|
| scaffold | ok | created 6 dir(s); 6 README(s) |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml |
| corridor-ddf | ok | reference/hydrology/bryan/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/bryan/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/bryan/nasa-power-climatology.yaml |
| basin-screen | ok | 7/129 dischargers screened (1 violations, 2 tight) |
| econ-baseline | ok | reference/economics/bryan/baseline.yaml |
| rsei | ok | reference/rsei/bryan/inventory.yaml |
| consumer-energy | ok | reference/eia/bryan/consumer-energy.yaml |
| grid-profile | ok | reference/eia/bryan/grid-profile.yaml |

## GIS discovery (2026-06-19; schema-driven GIS, #237)

Unlike Van Wert (county PAT MapServer with an **expired** TLS cert) and Fort Wayne (no clean
catalog), **Williams County publishes a full, valid-cert, queryable ArcGIS** across two AGOL orgs —
the county GIS opendata site (`services1.arcgis.com/D85sDZoJyameepNh`) and the county engineer
(`services8.arcgis.com/KG1citvUsI75VegT`). It is the best-equipped small-county GIS in the network:
the parcel layer carries owner **and** CAMA values together (no separate land-values join, unlike
Lucas AREIS). Nothing is committed yet — registering the field-maps from the live `?f=json` is a
reviewed follow-up, not this discovery pass.

| layer | endpoint | finding | status |
|---|---|---|---|
| floodzone | FEMA NFHL (national, layer 28) | wired in the profile (`gis_flood`) | wired |
| parcels (CAMA) | `D85sDZoJyameepNh/ParcelsWeb/FeatureServer/0` (`Parcels_WC`, polygon, 58 fields) | `p_ParcelID`, `p_OwnerName` + owner address, `p_PrimaryParcelUse`, `p_DeededAcres`, `p_Residential/Commercial/Agriculture*LandValue` + `p_*StructureValue`, `p_TotalValue`, `p_TaxingDistrict` — owner **and** values on one layer | wireable lead |
| parcels (engineer) | `KG1citvUsI75VegT/Williams_County_Parcels/FeatureServer/0` + `Auditor_Landcover/FeatureServer/0` | county-engineer parcels + auditor land-cover (alternate/derived source) | wireable lead |
| zoning | `D85sDZoJyameepNh/Zoning_OD/FeatureServer/0` (polygon; fields `Zoning`, `Updated_Zo`) | a parcel-area zoning catalog — directly registerable as a `GisZoningSchema` (polygon-only, like Findlay: district catalog, no parcel-id join) | wireable lead |
| taxing districts | `D85sDZoJyameepNh/TaxingDistricts/FeatureServer/0` | tax/school/fire/ambulance districts | reference |

Follow-up (a strong issue lead): register Williams County `gis_parcel` (`ParcelsWeb` `p_*` field-map —
the network's most complete single-layer parcel GIS, owner+value, no join) and `gis_zoning`
(`Zoning_OD`) from the live `?f=json` — Bryan is a strong candidate to be the network's second
fully-wired GIS after Lima.

## Self-research (Phase 5; #247) — 2026-06-21

First automated-research pass (`bosc research run`, 24 turns, $1.27, read-only over the corpus) →
`data/research/onboard-bryan-bryan-data-center-activity-receivi-2026-06-21/` (`findings.md` + `manifest.yaml`).

**Headline — the network's first municipal utility is the reason to onboard; the receiving-water
screen is unrun.** Bryan's distinction is the **grid**: Bryan Municipal Utilities (City of Bryan,
EIA #2439, an AMP member scheduled into PJM) is the network's first municipal / short-form /
home-rule electric point, exercising the EIA-861S fallback + ownership-aware regulator paths no IOU
site does (cf. PR #388). But the assimilative screen **cannot yet be computed**: Bryan WWTP
(OH0020532, 3.1 MGD ≈ 4.8 cfs — *larger* than Lima's Shawnee II) discharges to **Prairie Creek**
(Tiffin subbasin), which has **no 7Q10** in the corpus, so `bosc basin-network` records `no_7q10`,
dilution `null`. The pre-applied `effluent_dominated_tributary` label is an **`[inference]`**, not a
finding (proposals #408/#409).

**Data-center activity — no documented facility, scoped honestly.** No disclosed facility
(`facility=None`); information-sector LQ 0.19 corroborates the absence. **But scope it honestly:**
unlike Lima (recorder deeds + NPDES applications + site plans), Bryan has **no Williams County
parcel/recorder/permit layer in the corpus** — so "no activity" is *evidence not yet gathered*, not
land assembly ruled out, and the tripwire that would catch quiet assembly isn't installed (proposal
#410). Williams County does have the network's **best-equipped, wire-ready GIS** (full valid-cert
ArcGIS — see GIS discovery above), so that tripwire is genuinely buildable.

**Serving utility — VERIFIED: Bryan IS the municipal (the site the "Bryan trap" is named for).** The
grid connector's EIA-861S short-form fallback correctly identifies City of Bryan #2439 as
**Municipal / home-rule** (NOT PUCO rate-regulated), AMP/PJM — the inverse of the IOU sites'
verification. One flagged placeholder: `lmp_usd_mwh=35.0` is an **`[inference]`** (the AMP/PJM
transmission zone is not yet pinned via PJM Data Miner) — proposal #411.

**Economy / toxics:** manufacturing LQ **4.54** (heavily industrial, declining population) against
info LQ 0.19 — the load-not-jobs shape again; RSEI is county-wide + legacy (vintage tails off by
2014) and `toxic_corridor_bbox` is undelineated (proposal #412).

**Proposals — 5 filed as sub-issues of #380:** #408 (Prairie Creek 7Q10 + the WWTP screen), #409
(ingest the OH0020532 NPDES fact sheet), #410 (the Williams County parcel/recorder tripwire), #411
(pin the AMP/PJM zone + replace the placeholder LMP), #412 (corridor-scope the RSEI/toxics to
Prairie Creek). The GIS lift (register the Williams County `ParcelsWeb`/`Zoning_OD` field-maps) is
the strong wire-ready lead tracked under GIS discovery above.

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.
- [ ] basin-screen coverage is sane for this site's receiving waters.
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [x] Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/) — see self-research summary above; 5 proposals filed as sub-issues of #380 (#408–412).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'bryan' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
