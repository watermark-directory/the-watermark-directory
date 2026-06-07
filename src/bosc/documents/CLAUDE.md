# CLAUDE.md — `bosc.documents`

Read-only source-document access. Defers to the root [`CLAUDE.md`](../../../CLAUDE.md).

- **Read-only.** Nothing here writes to `data/documents/**` (immutable evidence).
- `pdf.py` — two licence-clean backends: **pypdf** (BSD) for the OCR text layer
  (cheap structural hint; digits unreliable on degraded scans) and **pypdfium2**
  (PDFium) to render a page raster at a DPI for authoritative vision reading. Pages
  are **0-based**; printed `pdf_page == index + 1`.
- `odg.py` — OpenDocument Drawing (a zip of XML). Here the relationship inverts:
  **text leads, the preview thumbnail hints** (the scan hybrid is the opposite).
  Reads are deliberately CRC-tolerant — engineering exports can exceed 70 MB and
  ship a bad CRC on `content.xml`; salvage what decompresses rather than failing.
- New backends should stay permissively licensed (this is a proprietary project).
