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

import { type AskResult, assemblePrompt, extractCitations, isRefusal, REFUSAL } from "./_lib/ask";
import { AnthropicError, type AnthropicUsage, createMessage } from "./_lib/anthropic";
import { streamMessage } from "./_lib/anthropicStream";
import { loadAskIndex } from "./_lib/askIndexLoad";
import { validateAsk } from "./_lib/askSchema";
import { addUsage, DEFAULT_DAILY_TOKEN_BUDGET, isOverBudget } from "./_lib/budget";
import { checkRateLimit, type KVLike } from "./_lib/ratelimit";
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
  /** Model id; defaults to the repo default. */
  ASK_MODEL?: string;
  /** Hard answer-length cap (cost guard); default 1024. */
  ASK_MAX_TOKENS?: string;
  /** Retrieval depth; default 6. */
  ASK_TOP_K?: string;
  /** Optional override for the ask-index asset URL (sharded/CDN index). */
  ASK_INDEX_URL?: string;
  /** Optional KV namespace for per-IP rate limiting + the daily budget counter. */
  ASK_RATE_LIMIT?: KVLike;
  /** Per-IP fixed-window limits (defaults below). */
  ASK_RATE_LIMIT_MAX?: string;
  ASK_RATE_LIMIT_WINDOW_SEC?: string;
  /** Account-wide daily output-token budget (default 200k). */
  ASK_DAILY_TOKEN_BUDGET?: string;
}

// A paid endpoint deserves a tighter per-IP window than the tips form.
const DEFAULT_ASK_RATE_LIMIT = { max: 10, windowSec: 3600 };

interface RequestContext {
  request: Request;
  env: Env;
}

const json = (status: number, data: unknown, headers?: Record<string, string>): Response =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json", ...headers },
  });

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

  if (env.ASK_ENABLED !== "true") return json(503, { error: "the ask endpoint is not enabled" });
  if (!env.ANTHROPIC_API_KEY || !env.TURNSTILE_SECRET_KEY)
    return json(500, { error: "endpoint is misconfigured" });
  const apiKey = env.ANTHROPIC_API_KEY; // captured for the stream closure (narrowing is lost there)

  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    return json(400, { error: "invalid JSON" });
  }

  const parsed = validateAsk(raw);
  if (!parsed.ok) return json(400, { error: parsed.error });
  const { question, turnstile_token } = parsed.value;

  const remoteip = request.headers.get("CF-Connecting-IP") ?? undefined;
  const nowMs = Date.now();
  const budgetLimit = Math.max(0, Number(env.ASK_DAILY_TOKEN_BUDGET) || DEFAULT_DAILY_TOKEN_BUDGET);

  // Per-IP rate limit + account-wide budget guard, when a KV namespace is bound. Both
  // are soft + fail-open (Turnstile is the primary gate). Checked before the model call.
  if (env.ASK_RATE_LIMIT) {
    if (remoteip) {
      const cfg = {
        max: Number(env.ASK_RATE_LIMIT_MAX) || DEFAULT_ASK_RATE_LIMIT.max,
        windowSec: Math.max(60, Number(env.ASK_RATE_LIMIT_WINDOW_SEC) || DEFAULT_ASK_RATE_LIMIT.windowSec),
      };
      const rl = await checkRateLimit(env.ASK_RATE_LIMIT, remoteip, Math.floor(nowMs / 1000), cfg);
      if (!rl.allowed)
        return json(
          429,
          { error: "too many questions — please try again later" },
          { "Retry-After": String(rl.retryAfter) },
        );
    }
    if (await isOverBudget(env.ASK_RATE_LIMIT, nowMs, budgetLimit))
      return json(503, { error: "the ask endpoint has reached today's budget — please try again tomorrow" });
  }

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
  const k = Math.max(1, Number(env.ASK_TOP_K) || DEFAULT_TOP_K);
  const hits = search(getPrepared(units), question, k);

  const model = env.ASK_MODEL || DEFAULT_MODEL;
  const maxTokens = Math.max(256, Number(env.ASK_MAX_TOKENS) || DEFAULT_MAX_TOKENS);
  const wantsStream = (request.headers.get("Accept") ?? "").includes("text/event-stream");

  // Record spend against the daily budget + log usage/cost for observability.
  const record = async (usage?: AnthropicUsage): Promise<void> => {
    if (!usage) return;
    console.log(
      `ask: model=${model} in=${usage.input_tokens} out=${usage.output_tokens} hits=${hits.length}`,
    );
    if (env.ASK_RATE_LIMIT) await addUsage(env.ASK_RATE_LIMIT, nowMs, usage.output_tokens);
  };

  // Nothing relevant retrieved ⇒ refuse deterministically, before spending a model call.
  if (hits.length === 0) {
    if (wantsStream) {
      return sse(
        new ReadableStream({
          start(controller) {
            const enc = new TextEncoder();
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
        let full = "";
        let inTok: number | undefined;
        let outTok: number | undefined;
        try {
          for await (const chunk of streamMessage({ apiKey, model, system, messages, maxTokens })) {
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
    const res = await createMessage({ apiKey, model, system, messages, maxTokens });
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
