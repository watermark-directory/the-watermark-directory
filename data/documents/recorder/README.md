# Recorder filings — deeds & conveyances (original records)

**Collection:** `recorder/` · immutable source evidence

Allen County Recorder instruments (deeds, conveyances) for the BOSC-corridor
parcels. Raw bytes are never edited; structured reads live in the mirrored
[`data/extracted/recorder/`](../../extracted/recorder/) as `*.deed.yaml`.

## Layout

| Subfolder | What |
|---|---|
| [`bistrozzi-deeds/`](bistrozzi-deeds/) | Bistrozzi-entity deeds (5 instruments). |
| [`port-authority/`](port-authority/) | Port-authority conveyances (e.g. `…-amazon-deed.pdf`). |

Files are named by the Recorder's **instrument number** (e.g.
`202508130008300.pdf` = recording date + sequence). Keep the as-received names —
the instrument number is the authoritative handle.
