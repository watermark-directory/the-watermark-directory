#!/usr/bin/env node
// Local mock origin for the interactive dev stack (`mise run //frontend:dev:stack`).
//
// Stands in for the two paid/destructive externals the Pages Functions call, so the submit
// and ask endpoints can be clicked through end-to-end with NO real GitHub issues filed and
// NO Anthropic spend. The Functions reach it via GITHUB_API_BASE / ANTHROPIC_API_BASE in
// frontend/.dev.vars (the base-URL seam in functions/api/_lib/{github,anthropic}.ts).
//
// Lives under scripts/ — NOT the deployed functions/ tree — so it never ships. Turnstile is
// deliberately NOT mocked: the dev stack uses Cloudflare's always-pass dummy keys, which the
// Worker verifies against the real siteverify endpoint (one outbound call; needs network).
//
// Plain Node http, zero dependencies.

import { createServer } from "node:http";

// 8799 by default — off wrangler pages dev's own 8788 so the two don't collide.
const PORT = Number(process.env.MOCK_PORT) || 8799;

// In-memory issue store so a *resubmission* dedupes: the submit route scans open issues for
// a hidden marker, and these mock issues carry the body it filed. Reset on restart.
const issues = [];
let nextIssue = 1000;

const MOCK_ANSWER =
  "This is a local mock answer — no model was called. The sources retrieved for your " +
  "question are cited here [1][2]. Edit frontend/scripts/dev-mocks.mjs to change this text.";

function sendJson(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, { "content-type": "application/json", "content-length": Buffer.byteLength(body) });
  res.end(body);
}

async function readBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  return Buffer.concat(chunks).toString("utf8");
}

// Emit the answer as an Anthropic-style SSE stream so the ask route's real streamMessage /
// drainSse / mapAnthropicEvent path runs, and the page renders tokens progressively.
function anthropicSse(res, text) {
  res.writeHead(200, { "content-type": "text/event-stream; charset=utf-8", "cache-control": "no-cache" });
  const send = (event, data) => res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  send("message_start", {
    type: "message_start",
    message: { usage: { input_tokens: 40, output_tokens: 0 } },
  });
  for (const word of text.match(/\S+\s*/g) ?? [text]) {
    send("content_block_delta", {
      type: "content_block_delta",
      index: 0,
      delta: { type: "text_delta", text: word },
    });
  }
  send("message_delta", { type: "message_delta", usage: { output_tokens: 32 } });
  send("message_stop", { type: "message_stop" });
  res.end();
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://localhost:${PORT}`);
  const { pathname } = url;
  const method = req.method ?? "GET";

  // --- Anthropic Messages API (/api/ask) ---
  if (pathname === "/v1/messages" && method === "POST") {
    await readBody(req); // drain; the canned answer ignores it
    if ((req.headers.accept ?? "").includes("text/event-stream")) return anthropicSse(res, MOCK_ANSWER);
    return sendJson(res, 200, {
      id: "msg_mock",
      type: "message",
      role: "assistant",
      content: [{ type: "text", text: MOCK_ANSWER }],
      usage: { input_tokens: 40, output_tokens: 32 },
      stop_reason: "end_turn",
    });
  }

  // --- GitHub App auth + issues (/api/submit) ---
  if (pathname.endsWith("/installation") && method === "GET") return sendJson(res, 200, { id: 42 });
  if (pathname.endsWith("/access_tokens") && method === "POST")
    return sendJson(res, 201, { token: "ghs_mock", expires_at: "2099-01-01T00:00:00Z" });
  if (pathname.endsWith("/issues") && method === "GET") return sendJson(res, 200, issues);
  if (pathname.endsWith("/issues") && method === "POST") {
    const body = JSON.parse((await readBody(req)) || "{}");
    const number = nextIssue++;
    const htmlUrl = `https://github.com/local-mock/bosc/issues/${number}`;
    issues.push({ number, html_url: htmlUrl, body: body.body ?? "", title: body.title ?? "" });
    console.log(`[dev-mocks] filed mock issue #${number}: ${body.title ?? "(untitled)"}`);
    return sendJson(res, 201, { number, html_url: htmlUrl });
  }

  sendJson(res, 404, { error: `dev-mocks: no route for ${method} ${pathname}` });
});

server.listen(PORT, () => {
  console.log(
    `[dev-mocks] GitHub + Anthropic mock on http://localhost:${PORT} (submit/ask hit this, no real spend)`,
  );
});
