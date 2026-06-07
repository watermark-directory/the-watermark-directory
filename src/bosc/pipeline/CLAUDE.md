# CLAUDE.md — `bosc.pipeline`

The ingest → extract → analyze stages plus the cross-document layers. Defers to the
root [`CLAUDE.md`](../../../CLAUDE.md).

- **Stages:** `ingest.py` (inventory `data/documents`, no parsing) → `extract.py`
  (hybrid vision read → Pydantic `Estimate`) → `analyze.py` (deterministic
  `reconcile` **and** the agentic `research_question`).
- **`extract.py` dispatches by document `kind`** (`opc` today) via `EXTRACTORS`, and
  within OPC by **`Profile`** (`bosc.profiles`). Keep it contractor-agnostic: section
  taxonomy and markup rate come from the data/profile — **don't add fixed section
  fields**. Add a contractor by registering a `Profile`, not by editing models here.
- **`analyze.reconcile_*` is format-agnostic** (line item → subtotal → total, markup
  convention from the profile). The legacy `reconcile`/`OPCSummary` path (25%
  convention) still covers the assembled summary artifact — leave it intact.
- `corpus.py`, `entities.py`, `timeline.py`, `hydrology.py` build the cross-document
  layers the site/agent read. They consume **committed `data/extracted/**` +
  `data/reference/**`** — never re-read raw documents or fabricate links.
- Figures come from the image, never the garbled OCR digits.
