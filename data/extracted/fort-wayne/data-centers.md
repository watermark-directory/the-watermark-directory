# Fort Wayne / Allen Co., IN — Data-Center Activity Register

Discover-and-pin register for the Fort Wayne watershed point (St. Joseph + St. Marys → **Maumee**
headwaters). Status **as of 2026-11-02** (#1262). Tags are BOSC evidentiary discipline:
`[verified]` = cited primary/government source, `[reference]` = secondary source or a party's own
self-report (leads only, never a finding), `[inference]` = arithmetic or pattern from cited inputs,
`[open]` = not found in any public source yet. This records the public record as of the date above
and the primary instruments to *pull*. Nothing here is fabricated; every figure is cited or marked
`[open]`.

This register is the **activity log**. The facility itself — operator, codename, phases, timeline,
utility — is documented in [`datacenter-facility.md`](datacenter-facility.md) and is not repeated
here. The corpus-held IDEM documents are under `data/documents/idem/fort-wayne/`, with extractions
under `data/extracted/idem/fort-wayne/`.

## Disambiguation guardrail — run first, always

- **Allen County, Indiana (FIPS 18003)** is the scope. **Allen County, Ohio** is Lima's county;
  nothing in Lima's land-assembly graph bridges to this site.
- **Hatchworks LLC** is the permittee on the Phase 3 §401 approval; Google is the operator by the
  facility file's sourcing. Do not merge the two as one entity without a document that does.
- **Wabash County, IN** (§3) is a neighbouring county's moratorium — context, not an entry.

## 1 — Google "Project Zodiac" (GCP), Phases 1–3

### 1.1 — Phase 3 water-quality certification `[verified]`

- IDEM **§401 WQC001454 — APPROVAL**, issued **2026-06-05**, authorized impacts to be completed by
  **2028-06-05**; permittee **Hatchworks LLC**, on the 858-acre parcel; **Adams Ditch** relocation
  of **3,415 lf / 0.78 ac**. Source: `data/documents/idem/fort-wayne/WQC001454-Section-401-WQC-Approval.pdf`;
  extraction `data/extracted/idem/fort-wayne/wqc001454.idem.yaml`. The public notice, the hearing
  record and IDEM's response to comments are filed alongside it.
- This closes the "final decision `[open]`" of the 2026-11-02 NW-Ohio sweep. An undated Inside
  Indiana Business "IDEM approves" headline was **not** used: it may describe Phase II.

### 1.2 — Emergency generation (air) `[verified]` + `[inference]`

- IDEM air draft **`48739d.pdf`** (public-hearing draft dated **2025-11-13**; SSM 003-48739-00530 +
  SPM 003-48840-00530) describes "One hundred and forty (140) diesel-fired emergency generators,
  identified as Gen 35 through Gen 174 … each with an output rate capacity of 4049 HP (3019.30 kW)"
  (0-based pp. 11, 31, 35, 38), plus 143 diesel tanks (DST37–179) and 15 cooling towers (CT1–15).
  ⚠️ p. 4 of the same draft writes "3019.30 HP" — a unit slip in the draft; the kW figure on the
  four other pages is the consistent one.
- `[inference]` 140 × 3.0193 MW ≈ **422.7 MW** of added *backup* nameplate, from the **draft's**
  rating. This is not IT load and not a power basis. It sits beside the original permit `47378f`,
  whose per-engine rating (34 engines) is CBI-redacted and was bracketed at 2.9–3.3 MW
  (`data/extracted/idem/fort-wayne/47378f.idem.yaml`). **No edit to `SiteProfile.facility` or the
  facility file is made here** — the final permit, not a draft, is what grounds a figure.
- Final issuance is recorded as 2026-04-10 / 2026-06-01 in the filename-map note citing IDEM's
  permit table; **the final permits are not in the corpus** `[open]`.
- `[reference]` IDEM approval of the 140-generator modification reported 2026-04-14/15 (WBOI, IPM).
  A further application for **228 more generators** was reported in September 2026 (WANE, Journal
  Gazette, WBOI 2026-09-21, 21Alive). No IDEM permit number for it has been read `[open]`.

### 1.3 — Water / hydrology hook

The campus's water and wastewater relation is the City's WWTP (NPDES IN0032191) — see
[`wwtp-receiving-water.md`](wwtp-receiving-water.md) and `wwtp-in0032191.dmr.yaml`. Fifteen cooling
towers in the air draft (§1.2) imply evaporative cooling for that unit set `[inference]`; the
make-up source and volume are `[open]`.

## 2 — City of Fort Wayne: proposed moratorium and review commission

- `[reference]` On **2026-09-08** Councilwoman **Rohli Booker** introduced a one-year moratorium on
  new data-center development (reported as not affecting the existing Google campus) and an
  ordinance creating a "Community Infrastructure and Environmental Review Commission".
  Councilman Jehl withdrew his June task-force proposal (WBOI 2026-09-09). **The vote outcome is
  `[open]`** — no Council journal has been read.

## 3 — Elsewhere in the region (context, not entries)

- **Wabash County, IN — Ord. 2026-85-08** `[verified]` (scanned PDF; page images read): a temporary
  moratorium on data centers adopted **2026-08-31**, signed by Commissioners Niccum, Ross and Dawes,
  attested by Auditor Shelly Baucco. It covers the unincorporated county, and LaFontaine, Lagro and
  Roann only on their own adoption; it runs until the zoning amendment or **18 months**, whichever
  is sooner. Not committed to the corpus.

## Instruments to pull (priority order)

1. IDEM **final** air permit(s) for SSM 003-48739-00530 / SPM 003-48840-00530 — the per-engine
   rating as issued.
2. IDEM application for the reported 228-generator expansion (permit number, engine rating).
3. Fort Wayne Common Council journal for the Booker moratorium + commission ordinances.
4. Make-up water source / volume for the cooling towers (City Utilities agreement).

## Sources

- `data/documents/idem/fort-wayne/WQC001454-Section-401-WQC-Approval.pdf` (and the notice, hearing
  and response-to-comments files beside it) `[verified]`
- `data/documents/idem/fort-wayne/48739d.pdf` `[verified]`
- `data/documents/idem/fort-wayne/47378f.pdf` `[verified]`
- WBOI 2026-04-14: <https://www.wboi.org/business/2026-04-14/idem-grants-google-data-center-developers-permits-for-additional-emergency-generators> `[reference]`
- WBOI 2026-09-09: <https://www.wboi.org/government/2026-09-09/fort-wayne-city-councilwoman-introduces-ordinances-to-rein-in-future-data-center-development> `[reference]`
- Wabash Co. Ord. 2026-85-08: <https://secure.in.gov/counties/wabash/files/ordinances/2026-85-08-Ordinance-Imposing-a-Temporary-Moratorium-on-Data-Centers.pdf> `[verified]`
