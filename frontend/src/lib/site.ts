/** Site-wide constants and the base-path helper for internal links/assets. */

import { SITE_BASE, siteBase, STORY_BASE, storyBase } from "./routes";

export { SITE_BASE, STORY_BASE, siteBase, siteUrl, storyBase, storyUrl } from "./routes";

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
 * Prefix a path with a site's root (by registry slug) and the deploy base.
 * `siteHref("lima", "/site/")` → `/network/american-sugar-creek-allen-co/site/`;
 * `siteHref("fort-wayne")` → that site's home. The slug-parameterized peer of `withSite`,
 * for the multi-site routes that know which site they render (#724).
 */
export function siteHref(slug: string, path = ""): string {
  return withBase(`${siteBase(slug)}${path}`);
}

/**
 * Prefix a path with a story's root (by site slug + codename) and the deploy base.
 * `storyHref("lima", "project-bosc", "/water")` → that chapter. The slug-parameterized
 * peer of `withStory`.
 */
export function storyHref(slug: string, codename: string, path = ""): string {
  return withBase(`${storyBase(slug, codename)}${path}`);
}

/**
 * Prefix a path with the live (Lima) site root (`SITE_BASE`, was `/bosc`) and the deploy
 * base. `withSite("/site/")` → `/network/american-sugar-creek-allen-co/site/`. Pass "" for
 * the site home. The Lima-pinned convenience over `siteHref`; multi-site callers that know
 * their slug should use `siteHref(slug, …)` instead.
 */
export function withSite(path = ""): string {
  return withBase(`${SITE_BASE}${path}`);
}

/**
 * Prefix a path with the Lima story root (`STORY_BASE` = `stories/project-bosc`).
 * `withStory("")` → the story home; `withStory("/water")` → a flattened chapter. The
 * Lima-pinned convenience over `storyHref`.
 */
export function withStory(path = ""): string {
  return withBase(`${STORY_BASE}${path}`);
}
