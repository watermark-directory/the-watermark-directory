/**
 * Entity-link resolution. A profile (place, person, entity) can reference a
 * related entity that has no generated `/wiki/entities/<slug>/` page — e.g. a
 * relationship target that isn't itself in the `entities` feed, or any entity
 * absent from a trimmed bundle (the CI sample bundle). Linking to it
 * unconditionally emits a 404. `entityHref` returns a href only when the page
 * will exist, so callers fall back to plain text instead. The present set
 * mirrors the `getStaticPaths` of `wiki/entities/[key].astro`.
 */
import { hasFeed, loadFeed } from "./bundle";
import { slugify, type EntityNode } from "./feeds";
import { withBase } from "./site";

const present: Set<string> = new Set(
  (hasFeed("entities") ? loadFeed<EntityNode[]>("entities") : []).map((e) => slugify(e.key)),
);

/** Href to an entity's page, or `undefined` if no page is generated for it. */
export function entityHref(key: string): string | undefined {
  const slug = slugify(key);
  return present.has(slug) ? `${withBase("/wiki/entities/")}${slug}/` : undefined;
}
