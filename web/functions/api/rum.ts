// POST /api/rum — Browser RUM beacon (Epic #961).
//
// Receives Core Web Vitals and JS-error payloads from the browser's sendBeacon
// and forwards them to Honeycomb, keeping HONEYCOMB_API_KEY server-side.
//
// Always returns 204 — the client must not branch on the response. Kill switch,
// rate-limit blocks, validation failures, and upstream Honeycomb errors are all
// absorbed silently so the browser never retries on a non-2xx.

import { fetchWithTimeout } from "./_lib/http";
import { checkRateLimit, type KVLike, type RateLimitConfig } from "./_lib/ratelimit";

interface Env {
  /** Kill switch — anything but "true" → 204 no-op (not 503; client must not retry). */
  RUM_ENABLED?: string;
  /** Honeycomb write key (shared with backend OTel from #959; set as dashboard secret). */
  HONEYCOMB_API_KEY?: string;
  /** Honeycomb dataset (default "watermark-browser"). */
  RUM_HONEYCOMB_DATASET?: string;
  /** Optional KV for per-IP rate limiting (60 events / 60 s per IP). */
  RUM_RATE_LIMIT?: KVLike;
}

const DATASET_DEFAULT = "watermark-browser";
const HONEYCOMB_EVENTS = "https://api.honeycomb.io/1/events";
const MAX_BODY_BYTES = 64 * 1024;
const RATE_CFG: RateLimitConfig = { max: 60, windowSec: 60 };

const noContent = (): Response => new Response(null, { status: 204 });

interface Ctx {
  request: Request;
  env: Env;
}

export async function onRequestPost({ request, env }: Ctx): Promise<Response> {
  if (env.RUM_ENABLED !== "true") return noContent();

  // Per-IP rate limit — fail-open when KV absent or errored (same pattern as ask.ts)
  if (env.RUM_RATE_LIMIT) {
    const ip = request.headers.get("CF-Connecting-IP") ?? "unknown";
    const rl = await checkRateLimit(env.RUM_RATE_LIMIT, ip, Math.floor(Date.now() / 1000), RATE_CFG);
    if (!rl.allowed) return noContent(); // silently drop; client must not retry
  }

  const buf = await request.arrayBuffer();
  if (buf.byteLength === 0 || buf.byteLength > MAX_BODY_BYTES) return noContent();

  let payload: unknown;
  try {
    payload = JSON.parse(new TextDecoder().decode(buf));
  } catch {
    return noContent();
  }

  // Accept a single event object; ignore arrays and non-objects
  if (typeof payload !== "object" || payload === null || Array.isArray(payload)) return noContent();

  const apiKey = env.HONEYCOMB_API_KEY;
  if (!apiKey) return noContent();

  const dataset = env.RUM_HONEYCOMB_DATASET ?? DATASET_DEFAULT;

  try {
    await fetchWithTimeout(
      `${HONEYCOMB_EVENTS}/${encodeURIComponent(dataset)}`,
      {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-honeycomb-team": apiKey,
          "x-event-time": new Date().toISOString(),
        },
        body: JSON.stringify(payload),
      },
      5_000,
    );
  } catch {
    // Absorb — upstream failures are never surfaced to the client
  }

  return noContent();
}
