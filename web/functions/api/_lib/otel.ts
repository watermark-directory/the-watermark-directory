// Minimal OTLP/JSON edge tracer for the Cloudflare Workers runtime (Epic #958).
//
// Ships dark: initTracer() returns null when HONEYCOMB_API_KEY is absent.
// No Node.js APIs — uses only Web Crypto + fetch, which Workers always provide.
// Uses SimpleSpanProcessor semantics (no batching) since Workers have request-scoped
// lifetimes; spans are flushed via ctx.waitUntil after the response is sent.

const HONEYCOMB_OTLP = "https://api.honeycomb.io/v1/traces";

// ─── Public span API ────────────────────────────────────────────────────────

export type SpanAttrValue = string | number | boolean;

export interface Span {
  setAttribute(key: string, value: SpanAttrValue): void;
  setStatus(code: "ok" | "error"): void;
  end(): void;
}

// ─── Internal span storage ──────────────────────────────────────────────────

interface SpanData {
  name: string;
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  startNs: bigint;
  endNs: bigint | null;
  attrs: [string, SpanAttrValue][];
  status: "ok" | "error" | "unset";
}

function randomHex(bytes: number): string {
  const buf = crypto.getRandomValues(new Uint8Array(bytes));
  return Array.from(buf, (b) => b.toString(16).padStart(2, "0")).join("");
}

function nowNs(): bigint {
  return BigInt(Math.round(Date.now() * 1_000_000));
}

class SpanImpl implements Span {
  readonly data: SpanData;
  constructor(name: string, traceId: string, parentSpanId?: string) {
    this.data = {
      name,
      traceId,
      spanId: randomHex(8),
      parentSpanId,
      startNs: nowNs(),
      endNs: null,
      attrs: [],
      status: "unset",
    };
  }
  setAttribute(key: string, value: SpanAttrValue): void {
    this.data.attrs.push([key, value]);
  }
  setStatus(code: "ok" | "error"): void {
    this.data.status = code;
  }
  end(): void {
    if (this.data.endNs === null) this.data.endNs = nowNs();
  }
}

// ─── OTLP/JSON serialization ────────────────────────────────────────────────

function serializeAttr(key: string, val: SpanAttrValue) {
  if (typeof val === "string") return { key, value: { stringValue: val } };
  if (typeof val === "boolean") return { key, value: { boolValue: val } };
  return Number.isInteger(val)
    ? { key, value: { intValue: String(val) } }
    : { key, value: { doubleValue: val } };
}

function buildOtlp(spans: SpanData[], service: string, environment: string): unknown {
  const now = nowNs();
  return {
    resourceSpans: [
      {
        resource: {
          attributes: [
            { key: "service.name", value: { stringValue: service } },
            { key: "deployment.environment", value: { stringValue: environment } },
          ],
        },
        scopeSpans: [
          {
            scope: { name: service },
            spans: spans.map((s) => ({
              traceId: s.traceId,
              spanId: s.spanId,
              ...(s.parentSpanId != null ? { parentSpanId: s.parentSpanId } : {}),
              name: s.name,
              kind: 2, // SPAN_KIND_SERVER
              startTimeUnixNano: String(s.startNs),
              endTimeUnixNano: String(s.endNs ?? now),
              attributes: s.attrs.map(([k, v]) => serializeAttr(k, v)),
              status: { code: s.status === "error" ? 2 : s.status === "ok" ? 1 : 0 },
            })),
          },
        ],
      },
    ],
  };
}

// ─── Public API ─────────────────────────────────────────────────────────────

export interface TracerHandle {
  /** Start a new span. Pass `parent` to nest it; omit for a root span. */
  startSpan(name: string, parent?: Span): Span;
  /** Send all completed spans to Honeycomb. Call via ctx.waitUntil after the response. */
  flush(): Promise<void>;
}

export interface OtelEnv {
  HONEYCOMB_API_KEY?: string;
  /** Sets deployment.environment attribute (default "prod"). */
  OTEL_ENVIRONMENT?: string;
}

/**
 * Initialize a request-scoped tracer. Returns null when HONEYCOMB_API_KEY is absent so
 * the caller can use optional-chaining throughout without separate feature-flag checks.
 */
export function initTracer(env: OtelEnv): TracerHandle | null {
  const apiKey = env.HONEYCOMB_API_KEY;
  if (!apiKey) return null;

  const environment = env.OTEL_ENVIRONMENT ?? "prod";
  const traceId = randomHex(16);
  const spans: SpanData[] = [];

  return {
    startSpan(name: string, parent?: Span): Span {
      const parentId = parent instanceof SpanImpl ? parent.data.spanId : undefined;
      const s = new SpanImpl(name, traceId, parentId);
      spans.push(s.data);
      return s;
    },

    async flush(): Promise<void> {
      if (spans.length === 0) return;
      const payload = buildOtlp(spans, "watermark-edge", environment);
      try {
        await fetch(HONEYCOMB_OTLP, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-honeycomb-team": apiKey,
          },
          body: JSON.stringify(payload),
        });
      } catch {
        // Absorb — tracing failures must never affect request handling
      }
    },
  };
}
