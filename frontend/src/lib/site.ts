/** Site-wide constants and the base-path helper for internal links/assets. */

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
