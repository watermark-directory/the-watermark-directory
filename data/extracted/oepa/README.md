# Ohio EPA NPDES permit extractions

Reviewed structured reads (`*.npdes.yaml`) of the Ohio EPA NPDES permit documents
under [`data/documents/oepa/`](../../documents/oepa/README.md). One file per source
PDF, mirroring the source filename.

## Coverage

Three document types — issued **permit**, **fact sheet**, and draft public notice
(`draft-pn`) — across permits `2PH00006` (American II), `2PH00007` (American/Bath),
and `2PK00002` (Shawnee II).

## Conventions

Figures (design flow, limits, dates) come from the document image/text, never
inferred. Each file's `meta` block records the source PDF, pages read, and a
confidence note. `null` means the document stated no value — not an estimate.
