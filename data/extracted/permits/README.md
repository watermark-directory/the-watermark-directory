# Permit & corporate-filing extractions

Reviewed structured reads of the permit applications under
[`data/documents/permits/`](../../documents/permits/README.md), plus a few Ohio
Secretary of State business filings.

## Files

| Pattern | Kind | What |
|---|---|---|
| `<app-id>.epa.yaml` | `epa` | One Section 401 Water Quality Certification application per EPA Application ID (Bistrozzi + Dazzler filings). |
| `<app-id>.wetland.yaml` | `wetland` | A USACE Wetland Determination Data Form — field point-sample of the three wetland criteria (`3727950` WD-1, `3727951` WE-1; Project BOSC, Bistrozzi parcels). |
| `sos-<entity>-<date>.sos.yaml` | `sos` | Ohio Secretary of State business-entity filings (Bistrozzi Addition LLC, Magenta Capital LLC, Tilted Gate LLC). |
| `<person>.person.yaml` | `person_intel` | Person-intel notes on individuals in the Bistrozzi research folder (e.g. `montfort-michael` — WSGR D.C. benefits/comp counsel; low-significance). |

## Conventions

Each file records `doc_id`, `source_path`, `pages_read`, and a provenance block.
Applicant / consultant / entity details are read from the document, never inferred.
Keep the EPA Application ID as the filename — it is the authoritative handle.
