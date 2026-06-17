// The submissions payload contract — see docs/submissions-api.md.
//
// Allowlist validation: any field not named here is *rejected*, not ignored, so the
// abuse surface can't grow by a submitter adding fields. Pure and dependency-free
// (only the `URL` global), so it runs on the Workers runtime and is unit-testable.

export type SubmissionKind = "tip" | "correction" | "new_source";
export type RefKind = "record" | "document" | "entity" | "concept" | "page" | "general";

export interface SubmissionTarget {
  ref_kind: RefKind;
  /** Empty for `general`; the bundle id otherwise (record `rel`, entity `key`, …). */
  ref_id: string;
  ref_label?: string;
}

export interface Submission {
  kind: SubmissionKind;
  body: string;
  target?: SubmissionTarget;
  evidence_url?: string;
  page_url?: string;
  turnstile_token: string;
}

/** Size caps — mirror the contract table in docs/submissions-api.md. */
export const LIMITS = {
  body: 4000,
  ref_id: 300,
  ref_label: 200,
  url: 500,
  token: 4096,
} as const;

const KINDS: readonly SubmissionKind[] = ["tip", "correction", "new_source"];
const REF_KINDS: readonly RefKind[] = ["record", "document", "entity", "concept", "page", "general"];

export type ValidationResult = { ok: true; value: Submission } | { ok: false; error: string };

function isHttpUrl(s: string): boolean {
  let u: URL;
  try {
    u = new URL(s);
  } catch {
    return false;
  }
  return u.protocol === "http:" || u.protocol === "https:";
}

function err(error: string): ValidationResult {
  return { ok: false, error };
}

export function validateSubmission(raw: unknown): ValidationResult {
  if (typeof raw !== "object" || raw === null) return err("body must be a JSON object");
  const o = raw as Record<string, unknown>;

  const allowed = new Set(["kind", "body", "target", "evidence_url", "page_url", "turnstile_token"]);
  for (const k of Object.keys(o)) if (!allowed.has(k)) return err(`unexpected field: ${k}`);

  if (typeof o.kind !== "string" || !KINDS.includes(o.kind as SubmissionKind))
    return err("kind must be 'tip', 'correction', or 'new_source'");

  if (typeof o.body !== "string" || o.body.trim().length === 0) return err("body is required");
  if (o.body.length > LIMITS.body) return err(`body exceeds ${LIMITS.body} characters`);

  if (typeof o.turnstile_token !== "string" || o.turnstile_token.length === 0)
    return err("turnstile_token is required");
  if (o.turnstile_token.length > LIMITS.token) return err("turnstile_token is too long");

  const value: Submission = {
    kind: o.kind as SubmissionKind,
    body: o.body,
    turnstile_token: o.turnstile_token,
  };

  if (o.target !== undefined) {
    if (typeof o.target !== "object" || o.target === null) return err("target must be an object");
    const t = o.target as Record<string, unknown>;
    const tAllowed = new Set(["ref_kind", "ref_id", "ref_label"]);
    for (const k of Object.keys(t)) if (!tAllowed.has(k)) return err(`unexpected target field: ${k}`);

    if (typeof t.ref_kind !== "string" || !REF_KINDS.includes(t.ref_kind as RefKind))
      return err("target.ref_kind is invalid");
    const ref_kind = t.ref_kind as RefKind;

    let ref_id = "";
    if (ref_kind !== "general") {
      if (typeof t.ref_id !== "string" || t.ref_id.trim().length === 0)
        return err("target.ref_id is required");
      if (t.ref_id.length > LIMITS.ref_id) return err("target.ref_id is too long");
      ref_id = t.ref_id;
    }

    const target: SubmissionTarget = { ref_kind, ref_id };
    if (t.ref_label !== undefined) {
      if (typeof t.ref_label !== "string") return err("target.ref_label must be a string");
      if (t.ref_label.length > LIMITS.ref_label) return err("target.ref_label is too long");
      target.ref_label = t.ref_label;
    }
    value.target = target;
  }

  if (o.evidence_url !== undefined) {
    if (typeof o.evidence_url !== "string") return err("evidence_url must be a string");
    if (o.evidence_url.length > LIMITS.url) return err("evidence_url is too long");
    if (!isHttpUrl(o.evidence_url)) return err("evidence_url must be http(s)");
    value.evidence_url = o.evidence_url;
  }

  if (o.page_url !== undefined) {
    if (typeof o.page_url !== "string") return err("page_url must be a string");
    if (o.page_url.length > LIMITS.url) return err("page_url is too long");
    if (!isHttpUrl(o.page_url)) return err("page_url must be http(s)");
    value.page_url = o.page_url;
  }

  return { ok: true, value };
}
