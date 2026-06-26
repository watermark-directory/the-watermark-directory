/**
 * Active-site middleware (#724/#739). Resolves the network site a request renders from its
 * URL (`/network/<id>/…` → registry slug), stashes the slug on `Astro.locals.site`, AND runs the
 * page render inside `runWithSite` — so every build-time `loadFeed`/`hasFeed` the render performs
 * (transitively, through the ~12 feed libs) reads that site's bundle, with no slug threaded
 * through each call. Runs during static generation (Astro runs middleware for prerendered pages).
 *
 * A request outside `/network/<id>/` (the network-global pages: about, wiki, ask, search, the
 * `/network` hub) has no active site, so the render falls through to Lima (`activeSite`'s
 * default). `getStaticPaths` runs before middleware, so its enumeration is Lima-default too — a
 * second selectable site's per-site path enumeration is handled at onboarding (#235).
 */
import { runWithSite } from "./lib/bundle";
import { LIMA_SLUG, slugForSiteId } from "./lib/routes";
import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware((context, next) => {
  const match = context.url.pathname.match(/\/network\/([^/]+)(?:\/|$)/);
  const slug = match ? slugForSiteId(match[1]) : LIMA_SLUG;
  context.locals.site = slug;
  return runWithSite(slug, () => next());
});
