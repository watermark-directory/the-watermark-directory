// @ts-check
import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

// Static build (the default). `site`/`base` come from the environment so the
// parity-gated Pages cutover can set them later without a code change — until
// then they're unset and the build emits root-relative URLs.
//
// The content bundle this site reads is resolved at build time by
// `src/lib/bundle.ts` (see BOSC_BUNDLE_DIR there); it is not an Astro concern.
export default defineConfig({
  site: process.env.SITE_URL || undefined,
  base: process.env.BASE_PATH || undefined,
  integrations: [mdx()],
});
