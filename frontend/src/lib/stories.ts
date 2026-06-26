/**
 * Derive the per-site `Story` model (`./walk`) from the `stories` MDX content collection
 * (#724/#730). One MDX file per chapter under `src/content/stories/<site>/<codename>/<slug>.mdx`;
 * the frontmatter is the chapter spine, the body is the prose (rendered in #732).
 *
 * `buildStory` is a pure function (no `astro:content`), so it's unit-testable and the spine
 * derivation is verified against the canonical Lima story. `loadStories` is the build-time
 * wrapper that reads the collection (lazy `astro:content` import keeps this module importable
 * outside the Astro runtime, e.g. in vitest). The collection becomes the live source of
 * `STORIES` when Lima's prose is migrated and the source flips (#733).
 */
import { SITES } from "./sites";
import type { Chapter, Story, WalkAnchor } from "./walk";

/** A chapter's parsed frontmatter — the TS mirror of `STORY_CHAPTER_SCHEMA` (content.config.ts). */
export interface StoryChapterSpine {
  step: number;
  slug: string;
  title: string;
  skill: string;
  anchor: string;
  anchorRecordRels: string[];
  live: boolean;
  eyebrow?: string;
}

/** Story-level metadata not carried per chapter — supplied by the registry (`StoryRef`). */
export interface StoryMeta {
  title: string;
  dek: string;
}

/**
 * Assemble a `Story` from its chapter spines: order by step, map to `Chapter`s, and invert
 * each chapter's `anchorRecordRels` into the record→chapter backlink map (`ch` = zero-padded
 * step, `label` = chapter title) — exactly the shape the record block reads.
 */
export function buildStory(
  site: string,
  codename: string,
  meta: StoryMeta,
  spines: readonly StoryChapterSpine[],
): Story {
  const ordered = [...spines].sort((a, b) => a.step - b.step);
  const chapters: Chapter[] = ordered.map((c) => ({
    step: c.step,
    slug: c.slug,
    title: c.title,
    skill: c.skill,
    anchor: c.anchor,
    live: c.live,
  }));
  const anchors: Record<string, WalkAnchor> = {};
  for (const c of ordered) {
    for (const rel of c.anchorRecordRels) {
      anchors[rel] = { ch: String(c.step).padStart(2, "0"), slug: c.slug, label: c.title };
    }
  }
  return { site, codename, title: meta.title, dek: meta.dek, chapters, anchors };
}

/** The registry metadata for a (site, codename), or a codename-titled fallback. */
function storyMetaFor(site: string, codename: string): StoryMeta {
  const ref = SITES.find((s) => s.slug === site)?.stories?.find((r) => r.codename === codename);
  return { title: ref?.title ?? codename, dek: ref?.dek ?? "" };
}

/**
 * Read every story from the `stories` collection and group its chapters into `Story`s, keyed by
 * the `<site>/<codename>` prefix of each entry's id. Build-time only (Astro/MDX context).
 */
export async function loadStories(): Promise<Story[]> {
  const { getCollection } = await import("astro:content");
  const entries = await getCollection("stories");

  const groups = new Map<string, { site: string; codename: string; spines: StoryChapterSpine[] }>();
  for (const entry of entries) {
    const [site, codename] = String(entry.id).split("/");
    if (!site || !codename) continue;
    const key = `${site}/${codename}`;
    let group = groups.get(key);
    if (!group) {
      group = { site, codename, spines: [] };
      groups.set(key, group);
    }
    group.spines.push(entry.data as StoryChapterSpine);
  }

  return [...groups.values()].map((g) =>
    buildStory(g.site, g.codename, storyMetaFor(g.site, g.codename), g.spines),
  );
}
