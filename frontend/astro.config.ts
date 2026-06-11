import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";
import rehypeDocLinks from "./src/lib/rehype-doc-links";

// Static build (the default). `site`/`base` come from the environment so the
// parity-gated Pages cutover can set them later without a code change.
//
// React powers the interactive deck.gl/MapLibre islands (Epic #55); they mount
// client:only over an SSR fallback, so the rest of the site stays zero-framework.
// MDX must come after React so .mdx still renders.
//
// The rehype plugin rewrites the migrated `docs/` narrative's in-repo links into
// the new IA (issue #69) without editing the source — see rehype-doc-links.ts.
const base = process.env.BASE_PATH || "";

export default defineConfig({
  site: process.env.SITE_URL || undefined,
  base: process.env.BASE_PATH || undefined,
  integrations: [react(), mdx()],
  markdown: {
    // Shiki's default theme is github-dark; the site chrome is light (and
    // `.prose pre` styles a light code block), so pin a light theme so fenced
    // code matches inline code and the rest of the page (#106).
    shikiConfig: { theme: "github-light" },
    rehypePlugins: [[rehypeDocLinks, { base }]],
  },
});
