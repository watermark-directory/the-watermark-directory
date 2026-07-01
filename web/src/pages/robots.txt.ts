import type { APIRoute } from "astro";

// Emitted as a build-time endpoint (not a static public/ file) so the `Sitemap:`
// and `MCP:` lines track the deploy origin — `Astro.site` is only set in
// production builds (SITE_URL), so locally / in CI we serve a bare allow-all.
const AI_CRAWLERS = ["GPTBot", "ClaudeBot", "CCBot", "Google-Extended", "PerplexityBot", "Applebot-Extended"];

export const GET: APIRoute = ({ site }) => {
  const sitemap = site ? `\nSitemap: ${new URL("sitemap-index.xml", site).href}` : "";
  const mcp = site ? `\nMCP: ${new URL(".well-known/mcp.json", site).href}` : "";

  const defaultBlock = `User-agent: *\nAllow: /${sitemap}${mcp}`;
  const crawlerBlocks = AI_CRAWLERS.map((bot) => `User-agent: ${bot}\nAllow: /${sitemap}${mcp}`).join("\n\n");

  return new Response(`${defaultBlock}\n\n${crawlerBlocks}\n`, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
