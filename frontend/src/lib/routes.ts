/**
 * The URL roots for the live reference site and its stories — the single source of truth.
 *
 * Plain string constants with NO Astro/runtime dependency, so `astro.config.ts` can import
 * them too (it feeds `SITE_BASE` to the base-aware `rehype-doc-links` plugin). The live site
 * was historically rooted at `/bosc`; it now lives under `/network/<id>` so future watershed
 * sites are clean siblings, and an investigation is a *story* beneath the site (so a site can
 * host several over time — the `/network/<id>/stories/<codename>` shape is the seam).
 *
 * The internal registry `slug` stays `"lima"` (facility maps, grouping, the Python `bosc.sites`
 * peer) — only the URL changed. Re-rooting again is a one-line change here.
 */

/** The live reference site's URL root (was `/bosc`). */
export const SITE_BASE = "/network/american-sugar-creek-allen-co";

/** The Project BOSC story under that site — `stories/<codename>`. */
export const STORY_BASE = `${SITE_BASE}/stories/project-bosc`;

/**
 * Build a Lima-site URL with NO deploy-base prefix — the Astro-free peer of `withSite()`
 * (`src/lib/site.ts`). Use this in `.ts` modules that must stay free of `import.meta.env`
 * (anything `astro.config.ts` / the rehype plugin can reach) or that emit *stored* canonical
 * paths (the search / ask index), where the deploy base is applied at render, not at storage.
 * `siteUrl("/site/")` → `/network/american-sugar-creek-allen-co/site/`.
 */
export function siteUrl(path = ""): string {
  return `${SITE_BASE}${path}`;
}

/** The story-root peer of `siteUrl()` — `storyUrl("/water")` → the flattened chapter path. */
export function storyUrl(path = ""): string {
  return `${STORY_BASE}${path}`;
}
