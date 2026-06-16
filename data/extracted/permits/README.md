# Permit & corporate-filing extractions

Reviewed structured reads of the permit applications under
[`data/documents/permits/`](../../documents/permits/README.md), plus a few Ohio
Secretary of State business filings.

## Files

| Pattern | Kind | What |
|---|---|---|
| `<app-id>.epa.yaml` | `epa` | One Ohio EPA permit action per document ID — mostly Division of Surface Water §401 / PTI letters (Bistrozzi + Dazzler), plus the DAPC **air Permit-to-Install P0138965**: the draft (`3987141`/`3987144`) and the 2026-05-28 **final** (`4132514`, which adds the emission-unit groups, synthetic-minor caps, and 64-item Response to Comments in extra fields). |
| `lma1a-npdes-cgp-coverage.epa.yaml` | `epa` | The campus's **NPDES Construction Stormwater coverage** history (facility `2GC08468`, "LMA 1A") under OHC000006 — Turner's `*AG` (eff. 2025-11-10), Igel co-permittee (`*BG`, 2025-11-12), 2026-06-10 modification to 309.2 ac — spanning 5 eDocs (`3898350`/`3898357`/`4150342`/`4150344`/`4150345`). Carries a `coverage_history` + `timing_determination` (coverage preceded the 2025-12-08 disturbance; resolves #143/#154). |
| `<app-id>.wetland.yaml` | `wetland` | A USACE Wetland Determination Data Form — field point-sample of the three wetland criteria (`3727950` WD-1, `3727951` WE-1; Project BOSC, Bistrozzi parcels). |
| `sos-<entity>-<date>.sos.yaml` | `sos` | Ohio Secretary of State business-entity filings (Bistrozzi Addition LLC, Magenta Capital LLC, Tilted Gate LLC). |
| `<person>.person.yaml` | `person_intel` | Person-intel notes on individuals in the Bistrozzi research folder (e.g. `montfort-michael` — WSGR D.C. benefits/comp counsel; low-significance). |

## Conventions

Each file records `doc_id`, `source_path`, `pages_read`, and a provenance block.
Applicant / consultant / entity details are read from the document, never inferred.
Keep the EPA Application ID as the filename — it is the authoritative handle.
