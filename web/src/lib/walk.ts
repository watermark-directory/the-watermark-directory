/**
 * The story model — the per-site narrative spine (#724/#729), layered over a site's
 * reference library. A `Story` is one reading path (a codename) over a site's record: an
 * ordered list of teaching `Chapter`s plus the record→chapter backlink anchors. A site can
 * host several stories over time; today the only one is Lima's `project-bosc` (the original
 * guided walk).
 *
 * This module is the single source of truth for chapter order, the wayfinding bar, the story
 * home (the on-ramp), and the table of contents. A story lives under its site at
 * `/network/<id>/stories/<codename>`; chapters are flattened directly beneath. The
 * `storyFor(site, codename)` lookup + the per-story `chapterHref`/`storyChapterByStep`/…
 * helpers are the framework API; the `WALK_*`/`walk*` exports are the Lima-pinned
 * conveniences that keep today's callers (the story pages, nav, the record block) unchanged.
 *
 * Chapter ordering is cause → consequence so no figure depends on a number established in a
 * later chapter — Assembly (how the land + deal were put together and kept quiet) follows Who
 * and precedes Scale; Scale (air) precedes Water because the cooling draw derives from the IT
 * load. `live` is the build flag the wayfinding/index gate their go-links on.
 */

import { DEFAULT_STORY_CODENAME, LIMA_SLUG } from "./routes";
import { storyHref } from "./site";
import { buildAllStories } from "./stories";

export interface Chapter {
  /** 1-based position among the teaching chapters. */
  step: number;
  /** Route slug, flattened directly under the story (`storyBase/<slug>`). */
  slug: string;
  title: string;
  /** The record-reading skill the chapter teaches. */
  skill: string;
  /** The anchor record(s) it tears down. */
  anchor: string;
  /** Whether the chapter page exists (vs. still drafting). */
  live: boolean;
}

/** @deprecated Prefer {@link Chapter}; kept so existing type imports don't break. */
export type WalkChapter = Chapter;

/**
 * The reciprocal of the teardowns' `recordRel`: which chapter tears a library record down,
 * keyed by the record's `rel`. Drives the "↩ seen in the walk" backlink on the record block,
 * so the deep links resolve both directions.
 */
export interface WalkAnchor {
  ch: string;
  slug: string;
  label: string;
}

/** A site's story: a reading path (codename) over its record. */
export interface Story {
  /** Registry slug of the site this story belongs to (the `bosc.sites` / map key). */
  site: string;
  /** Story codename — the URL segment under the site's `stories/` and the store key. */
  codename: string;
  /** Display title, e.g. "Project BOSC". */
  title: string;
  /** One-line description (the on-ramp dek / nav blurb). */
  dek: string;
  /** The teaching chapters, in reading order. */
  chapters: Chapter[];
  /** record `rel` → the chapter that tears it down. */
  anchors: Record<string, WalkAnchor>;
}

/**
 * Every registered story across the network — built from the `stories` MDX collection (#733):
 * each chapter's frontmatter is its spine, grouped by `<site>/<codename>` and assembled by
 * `buildStory` (title/dek come from the site registry). The collection is now the single source
 * of truth; the hand-maintained Lima spine that used to live here is gone. Adding a chapter (or a
 * whole site's story) is an MDX edit, not a code edit.
 */
export const STORIES: readonly Story[] = buildAllStories();

/** The story for a (site, codename) pair, or `undefined` if none is registered. */
export function storyFor(site: string, codename: string): Story | undefined {
  return STORIES.find((s) => s.site === site && s.codename === codename);
}

/** The story home (on-ramp) href for a story. */
export function storyHomeHref(story: Story): string {
  return storyHref(story.site, story.codename, "");
}

/** The table-of-contents href for a story. */
export function storyContentsHref(story: Story): string {
  return storyHref(story.site, story.codename, "/contents");
}

/** A chapter href within a story (`storyBase/<slug>`). */
export function chapterHref(story: Story, slug: string): string {
  return storyHref(story.site, story.codename, `/${slug}`);
}

/** The chapter at a given step within a story. */
export function storyChapterByStep(story: Story, step: number): Chapter | undefined {
  return story.chapters.find((c) => c.step === step);
}

/** The record→chapter backlink for a `rel` within a story. */
export function storyAnchorFor(story: Story, rel: string): WalkAnchor | undefined {
  return story.anchors[rel];
}

// ── Lima-pinned conveniences ────────────────────────────────────────────────
// The original `WALK_*` / `walk*` API, now derived from the Lima `project-bosc` story (resolved
// from the collection) so every existing caller (the story pages, nav, the record block) is
// unchanged. Multi-site callers resolve a `Story` via `storyFor` and use the per-story helpers.

const LIMA_STORY: Story = (() => {
  const story = storyFor(LIMA_SLUG, DEFAULT_STORY_CODENAME);
  if (!story) {
    throw new Error(
      `The Lima "${DEFAULT_STORY_CODENAME}" story is missing from the stories collection — ` +
        "the WALK_* conveniences derive from it.",
    );
  }
  return story;
})();

export const WALK_CHAPTERS: Chapter[] = LIMA_STORY.chapters;
export const WALK_TOTAL = WALK_CHAPTERS.length;
export const WALK_ANCHORS: Record<string, WalkAnchor> = LIMA_STORY.anchors;

/** The story home (the on-ramp / "where the walk begins"). */
export const WALK_START_HREF = storyHomeHref(LIMA_STORY);
/** The table of contents — all chapters in order. */
export const WALK_INDEX_HREF = storyContentsHref(LIMA_STORY);

export function walkHref(slug: string): string {
  return chapterHref(LIMA_STORY, slug);
}

export function chapterByStep(step: number): Chapter | undefined {
  return storyChapterByStep(LIMA_STORY, step);
}

export function walkAnchorFor(rel: string): WalkAnchor | undefined {
  return storyAnchorFor(LIMA_STORY, rel);
}
