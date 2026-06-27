# IDEM — Fort Wayne (Hatchworks LLC / Project Zodiac) air permits

Indiana Department of Environmental Management (IDEM), **Office of Air Quality** source
documents for the **Hatchworks LLC** data-center campus — Google's "Project Zodiac",
7510 Zodiac Way, Fort Wayne, IN 46816 (Allen County). The first non-Ohio jurisdiction in
the corpus; `idem/` is the Indiana peer of `oepa/`, scoped per site (`idem/<site>/`).

This is **raw, immutable, LFS-tracked source evidence** (chain of custody). Files keep
their AS-RECEIVED IDEM portal names (permit/document number + a stage suffix — `f` final,
`d` draft); canonical names + content-verified dates are recorded non-destructively in
[`filename-map.yaml`](filename-map.yaml). Do not rename or alter a source byte in place.

## Source

Indiana DEM Permit Status Search — https://apps.idem.in.gov/PermitStatusSearch/
(facility: Hatchworks LLC; IDEM **AI ID 133680**; OAQ Stationary Source ID **1800300530**).

## Contents

| File | Permit | Level | Date | Pages |
|---|---|---|---|---|
| `47378f.pdf` | `003-47378-00530` | Title V New Source Construction (Minor PSD/EO) | 2024-09-06 | 226 |
| `48739d.pdf` | `003-48739-00530` (+ `003-48840-00530`) | Part 70 Significant Modification — public-hearing draft | 2025-11-13 | 187 |

The facility is a **Title V (major) air source** — for a data center, the permitted units
are the standby/backup engine fleet. The 2024 NSC permit is the construction authorization;
the 2025 filing is the significant Part 70 operating-permit modification (public-hearing
stage). Ties to `bosc.sites` `_FORT_WAYNE` (#360/#362) and the Hatchworks parcel assemblage
(`data/reference/fort-wayne/bosc-parcels.geojson`).

## Known gaps & caveats

- The IDEM table lists further authorizations not yet captured here: the issued `003-48739`
  (2026-04-10) and `003-48840` TV SPM (2026-06-01) final permits, plus a 2023 confidentiality
  claim (`47378C`) and a Hazardous Waste ID (`INR000158436`, 2025-03-11). Pull as needed.
- Extraction (structured air-permit data → `data/extracted/idem/fort-wayne/`) is a separate,
  later effort — the extract pipeline's profiles do not yet cover air permits.
- A stray file in the source drop (`23665f.pdf` = Keller Crescent Company, Indianapolis) was
  **not** ingested; it is an unrelated facility. The exclusion is recorded in `filename-map.yaml`.
