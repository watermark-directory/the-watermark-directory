// MCP session management for the Streamable HTTP transport (#911).
// Sessions are KV-backed with a 30-minute idle TTL. Each session carries the
// negotiated protocol version so the server can tailor responses per client.

import type { KVLike } from "./ratelimit";

export interface McpSession {
  id: string;
  protocol: string; // negotiated MCP protocol version, e.g. "2025-03-26"
  created: number; // unix ms
}

const SESSION_PREFIX = "mcp:session:";
const SESSION_TTL_S = 30 * 60; // 30 minutes — reset on each use

export function newSessionId(): string {
  return crypto.randomUUID();
}

export async function getSession(kv: KVLike, id: string): Promise<McpSession | null> {
  try {
    const raw = await kv.get(`${SESSION_PREFIX}${id}`);
    if (!raw) return null;
    return JSON.parse(raw) as McpSession;
  } catch {
    return null;
  }
}

export async function putSession(kv: KVLike, session: McpSession): Promise<void> {
  await kv.put(`${SESSION_PREFIX}${session.id}`, JSON.stringify(session), {
    expirationTtl: SESSION_TTL_S,
  });
}
