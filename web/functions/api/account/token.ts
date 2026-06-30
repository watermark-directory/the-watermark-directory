// POST /api/account/token — Exchanges a Cognito authorization code for tokens.
//
// Part of the PKCE auth flow (Epic #919 A4). The client POSTs { code, code_verifier }
// after Cognito's Hosted UI redirects back with ?code=…; this Function calls the
// Cognito token endpoint server-side, sets the refresh token in an HttpOnly Secure
// cookie (unavailable to JS), and returns { id_token, access_token } to the client.
//
// AUTH_ENABLED acts as a kill switch — absent or "false" → 503, same as the other
// platform endpoints. COGNITO_CLIENT_SECRET is optional; a public app client omits it.

import { json } from "../_lib/http";

interface Env {
  AUTH_ENABLED?: string;
  COGNITO_CLIENT_ID: string;
  COGNITO_CLIENT_SECRET?: string;
  COGNITO_DOMAIN: string;
  APP_BASE_URL: string;
}

interface TokenRequest {
  code: string;
  code_verifier: string;
}

interface CognitoTokenResponse {
  id_token: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

interface RequestContext {
  request: Request;
  env: Env;
}

export const onRequestPost = async ({ request, env }: RequestContext): Promise<Response> => {
  if (env.AUTH_ENABLED !== "true") return json(503, { error: "auth not enabled" });

  let body: TokenRequest;
  try {
    body = (await request.json()) as TokenRequest;
  } catch {
    return json(400, { error: "invalid JSON" });
  }

  const { code, code_verifier } = body;
  if (!code || !code_verifier) return json(400, { error: "missing code or code_verifier" });

  const redirectUri = `${env.APP_BASE_URL}/account/callback`;
  const tokenUrl = `https://${env.COGNITO_DOMAIN}/oauth2/token`;

  const params = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: env.COGNITO_CLIENT_ID,
    code,
    redirect_uri: redirectUri,
    code_verifier,
  });

  const reqHeaders: Record<string, string> = {
    "content-type": "application/x-www-form-urlencoded",
  };
  if (env.COGNITO_CLIENT_SECRET) {
    const creds = btoa(`${env.COGNITO_CLIENT_ID}:${env.COGNITO_CLIENT_SECRET}`);
    reqHeaders.authorization = `Basic ${creds}`;
  }

  let res: Response;
  try {
    res = await fetch(tokenUrl, { method: "POST", headers: reqHeaders, body: params.toString() });
  } catch {
    return json(502, { error: "token endpoint unreachable" });
  }

  if (!res.ok) {
    const text = await res.text();
    console.error("Cognito token exchange failed:", res.status, text);
    return json(502, { error: "token exchange failed" });
  }

  const tokens = (await res.json()) as CognitoTokenResponse;

  // Refresh token lives in an HttpOnly Secure cookie — JS cannot read it.
  // Scoped to /api/account so it's only sent to auth endpoints, not every request.
  const cookieAttrs = [
    `__rt=${tokens.refresh_token}`,
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    "Path=/api/account",
    "Max-Age=2592000", // 30 days
  ].join("; ");

  return new Response(JSON.stringify({ id_token: tokens.id_token, access_token: tokens.access_token }), {
    status: 200,
    headers: {
      "content-type": "application/json",
      "set-cookie": cookieAttrs,
    },
  });
};
