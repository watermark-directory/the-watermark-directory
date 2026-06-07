# Ohio EPA NPDES permits & fact sheets (original records)

**Collection:** `oepa/` · immutable source evidence

Ohio EPA NPDES permit documents for the sanitary/wastewater facilities relevant to
the BOSC corridor. Raw bytes are never edited; structured reads live in the mirrored
[`data/extracted/oepa/`](../../extracted/oepa/) as `*.npdes.yaml`.

## Contents

Three document types per permit number — the issued **permit**, its **fact sheet**,
and the **draft public notice** (`draft-pn`):

| Permit | Facility |
|---|---|
| `2PH00006` | American II |
| `2PH00007` | American / Bath |
| `2PK00002` | Shawnee II |

Filenames carry the permit number, facility slug, document type, and (where stated)
a date. Each PDF keeps its as-received name; provenance is recorded in the matching
extraction's `meta` block.
