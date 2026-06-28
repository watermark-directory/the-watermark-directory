# Highland55 — investigative findings

**Corpus**: `data/documents/permits/highland55/` (10 instruments, PR #803)
**Issue**: #447
**As of**: 2026-06-28

## Verified facts from primary instruments

| Fact | Source | Tag |
|---|---|---|
| Developer: **Highland Realty Development LLC / Urbana Owner I LLC**, 720 E Broad St Suite 200, Columbus OH 43215 | Prelim JD cover (3938251) | `[verified]` |
| Contact: **Brian Hughes-Cromwick, VP Acquisitions, Thor Equities** (bhcromwick at thorequities.com) | 401 WQC application (3938244) | `[verified]` |
| Location: west of S U.S. Highway 68, **Urbana Township, Champaign County, OH** | Approved JD cover (3938271) | `[verified]` |
| Vance Brands parcel coordinates: **40.0887°N, -83.7611°W** | Approved JD (3938271) | `[verified]` |
| Vance Brands parcel ID: Champaign Co **K48-25-11-01-30-001-00**, current owner **Brand Investments LTD** | Approved JD (3938271) | `[verified]` |
| Vance Brands parcel area: **~47.6 acres** (agricultural field + wooded fringe) | Approved JD (3938271) | `[verified]` |
| Vance Brands parcel: **no wetlands, no streams** — one non-jurisdictional erosional feature (1,206 LF) | Approved JD (3938271) | `[verified]` |
| Commerce Park AOI: **~40.0812–40.0851°N, -83.7637–83.7645°W** | Prelim JD (3938251) | `[verified]` |
| Commerce Park wetlands: Wetland A (1.31 ac, Cat 1 non-jurisd.) + Wetland B (0.06 ac, Cat 1 non-jurisd.) | Prelim JD (3938251) | `[verified]` |
| Project name in 401 WQC: **"Urbana Brand I"** | 401 WQC (3938244) | `[verified]` |
| 401 WQC project description: "commercial retail buildings, **an industrial warehouse**, **a electrical substation**, roads, parking, stormwater" | 401 WQC (3938244) | `[verified]` |
| 401 WQC project purpose: **"build-to-suit commercial development for future tenants"** | 401 WQC (3938244) | `[verified]` |
| Construction timeline: **06/01/2026 – 06/01/2027** | 401 WQC (3938244) | `[verified]` |
| Wetland impact: **0.07 acres** across three Category 1 non-forested wetlands | 401 WQC (3938244) | `[verified]` |
| Corps district: **Huntington WV** (Teresa Spagna, contact) | Prelim + Approved JD covers | `[verified]` |
| Engineer: **Civil & Environmental Consultants, Inc. (CEC)**, Columbus OH | All instruments | `[verified]` |
| CEC sub-projects: 344-735 (Commerce Park prelim JD), 352-387 (Vance Brands approved JD), 354-449 / 355-192 (third parcel, wetland photos) | 401 WQC (3938244), photo report (3938260) | `[verified]` |
| Photo dates for wetland documentation: **June 26 & July 28, 2025** | Photo report (3938260) | `[verified]` |
| SSURGO (Vance Brands, 352-387): 7 units — BsA (hydric), CnB, CrA, FnA, MIB, MIC2, WsA | Approved JD (3938271) | `[verified]` |
| FEMA flood status: AOI **not in 100-year floodplain** (both parcels) | Both JDs | `[verified]` |

## Signal analysis

**Data-center indicators:**

- **Electrical substation** — the 401 WQC explicitly includes a dedicated substation in the
  project description. Standard warehouse/retail development uses the utility's padmount transformer;
  a dedicated substation indicates high-voltage service (typically 69 kV or 115 kV stepped down
  on-site) for a load >5–10 MW. This is the strongest data-center signal in the corpus. `[inference]`
- **Build-to-suit for future tenants** — developer language common in data center site acquisition,
  preserving tenant anonymity during permitting. `[inference]`
- **"Vance Brands" as named end user** — the name appears in Corps JD filings but is not identified
  in public business records available to the corpus. May be a project codename or SPE name.
  `[open]`
- **47.6+ acre greenfield site** — consistent with a campus-scale facility but also with
  large-format logistics/manufacturing. `[inference]`
- **Thor Equities as developer** — primarily a commercial real estate developer (retail, office,
  industrial); history includes large-format industrial build-to-suit projects. Not a specialist
  data center developer, which is a mild counter-signal. `[inference]`

**Counter-indicators / open questions:**

- Project description includes "commercial retail buildings" — atypical for a pure data center
  campus; could indicate a mixed-use development or placeholder language. `[open]`
- NPDES General Permit scheduled for 03/31/2026 — likely a construction stormwater general
  permit (OHC000002), which all large construction projects require. Not specific to data centers.
- No power spec, cooling system type, or floor plan density visible in available instruments
  (exhibits are image-only, no text layer).

## What the instruments do NOT tell us

- Total project acreage (the full assembly — Commerce Park + Vance Brands + 354-449/355-192
  parcels combined; only the 47.6-acre Vance Brands parcel is measured)
- Any power or load specification
- Cooling system type (once-through, evaporative tower, dry)
- Whether "Vance Brands" is a data center operator or another industrial tenant

## Assessment

Highland55 is a **real, active development project** — not a rumor. Thor Equities is
building a 47.6-acre (minimum) greenfield site west of US-68 in Urbana Township with an
electrical substation. Construction is planned for mid-2026. The end use remains `[open]`:
the substation and build-to-suit framing are consistent with a data center, but also
consistent with high-load industrial or logistics development.

**Current evidentiary state**: `[inference]` — primary instruments confirm the project and
identify the developer (Thor Equities), site, and key infrastructure (substation). The
data-center determination requires one of:

- A county recorder deed naming a data center operator as grantee
- A utility interconnection application showing the expected load (MW)
- A public announcement or ODOD/JobsOhio record identifying the tenant
- An air permit or building permit that names the facility type

Until one of these is in corpus, the Highland55 lead remains `[inference]` on data-center end use.
