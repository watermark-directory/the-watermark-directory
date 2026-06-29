// Shared formatters + small numeric/string utils (#581) — the peer of `money.ts` / `charts.ts`.
// These were each duplicated (and quietly diverging) across `lib/` and `components/islands/`;
// this is the one home for them.

/** Round `n` to `decimals` places (half-up via `Math.round`). */
export function round(n: number, decimals = 0): number {
  const f = 10 ** decimals;
  return Math.round(n * f) / f;
}

/** A dilution / ratio multiple: `"∞×"` when non-finite, an integer at ≥10×, else one decimal. */
export function fmtMult(m: number): string {
  if (!Number.isFinite(m)) return "∞×";
  return `${m >= 10 ? Math.round(m) : m.toFixed(1)}×`;
}

/** Megawatts, rounded to whole MW. */
export function fmtMw(n: number): string {
  return `${Math.round(n)} MW`;
}

const HTML_ESCAPES: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
};

/** Escape the HTML metacharacters in `s` before interpolating it into an HTML string. */
export function escapeHtml(s: string): string {
  return s.replace(/[&<>"]/g, (c) => HTML_ESCAPES[c]);
}

/** Join the defined, non-empty string parts into one searchable blob (` · `-separated). */
export function blob(...parts: (string | null | undefined)[]): string {
  return parts.filter((p): p is string => typeof p === "string" && p.trim().length > 0).join(" · ");
}
