// JSON-RPC 2.0 router for the MCP Streamable HTTP transport (#911).
// Each method returns a result object or throws a McpError. Tool implementations
// live in sub-issues (#913-#915); this layer carries stubs so the protocol
// handshake and session round-trips work end-to-end today.
// Tool schemas are in src/lib/mcpTools.ts (shared with the /network/connect page, #917).

import { MCP_TOOLS } from "../../../src/lib/mcpTools";

export interface JsonRpcRequest {
  jsonrpc: string;
  id?: string | number | null;
  method: string;
  params?: unknown;
}

export interface JsonRpcResponse {
  jsonrpc: "2.0";
  id: string | number | null;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

export class McpError extends Error {
  constructor(
    readonly code: number,
    message: string,
    readonly data?: unknown,
  ) {
    super(message);
  }
}

// Standard JSON-RPC 2.0 error codes (MCP uses the same set)
export const RPC = {
  PARSE_ERROR: -32700,
  INVALID_REQUEST: -32600,
  METHOD_NOT_FOUND: -32601,
  INVALID_PARAMS: -32602,
  INTERNAL_ERROR: -32603,
} as const;

const PROTOCOL_VERSION = "2025-03-26";
const SERVER_INFO = { name: "watermark-directory", version: "1.0.0" };

// Tool stubs — filled by #913 (search_corpus) and #914 (bundle reader tools).
// Schema definitions live in src/lib/mcpTools.ts (shared with /network/connect, #917).

function parseRequest(body: unknown): JsonRpcRequest {
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    throw new McpError(RPC.INVALID_REQUEST, "Expected a JSON-RPC 2.0 request object");
  }
  const r = body as Record<string, unknown>;
  if (r.jsonrpc !== "2.0") {
    throw new McpError(RPC.INVALID_REQUEST, 'jsonrpc must be "2.0"');
  }
  if (typeof r.method !== "string") {
    throw new McpError(RPC.INVALID_REQUEST, "method must be a string");
  }
  return r as unknown as JsonRpcRequest;
}

function handleInitialize(params: unknown): unknown {
  const p = (params ?? {}) as Record<string, unknown>;
  // Client may send its preferred protocol version — honour an older request, clamp a newer one.
  const clientVersion = typeof p.protocolVersion === "string" ? p.protocolVersion : PROTOCOL_VERSION;
  const negotiated = clientVersion <= PROTOCOL_VERSION ? clientVersion : PROTOCOL_VERSION;
  return {
    protocolVersion: negotiated,
    capabilities: {
      tools: { listChanged: false },
      resources: { subscribe: false, listChanged: false },
    },
    serverInfo: SERVER_INFO,
  };
}

function handleToolsList(): unknown {
  return { tools: MCP_TOOLS };
}

function handleToolsCall(params: unknown): unknown {
  const p = (params ?? {}) as Record<string, unknown>;
  const name = p.name;
  if (typeof name !== "string") {
    throw new McpError(RPC.INVALID_PARAMS, "params.name must be a string");
  }
  const tool = MCP_TOOLS.find((t) => t.name === name);
  if (!tool) {
    throw new McpError(RPC.INVALID_PARAMS, `Unknown tool: ${name}`);
  }
  // Stub result — actual implementations land in #913 / #914
  return {
    content: [
      {
        type: "text",
        text: `Tool "${name}" is registered but its implementation is pending (#913/#914). Call /api/mcp with tools/list to see what's available.`,
      },
    ],
    isError: false,
  };
}

function handleResourcesList(): unknown {
  // Stub — filled by #915 (watermark://{site}/feeds/{name} resources)
  return { resources: [] };
}

export function dispatch(body: unknown): JsonRpcResponse {
  let req: JsonRpcRequest;
  try {
    req = parseRequest(body);
  } catch (e) {
    const err = e instanceof McpError ? e : new McpError(RPC.PARSE_ERROR, "Parse error");
    return { jsonrpc: "2.0", id: null, error: { code: err.code, message: err.message } };
  }

  const id = req.id ?? null;

  // Notifications (no id) get no response — caller should 202 directly
  if (req.id === undefined && req.method === "notifications/initialized") {
    return { jsonrpc: "2.0", id: null, result: null };
  }

  try {
    let result: unknown;
    switch (req.method) {
      case "initialize":
        result = handleInitialize(req.params);
        break;
      case "tools/list":
        result = handleToolsList();
        break;
      case "tools/call":
        result = handleToolsCall(req.params);
        break;
      case "resources/list":
        result = handleResourcesList();
        break;
      default:
        throw new McpError(RPC.METHOD_NOT_FOUND, `Method not found: ${req.method}`);
    }
    return { jsonrpc: "2.0", id, result };
  } catch (e) {
    const err = e instanceof McpError ? e : new McpError(RPC.INTERNAL_ERROR, "Internal error");
    return {
      jsonrpc: "2.0",
      id,
      error: { code: err.code, message: err.message, data: err.data },
    };
  }
}
