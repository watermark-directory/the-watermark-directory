// GET /api/admin/audit?sub=<sub> — list recent role-change audit entries for a user.
// Returns up to 20 entries in reverse-chronological order.
//
// Requires `admin` or `site-admin` role.
// site-admin: may only query audit entries for users in their own site scope
//   (enforcement is best-effort — audit entries don't carry the target's adminSites,
//    so this endpoint accepts any sub for site-admins; the intent is reviewed tooling).
//
// Ships dark: AUTH_ENABLED kill switch must be "true".

import { requireAuth, type AuthEnv } from "../_lib/auth";
import { json } from "../_lib/http";
import { listAuditEntries, type KVListable } from "../_lib/audit";

interface Env extends AuthEnv {
  AUTH_ENABLED?: string;
  AUTH_PREFS?: KVListable;
}

interface RequestContext {
  request: Request;
  env: Env;
}

export const onRequestGet = async ({ request, env }: RequestContext): Promise<Response> => {
  if (env.AUTH_ENABLED !== "true") return json(503, { error: "auth not enabled" });

  const auth = await requireAuth(request, env);
  if (!auth.ok) return auth.response;

  if (auth.ctx.role === "standard") {
    return json(403, { error: "forbidden" });
  }

  if (!env.AUTH_PREFS) return json(503, { error: "prefs store not configured" });

  const url = new URL(request.url);
  const sub = url.searchParams.get("sub");
  if (!sub) return json(400, { error: "sub is required" });

  const entries = await listAuditEntries(env.AUTH_PREFS, sub);
  return json(200, entries);
};
