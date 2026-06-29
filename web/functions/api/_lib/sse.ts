// Tiny, dependency-free Server-Sent Events helpers (#214). Used both to relay the
// Anthropic stream and to parse it — and the /ask page imports `drainSse` to consume our
// own stream, so build- and runtime-side parsing can't drift. Pure string ops, so it
// runs on the Workers runtime and in the browser, and is unit-testable.

export interface SseEvent {
  /** The `event:` name (defaults to "message" when omitted, per the SSE spec). */
  event: string;
  /** The joined `data:` payload. */
  data: string;
}

/** Encode one SSE frame: `event: <name>\ndata: <json>\n\n`. */
export function frame(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
}

/**
 * Pull every complete event (terminated by a blank line) out of an accumulating buffer,
 * returning the parsed events plus the unconsumed tail to carry into the next chunk.
 * Tolerates CRLF. A frame with no `data:` line is skipped (e.g. bare `ping`/comments).
 */
export function drainSse(buffer: string): { events: SseEvent[]; rest: string } {
  let buf = buffer.replace(/\r\n/g, "\n");
  const events: SseEvent[] = [];
  let idx = buf.indexOf("\n\n");
  while (idx >= 0) {
    const block = buf.slice(0, idx);
    buf = buf.slice(idx + 2);
    let event = "message";
    const dataLines: string[] = [];
    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) event = line.slice(6).trim();
      else if (line.startsWith("data:")) dataLines.push(line.slice(5).replace(/^ /, ""));
    }
    if (dataLines.length > 0) events.push({ event, data: dataLines.join("\n") });
    idx = buf.indexOf("\n\n");
  }
  return { events, rest: buf };
}
