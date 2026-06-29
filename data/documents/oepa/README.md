# Ohio EPA NPDES permits & fact sheets (original records)

**Collection:** `oepa/` · immutable source evidence

Ohio EPA NPDES permit documents for the sanitary/wastewater facilities relevant to
the BOSC corridor. Raw bytes are never edited; structured reads live in the mirrored
[`data/extracted/oepa/`](../../extracted/oepa/) as `*.npdes.yaml`.

## Contents

### Site-specific NPDES permits

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

### Statewide general permits

#### `OHD000001_Draft.pdf` / `OHD000001_Draft_PN.pdf` / `OHD000001_Draft.fs.pdf`

**Ohio EPA Draft General NPDES Permit for Data Center Facilities** — Permit No. OHD000001.
Ohio's first statewide general permit class specifically for data center discharges. All
three document types: draft permit (31 pp.), public notice (2 pp., No. 215991), and fact
sheet (7 pp.).

Issued: October 31, 2025. Public hearing: December 17, 2025.
Director: John Logue. Contact: Allison Cycyk [Allison.Cycyk at epa.ohio.gov], 330-963-1132.

**Scope:** Cooling water (once-through and recirculated), low-volume wastewaters (cooling
tower blowdown, boiler blowdown, air compressor condensate), stormwater. SIC code 7374.
Excludes: >2 MGD surface water intake, thermal limit exceedances, within 500 yards of a
public water supply intake, Outstanding State Waters, Ohio River direct discharge.

**Antidegradation:** OAC 3745-1-05(D)(1)(j) invoked — social/economic development
carve-out applied. No alternatives analysis required.

**Lima relevance:** The 500-yard-upstream-of-intake exclusion is the key eligibility gate
for any data center on the American Sugar Creek / Ottawa River corridor near Lima's water
supply intake.
