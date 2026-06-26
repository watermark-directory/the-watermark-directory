/**
 * Active-site middleware (#724, Phase 0). Resolves the network site a request renders and
 * stashes its registry slug on `Astro.locals.site` — the seam the multi-site build routes on.
 *
 * Today there is exactly one rendered site (Lima), so this always sets `"lima"`. When the
 * library tree moves under the `[site]` dynamic route (#734), this resolves the slug from the
 * route param instead, and the rest of the chrome reads it from locals rather than assuming
 * Lima. Establishing the contract now keeps Phase 0 free of behavioral change while giving
 * later phases a populated `locals.site` to build on.
 */
import { LIMA_SLUG } from "./lib/routes";
import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware((context, next) => {
  context.locals.site = LIMA_SLUG;
  return next();
});
