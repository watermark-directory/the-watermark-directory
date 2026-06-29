import type { APIRoute } from "astro";

// Emitted as a build-time endpoint (not a static public/ file) so the `Sitemap:`
// line tracks the deploy origin — `Astro.site` is only set in production builds
// (SITE_URL), so locally / in CI we serve a bare allow-all with no stale URL.
export const GET: APIRoute = ({ site }) => {
  const lines = ["User-agent: *", "Allow: /"];
  if (site) lines.push("", `Sitemap: ${new URL("sitemap-index.xml", site).href}`);
  return new Response(`${lines.join("\n")}\n`, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
