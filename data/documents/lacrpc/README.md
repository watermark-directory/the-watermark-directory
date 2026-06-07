# LACRPC comprehensive planning / land use / zoning (original records)

**Collection:** `lacrpc/` · immutable source evidence

Comprehensive plans, township/municipal zoning resolutions, and subdivision/land-use
regulations published by the **Lima-Allen County Regional Planning Commission**
(LACRPC). The land-use context for the BOSC corridor. Raw bytes are never edited.

## Source & provenance

All 36 documents were pulled 2026-06-06 from the LACRPC
[Comprehensive Planning · Land Use · Zoning](https://www.lacrpc.com/182/Comprehensive-Planning-Land-Use-Zoning)
page (a CivicPlus DocumentCenter site) via curl. Full per-document provenance —
source URL, the server-declared `as_received_filename`, the raw percent-encoded
`content_disposition_raw`, the source-page section, and a `content_verified_date`
drawn **only** from the document's own text layer — is recorded in
[`MANIFEST.yaml`](MANIFEST.yaml).

## Caveats

- `content_verified_date: null` means the PDF is an image-only scan or states no
  date on its cover (OCR not performed); never infer a date from the filename.
- Filenames are kept exactly as received. A handful (manifest ids 171, 184, 346,
  347, 353, 374) were served with native, already-decoded names.
