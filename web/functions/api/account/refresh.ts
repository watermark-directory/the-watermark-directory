// POST /api/account/refresh — Issues a new ID token using the stored HttpOnly refresh cookie.
//
// The client calls this on page load when sessionStorage has no id_token (e.g. after a
// hard refresh or new tab). Returns { id_token, access_token } if the refresh token is
// valid; 401 if absent or Cognito rejects it.

import { parseCookie } from "../_lib/auth";
import { json } from "../_lib/http";

interface Env {
  AUTH_ENABLED?: string;
  COGNITO_CLIENT_ID: string;
  COGNITO_CLIENT_SECRET?: string;
  COGNITO_DOMAIN: string;
}

interface RequestContext {
  request: Request;
  env: Env;
}

export const onRequestPost = async ({ request, env }: RequestContext): Promise<Response> => {
  if (env.AUTH_ENABLED !== "true") return json(503, { error: "auth not enabled" });

  const refreshToken = parseCookie(request.headers.get("cookie"), "__rt");
  if (!refreshToken) return json(401, { error: "no refresh token" });

  const tokenUrl = `https://${env.COGNITO_DOMAIN}/oauth2/token`;
  const params = new URLSearchParams({
    grant_type: "refresh_token",
    client_id: env.COGNITO_CLIENT_ID,
    refresh_token: refreshToken,
  });

  const reqHeaders: Record<string, string> = {
    "content-type": "application/x-www-form-urlencoded",
  };
  if (env.COGNITO_CLIENT_SECRET) {
    const creds = btoa(`${env.COGNITO_CLIENT_ID}:${env.COGNITO_CLIENT_SECRET}`);
    reqHeaders["authorization"] = `Basic ${creds}`;
  }

  let res: Response;
  try {
    res = await fetch(tokenUrl, { method: "POST", headers: reqHeaders, body: params.toString() });
  } catch {
    return json(502, { error: "token endpoint unreachable" });
  }

  if (!res.ok) return json(401, { error: "refresh failed" });

  const tokens = (await res.json()) as { id_token: string; access_token: string };
  return json(200, { id_token: tokens.id_token, access_token: tokens.access_token });
};
