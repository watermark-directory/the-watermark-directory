// MCP Resources layer (#915): `resources/list` and `resources/read` handlers.
//
// Resources are exposed with the `watermark://{site}/feeds/{name}` URI scheme.
// The descriptor list is fetched from the `/mcp-resources.json` static endpoint
// (src/pages/mcp-resources.json.ts) which is built from the bundle manifest.
// Feed content is fetched from `/feeds/{name}.json` static endpoints.

import { fetchWithTimeout } from "./http";
import { McpError, RPC } from "./mcpDispatch";

interface McpResource {
  uri: string;
  name: string;
  description: string;
  mimeType: string;
}

/** Parse a `watermark://{site}/feeds/{name}` URI. Returns null if unrecognised. */
function parseWatermarkUri(uri: string): { site: string; feed: string } | null {
  const m = /^watermark:\/\/([^/]+)\/feeds\/([^/]+)$/.exec(uri);
  if (!m) return null;
  return { site: m[1], feed: m[2] };
}

export async function listResources(requestUrl: string): Promise<{ resources: McpResource[] }> {
  const url = new URL("/mcp-resources.json", requestUrl).toString();
  try {
    const res = await fetchWithTimeout(url);
    if (!res.ok) return { resources: [] };
    const resources = (await res.json()) as McpResource[];
    return { resources };
  } catch {
    return { resources: [] };
  }
}

export async function readResource(
  params: unknown,
  requestUrl: string,
): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
  const p = (params ?? {}) as Record<string, unknown>;
  const uri = typeof p.uri === "string" ? p.uri : null;
  if (!uri) {
    throw new McpError(RPC.INVALID_PARAMS, "params.uri must be a string");
  }

  const parsed = parseWatermarkUri(uri);
  if (!parsed) {
    throw new McpError(
      RPC.INVALID_PARAMS,
      `Unknown resource URI: ${uri}. Expected watermark://{site}/feeds/{name}`,
    );
  }

  // Hypotheses and hypothesis-assessments share a combined endpoint.
  const feedName = parsed.feed === "hypothesis-assessments" ? "hypotheses" : parsed.feed;

  const feedUrl = new URL(`/feeds/${feedName}.json`, requestUrl).toString();
  let res: Response;
  try {
    res = await fetchWithTimeout(feedUrl);
  } catch (e) {
    throw new McpError(RPC.INTERNAL_ERROR, `Failed to fetch feed: ${String(e)}`);
  }

  if (!res.ok) {
    throw new McpError(
      RPC.INVALID_PARAMS,
      `Resource not found: ${uri} (feed ${parsed.feed} returned ${res.status})`,
    );
  }

  const text = await res.text();

  // If the caller asked for hypothesis-assessments specifically, extract that sub-key.
  let content = text;
  if (parsed.feed === "hypothesis-assessments") {
    try {
      const payload = JSON.parse(text) as { assessments?: unknown };
      content = JSON.stringify(payload.assessments ?? []);
    } catch {
      // Return the raw response if parse fails.
    }
  }

  return {
    contents: [{ uri, mimeType: "application/json", text: content }],
  };
}
