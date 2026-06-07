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
| `witness-submissions.digest.yaml` | Per-witness digest of the 16 written submissions (Google, QTS, ODNR, ODOD, Ohio EPA, OCC, PUCO, PJM, ELPC, Koger Kidd, DCC, et al.) + the cross-cutting BOSC findings (Google omits Lima; ratepayer-cost dispute; ODNR water blind spot; the ODOD DCTE second subsidy; route-to-POTW; ORC 9.66(D) repeal). |

## Caveats

Transcripts are **machine-derived from audio** and approximate — verify any quote
against the source `.wav` before relying on it. Witness-submission reads trace to the
PDFs under `documents/.../witnesses/`.
