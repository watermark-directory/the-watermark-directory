// POST /api/ask — the public "Ask the corpus" endpoint (Epic #207).
//
// A Cloudflare Pages Function colocated with the static site, so the /ask page posts
// same-origin (mirrors api/submit.ts). Workers runtime, Web platform globals only, no
// Node/Python, no SDK deps — the Anthropic Messages API is called directly over fetch.
// See docs/ask-api.md for the contract and the grounding/refusal policy.
//
// Flow: kill switch → parse + length-cap → per-IP rate limit → daily budget guard →
// verify Turnstile → retrieve top-K from the build-time ask-index → if nothing relevant,
// refuse deterministically (no model call) → else assemble a grounding prompt and ask the
// model to answer ONLY from those sources, citing each claim → return the answer +
// structured citations, then record the spend.

import {
  type AskResult,
  assemblePrompt,
  candidateCitations,
  extractCitations,
  isRefusal,
  REFUSAL,
} from "./_lib/ask";
import { AnthropicError, type AnthropicUsage, createMessage } from "./_lib/anthropic";
import { streamMessage } from "./_lib/anthropicStream";
import { loadAskIndex } from "./_lib/askIndexLoad";
import { validateAsk } from "./_lib/askSchema";
import { addUsage, costDollars, DEFAULT_DAILY_TOKEN_BUDGET, isOverBudget } from "./_lib/budget";
import { intEnv } from "./_lib/env";
import { json, parseJsonBody, requireEnabled } from "./_lib/http";
import { enforceRateLimit, type KVLike } from "./_lib/ratelimit";
import { type PreparedIndex, prepare, search } from "./_lib/retrieval";
import { frame } from "./_lib/sse";
import { verifyTurnstile } from "./_lib/turnstile";

interface Env {
  /** On/kill switch — anything but "true" disables the endpoint (mirror submit). */
  ASK_ENABLED?: string;
  /** Anthropic key (Cloudflare secret). Absent ⇒ the endpoint is misconfigured. */
  ANTHROPIC_API_KEY?: string;
  /** Server-side Turnstile secret (Cloudflare secret). Absent ⇒ misconfigured. */
  TURNSTILE_SECRET_KEY?: string;
  /** Override the Messages API endpoint (local dev mock). Absent ⇒ api.anthropic.com. */
  ANTHROPIC_API_BASE?: string;
  /** Model id; defaults to the repo default. */
  ASK_MODEL?: string;
  /** Hard answer-length cap (cost guard); default 1024. */
  ASK_MAX_TOKENS?: string;
  /** Retrieval depth; default 6. */
  ASK_TOP_K?: string;
  /** Optional override for the ask-index asset URL (sharded/CDN index). */
  ASK_INDEX_URL?: string;
  /** Optional KV namespace for per-IP rate limiting. */
  ASK_RATE_LIMIT?: KVLike;
  /** Per-IP fixed-window limits (defaults below). */
  ASK_RATE_LIMIT_MAX?: string;
  ASK_RATE_LIMIT_WINDOW_SEC?: string;
  /** Optional KV namespace for the account-wide daily budget counter. Falls back to
   *  ASK_RATE_LIMIT, so the budget can be enforced independently of per-IP limiting (#587). */
  ASK_BUDGET?: KVLike;
  /** Account-wide daily total-token budget — input + output (default 200k). A configured "0" is a hard stop. */
  ASK_DAILY_TOKEN_BUDGET?: string;
  /** Escape hatch: with no budget KV bound the paid endpoint fails closed (#587) unless this
   *  is "true" (local dev / explicit operator opt-in to an uncapped endpoint). */
  ASK_ALLOW_UNCAPPED?: string;
}

// A paid endpoint deserves a tighter per-IP window than the tips form.
const DEFAULT_ASK_RATE_LIMIT = { max: 10, windowSec: 3600 };

interface RequestContext {
  request: Request;
  env: Env;
}

const sse = (stream: ReadableStream): Response =>
  new Response(stream, {
    headers: {
      "content-type": "text/event-stream; charset=utf-8",
      "cache-control": "no-cache, no-transform",
      "x-accel-buffering": "no",
    },
  });

const DEFAULT_MODEL = "claude-opus-4-8";
const DEFAULT_MAX_TOKENS = 1024;
const DEFAULT_TOP_K = 6;

// Prepared-index cache: keyed by units identity so it rebuilds only when the cached
// asset does (both live for the isolate's lifetime).
let preparedFor: unknown = null;
let prepared: PreparedIndex | null = null;
function getPrepared(units: Parameters<typeof prepare>[0]): PreparedIndex {
  if (prepared && preparedFor === units) return prepared;
  prepared = prepare(units);
  preparedFor = units;
  return prepared;
}

export const onRequestPost = async (ctx: RequestContext): Promise<Response> => {
  const { request, env } = ctx;

  const disabled = requireEnabled(env.ASK_ENABLED, () =>
    json(503, { error: "the ask endpoint is not enabled" }),
  );
  if (disabled) return disabled;
  if (!env.ANTHROPIC_API_KEY || !env.TURNSTILE_SECRET_KEY)
    return json(500, { error: "endpoint is misconfigured" });
  const apiKey = env.ANTHROPIC_API_KEY; // captured for the stream closure (narrowing is lost there)

  const body = await parseJsonBody(request);
  if (!body.ok) return body.response;

  const parsed = validateAsk(body.value);
  if (!parsed.ok) return json(400, { error: parsed.error });
  const { question, turnstile_token } = parsed.value;

  const remoteip = request.headers.get("CF-Connecting-IP") ?? undefined;
  const nowMs = Date.now();
  const budgetLimit = Math.max(0, intEnv(env.ASK_DAILY_TOKEN_BUDGET, DEFAULT_DAILY_TOKEN_BUDGET));
  // Budget counter KV — its own optional binding, falling back to the rate-limit namespace, so
  // the daily cap can be enforced without also enabling per-IP limiting (#587).
  const budgetKv = env.ASK_BUDGET ?? env.ASK_RATE_LIMIT;

  // A paid endpoint must be capped. With no KV to enforce the daily budget, fail closed rather
  // than allow unbounded model spend behind Turnstile alone — unless explicitly opted out (#587).
  if (!budgetKv && env.ASK_ALLOW_UNCAPPED !== "true") {
    console.error("ask: no budget KV bound and ASK_ALLOW_UNCAPPED!=true — refusing (fail-closed)");
    return json(503, { error: "the ask endpoint is temporarily unavailable" });
  }

  // Per-IP rate limit (independent of the budget) + account-wide budget guard. Both are soft +
  // fail-open on KV error (Turnstile is the primary gate). Checked before the model call.
  if (env.ASK_RATE_LIMIT && remoteip) {
    const blocked = await enforceRateLimit(
      env.ASK_RATE_LIMIT,
      remoteip,
      Math.floor(nowMs / 1000),
      {
        max: intEnv(env.ASK_RATE_LIMIT_MAX, DEFAULT_ASK_RATE_LIMIT.max),
        windowSec: Math.max(60, intEnv(env.ASK_RATE_LIMIT_WINDOW_SEC, DEFAULT_ASK_RATE_LIMIT.windowSec)),
      },
      "too many questions — please try again later",
    );
    if (blocked) return blocked;
  }
  if (budgetKv && (await isOverBudget(budgetKv, nowMs, budgetLimit)))
    return json(503, { error: "the ask endpoint has reached today's budget — please try again tomorrow" });

  // Verify the human-challenge token (single-use, then discarded).
  if (!turnstile_token) return json(403, { error: "verification required — please complete the challenge" });
  const human = await verifyTurnstile(turnstile_token, env.TURNSTILE_SECRET_KEY, remoteip);
  if (!human) return json(403, { error: "verification failed — please retry the challenge" });

  // Retrieve grounding context.
  let units: Awaited<ReturnType<typeof loadAskIndex>>;
  try {
    units = await loadAskIndex(request.url, env.ASK_INDEX_URL);
  } catch (e) {
    console.error("ask-index load failed:", e);
    return json(500, { error: "the corpus index is unavailable" });
  }
  const k = Math.max(1, intEnv(env.ASK_TOP_K, DEFAULT_TOP_K));
  const hits = search(getPrepared(units), question, k);

  const model = env.ASK_MODEL || DEFAULT_MODEL;
  const maxTokens = Math.max(256, intEnv(env.ASK_MAX_TOKENS, DEFAULT_MAX_TOKENS));
  const wantsStream = (request.headers.get("Accept") ?? "").includes("text/event-stream");

  // Record spend against the daily budget + emit structured telemetry for observability.
  let callT0 = 0;
  const record = async (usage?: AnthropicUsage): Promise<void> => {
    if (!usage) return;
    const latencyMs = callT0 > 0 ? Date.now() - callT0 : undefined;
    console.log(
      JSON.stringify({
        endpoint: "ask",
        model,
        input_tokens: usage.input_tokens,
        output_tokens: usage.output_tokens,
        cost_usd: costDollars(usage, model),
        ...(latencyMs != null && { latency_ms: latencyMs }),
        hits: hits.length,
      }),
    );
    if (budgetKv) await addUsage(budgetKv, nowMs, usage);
  };

  // Nothing relevant retrieved ⇒ refuse deterministically, before spending a model call.
  if (hits.length === 0) {
    if (wantsStream) {
      return sse(
        new ReadableStream({
          start(controller) {
            const enc = new TextEncoder();
            // Emit `meta` first on every stream so the client has one code path (#331).
            controller.enqueue(enc.encode(frame("meta", { searched: 0, candidates: [] })));
            controller.enqueue(enc.encode(frame("delta", { text: REFUSAL })));
            controller.enqueue(enc.encode(frame("done", { citations: [], refused: true, model })));
            controller.close();
          },
        }),
      );
    }
    return json(200, { answer: REFUSAL, citations: [], refused: true, model } satisfies AskResult);
  }

  const { system, user } = assemblePrompt(question, hits);
  const messages = [{ role: "user" as const, content: user }];

  // Streaming path (#214): relay Anthropic token deltas as SSE, reconcile citations at
  // end-of-stream. Abuse/cost guards above already ran; spend is recorded once usage lands.
  if (wantsStream) {
    const enc = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const send = (event: string, data: unknown): void =>
          controller.enqueue(enc.encode(frame(event, data)));
        // Pre-answer: tell the client how many records ground this answer and ship the
        // candidate citations so it can resolve `[n]` markers as tokens stream in (#331).
        send("meta", { searched: hits.length, candidates: candidateCitations(hits) });
        let full = "";
        let inTok: number | undefined;
        let outTok: number | undefined;
        try {
          callT0 = Date.now();
          for await (const chunk of streamMessage({
            apiKey,
            model,
            system,
            messages,
            maxTokens,
            apiUrl: env.ANTHROPIC_API_BASE,
          })) {
            if (chunk.text) {
              full += chunk.text;
              send("delta", { text: chunk.text });
            }
            if (chunk.inputTokens != null) inTok = chunk.inputTokens;
            if (chunk.outputTokens != null) outTok = chunk.outputTokens;
          }
        } catch (e) {
          console.error("ask stream failed:", e);
          send("error", { error: "could not generate an answer — please try again later" });
          controller.close();
          return;
        }
        const usage =
          inTok != null && outTok != null ? { input_tokens: inTok, output_tokens: outTok } : undefined;
        await record(usage);
        const refused = isRefusal(full);
        send("done", { citations: refused ? [] : extractCitations(full, hits), refused, model, usage });
        controller.close();
      },
    });
    return sse(stream);
  }

  // Non-streaming path — the JSON contract for tools / the eval / no-SSE clients.
  let text: string;
  let usage: AskResult["usage"];
  try {
    callT0 = Date.now();
    const res = await createMessage({
      apiKey,
      model,
      system,
      messages,
      maxTokens,
      apiUrl: env.ANTHROPIC_API_BASE,
    });
    text = res.text;
    usage = res.usage;
  } catch (e) {
    const status = e instanceof AnthropicError ? e.status : 0;
    console.error("ask model call failed:", status, e);
    return json(502, { error: "could not generate an answer — please try again later" });
  }
  await record(usage);
  const refused = isRefusal(text);
  return json(200, {
    answer: text,
    citations: refused ? [] : extractCitations(text, hits),
    refused,
    model,
    usage,
  } satisfies AskResult);
};
