# 2026 select-committee hearing extractions

Reviewed reads of the 2026 select-committee hearing record. Sources (audio,
testimony PDFs, witness submissions) live under
[`data/documents/legal/select-committee-2026/`](../../../documents/legal/select-committee-2026/README.md).

## Layout

| Path | What |
|---|---|
| `select-committee-2026.hearing-index.yaml` | Top-level index of the hearing record. |
| `hearings-audio/` | Per-session `*.transcript.md` + `*.index.yaml` derived from the `.wav` recordings (2026-06-04 AM/PM/testimony). |
| `relator-testimony/` | The relator's written testimony, deck, and data appendix as markdown + an index YAML (2026-06-01). |

## Caveats

Transcripts are **machine-derived from audio** and approximate — verify any quote
against the source `.wav` before relying on it. Witness-submission reads trace to the
PDFs under `documents/.../witnesses/`.
