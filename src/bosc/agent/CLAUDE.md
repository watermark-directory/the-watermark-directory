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
  - **Read-side is Lima-keyed (#424).** The corpus + hydrology tools serve the **Lima
    reference build**; a per-site run (`bosc --site <slug> research run`) gets Lima data.
    Site-sensitive tools return via `_scoped(...)`, which prepends an explicit
    active-site banner (empty for Lima) so a non-Lima run isn't *silently* fed Lima's
    record. Making the tools read the active site's **own** corpus/scenario is the
    parity-gated flip that seam prepares — don't fabricate per-site reads before a site
    has the committed data.
- Models come from `get_settings()` (`BOSC_MODEL` for research, `BOSC_EXTRACT_MODEL`
  for bulk extraction) — never hardcode a model id here.
- Figures come from the rendered **image**, not the OCR text layer; the extractor
  passes OCR text only as a hint.
