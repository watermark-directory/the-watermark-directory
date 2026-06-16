# Engineering plans / drawings (original records)

**Collection:** `plans/` · immutable source evidence

Engineering plan sets, drawings, and engineering reports for the BOSC-corridor
build-out. Raw bytes are never edited; structured reads live in the mirrored
[`data/extracted/plans/`](../../extracted/plans/).

## Layout

| Path | What |
|---|---|
| [`bistrozzi-plans/`](bistrozzi-plans/) | Bistrozzi plan sheets — e.g. `LMA1A-95-SPS-2025-10-28.odg` (an OpenDocument Drawing storm/site sheet, read via `bosc.documents.odg`). |
| `4091286.pdf` | Storm Water Pollution Prevention Plan (**SWP3**) for the **Beery Rd. & Cole St. roundabout / BOSC Storm Outfall** — operator George J. Igel & Co., engineer WSP USA; Ohio EPA eDocument ID kept as the as-received handle, read as `4091286.engineering.yaml` (`kind=engineering`). |

`.odg` is a vector drawing format; see [`data/extracted/plans/`](../../extracted/plans/)
for the parsed storm-inventory, plan, and engineering extractions.
