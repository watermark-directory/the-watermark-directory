// Fetch the build-time ask-index (`/ask-index.json`, #209) as a static asset from the
// same origin and cache the parsed units in module scope. The asset is immutable per
// deploy, so caching across requests in the same Workers isolate is safe and saves a
// fetch + parse on every question. Mirrors how the search box fetches its index — the
// retrieval glue stays dependency-free.

import { fetchWithTimeout } from "./http";
import type { AskUnit } from "./retrieval";

let cached: AskUnit[] | null = null;

/** Test seam: drop the isolate cache. */
export function _resetAskIndexCache(): void {
  cached = null;
}

/**
 * Load the ask-index. `indexUrl` overrides the default same-origin asset URL (set via
 * the optional `ASK_INDEX_URL` var, e.g. for a sharded/CDN index). Throws if the asset
 * is missing or malformed — the route turns that into a 500 (misconfigured deploy).
 */
export async function loadAskIndex(requestUrl: string, indexUrl?: string): Promise<AskUnit[]> {
  if (cached) return cached;
  const url = indexUrl ?? new URL("/ask-index.json", requestUrl).toString();
  const res = await fetchWithTimeout(url);
  if (!res.ok) throw new Error(`ask-index fetch failed: ${res.status}`);
  const units = (await res.json()) as AskUnit[];
  if (!Array.isArray(units)) throw new Error("ask-index is not an array");
  cached = units;
  return units;
}
