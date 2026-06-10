// @ts-check
import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";

// Static build (the default). `site`/`base` come from the environment so the
// parity-gated Pages cutover can set them later without a code change — until
// then they're unset and the build emits root-relative URLs.
//
// The content bundle this site reads is resolved at build time by
// `src/lib/bundle.ts` (see BOSC_BUNDLE_DIR there); it is not an Astro concern.
export default defineConfig({
  site: process.env.SITE_URL || undefined,
  base: process.env.BASE_PATH || undefined,
  // React powers the interactive deck.gl/MapLibre islands (Epic #55). They mount
  // client-side only (client:only) over an SSR no-JS fallback; the rest of the
  // site stays zero-framework. MDX must come after React so .mdx still renders.
  integrations: [react(), mdx()],
});
