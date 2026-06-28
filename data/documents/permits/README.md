# Section 401 / EPA permit applications (original records)

**Collection:** `permits/` · immutable source evidence

Ohio EPA permit applications, issued permits, and related filings for the
BOSC-corridor developers — mostly Division of Surface Water **Section 401 Water
Quality Certification** applications, plus the Division of Air Pollution Control
(DAPC) **air Permit-to-Install P0138965** for the data center (Facility
`0302022054`): the 2025-12-10 **draft** (`3987141.pdf`, `3987144.pdf`) and the
2026-05-28 **final** issuance (`4132514.pdf`, eDocument ID — 66 pp incl. the
64-item Response to Comments). Also here: the campus's **NPDES Construction
Stormwater General Permit coverage** under OHC000006 — facility **`2GC08468`** ("LMA
1A", Turner Construction): the New NOI + `*AG` approval (`3898350`/`3898357`, eff.
2025-11-10), the Igel co-permittee approval (`4150344`), and the 2026-06 Modification
NOI + approval (`4150342`/`4150345`). Raw bytes are never edited; structured reads
live in the mirrored [`data/extracted/permits/`](../../extracted/permits/) as
`*.epa.yaml` (permit-action letters, the air PTI, and the CGP coverage history,
`kind=epa`). Two documents are a different
shape — USACE **Wetland Determination Data Forms** (`3727950.pdf`, `3727951.pdf`,
the field-delineation point samples) — and are read as `*.wetland.yaml`
(`kind=wetland`, `watermark.models.WetlandDetermination`).

## Layout

| Subfolder | Applicant |
|---|---|
| [`bistrozzi-permits/`](bistrozzi-permits/) | Bistrozzi LLC + BOSC-site filings (35 PDFs; incl. Turner's NPDES CGP coverage `2GC08468` and the DAPC trade-secret grant `3859883`/`3859888`). |
| [`dazzler-permits/`](dazzler-permits/) | Dazzler-entity filings (10 PDFs). |

Files are named by the EPA **Application ID** (e.g. `3702676.pdf`); the applicant,
consultant/agent, and project details live inside each application's text. Keep the
as-received numeric filenames — they are the authoritative document handle.
