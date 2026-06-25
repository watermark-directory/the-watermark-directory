// Shared response envelopes + request guards for the Pages Functions (#583). Each handler
// used to re-declare its own json()/text(), kill-switch, and JSON-body parse; they live
// here now. HTTP header names are case-insensitive (the Headers object lowercases them), so
// the prior `Content-Type` vs `content-type` split was cosmetic — unified to lowercase.

/** JSON response envelope. */
export function json(status: number, data: unknown, headers?: Record<string, string>): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json", ...headers },
  });
}

/** Plain-text response envelope. */
export function text(status: number, body: string, headers?: Record<string, string>): Response {
  return new Response(body, {
    status,
    headers: { "content-type": "text/plain; charset=utf-8", ...headers },
  });
}

/** Kill-switch guard: returns a 503 (built by `deny`) when `flag` isn't exactly "true",
 *  else null so the caller proceeds. */
export function requireEnabled(flag: string | undefined, deny: () => Response): Response | null {
  return flag === "true" ? null : deny();
}

/** Parse a JSON request body; on malformed input, carry a ready 400 envelope to return. */
export async function parseJsonBody(
  request: Request,
): Promise<{ ok: true; value: unknown } | { ok: false; response: Response }> {
  try {
    return { ok: true, value: await request.json() };
  } catch {
    return { ok: false, response: json(400, { error: "invalid JSON" }) };
  }
}
