// Streaming variant of the Anthropic Messages client (#214) — Web globals only, no SDK.
// Calls the Messages API with `stream: true`, parses the upstream SSE, and yields plain
// text deltas + final usage so the route can relay them as our own SSE protocol. The
// event→delta mapping is a pure function (`mapAnthropicEvent`), unit-tested.
// https://docs.anthropic.com/en/api/messages-streaming

import { AnthropicError, type AnthropicUsage, type MessageRequest } from "./anthropic";
import { drainSse, type SseEvent } from "./sse";

const API_URL = "https://api.anthropic.com/v1/messages";
const API_VERSION = "2023-06-01";

/** A normalized chunk from the Anthropic stream. */
export interface StreamChunk {
  /** Incremental answer text (a `text_delta`). */
  text?: string;
  /** Token counts, accumulated across `message_start` + `message_delta`. */
  inputTokens?: number;
  outputTokens?: number;
}

/** Map one upstream SSE event to a normalized chunk (or null to ignore it). Pure. */
export function mapAnthropicEvent(ev: SseEvent): StreamChunk | null {
  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(ev.data) as Record<string, unknown>;
  } catch {
    return null;
  }
  switch (ev.event) {
    case "content_block_delta": {
      const delta = payload.delta as { type?: string; text?: string } | undefined;
      return delta?.type === "text_delta" && typeof delta.text === "string" ? { text: delta.text } : null;
    }
    case "message_start": {
      const usage = (payload.message as { usage?: AnthropicUsage } | undefined)?.usage;
      return usage ? { inputTokens: usage.input_tokens } : null;
    }
    case "message_delta": {
      const usage = payload.usage as { output_tokens?: number } | undefined;
      return usage?.output_tokens != null ? { outputTokens: usage.output_tokens } : null;
    }
    default:
      return null;
  }
}

/** Stream a grounded answer, yielding normalized chunks. Throws AnthropicError on a bad start. */
export async function* streamMessage(req: MessageRequest): AsyncGenerator<StreamChunk> {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": req.apiKey,
      "anthropic-version": API_VERSION,
      accept: "text/event-stream",
    },
    body: JSON.stringify({
      model: req.model,
      max_tokens: req.maxTokens,
      temperature: req.temperature ?? 0,
      system: req.system,
      messages: req.messages,
      stream: true,
    }),
  });
  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    throw new AnthropicError(detail || `Anthropic API error ${res.status}`, res.status);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const { events, rest } = drainSse(buffer);
    buffer = rest;
    for (const ev of events) {
      const chunk = mapAnthropicEvent(ev);
      if (chunk) yield chunk;
    }
  }
}
