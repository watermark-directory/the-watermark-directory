// A global daily spend cap for /api/ask (#211). The ask endpoint calls a paid model, so
// beyond per-IP rate limiting we keep a coarse, account-wide guard: a per-day counter of
// total tokens (input + output) in KV. When the day's total reaches the budget, new questions
// are turned away (the route returns 503) until the next UTC day.
//
// Like the rate limiter this is a *soft* dampener layered behind Turnstile: KV is
// eventually consistent and the check is pre-call (so the request in flight when the
// budget tips over still completes). Any KV error fails **open** — a budget-counter
// outage must not take the endpoint down. Reuses the submit endpoint's KVLike shape.

import type { AnthropicUsage } from "./anthropic";
import type { KVLike } from "./ratelimit";

/** Default daily total-token budget — input + output combined (override with ASK_DAILY_TOKEN_BUDGET). */
export const DEFAULT_DAILY_TOKEN_BUDGET = 200_000;

/** Per-million-token pricing for models this platform calls. */
const PRICE_PER_MTOK: Record<string, { input: number; output: number }> = {
  "claude-opus-4-8": { input: 5.0, output: 25.0 },
  "claude-opus-4-7": { input: 5.0, output: 25.0 },
  "claude-sonnet-4-6": { input: 3.0, output: 15.0 },
  "claude-haiku-4-5": { input: 1.0, output: 5.0 },
};

/**
 * Estimated dollar cost for one Messages API call.
 * Returns `null` for unknown model IDs so callers can emit a `pricing_unknown` signal
 * rather than silently logging a misleading zero.
 */
export function costDollars(usage: AnthropicUsage, model: string): number | null {
  const p = PRICE_PER_MTOK[model];
  if (!p) return null;
  return (usage.input_tokens * p.input + usage.output_tokens * p.output) / 1_000_000;
}

/** Deterministic per-UTC-day key, e.g. `ask:budget:2026-06-17`. Pure — unit-tested. */
export function dayKey(nowMs: number, prefix = "ask:budget"): string {
  const day = new Date(nowMs).toISOString().slice(0, 10);
  return `${prefix}:${day}`;
}

/** True when today's recorded spend has reached `limit`. Fails open (false) on KV error. */
export async function isOverBudget(kv: KVLike, nowMs: number, limit: number): Promise<boolean> {
  try {
    const spent = Number((await kv.get(dayKey(nowMs))) ?? "0");
    return spent >= limit;
  } catch {
    return false; // fail open — Turnstile + rate limit remain the primary gates
  }
}

/**
 * Add this call's tokens (input + output) to today's spend counter. Best-effort; TTL self-reaps.
 *
 * Note: Workers KV has no atomic increment, so this is a read-modify-write and can undercount
 * when two requests complete concurrently. This is an accepted trade-off — the counter is an
 * explicitly soft cap (fail-open, eventually-consistent by design); Turnstile and per-IP rate
 * limiting are the primary gates.
 */
export async function addUsage(kv: KVLike, nowMs: number, usage: AnthropicUsage): Promise<void> {
  const tokens = usage.input_tokens + usage.output_tokens;
  if (tokens <= 0) return;
  try {
    const key = dayKey(nowMs);
    const spent = Number((await kv.get(key)) ?? "0");
    await kv.put(key, String(spent + tokens), { expirationTtl: 60 * 60 * 48 });
  } catch {
    // best-effort — a missed increment just under-counts spend for the day
  }
}
