# CLAUDE.md — `bosc.agent`

Wraps the Claude Agent SDK and the Anthropic Messages API. Defers to the root
[`CLAUDE.md`](../../../CLAUDE.md) for global rules.

- **Two distinct surfaces, don't conflate them:**
  - `client.py` — the open-ended **research agent** (Agent SDK). Use for free-form
    Q&A over already-extracted data.
  - `extractor.py` — a **single-shot, deterministic** structured extraction
    (Messages API + forced tool use + Pydantic validation). It is *not* the Agent
    SDK on purpose: that makes vision extraction predictable and unit-testable.
- `tools.py` — in-process tools exposed to the research agent via an SDK MCP server.
  Each tool is a **thin, deterministic adapter over the pipeline** (read real data,
  never fabricate) and must return the MCP shape
  `{"content": [{"type": "text", "text": ...}]}`.
  - **Read-side resolves per active site (#424).** The extraction-reading tools
    (`list_extractions`, `read_extraction`, `program_overview`, `reconcile_*`) resolve the
    **active site's own** corpus: the whole `data/extracted/` tree for the corpus home
    (`_CORPUS_HOME` = Lima), else that site's subtree (`data/extracted/<slug>/`) via
    `_site_extracted_root` — so a per-site run reads its own record, never another site's,
    and `_scoped(...)` labels whose corpus it is. The corpus + hydrology **reference** models
    (`entities`, `timeline`, the hydrology suite) are still the Lima reference build; off-home
    they return an honest `_reference_only(...)` notice rather than *silently* serving Lima's
    record. Resolving a non-home site's own entity/timeline/scenario equivalents is the
    remaining parity work — don't fabricate per-site reads before a site has the committed data.
- Models come from `get_settings()` (`BOSC_MODEL` for research, `BOSC_EXTRACT_MODEL`
  for bulk extraction) — never hardcode a model id here.
- Figures come from the rendered **image**, not the OCR text layer; the extractor
  passes OCR text only as a hint.
