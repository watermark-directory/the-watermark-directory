---
name: entity-and-document-deconstruction
description: Use when extracting structured facts from primary-source documents, building or auditing an entity graph, constructing timelines, identifying shell-company structures, tracing land assembly or acquisition models, or auditing the investigative record for gaps. Trigger on document extraction, entity resolution, shell-company analysis, timeline construction, "who is behind X", acquisition-model identification, or gap audits of the evidence base. Methodology only; actual entities live in the project enrichment layer.
---

# Entity & Document Deconstruction

Methodology for turning a pile of primary sources into a structured, queryable, auditable record.

## Extraction discipline

- Extract facts with provenance attached: each fact carries the source document, location within it, and date. A fact without provenance is a lead, not a fact.
- Preserve redactions as data. A redacted specification is itself a finding — record *that* it was redacted, *where*, and on *what asserted basis* (e.g. "redacted as proprietary").
- Capture the professional network around an instrument (counsel, consultants, registered agents) when it appears in the record. Who prepared a filing is often more telling than the filing.

## Entity graph

- Nodes are entities (people, companies, agencies, parcels, instruments). Edges are **documented** relationships only — a filing naming both, a recorded conveyance, a dated communication.
- Do not encode an inferred relationship as an edge. If two nodes are only plausibly related, that belongs in a notes/hypothesis layer, not the graph.
- When the real principal behind a shell is later confirmed, update the graph explicitly rather than leaving the confirmed attribution buried in prose. An out-of-date graph is a gap.

## Shell-company and acquisition-model analysis

- Distinguish **end-user shells** (the eventual occupant hides behind a single-purpose entity) from **developer shells** (a developer assembles and later places). The shell pattern is the primary operational signal for which acquisition model is in play.
- Trace land assembly through recorded conveyances and registered-agent / counsel overlap. Common counsel or agent across shells is documentable; intent is not.
- Watch for expansion vehicles (a second entity registered through the same counsel) as a signal of scope beyond the disclosed footprint.

## Timeline construction

Build a single dated timeline across all threads. Dates are documentable; sequence often carries the argument. Flag where the timeline shows that decisions were made before the public had visibility — that gap is frequently the story.

## Gap audits

Periodically audit the record for material gaps. A gap audit names, for each gap: what is missing, why it matters to the thesis, and the specific artifact that would close it. Treat retired hypotheses explicitly — when a hypothesis is refuted, record that it was refuted and on what data points, so it is not silently resurrected.

## Project enrichment

The project layer supplies the actual entities, the graph schema, the extractor pipeline, and the current gap audit. In *Project BOSC* the graph and timeline are built by `bosc.pipeline.entities` (`EntityGraph`) and `bosc.pipeline.timeline` over the reviewed `data/extracted/**` corpus; the standing gap audit is `data/extracted/legal/corpus-completeness-audit.md` plus per-body `completeness-audit.yaml` files. Bind to those; keep this file entity-free. See `docs/investigative-method/ENRICHMENT.md`.
