// GET /api/admin/users?q=<email> — search users in the Cognito User Pool.
//
// Requires the caller to be `admin` or `site-admin` (else 403).
// - admin: returns all matching users with their current group memberships.
// - site-admin: returns only users whose custom:admin_sites overlaps the caller's sites.
//
// Response: [{ sub, email, groups, adminSites }]
//
// Ships dark: AUTH_ENABLED kill switch must be "true".
// Requires COGNITO_ADMIN_ACCESS_KEY_ID + COGNITO_ADMIN_SECRET_ACCESS_KEY in the dashboard.

import { requireAuth, type AuthEnv } from "../_lib/auth";
import { json } from "../_lib/http";
import { listUsers, listGroupsForUser, type CognitoAdminEnv } from "../_lib/cognitoAdmin";

interface Env extends AuthEnv, CognitoAdminEnv {
  AUTH_ENABLED?: string;
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

  const url = new URL(request.url);
  const q = url.searchParams.get("q") ?? "";

  let users = await listUsers(env, q);

  // Site admins can only see users in their own site scope.
  if (auth.ctx.role === "site-admin") {
    const callerSites = new Set(auth.ctx.adminSites);
    users = users.filter((u) => u.adminSites.some((s) => callerSites.has(s)));
  }

  // Enrich each user with their current group memberships. Swallowing failures
  // here would make an error look like "no groups", which could cause a save to
  // silently strip memberships, so propagate and return 502 on Cognito error.
  let enriched: Array<{ sub: string; email: string; adminSites: string[]; groups: string[] }>;
  try {
    enriched = await Promise.all(
      users.map(async (u) => {
        const groups = await listGroupsForUser(env, u.sub);
        return { ...u, groups };
      }),
    );
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return json(502, { error: `Cognito error: ${msg}` });
  }

  return json(200, enriched);
};
