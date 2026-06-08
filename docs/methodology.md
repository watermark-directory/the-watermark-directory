# Methodology — how we read the record

Project BOSC reconstructs a deliberately thin public record from primary
documents: degraded scans and OCR'd PDFs are read into reviewed, cited,
structured data, and the analysis is built only on what the documents support.
This section teaches the methods — each article paired with a runnable notebook
so you can inspect the real data behind a claim.

The runnable companions live on the [interactive notebooks](../notebooks.md) page —
each reads a committed, read-only corpus artifact and recomputes in your browser
(marimo + WebAssembly, no backend).

**Live now:**

- **[Reading a degraded OPC scan into structured data](../notebooks.md)** — a
  reactive view of the six Tetra Tech cost sub-estimates behind the
  [roadwork numbers](../records/opc.md).

!!! note "More articles in progress"
    Planned next:

    - **Resolving entities without overclaiming** — how the
      [entity graph](../entities.md) stays corpus-verified, and what the
      `[verified]` / `[inference]` tags mean.
    - **The Tier-0 water balance** — the assimilative screen behind the
      [Hydrology](HYDROLOGY.md) findings.

The evidence discipline these articles formalize is summarized on every page:
claims are tagged `[verified]` (read from a cited extraction) or `[inference]`
(a labelled reading of the assembled record).
