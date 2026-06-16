# Engineering-plan extractions

Reviewed structured reads of the plan sheets under
[`data/documents/plans/`](../../documents/plans/README.md).

## Files

| File | What |
|---|---|
| `LMA1A-95-SPS-2025-10-28.plan.yaml` | Sheet-level metadata for the 95% SPS grading & storm plan (`.odg`) — sheet id, discipline, phase, engineer (EMH&T), label counts. |
| `lma1a.storm-inventory.yaml` | Parsed storm-structure inventory (rim labels, distinct structures) read from that drawing via `bosc.documents.odg`. |
| `4091286.engineering.yaml` | SWP3 (NPDES construction-stormwater plan) for the **Beery Rd. & Cole St. roundabout / BOSC Storm Outfall** — operator George J. Igel & Co., engineer WSP USA; 5.71 ac disturbed (roundabout 5.6 + outfall 1.56), discharges to **Pike Run → Ottawa**. Discipline-agnostic `EngineeringRecord` (`kind=engineering`); CGP coverage number is in Appendix A, not the body text. |

Counts (e.g. `rim_labels` vs `rim_distinct`) come from the vector drawing's text
layer; verify against the source sheet before relying on them.
