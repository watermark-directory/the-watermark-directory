// The single source of truth for the evidence-discipline tag taxonomy (#579).
//
// Two related types, both canonical:
//  - `TagKind`    — the *data* vocabulary the corpus actually carries on a figure/record/event
//    (`verified` read from a cited record, `inference` a labelled reading, `open` withheld/
//    unresolved). This is what the feeds/teardown/end-use/defense-nexus/leads modules tag with.
//  - `EvidenceKind` — the *render* taxonomy `EvidenceTag` knows how to tint: `TagKind` plus the
//    three annotation-only kinds (`filename` provenance, `gap` scope-gap, `key` key-figure) that
//    are added at the presentation layer, never stored as a data tag.
//
// The uncertainty engine uses `assumption` where this vocabulary uses `inference` (its inputs are
// cited *bounds*, not a single reading) — a deliberate dialect, kept distinct in `uncertainty.ts`.

/** The data vocabulary: what a corpus figure/record/event is actually tagged with. */
export type TagKind = "verified" | "inference" | "open";

/** The render taxonomy `EvidenceTag` tints — `TagKind` + the annotation-only kinds. */
export type EvidenceKind = TagKind | "filename" | "gap" | "key";

/** Kinds whose printed label differs from the kind name (design-system labels). */
export const EVIDENCE_LABELS: Partial<Record<EvidenceKind, string>> = {
  gap: "scope gap",
  key: "key figure",
};
