# Section 401 / EPA permit applications (original records)

**Collection:** `permits/` · immutable source evidence

Ohio EPA permit applications, issued permits, and related filings for the
BOSC-corridor developers — mostly Division of Surface Water **Section 401 Water
Quality Certification** applications, plus the Division of Air Pollution Control
(DAPC) **air Permit-to-Install P0138965** for the data center (Facility
`0302022054`): the 2025-12-10 **draft** (`3987141.pdf`, `3987144.pdf`) and the
2026-05-28 **final** issuance (`4132514.pdf`, eDocument ID — 66 pp incl. the
64-item Response to Comments). Raw bytes are never edited; structured reads live in
the mirrored [`data/extracted/permits/`](../../extracted/permits/) as `*.epa.yaml`
(permit-action letters and the air PTI, `kind=epa`). Two documents are a different
shape — USACE **Wetland Determination Data Forms** (`3727950.pdf`, `3727951.pdf`,
the field-delineation point samples) — and are read as `*.wetland.yaml`
(`kind=wetland`, `bosc.models.WetlandDetermination`).

## Layout

| Subfolder | Applicant |
|---|---|
| [`bistrozzi-permits/`](bistrozzi-permits/) | Bistrozzi LLC filings (28 PDFs). |
| [`dazzler-permits/`](dazzler-permits/) | Dazzler-entity filings (10 PDFs). |

Files are named by the EPA **Application ID** (e.g. `3702676.pdf`); the applicant,
consultant/agent, and project details live inside each application's text. Keep the
as-received numeric filenames — they are the authoritative document handle.
