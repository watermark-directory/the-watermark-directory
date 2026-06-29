// Pure, runtime-agnostic helpers for the /api/doc source-document Function (#278).
// Side-effect-free so they can be unit-tested from src/ (src/lib/docServe.test.ts),
// mirroring functions/api/_lib/askSchema.ts. No Cloudflare/Worker globals here.

/** An inclusive byte range resolved against a known object size. */
export interface RangeSpec {
  offset: number;
  length: number;
  end: number; // inclusive
}

/**
 * Resolve the `[[path]]` catch-all to a `data/documents` key, or null if it's empty or
 * attempts traversal. Cloudflare passes the catch-all as a string (possibly with slashes)
 * or a string[]; handle both, and reject `..` / NUL / leading slashes.
 */
export function resolveDocKey(path: string | string[] | undefined): string | null {
  const raw = Array.isArray(path) ? path.join("/") : (path ?? "");
  if (!raw) return null;
  let key: string;
  try {
    key = decodeURIComponent(raw);
  } catch {
    return null;
  }
  key = key.replace(/^\/+/, "");
  if (!key || key.includes("..") || key.includes("\0")) return null;
  return key;
}

/**
 * Parse an HTTP `Range` header against `size`. Returns null when absent or unparseable
 * (serve a full 200 — spec-allowed), the resolved single range when satisfiable, or
 * "unsatisfiable" for an out-of-bounds range (→ 416). Only a single `bytes=` range is
 * supported — enough for PDF.js progressive loading.
 */
export function parseByteRange(
  header: string | null | undefined,
  size: number,
): RangeSpec | null | "unsatisfiable" {
  if (!header) return null;
  const m = /^bytes=(\d*)-(\d*)$/.exec(header.trim());
  if (!m) return null;
  const [, s, e] = m;
  if (s === "" && e === "") return null;
  let start: number;
  let end: number;
  if (s === "") {
    const suffix = Number.parseInt(e, 10);
    if (suffix <= 0) return "unsatisfiable";
    start = Math.max(0, size - suffix);
    end = size - 1;
  } else {
    start = Number.parseInt(s, 10);
    end = e === "" ? size - 1 : Math.min(Number.parseInt(e, 10), size - 1);
  }
  if (start < 0 || start >= size || start > end) return "unsatisfiable";
  return { offset: start, length: end - start + 1, end };
}

/**
 * Content-Type for an object: its stored type, else the `media_type` metadata (set by the
 * sync tool, #279), else octet-stream.
 */
export function docContentType(httpContentType?: string | null, mediaTypeMeta?: string | null): string {
  return httpContentType || mediaTypeMeta || "application/octet-stream";
}

/**
 * Whether the public publish allowlist is enforced for this deploy. `wrangler pages dev`
 * and preview deployments serve the whole corpus (dev-full); only the production branch
 * enforces. `DOCS_PUBLIC_GATE` ("on" / "off") lets an operator override either way.
 */
export function enforcePublishGate(env: { CF_PAGES_BRANCH?: string; DOCS_PUBLIC_GATE?: string }): boolean {
  if (env.DOCS_PUBLIC_GATE === "on") return true;
  if (env.DOCS_PUBLIC_GATE === "off") return false;
  return env.CF_PAGES_BRANCH === "main";
}
