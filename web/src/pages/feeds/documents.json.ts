import type { APIRoute } from "astro";
import { hasFeed, loadFeed } from "~/lib/bundle";

export const GET: APIRoute = () =>
  new Response(JSON.stringify(hasFeed("documents") ? loadFeed("documents") : []), {
    headers: { "content-type": "application/json; charset=utf-8" },
  });
