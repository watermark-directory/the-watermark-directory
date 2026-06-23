/**
 * The guided walk — the narrative spine of the Project BOSC *story*, layered over the
 * reference library. Single source of truth for the chapter order, the wayfinding bar, the
 * story home (the on-ramp), and the table of contents. The story lives under the site at
 * `STORY_BASE` (`/network/<id>/stories/project-bosc`); chapters are flattened directly beneath.
 *
 * Six teaching chapters (steps 1–6), bookended by the story home (Ch. 0).
 * Ordering is cause → consequence so no figure depends on a number established in
 * a later chapter — Assembly (how the land + deal were put together and kept
 * quiet) follows Who and precedes Scale; Scale (air) precedes Water because the
 * cooling draw derives from the IT load. All chapter pages are live; `live` is
 * kept on each chapter as the build flag the wayfinding/index gate their go-links
 * on.
 */

import { withStory } from "./site";

export interface WalkChapter {
  /** 1-based position among the five teaching chapters. */
  step: number;
  /** Route slug, flattened directly under the story (`STORY_BASE/<slug>`). */
  slug: string;
  title: string;
  /** The record-reading skill the chapter teaches. */
  skill: string;
  /** The anchor record(s) it tears down. */
  anchor: string;
  /** Whether the chapter page exists (vs. still drafting). */
  live: boolean;
}

export const WALK_TOTAL = 6;

export const WALK_CHAPTERS: WalkChapter[] = [
  {
    step: 1,
    slug: "who",
    title: "Who is actually building this?",
    skill: "Reading a deed · cross-document entity resolution",
    anchor: "The deed chain + the Bistrozzi Delaware shell cluster",
    live: true,
  },
  {
    step: 2,
    slug: "assembly",
    title: "How it was assembled & hidden",
    skill: "Reading an options-to-assignment chain · the confidentiality-first sequence",
    anchor: "The Port Authority options → Bistrozzi assignment + the blank DTE-100 prices",
    live: true,
  },
  {
    step: 3,
    slug: "scale",
    title: "How big is it — and what won't they tell you?",
    skill: "Reading an air permit · recognizing a CBI redaction",
    anchor: "Ohio EPA Air Permit-to-Install P0138965",
    live: true,
  },
  {
    step: 4,
    slug: "water",
    title: "What it does to the water",
    skill: "Reading an NPDES permit · the 7Q10 low-flow screen",
    anchor: "NPDES dilution + the cooling-draw screen",
    live: true,
  },
  {
    step: 5,
    slug: "cost",
    title: "What it costs the public",
    skill: "Reading a cost estimate · reading a contract clause",
    anchor: "Tetra Tech OPC + the Roadwork Development Agreement",
    live: true,
  },
  {
    step: 6,
    slug: "opacity",
    title: "Why you had to dig for this",
    skill: "Reading statutory exemptions",
    anchor: "The withholding stack + the mandamus thread",
    live: true,
  },
];

/** The story home (the on-ramp / "where the walk begins"). */
export const WALK_START_HREF = withStory("");
/** The table of contents — all six chapters in order. */
export const WALK_INDEX_HREF = withStory("/contents");

export function walkHref(slug: string): string {
  return withStory(`/${slug}`);
}

export function chapterByStep(step: number): WalkChapter | undefined {
  return WALK_CHAPTERS.find((c) => c.step === step);
}

/**
 * The reciprocal of the teardowns' `recordRel`: which library records a chapter
 * tears down, keyed by the record's `rel`. Drives the "↩ seen in the walk"
 * backlink on the record block, so the deep links resolve both directions.
 */
export interface WalkAnchor {
  ch: string;
  slug: string;
  label: string;
}
export const WALK_ANCHORS: Record<string, WalkAnchor> = {
  "recorder/202508130008300.deed.yaml": { ch: "01", slug: "who", label: "Who is actually building this?" },
  "permits/sos-tilted-gate-llc-2025-09-29.sos.yaml": {
    ch: "01",
    slug: "who",
    label: "Who is actually building this?",
  },
  "permits/4132514.epa.yaml": {
    ch: "03",
    slug: "scale",
    label: "How big is it — and what won't they tell you?",
  },
  "oepa/oepa-2PH00006-american-ii-fact-sheet.npdes.yaml": {
    ch: "04",
    slug: "water",
    label: "What it does to the water",
  },
  "aedg/roundabouts.summary.opc.yaml": { ch: "05", slug: "cost", label: "What it costs the public" },
};

export function walkAnchorFor(rel: string): WalkAnchor | undefined {
  return WALK_ANCHORS[rel];
}
