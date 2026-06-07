# Permit & corporate-filing extractions

Reviewed structured reads of the permit applications under
[`data/documents/permits/`](../../documents/permits/README.md), plus a few Ohio
Secretary of State business filings.

## Files

| Pattern | Kind | What |
|---|---|---|
| `<app-id>.epa.yaml` | `epa` | One Section 401 Water Quality Certification application per EPA Application ID (Bistrozzi + Dazzler filings). |
| `sos-<entity>-<date>.sos.yaml` | `sos` | Ohio Secretary of State business-entity filings (Bistrozzi Addition LLC, Magenta Capital LLC, Tilted Gate LLC). |

## Conventions

Each file records `doc_id`, `source_path`, `pages_read`, and a provenance block.
Applicant / consultant / entity details are read from the document, never inferred.
Keep the EPA Application ID as the filename — it is the authoritative handle.
