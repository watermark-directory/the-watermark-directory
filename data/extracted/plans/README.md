# Engineering-plan extractions

Reviewed structured reads of the plan sheets under
[`data/documents/plans/`](../../documents/plans/README.md).

## Files

| File | What |
|---|---|
| `LMA1A-95-SPS-2025-10-28.plan.yaml` | Sheet-level metadata for the 95% SPS grading & storm plan (`.odg`) — sheet id, discipline, phase, engineer (EMH&T), label counts. |
| `lma1a.storm-inventory.yaml` | Parsed storm-structure inventory (rim labels, distinct structures) read from that drawing via `bosc.documents.odg`. |

Counts (e.g. `rim_labels` vs `rim_distinct`) come from the vector drawing's text
layer; verify against the source sheet before relying on them.
