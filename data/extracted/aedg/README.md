# AEDG cost-estimate extractions

Reviewed structured reads of the Tetra Tech roundabout **OPC** (Opinion of Probable
Cost) estimates. Source: [`data/documents/aedg/PRR-01-bundle.ocr.pdf`](../../documents/aedg/README.md)
(summary at 0-based PDF page 317, detail 318–327). This is the project's
**reference extraction** — the target the extract stage is built against.

## Files

| File | What |
|---|---|
| `roundabouts.summary.opc.yaml` | Section subtotals, markups (25% contingency), construction subtotal, and total per roundabout — the roll-up table. |
| `roundabouts.detail.opc.yaml` | Full per-section line items (item number, description, quantity, unit, unit rate, extended amount). |

## Conventions

- Figures are read off the 300 DPI render, **not** the garbled OCR text layer.
- Dollar totals/subtotals are high-confidence; uncertain quantities carry the `~`
  approximate marker (see [`data/README.md`](../../README.md)).
- Validated by `bosc.models`; `bosc reconcile` checks line-item → subtotal → total
  arithmetic and the contingency convention. Provenance is in each file's `meta`.
