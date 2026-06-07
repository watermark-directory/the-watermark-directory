# Allen County Commissioners minutes & agendas (original records)

**Collection:** `commissioners/minutes/` · immutable source evidence

The raw PDF source for the Board of Commissioners' published meeting record.
Bytes are never edited and **filenames are kept exactly as received** (chain of
custody). The derived index/OCR bundle and full provenance live in the mirrored
[`data/extracted/commissioners/minutes/`](../../../extracted/commissioners/minutes/README.md).

## Contents

`raw/` — **930 PDFs** (Git-LFS-tracked), scraped from
`commissioners.allencountyohio.com`. Filenames encode the meeting:
`[AM]MMDDYY` — `A011624` = agenda, 2024-01-16; `M…` = minutes.

## Caveats (read before parsing dates)

- The **filename is the meeting date** (not the upload path, which lags for minutes).
- Three filenames carry a typo extra digit and would mis-parse to a bogus old year —
  treat them as their **real** dates, recorded in the
  [extracted README](../../../extracted/commissioners/minutes/README.md):
  `A0101024` → Oct 10 2024, `A0404024` → Apr 4 2024, `M0115226` → Jan 15 2026.
  Do **not** rename the files; record the canonical date non-destructively.
- A 2023 backfill (299 PDFs) is **raw-only** here — not yet OCR'd into the parquet
  index. Re-run the OCR/index pipeline to fold it in.
