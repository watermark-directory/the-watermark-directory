// GET /api/doc/<rel> — stream a source document from R2 (epic #274 / #278).
// The single byte path for both dev (wrangler local R2) and prod. The public publish gate
// (#280) is enforced HERE, server-side. Ships dark: DOCS_ENABLED must be "true". HTML docs
// are served nosniff + inline (the viewer only ever loads them in a sandboxed iframe).
// See docs/object-store.md.

import { loadPublishedDocs } from "../_lib/docAllowlist";
import { docContentType, enforcePublishGate, parseByteRange, resolveDocKey } from "../_lib/docServe";

// Minimal R2 surface (avoids a dep on @cloudflare/workers-types).
interface R2Object {
  size: number;
  httpEtag: string;
  httpMetadata?: { contentType?: string };
  customMetadata?: Record<string, string>;
}
interface R2ObjectBody extends R2Object {
  body: ReadableStream;
}
interface R2Bucket {
  head(key: string): Promise<R2Object | null>;
  get(key: string, options?: { range?: { offset: number; length?: number } }): Promise<R2ObjectBody | null>;
}

interface Env {
  DOCS?: R2Bucket;
  /** On/kill switch — anything but "true" disables the endpoint (ships dark). */
  DOCS_ENABLED?: string;
  /** Set by Cloudflare Pages; the production branch enforces the public gate. */
  CF_PAGES_BRANCH?: string;
  /** Operator override of the gate ("on" / "off"). */
  DOCS_PUBLIC_GATE?: string;
  /** Override the published-allowlist asset URL (e.g. a sharded/CDN copy). */
  DOCS_ALLOWLIST_URL?: string;
}

interface RequestContext {
  request: Request;
  env: Env;
  params: { path?: string | string[] };
}

const text = (status: number, body: string): Response =>
  new Response(body, { status, headers: { "content-type": "text/plain; charset=utf-8" } });

function baseHeaders(obj: R2Object): Headers {
  const h = new Headers();
  h.set("content-type", docContentType(obj.httpMetadata?.contentType, obj.customMetadata?.["media-type"]));
  h.set("content-disposition", "inline");
  h.set("accept-ranges", "bytes");
  h.set("cache-control", "public, max-age=31536000, immutable");
  h.set("x-content-type-options", "nosniff"); // HTML is only ever loaded in a sandboxed iframe
  if (obj.httpEtag) h.set("etag", obj.httpEtag);
  return h;
}

export const onRequest = async (ctx: RequestContext): Promise<Response> => {
  const { request, env, params } = ctx;

  if (request.method !== "GET" && request.method !== "HEAD") return text(405, "method not allowed");
  if (env.DOCS_ENABLED !== "true") return text(503, "document serving is not enabled");
  if (!env.DOCS) return text(500, "document store is not configured");

  const key = resolveDocKey(params.path);
  if (!key) return text(400, "bad document path");

  // Public gate: production serves only allowlisted rels; dev/preview serve everything.
  if (enforcePublishGate(env)) {
    let published: Set<string>;
    try {
      published = await loadPublishedDocs(request.url, env.DOCS_ALLOWLIST_URL);
    } catch {
      return text(503, "document gate unavailable"); // fail closed
    }
    if (!published.has(key)) return text(404, "not found");
  }

  if (request.method === "HEAD") {
    const obj = await env.DOCS.head(key);
    if (!obj) return text(404, "not found");
    const headers = baseHeaders(obj);
    headers.set("content-length", String(obj.size));
    return new Response(null, { status: 200, headers });
  }

  // Range support (PDF.js progressive loading): head for the full size, then a ranged get.
  const rangeHeader = request.headers.get("range");
  if (rangeHeader) {
    const meta = await env.DOCS.head(key);
    if (!meta) return text(404, "not found");
    const spec = parseByteRange(rangeHeader, meta.size);
    if (spec === "unsatisfiable") {
      return new Response(null, {
        status: 416,
        headers: { "content-range": `bytes */${meta.size}`, "accept-ranges": "bytes" },
      });
    }
    if (spec) {
      const obj = await env.DOCS.get(key, { range: { offset: spec.offset, length: spec.length } });
      if (!obj) return text(404, "not found");
      const headers = baseHeaders(obj);
      headers.set("content-range", `bytes ${spec.offset}-${spec.end}/${meta.size}`);
      headers.set("content-length", String(spec.length));
      return new Response(obj.body, { status: 206, headers });
    }
  }

  const obj = await env.DOCS.get(key);
  if (!obj) return text(404, "not found");
  const headers = baseHeaders(obj);
  headers.set("content-length", String(obj.size));
  return new Response(obj.body, { status: 200, headers });
};
