// Two-tier auth middleware for POST /api/mcp (#916).
//
// Public tier:  no Authorization header → passthrough to rate-limit + shared budget.
// Cognito tier: Authorization: Bearer <token> → SHA-256 hash → MCP_KEYS KV lookup
//               → per-key budget + higher rate limits.
//
// The "Cognito" label is a stub seam — this KV key-lookup path will be replaced with
// real Cognito JWT verification once the Cognito auth work lands (#919/#921).
// Swapping verifyToken for JWT validation is a one-function change:
//   TODO(#916): replace KV lookup with verifyCognitoJwt(token, env) when #919 lands.
//
// On auth error: returns MCP JSON-RPC -32600 with data "auth" (spec-compliant, not HTTP 401).

import type { KVLike } from "./ratelimit";

export interface McpAuthEnv {
  MCP_KEYS?: KVLike;
}

interface KeyRecord {
  owner: string;
  tier: string;
  created_at: string;
  revoked: boolean;
}

export type AuthResult =
  | { tier: "public" }
  | { tier: "cognito"; keyHash: string; owner: string }
  | { error: "invalid_token" | "revoked" };

async function sha256Hex(token: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token));
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Verify the request's auth header and return a tiered auth result.
 * Missing header → public. Bearer token → hash → KV lookup.
 * If MCP_KEYS is not bound, all Bearer tokens fall through as public
 * (keys haven't been provisioned yet; no KV means no key management).
 */
export async function verifyToken(request: Request, env: McpAuthEnv): Promise<AuthResult> {
  const authHeader = request.headers.get("authorization");
  if (!authHeader) return { tier: "public" };

  const match = /^Bearer (.+)$/i.exec(authHeader);
  if (!match) return { error: "invalid_token" };

  const token = match[1];
  const keyHash = await sha256Hex(token);

  if (!env.MCP_KEYS) return { tier: "public" };

  try {
    const raw = await env.MCP_KEYS.get(`key:${keyHash}`);
    if (!raw) return { error: "invalid_token" };
    const rec = JSON.parse(raw) as KeyRecord;
    if (rec.revoked) return { error: "revoked" };
    return { tier: "cognito", keyHash, owner: rec.owner };
  } catch {
    return { error: "invalid_token" };
  }
}
