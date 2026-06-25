// Fetch the build-time publish allowlist (`/published-documents.json`, #280) as a static
// asset and cache the parsed set in module scope. The asset is immutable per deploy, so
// caching across requests in the same Workers isolate is safe. Mirrors askIndexLoad.ts.

import { fetchWithTimeout } from "./http";

let cached: Set<string> | null = null;

/** Test seam: drop the isolate cache. */
export function _resetPublishedCache(): void {
  cached = null;
}

/**
 * Load the set of `data/documents` rels cleared for public serving. `listUrl` overrides
 * the default same-origin asset URL (set via the optional `DOCS_ALLOWLIST_URL` var).
 * Throws if the asset is missing/malformed — the route turns that into a fail-closed 503.
 */
export async function loadPublishedDocs(requestUrl: string, listUrl?: string): Promise<Set<string>> {
  if (cached) return cached;
  const url = listUrl ?? new URL("/published-documents.json", requestUrl).toString();
  const res = await fetchWithTimeout(url);
  if (!res.ok) throw new Error(`published-documents fetch failed: ${res.status}`);
  const data = (await res.json()) as { rels?: string[] };
  if (!Array.isArray(data.rels)) throw new Error("published-documents is malformed");
  cached = new Set(data.rels);
  return cached;
}
