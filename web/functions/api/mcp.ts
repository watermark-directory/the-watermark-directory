// POST /api/mcp — MCP Streamable HTTP transport endpoint (#911).
//
// Implements the MCP Streamable HTTP transport (spec 2025-03-26):
// https://spec.modelcontextprotocol.io/specification/2025-03-26/basic/transports/#streamable-http
//
// JSON-RPC 2.0 dispatch over a single POST endpoint. Synchronous methods
// (initialize, tools/list, resources/list) return application/json directly;
// tools/call returns text/event-stream so implementations can stream results.
// Sessions are stored in MCP_SESSIONS KV (Mcp-Session-Id header round-trip).
//
// Flow: kill switch → parse body → rate limit → session lookup/create →
//       dispatch → return JSON or SSE response.

import { dispatch, RPC } from "./_lib/mcpDispatch";
import { json, parseJsonBody } from "./_lib/http";
import { enforceRateLimit, type KVLike } from "./_lib/ratelimit";
import { frame } from "./_lib/sse";
import { getSession, newSessionId, putSession } from "./_lib/mcpSession";

interface Env {
  /** Kill switch — anything but "true" disables the endpoint. */
  MCP_ENABLED?: string;
  /** KV namespace for session storage. */
  MCP_SESSIONS?: KVLike;
  /** Optional KV namespace for per-IP rate limiting. */
  MCP_RATE_LIMIT?: KVLike;
  MCP_RATE_LIMIT_MAX?: string;
  MCP_RATE_LIMIT_WINDOW_SEC?: string;
}

const DEFAULT_MCP_RATE_LIMIT = { max: 60, windowSec: 60 }; // 60 req/min per IP
const _IDLE_TIMEOUT_MS = 30_000;

function sseResponse(body: string, headers?: Record<string, string>): Response {
  return new Response(body, {
    headers: {
      "content-type": "text/event-stream; charset=utf-8",
      "cache-control": "no-cache, no-transform",
      "x-accel-buffering": "no",
      ...headers,
    },
  });
}

interface RequestContext {
  request: Request;
  env: Env;
}

export async function onRequestPost({ request, env }: RequestContext): Promise<Response> {
  // Kill switch
  if (env.MCP_ENABLED !== "true") {
    return json(503, {
      jsonrpc: "2.0",
      id: null,
      error: { code: RPC.INTERNAL_ERROR, message: "MCP endpoint is not enabled" },
    });
  }

  // Per-IP rate limit
  if (env.MCP_RATE_LIMIT) {
    const ip =
      request.headers.get("cf-connecting-ip") ??
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ??
      "unknown";
    const cfg = {
      max: Number(env.MCP_RATE_LIMIT_MAX ?? DEFAULT_MCP_RATE_LIMIT.max),
      windowSec: Number(env.MCP_RATE_LIMIT_WINDOW_SEC ?? DEFAULT_MCP_RATE_LIMIT.windowSec),
    };
    const denied = await enforceRateLimit(
      env.MCP_RATE_LIMIT,
      ip,
      Math.floor(Date.now() / 1000),
      cfg,
      "rate limit exceeded",
    );
    if (denied) return denied;
  }

  // Parse JSON body
  const parsed = await parseJsonBody(request);
  if (!parsed.ok) {
    return json(400, {
      jsonrpc: "2.0",
      id: null,
      error: { code: RPC.PARSE_ERROR, message: "invalid JSON" },
    });
  }

  // Session management
  const incomingSessionId = request.headers.get("mcp-session-id");
  let sessionId: string;
  const body = parsed.value as Record<string, unknown>;
  const isInitialize = body["method"] === "initialize";

  if (isInitialize) {
    // Always create a fresh session on initialize
    sessionId = newSessionId();
  } else if (incomingSessionId) {
    // Verify the session exists
    if (env.MCP_SESSIONS) {
      const session = await getSession(env.MCP_SESSIONS, incomingSessionId);
      if (!session) {
        return json(404, {
          jsonrpc: "2.0",
          id: body["id"] ?? null,
          error: { code: RPC.INVALID_REQUEST, message: "unknown or expired session" },
        });
      }
    }
    sessionId = incomingSessionId;
  } else {
    return json(400, {
      jsonrpc: "2.0",
      id: body["id"] ?? null,
      error: {
        code: RPC.INVALID_REQUEST,
        message: "Mcp-Session-Id header required (call initialize first)",
      },
    });
  }

  // Dispatch
  const rpcResponse = dispatch(parsed.value);

  // Persist the session after a successful initialize
  if (isInitialize && env.MCP_SESSIONS && !rpcResponse.error) {
    await putSession(env.MCP_SESSIONS, {
      id: sessionId,
      protocol: "2025-03-26",
      created: Date.now(),
    });
  }

  const sessionHeaders: Record<string, string> = { "mcp-session-id": sessionId };

  // notifications/initialized: 202 No Content (no body needed)
  if (body["method"] === "notifications/initialized") {
    return new Response(null, { status: 202, headers: sessionHeaders });
  }

  // tools/call: SSE stream so implementations can stream results (#913/#914)
  if (body["method"] === "tools/call") {
    const eventData = frame("message", rpcResponse);
    return sseResponse(eventData, sessionHeaders);
  }

  // All other methods: direct JSON
  return json(200, rpcResponse, sessionHeaders);
}
