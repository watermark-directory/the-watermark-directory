# Maumee Watershed Nutrient TMDL (original records)

**Collection:** `maumee-tmdl/` · immutable source evidence

The Ohio EPA **Maumee Watershed Nutrient TMDL** (Total Maximum Daily Load) report,
its nine final appendices, fact sheet, and responsiveness summary, plus the US EPA
federal approval / decision package. The receiving-water / nutrient-loading
authority behind the hydrology axis's assimilative-capacity reasoning. Raw bytes
are never edited.

## Source & provenance

Retrieved 2026-06-06 via curl. Two source groupings (full per-file detail and
content-verified dates in [`MANIFEST.yaml`](MANIFEST.yaml)):

- **US EPA** (`epa.gov`) — the federal approval / decision package (transmittal
  letter, decision document, attachments).
- **Ohio EPA** (`epa.ohio.gov`) — the TMDL report, Appendices 1–9, fact sheet,
  FAQs, and the official-draft responsiveness summary.

## Caveats

- `content_verified_date` is drawn only from each document's own text layer; years
  appearing solely as bibliographic citations are **not** treated as the document's
  date. Every file was verified to begin with the `%PDF-` magic bytes.
- Appendix 4 (Individual NPDES Wasteload Allocations) overlaps the
  [ECHO NPDES inventory](../../reference/echo/README.md); cross-check rather than
  assume agreement.
