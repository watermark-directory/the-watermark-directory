// The /api/ask request contract — see docs/ask-api.md.
//
// Allowlist validation, mirroring submit's schema.ts: any field not named here is
// *rejected*, not ignored, so the abuse surface can't grow by a caller adding fields.
// Pure and dependency-free, so it runs on the Workers runtime and is unit-testable.

export interface AskRequest {
  question: string;
  turnstile_token?: string;
}

/** Size caps — mirror the contract table in docs/ask-api.md. */
export const ASK_LIMITS = {
  /** A grounded Q&A box, not an essay prompt — keep inputs short and cheap. */
  question_min: 3,
  question_max: 1000,
  token: 4096,
} as const;

export type AskValidation = { ok: true; value: AskRequest } | { ok: false; error: string };

export function validateAsk(raw: unknown): AskValidation {
  if (typeof raw !== "object" || raw === null) return { ok: false, error: "body must be a JSON object" };
  const o = raw as Record<string, unknown>;

  const allowed = new Set(["question", "turnstile_token"]);
  for (const k of Object.keys(o)) if (!allowed.has(k)) return { ok: false, error: `unexpected field: ${k}` };

  if (typeof o.question !== "string") return { ok: false, error: "question is required" };
  const question = o.question.trim();
  if (question.length < ASK_LIMITS.question_min) return { ok: false, error: "question is too short" };
  if (question.length > ASK_LIMITS.question_max)
    return { ok: false, error: `question exceeds ${ASK_LIMITS.question_max} characters` };

  const value: AskRequest = { question };

  if (o.turnstile_token !== undefined) {
    if (typeof o.turnstile_token !== "string")
      return { ok: false, error: "turnstile_token must be a string" };
    if (o.turnstile_token.length > ASK_LIMITS.token)
      return { ok: false, error: "turnstile_token is too long" };
    value.turnstile_token = o.turnstile_token;
  }

  return { ok: true, value };
}
