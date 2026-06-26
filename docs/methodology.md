# Methodology — how we read the record

Project BOSC reconstructs a deliberately thin public record from primary
documents: degraded scans and OCR'd PDFs are read into reviewed, cited,
structured data, and the analysis is built only on what the documents support.
This section teaches the methods — each article paired with a runnable companion
so you can inspect the real data behind a claim.

The runnable companions are interactive pages that each read a committed,
read-only corpus artifact and recompute it in your browser — over the record,
never editing it.

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

The evidence discipline these articles formalize is summarized on every page.
Every claim, figure, and record carries one of four evidence tags — read them as
confidence signals, not decoration:

- **`[verified]`** — read from a cited record or a live source: confirmed and
  reproducible.
- **`[inference]`** — a labelled reading or derivation from cited inputs: reasoning
  over the assembled record, not a record itself.
- **`[reference]`** — an outside published specification or dataset: authoritative,
  but not a record about this site.
- **`[open]`** — withheld, unresolved, or not yet checked: a question, not a verdict.

The same four-tag legend appears on the records index, and each tag explains itself
on hover anywhere it is shown.
