// GET /api/auth/unsubscribe?token=<token>
// One-click unsubscribe handler (#939 E2). No login required — the signed token is the
// credential. On success: removes the category from the user's AUTH_PREFS and returns 200.
// On bad/expired token: returns 400.
//
// The UNSUB_SECRET must match the secret used by the Lambda to mint the token (E1 #938).
// AUTH_PREFS KV must be bound (same namespace as the notifications prefs).

import { json } from "../_lib/http";
import { verifyUnsubToken } from "../_lib/unsub";
import { getPrefs, putPrefs } from "../_lib/prefs";
import type { KVLike } from "../_lib/ratelimit";
import type { NotifCategory } from "../_lib/prefs";
import { VALID_CATEGORIES } from "../_lib/prefs";

interface Env {
  AUTH_PREFS?: KVLike;
  UNSUB_SECRET?: string;
}

interface RequestContext {
  request: Request;
  env: Env;
}

export const onRequestGet = async ({ request, env }: RequestContext): Promise<Response> => {
  if (!env.UNSUB_SECRET) return json(503, { error: "unsubscribe not configured" });
  if (!env.AUTH_PREFS) return json(503, { error: "prefs store not configured" });

  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (!token) return json(400, { error: "token is required" });

  const payload = await verifyUnsubToken(token, env.UNSUB_SECRET);
  if (!payload) return json(400, { error: "invalid or expired token" });

  const { sub, category } = payload;

  if (!VALID_CATEGORIES.includes(category as NotifCategory)) {
    return json(400, { error: "unknown category" });
  }

  const prefs = await getPrefs(env.AUTH_PREFS, sub);
  const before = prefs.notifications.categories;
  prefs.notifications.categories = before.filter((c) => c !== category);
  await putPrefs(env.AUTH_PREFS, sub, prefs);

  return json(200, { ok: true, removed: category, remaining: prefs.notifications.categories });
};
