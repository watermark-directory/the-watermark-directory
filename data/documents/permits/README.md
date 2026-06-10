# Section 401 / EPA permit applications (original records)

**Collection:** `permits/` · immutable source evidence

Ohio EPA Section 401 Water Quality Certification permit applications (and related
filings) for the BOSC-corridor developers. Raw bytes are never edited; structured
reads live in the mirrored [`data/extracted/permits/`](../../extracted/permits/) as
`*.epa.yaml` (permit-action letters, `kind=epa`). Two documents are a different
shape — USACE **Wetland Determination Data Forms** (`3727950.pdf`, `3727951.pdf`,
the field-delineation point samples) — and are read as `*.wetland.yaml`
(`kind=wetland`, `bosc.models.WetlandDetermination`).

## Layout

| Subfolder | Applicant |
|---|---|
| [`bistrozzi-permits/`](bistrozzi-permits/) | Bistrozzi LLC filings (27 PDFs). |
| [`dazzler-permits/`](dazzler-permits/) | Dazzler-entity filings (10 PDFs). |

Files are named by the EPA **Application ID** (e.g. `3702676.pdf`); the applicant,
consultant/agent, and project details live inside each application's text. Keep the
as-received numeric filenames — they are the authoritative document handle.
