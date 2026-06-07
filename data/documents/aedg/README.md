# AEDG engineering cost estimates (original records)

**Collection:** `aedg/` · immutable source evidence

The OCR'd PRR bundle behind the project's reference extraction. Raw bytes are never
edited; structured reads live in the mirrored
[`data/extracted/aedg/`](../../extracted/aedg/).

## Contents

| File | What |
|---|---|
| `PRR-01-bundle.ocr.pdf` | The public-records PRR bundle, OCR'd. Holds the six Tetra Tech **OPC** (Opinion of Probable Cost) roundabout estimates — summary at 0-based PDF page **317**, detail at **318–327** (printed sheets `pdf_page` 318–328). Git-LFS-tracked. |
| `PRR-01-bundle.ocr.pdf.index.yaml` | Page index / sheet map for the bundle. |

## Caveats

- The **OCR text layer is badly garbled** (e.g. `$109,307.69` → `$108.307.89`).
  Never trust its digits — figures are read off the 300 DPI render at extract time.
  See the root [`CLAUDE.md`](../../../CLAUDE.md) and [`README.md`](../../../README.md)
  for the hybrid extract flow.
