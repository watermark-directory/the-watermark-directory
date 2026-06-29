// Shared env-var coercion for the Pages Functions.
//
// `Number(env.X) || DEFAULT` is a footgun for numeric caps: a configured `"0"` — the natural
// way to say "disable / hard-stop" — is falsy, so it silently reverts to the default instead of
// zeroing (frontend audit #588). `intEnv` honors a finite `0` and only falls back when the value
// is genuinely absent or non-numeric.

/** Parse a numeric env var, honoring a configured `0`; fall back when unset/empty/non-numeric. */
export function intEnv(raw: string | undefined, fallback: number): number {
  if (raw === undefined || raw.trim() === "") return fallback;
  const n = Number(raw);
  return Number.isFinite(n) ? n : fallback;
}
