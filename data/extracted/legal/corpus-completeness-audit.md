# Corpus completeness audit — what source documents are missing

**Audited 2026-06-06.** Scope: every collection under [`data/documents/`](../../documents/) cross-referenced against the corpus's own declared expectations — the PRR production tracker, the minutes manifest, the PRR-01 bundle index, and the provenance citations inside [`data/extracted/`](../).

> Method: (1) **Substantive gaps** read from the county's own item-by-item response in [`bosc-prr-production-2026-06-05.response-index.yaml`](prr-mandamus/bosc-prr-production-2026-06-05.response-index.yaml) — i.e. records *requested and not produced*, not inference. (2) **Integrity gaps** computed by script: minutes/agenda filename parsing + pairing over `commissioners/minutes/raw/`, existence-checks of every `*.pdf` cited across `extracted/**`, and the PRR-01 bundle's `derived_files`. Ambiguous date-typo filenames were **not** auto-resolved (the heuristic produced impossible dates); they are listed for human verification. Minutes findings reflect the **2026-04-17 manifest snapshot**, not today.

## Headline

**The archive itself is in good shape; what's "missing" is mostly what the county hasn't produced.** Provenance is clean (94 distinct source PDFs cited across the extractions, 0 genuinely absent). The PRR production binaries are all present. The substantive holes are the records the county **deferred or withheld** — above all the entire **county-wastewater engineering universe (PRR items 5–15)** and the **item-4 cost-benefit analysis** — plus a modest set of corpus-hygiene issues in the minutes series (publication lag + ~12 malformed/misfiled filenames), none of which indicate lost evidence.

---

## 1. Substantively missing — records the county has NOT produced

Declared in the county's first production tracker (cover letter 2026-06-05, Clerk of Board Brittany N. Woods). Of the 19-item request, these remain outstanding:

| Item(s) | Category | What's owed | County's stated posture |
|---|---|---|---|
| **5–15** | County wastewater works | BOSC pump-station/forcemain **RFP + bids**; permits **SWPTI-260294** & **DSW-6756**; **Shawnee II Phase 2** (12.6 MGD) design; **MS Consultants forcemain feasibility** (Res **#113-26**/**#136-26**); **1996 CWA consent decree**; **Cridersville WWTP** records | **Deferred** to the Allen County Sanitary Engineer; "better suited for the Sanitary Engineer." Not produced. |
| **4** | Project BOSC | Cost-benefit analysis / projected tax-revenue impact / public-ROI inputs & assumptions | **Withheld** "being reviewed by our legal counsel for compliance with R.C. 149.43 and R.C. 9.66." Not produced. |
| **2** | Project BOSC | County ⇄ DoD / federal-contractor (GDIT, GDLS) comms re the American Twp facility / corridor | "No records"; county narrowed the ask. Deemed fulfilled. |
| **16** | Website | CMS audit trail / edit history for the Sanitary Engineering pages, 2025-01-01→ | "No records… do not manage the county website." **Contested** — WordPress revision history exists behind a 401 gate (see below). |
| **17** | Website | Internal comms re adding/removing BOSC / RFP / Bistrozzi / Shawnee II references on county sites | "No responsive records." |
| **18** | Address | Records indexed to **4110 N. Cole St., Lima** not caught by entity/project name | "No responsive records" (partial). |
| **19** | Engineer of record | County ⇄ **EMH&T** comms | None as to Commissioners; may supplement from Sanitary Eng. |

**The Category-B deferral is the largest and most case-relevant hole.** Note its internal contradiction, already documented in the corpus: resolutions **#113-26** and **#136-26** (the forcemain-feasibility items the county pushed to the Sanitary Engineer) sit in the Commissioners' **own minutes** (`M021926.pdf:3`, `M022626.pdf:3`) — so the legislative acts plainly exist in the producing body's record. These wastewater records also tie directly to the rest of the corpus: the OEPA **Shawnee II** permit `2PK00002` in [`data/extracted/oepa/`](../oepa/) and the ECHO discharger inventory in [`data/reference/echo/`](../../reference/echo/).

**Item 16 is "missing" by custody disclaimer, not non-existence.** The response index's own rebuttal shows the Sanitary pages' WordPress `modified` dates fall inside the requested window and the `/revisions` endpoint returns **HTTP 401 (gated, not 404)** — the version history exists; the county simply disclaims holding it. Custody sits with the host (AhelioTech / CorpComm-built site) — see [`allen-county-web-vendor-audit.md`](web-vendor-audit/allen-county-web-vendor-audit.md) and [`allen-county-level-sites.md`](web-vendor-audit/allen-county-level-sites.md).

*Universe note:* per the relator's 2026-06-03 narrowing email, any request item not listed was treated as withdrawn — so the "owed" set is bounded by these items. Production is rolling ("every Friday"); items 4 and 5–15 are the ones to watch in subsequent batches.

---

## 2. Corpus-integrity gaps (minor)

### Commissioners minutes series — broadly complete
934 files in [`commissioners/minutes/raw/`](../../documents/commissioners/minutes/) spanning 2023–2026: **475 agendas (`A…`) / 453 minutes (`M…`)**, 468 distinct meeting-dates parsed. The 22-file agenda/minutes asymmetry is **mostly not real absence**:

- **Recent publication lag (not a gap):** 12 dates **2026-03-03 → 2026-04-20** have an agenda but no minutes — these are the most recent meetings relative to the 2026-04-17 manifest snapshot; minutes simply weren't posted yet.
- **Partial 2023 backfill (scope, not loss):** an 8-date cluster in **Dec 2023** (agendas, no minutes) sits in the partially-backfilled 2023 range (the corpus is pinned to 2024–2026).
- **Typo'd agendas masquerading as gaps:** several early-2024 "minutes, no agenda" dates *do* have an agenda under a malformed name — e.g. `A20524-Special.pdf` (2024-02-05), `A22124-Special-1.pdf` (2024-02-21), `A22824-Special.pdf` (2024-02-28).

### ~12 malformed / misfiled filenames (break automated indexing)
| Filename | Issue |
|---|---|
| `Govt.-Structure-Org-Chart-1.pdf` | **Not a meeting record** — reference handout misfiled in `minutes/raw/` |
| `Mayors-and-Zoning-Persons.pdf` | **Not a meeting record** — contact list misfiled |
| `Township-Trustees-Fiscal-Officers.pdf` | **Not a meeting record** — contact list misfiled |
| `CANCELLED-MEETING.pdf` | Cancelled-meeting placeholder (no date) |
| `Board-of-Commissioners-General-Session-September-9-2025-Meeting-Minutes.pdf` | Long-form name for the **2025-09-09 minutes** (should be `M090925.pdf`) |
| `ACC-M102423.pdf` | Stray `ACC-` prefix (minutes 2023-10-24) |
| `A0101024.pdf`, `A0404024.pdf`, `M0115226.pdf` | **7-digit date typos — ambiguous**; verify against the source before renaming |
| `A20524-Special.pdf`, `A22124-Special-1.pdf`, `A22824-Special.pdf` | 5-digit dates (leading zero dropped) |

### PRR-01 bundle derived files — not committed (low concern)
The [bundle index](../../documents/aedg/PRR-01-bundle.ocr.pdf.index.yaml) references seven `derived_files` (`Allen_County_PRR_searchable.pdf`, `..._full_text.txt`, `..._exhibit_index.txt`, `Allen_County_Project_Master_Table.md`, `BOSC_Tetra_Tech_OPC.yaml`, `BOSC_OPC_Detailed_Line_Items.yaml`). None are in `data/documents/aedg/` — but they are **regenerable derivatives** of `PRR-01-bundle.ocr.pdf`, which **is** present. Not lost source material.

### Provenance — clean
Every `*.pdf` cited across `extracted/**` resolves to a real file under `data/documents/`. (Of 94 distinct cited names, the only 2 "unresolved" are false positives: a Google-Slides export title and a prose fragment, not file references.) The 5 PRR-production binaries named in the response index are all present in [`prr-production-2026-06-05/`](../../documents/legal/prr-mandamus/prr-production-2026-06-05/) — the index's "binaries to be added" note is stale.

---

## Genuine-absence shortlist (verify upstream — not lag, not typos)
Low-confidence candidates worth a manual check against [commissioners.allencountyohio.com](https://commissioners.allencountyohio.com):

- **Agenda present, minutes apparently never captured:** 2024-09-25, 2024-12-30, 2025-12-30 *(year-end dates may be cancelled/organizational)*.
- **Minutes present, no agenda, not a known typo:** 2023-03-22, 2023-06-21, 2024-06-20, 2025-08-13, 2025-11-14 *(likely **special** meetings, which carry no separate agenda)*.

These are flagged for verification, **not** asserted as missing.

---

## Cross-refs
- [`bosc-prr-production-2026-06-05.response-index.yaml`](prr-mandamus/bosc-prr-production-2026-06-05.response-index.yaml) — the production tracker §1 is read from
- [`bosc-prr-production-2026-06-05.analysis.md`](prr-mandamus/bosc-prr-production-2026-06-05.analysis.md) · [`../../../docs/legal/mandamus-analysis.md`](../../../docs/legal/mandamus-analysis.md)
- [`allen-county-web-vendor-audit.md`](web-vendor-audit/allen-county-web-vendor-audit.md) · [`allen-county-level-sites.md`](web-vendor-audit/allen-county-level-sites.md) — item-16 custody
- [`../oepa/`](../oepa/) (Shawnee II permit `2PK00002`) · [`../../reference/echo/`](../../reference/echo/) (Maumee discharger inventory) — Category-B wastewater ties
