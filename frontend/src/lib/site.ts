/** Site-wide constants and the base-path helper for internal links/assets. */

import { SITE_BASE, STORY_BASE } from "./routes";

export { SITE_BASE, STORY_BASE } from "./routes";

export const SITE_NAME = "Watermark";
export const SITE_TAGLINE = "the public record, by watershed";
export const SITE_DESCRIPTION =
  "Watermark — a browsable, citable view of the public record, by watershed: primary " +
  "documents read from scans into structured data, the cross-document analysis, and the " +
  "Maumee-watershed hydrology.";

/**
 * Prefix an absolute in-site path with Astro's configured `base` so links work
 * whether the site is served from `/` or a subpath (the parity-gated Pages
 * cutover may set BASE_PATH). Pass a root-absolute path like `/bosc/site/`.
 */
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL || "/";
  const left = base.endsWith("/") ? base.slice(0, -1) : base;
  const right = path.startsWith("/") ? path : `/${path}`;
  return `${left}${right}` || "/";
}

/**
 * Prefix a path with the live site root (`SITE_BASE`, was `/bosc`) and the deploy base.
 * `withSite("/site/")` → `/network/american-sugar-creek-allen-co/site/`. Pass "" for the
 * site home. This (and `withStory`) is the one seam a future re-root touches.
 */
export function withSite(path = ""): string {
  return withBase(`${SITE_BASE}${path}`);
}

/**
 * Prefix a path with the story root (`STORY_BASE` = the site's `stories/project-bosc`).
 * `withStory("")` → the story home; `withStory("/water")` → a flattened chapter.
 */
export function withStory(path = ""): string {
  return withBase(`${STORY_BASE}${path}`);
}
