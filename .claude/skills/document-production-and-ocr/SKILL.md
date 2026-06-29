---
name: document-production-and-ocr
description: Use for producing, formatting, validating, or rendering finished documents (Word/docx, PDF), and for extracting text from scanned PDFs or normalizing tabular data exports. Trigger on docx generation or editing, applying a house format spec, PDF rendering or visual QA, OCR of scanned documents, or cleaning a spreadsheet/status-report export. Methodology and commands are generic; the house format spec and file-specific quirks live in the project enrichment layer.
---

# Document Production & OCR

Mechanics for turning analysis into finished, format-correct, validated deliverables.

## House format

Published documents follow a single consistent format spec (typeface, point/leading, margins in twips, section-break style, citation/superscript convention, numbered sources list). The project enrichment layer holds the exact values; apply them uniformly across every installment so the series reads as one body of work. Never improvise format on a published piece.

## docx production workflow

For non-trivial Word documents, work at the XML level rather than fighting a high-level API:

```
unpack docx → edit document XML → validate → repack → render to PDF (LibreOffice headless) → rasterize for visual QA (pdftoppm)
```

Validate after every structural edit; a docx that opens in one tool but is malformed will surface later. Always do a final visual QA pass on the rendered PDF — read the pages as images, do not trust that the XML edit produced the intended layout.

## PDF OCR workflow

For scanned / image-only PDFs:

```
copy source to a simple path (e.g. /tmp/src.pdf to avoid path-escaping issues)
pdftoppm -png -r 200   (or -r 300 for dense/small text) src page-prefix
tesseract <page-image> <out-base> --psm 1     (run per page, foreground, in batches)
```

`--psm 1` (automatic page segmentation with orientation detection) is a sound default for mixed-layout documents. Raise resolution before changing PSM if accuracy is poor. Keep page outputs separate so a bad page can be re-run without redoing the set.

## Tabular / status-report normalization

When ingesting structured exports (status reports, registers), expect:
- header rows that are not row 0 (specify the header offset)
- a known sheet name rather than the first sheet
- a type/category column needing normalization before grouping
- rows that must be dropped to avoid double-counting (e.g. a sub-status duplicate marker)

The specific sheet name, header offset, and drop rules for a recurring source belong in the project enrichment layer so the cleanup is reproducible.

## Provenance carries through

Values produced by the analysis skills arrive with provenance. Preserve it into the document — captions, footnotes, and source lists are where that provenance becomes the reader-facing evidentiary record.

## Project enrichment

The project layer supplies the exact format spec, recurring-file quirks (sheet names, header offsets, drop rules), and any installment-specific production steps. In *Project BOSC* the live read path is **vision-based**, not tesseract: `watermark.pipeline.extract` renders pages with pypdfium2 and reads figures from the image via a forced-tool-use `Estimate` extraction, treating the OCR text layer as a hint only (its digits are unreliable). Publishing is the Astro site (`web/`) and MkDocs `docs/`, not docx. The generic OCR / docx / tabular recipes above are fallbacks for sources the live pipeline does not cover. Bind to the live path; keep this file value-free. See `docs/investigative-method/ENRICHMENT.md`.
