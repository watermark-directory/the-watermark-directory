# Allen County (Ohio) Board of Elections — committed reference dataset

Publicly available election records for **Allen County, Ohio** (county seat: Lima),
captured for litigation research. Everything here is copied **verbatim** from the
authoritative source named below — no figure is computed, estimated, inferred, or
filled in. Where a value is missing it is left empty, never guessed.

**As-of capture date:** 2026-06-06.

## Authoritative sources

1. **Allen County Board of Elections** — `https://allen.boe.ohio.gov/`
   (the county BOE; mirror at `https://boe.allencountyohio.com/`). 204 N. Main,
   Lima OH 45801-4457, (419) 223-8530. Official results are posted under
   `https://allen.boe.ohio.gov/category/election-results/` and
   `https://allen.boe.ohio.gov/election-reports/`. The result documents themselves
   are hosted as PDFs on the BOE's Dropbox; each PDF's exact download URL is recorded
   in [`source-pdf/SOURCES.txt`](source-pdf/SOURCES.txt).
2. **Ohio Secretary of State** — `https://www.ohiosos.gov/` and the SoS Data Portal
   `https://data.ohiosos.gov/`. Attempted as the canonical machine-readable source
   for county/precinct results and voter-registration counts. **Could not be pulled
   automatically — see Gaps.**

The BOE election reports are produced by **Electionware** (the county's election
management system); the summary reports are the same per-contest canvass the BOE
certifies. PDFs carry a clean embedded text layer, which is what the CSVs below
were parsed from.

## What is here

### `results-csv/` — parsed countywide canvass (machine-readable)

One row per `(election, section, contest, choice)`. Columns:
`election, election_date, section, contest, choice, total, vote_pct, election_day,
absentee, provisional`. `section` is `statistics` (registration/ballots/turnout)
or `contest` (a race or issue). Values are copied verbatim from the source PDF's
text layer; `total` keeps the source thousands-commas (e.g. `33,201`) and `vote_pct`
keeps the printed percent (e.g. `70.87%`). Empty cells = the source printed nothing
in that column for that row (e.g. turnout rows print only a percent).

| file | source PDF | contests | choice rows | stat rows |
|------|-----------|---------:|------------:|----------:|
| [`2024-general-summary.csv`](results-csv/2024-general-summary.csv) | `2024_GEN_SUMMARY_OFFICIAL.pdf` | 20 | 150 | 4 |
| [`2026-primary-summary.csv`](results-csv/2026-primary-summary.csv) | `2026_PRIMARY_SUMMARY_OFFICIAL.pdf` | 103 | 132 | 12 |
| [`2019-general-summary.csv`](results-csv/2019-general-summary.csv) | `G2019_OFFICIAL_SUMMARY.pdf` | 64 | 425 | 4 |

(2026 is a partisan **primary**, so a race appears once per party ballot — e.g.
`Dem For Governor…` and `Rep For Governor…` are separate contest rows. That is the
source structure, not duplication.)

### `registration-turnout.csv` — cross-election statistics block

The 20 `statistics` rows from the three summaries pulled into one file: registered
voters (total, and by party for the 2026 primary), ballots cast (total / by category),
blank ballots, precincts reporting, and total voter turnout. Verbatim from the
summary PDFs. Example values, all as printed:

- 2024 General: Registered Voters - Total **66,201**; Ballots Cast - Total **46,845**;
  Voter Turnout - Total **70.76%**.
- 2026 Primary: Registered Voters - Total **63,151**; Ballots Cast - Total **12,815**;
  Voter Turnout - Total **20.29%**.
- 2019 General: Registered Voters - Total **64,568**; Ballots Cast - Total **12,496**;
  Voter Turnout - Total **19.35%**.

### `precincts-csv/` — per-precinct results (machine-readable, long form)

The precinct-level vote counts, flattened from the BOE **Precinct Results Report**
PDFs to tidy long form: one row per `(election, precinct, contest, choice)`. Columns:
`election, election_date, precinct_code, precinct_name, contest, choice, votes,
vote_pct, row_type`. `row_type` is `choice` (a ballot choice) or `tally`
(Overvotes / Undervotes / Contest Totals / Write-In Totals / Total Votes Cast).
Summed across the 88 precincts these reconcile to the countywide summary:

| file | source PDF | precincts | contests | choice rows | reconciliation vs summary |
|------|-----------|----------:|---------:|------------:|---------------------------|
| [`2024-general-precincts.csv`](precincts-csv/2024-general-precincts.csv) | `2024_GEN_PRECINCT_OFFICIAL.pdf` | 88 | 26 | 4,062 | **39/39 exact** |
| [`2019-general-precincts.csv`](precincts-csv/2019-general-precincts.csv) | `G2019_OFFICIAL_PRECINCT.pdf` | 88 | 72 | 1,061 | 110/114 (see caveat) |
| [`2026-primary-precincts.csv`](precincts-csv/2026-primary-precincts.csv) | `2026_PRIMARY_SOVC_OFFICIAL.pdf` | 88 | 102 | — | **94/103 contests exact** |

`parse_precincts.py` regenerates the 2024/2019 files. The **2026 Primary** has no
per-precinct report — only the wide SOVC cross-tab — so it is flattened separately
by `parse_sovc.py`, which reads word coordinates (`pdftotext -bbox-layout`) and
reconstructs the table (see that file's header). It adds two columns,
`contest_resolved` and `name_resolved`: for **94 of 103** contests the column data
matched a summary contest's candidate-total multiset exactly, so contest + candidate
names come from the committed summary (clean) and reconcile to the official totals;
the other ~9 (uncontested "No Valid Petition Filed" 0-vote races and write-in-only
Libertarian primaries) are retained with their raw stitched labels and flagged
`contest_resolved: no`.

### `source-pdf/` — the official BOE PDFs (primary-source records)

15 PDFs, unaltered bytes, with [`SHA256SUMS.txt`](source-pdf/SHA256SUMS.txt) for
chain-of-custody and [`SOURCES.txt`](source-pdf/SOURCES.txt) for the exact download
URL + any filename normalization. These cover the three elections the BOE currently
posts:

- **2024 General (Nov 5, 2024):** summary, precinct, SOVC (statement of votes cast
  by precinct), most-populous candidate races, most-populous questions/issues, and
  the post-election audit results.
- **2026 Primary / Special (May 5, 2026):** summary, SOVC by precinct, most-populous
  candidate races, most-populous questions/issues.
- **2019 General (Nov 5, 2019):** summary, precinct, SOVC overlaps, audit, and the
  Pandora-Gilboa School Board recount.

### `parse_summary.py`

Regenerates the four CSVs from the summary PDFs' text layer (run `pdftotext -layout`
on the three `*_SUMMARY*.pdf` first into a `txt/` dir, then run this). Kept so the
committed CSVs are reproducible; it copies numbers through verbatim and writes any
line it cannot confidently classify to a sidecar rather than guessing.

## GAPS (what could not be obtained, and why)

- **Ohio Secretary of State machine-readable data — BLOCKED.** Every SoS endpoint
  (`www.ohiosos.gov`, `data.ohiosos.gov` election + voter-registration dashboards,
  and the `www6.ohiosos.gov` ORDS **County Voter Files** FTP download page) returned
  an **HTTP 403 "Website Maintenance" interstitial** to automated requests on
  2026-06-06 — a WAF/bot block, not a real maintenance page. So the following were
  **not** captured here: the SoS statewide-canvass county XLSX files, the
  precinct-level result dashboards, the daily voter-registration snapshots (DATA Act
  archive), and the bulk **county voter file** (the full registered-voter roster with
  party/precinct/history, normally a weekly CSV). These remain available by manual
  browser download from the SoS Data Portal and should be pulled that way.
- **Precinct-level flattening — partly done.** The 2024 and 2019 **Precinct Results
  Report** PDFs are now flattened to `precincts-csv/` (see above), validated against
  the countywide summary (2024 reconciles exactly). Two pieces remain:
  - **2026 Primary** ships only the wide **SOVC** cross-tab (no per-precinct report).
    It is now flattened by `parse_sovc.py` via word coordinates; 94 of 103 contests
    reconcile exactly. The unresolved tail (~9): uncontested 0-vote races whose
    candidate-total signature `(0,)` collides, and Libertarian write-in-only
    primaries whose write-in columns don't sum-match the summary. These rows are kept
    with raw labels and flagged. The 2024/2019 `*_SOVC*` PDFs were not parsed (their
    cleaner per-precinct reports were used instead).
  - **2019 school-levy contest labels.** The per-district levy For/Against rows are
    captured and correctly separated by district, but inherit the adjacent
    `For Member of Board of Education - <district>` title rather than the levy's own
    (the 2019 precinct report groups them that way, as does the summary CSV). The
    **votes are correct**; only the contest label is imperfect for those rows (4 of
    114 reconciliation keys). Verify a 2019 levy's contest name against the source
    PDF before quoting it.
- **Polling-place / precinct master list — not published as a file.** The BOE site has
  no downloadable polling-location or precinct list; the count "88 precincts" appears
  in the summaries ("Election Day Precincts Reporting 88 of 88") but the precinct
  names/polling addresses are only inside the precinct/SOVC PDFs. The SoS precinct
  dashboard (blocked above) would be the structured source.
- **Voter-lookup / list tools are interactive only.** The county apps
  `https://lookup.boe.ohio.gov/vtrapp/allen/vtrlookup.aspx` (registration lookup),
  `…/vtrreport.aspx` (voter lists & labels), and `…/avreport.aspx` (absentee lists &
  labels) are ASP.NET postback forms (JS-driven, no direct file URL), so no bulk
  data could be pulled from them automatically. Noted, not scraped.
- **Write-in candidate labels in the CSVs may be garbled.** A handful of write-in
  presidential/judicial slate names wrap across lines in the PDF; the text-layer
  reflow occasionally attaches a wrapped name fragment to the adjacent row's label.
  The **vote numbers** for these rows are still correct (and are uniformly 0–6 votes);
  only the long write-in `choice` text may be mis-stitched. Named ballot candidates,
  totals, overvotes/undervotes, and contest totals are clean. Verify any write-in
  label against the source `*_SUMMARY*.pdf` before relying on it.
- **Coverage is limited to the three elections the BOE currently posts** (2019 Gen,
  2024 Gen, 2026 Primary). The BOE archive page does not link a 2025 general, 2022,
  2020, etc.; the BOE's "Past Election Reports" Dropbox folder
  (`https://www.dropbox.com/sh/cmdyyc1cncx62gw/AACf0gH2ydvhsH7f3BusjuNPa`) was not
  enumerated in this pass and may hold older elections.

## Regenerating

Raw downloads are cached (git-ignored) under `data/cache/allen-boe/`. To refresh:
re-download the PDFs from the URLs in `source-pdf/SOURCES.txt`, run
`pdftotext -layout` on the summary PDFs (into `data/cache/allen-boe/txt/`), then
`python3 parse_summary.py`. For the precinct CSVs, `pdftotext -layout` the
`*_PRECINCT*.pdf` into the same `txt/` dir, then `python3 parse_precincts.py`
(which also prints the summary reconciliation).

<!-- catalog:begin (generated by `bosc catalog render`; do not edit inside) -->

**Cataloged datasets** — generated from `data/catalog/reference/`; run `bosc catalog render --apply` after editing an entry.

### `allen-boe` — Allen County BOE — Cross-Election Registration & Turnout Statistics

Source: Allen County (OH) Board of Elections — statistics blocks of the three summary canvass PDFs · License: Public records (local government open data) · Access: public · Site scope: lima-legacy · Refresh: on-demand, last 2026-06-06

| file | type | lfs |
| --- | --- | --- |
| `reference/allen-boe/registration-turnout.csv` | text/csv | no |

### `allen-boe-precincts-csv` — Allen County BOE — Per-Precinct Election Results (Long Form)

Source: Allen County (OH) Board of Elections — precinct/SOVC result PDFs flattened to tidy long form · License: Public records (local government open data) · Access: public · Site scope: lima-legacy · Refresh: on-demand, last 2026-06-06

| file | type | lfs |
| --- | --- | --- |
| `reference/allen-boe/precincts-csv/2019-general-precincts.csv` | text/csv | no |
| `reference/allen-boe/precincts-csv/2024-general-precincts.csv` | text/csv | no |
| `reference/allen-boe/precincts-csv/2026-primary-precincts.csv` | text/csv | no |

### `allen-boe-results-csv` — Allen County BOE — Countywide Canvass Summary Results

Source: Allen County (OH) Board of Elections — official summary canvass PDFs (Electionware), parsed per (election, section, contest, choice) · License: Public records (local government open data) · Access: public · Site scope: lima-legacy · Refresh: on-demand, last 2026-06-06

| file | type | lfs |
| --- | --- | --- |
| `reference/allen-boe/results-csv/2019-general-summary.csv` | text/csv | no |
| `reference/allen-boe/results-csv/2024-general-summary.csv` | text/csv | no |
| `reference/allen-boe/results-csv/2026-primary-summary.csv` | text/csv | no |

### `allen-boe-source-pdf` — Allen County BOE — Official Election Result PDFs (Primary Source)

Source: Allen County (OH) Board of Elections — official result PDFs, downloaded verbatim · License: Public records (local government open data) · Access: public · Site scope: lima-legacy · Refresh: on-demand, last 2026-06-06

| file | type | lfs |
| --- | --- | --- |
| `reference/allen-boe/source-pdf/2024_GEN_OFFICIAL_CANDIDATES_MOST_POPULOUS.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2024_GEN_OFFICIAL_QUESTIONS-ISSUES_MOST_POPULOUS.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2024_GEN_PRECINCT_OFFICIAL.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2024_GEN_SUMMARY_OFFICIAL.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2024_Gen_Audit_Results.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2024_SOVC_OFFICIAL.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2026_PRIMARY_MOST_POPULOUS_CANDIDATES.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2026_PRIMARY_MOST_POPULOUS_ISSUES.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2026_PRIMARY_SOVC_OFFICIAL.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/2026_PRIMARY_SUMMARY_OFFICIAL.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/G2019_Audit.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/G2019_OFFICIAL_PRECINCT.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/G2019_OFFICIAL_SUMMARY.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/G2019_Official_Overlaps.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/G2019_Recount_PandoraGilboaSchoolBoard.pdf` | application/pdf | yes |
| `reference/allen-boe/source-pdf/SHA256SUMS.txt` | text/plain | no |
| `reference/allen-boe/source-pdf/SOURCES.txt` | text/plain | no |

<!-- catalog:end -->
