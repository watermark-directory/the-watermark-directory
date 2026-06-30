// Daily output-token budget guard for /api/mcp (#912).
// Two tiers: shared public cap (key = `public:YYYY-MM-DD`) and per-key cap
// (key = `key:<sha256>:YYYY-MM-DD`). Same soft-dampener pattern as budget.ts
// (ask endpoint) — KV errors fail open so a counter outage never takes the endpoint down.

import type { KVLike } from "./ratelimit";

export const DEFAULT_PUBLIC_DAILY = 100_000;
export const DEFAULT_KEY_DAILY = 500_000;

/** Per-UTC-day key for the shared public tier (e.g. `public:2026-06-29`). */
export function publicBudgetKey(nowMs: number): string {
  return `public:${new Date(nowMs).toISOString().slice(0, 10)}`;
}

/** Per-UTC-day key for a keyed (cognito) tier (e.g. `key:<hash>:2026-06-29`). */
export function keyedBudgetKey(keyHash: string, nowMs: number): string {
  return `key:${keyHash}:${new Date(nowMs).toISOString().slice(0, 10)}`;
}

/** True when today's recorded spend has reached `limit`. Fails open (false) on KV error. */
export async function isOverBudget(kv: KVLike, key: string, limit: number): Promise<boolean> {
  try {
    const spent = Number((await kv.get(key)) ?? "0");
    return spent >= limit;
  } catch {
    return false;
  }
}

/** Add `tokens` to the spend counter for `key`. Best-effort; 48h TTL self-reaps the entry. */
export async function addBudgetUsage(kv: KVLike, key: string, tokens: number): Promise<void> {
  if (tokens <= 0) return;
  try {
    const spent = Number((await kv.get(key)) ?? "0");
    await kv.put(key, String(spent + tokens), { expirationTtl: 60 * 60 * 48 });
  } catch {
    // best-effort — a missed increment under-counts spend for the day
  }
}
