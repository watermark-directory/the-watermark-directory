// A global daily spend cap for /api/ask (#211). The ask endpoint calls a paid model, so
// beyond per-IP rate limiting we keep a coarse, account-wide guard: a per-day counter of
// output tokens in KV. When the day's total reaches the budget, new questions are turned
// away (the route returns 503) until the next UTC day.
//
// Like the rate limiter this is a *soft* dampener layered behind Turnstile: KV is
// eventually consistent and the check is pre-call (so the request in flight when the
// budget tips over still completes). Any KV error fails **open** — a budget-counter
// outage must not take the endpoint down. Reuses the submit endpoint's KVLike shape.

import type { KVLike } from "./ratelimit";

/** Default daily output-token budget (override with ASK_DAILY_TOKEN_BUDGET). */
export const DEFAULT_DAILY_TOKEN_BUDGET = 200_000;

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

/** Add `tokens` to today's spend. Best-effort; TTL outlives the day so it self-reaps. */
export async function addUsage(kv: KVLike, nowMs: number, tokens: number): Promise<void> {
  if (tokens <= 0) return;
  try {
    const key = dayKey(nowMs);
    const spent = Number((await kv.get(key)) ?? "0");
    await kv.put(key, String(spent + tokens), { expirationTtl: 60 * 60 * 48 });
  } catch {
    // best-effort — a missed increment just under-counts spend for the day
  }
}
