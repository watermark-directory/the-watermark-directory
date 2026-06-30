// Map a validated submission to a GitHub issue draft — see docs/submissions-api.md.
//
// Pure and synchronous so it's unit-testable; the dedupe hash is computed by the
// caller (SHA-256 via Web Crypto is async) and passed in. The submitter's text never
// escapes a safe context: the body is fenced, inline fields are sanitized, and the
// title is plain text — so a submission can't inject markdown/HTML or forge the
// provenance footer.

import type { Submission } from "./schema";

export interface IssueDraft {
  title: string;
  body: string;
  labels: string[];
  /** GitHub logins to assign on issue creation (#244). Empty ⇒ no assignees set. */
  assignees?: string[];
}

/** `submission` is the provenance marker (cf. `agent-proposed`); `needs-triage` is inert-until-human. */
export const SUBMISSION_LABELS = ["submission", "needs-triage"];

/**
 * Hidden marker embedded in each issue body so a resubmission is detectable. The same
 * string is matched when scanning open issues for dedupe (`github.ts`) — one source of
 * the format.
 */
export function submissionMarker(dedupeHash: string): string {
  return `<!-- submission: ${dedupeHash} -->`;
}

/** Strip newlines/control chars and neutralize backticks for an inline-code context. */
function inlineSafe(s: string): string {
  return (
    s
      // biome-ignore lint/suspicious/noControlCharactersInRegex: the point is to strip control chars from untrusted input before it reaches a GitHub issue
      .replace(/[\u0000-\u001f]+/g, " ") // newlines + other control chars -> space
      .replace(/`/g, "ʼ") // modifier-letter apostrophe — looks close, isn't a backtick
      .trim()
  );
}

/** Render free text inside a fenced block; neutralize any backtick that could close it. */
function fence(s: string): string {
  return `\`\`\`\n${s.replace(/`/g, "ʼ")}\n\`\`\``;
}

function titleText(s: Submission): string {
  const prefix =
    s.kind === "correction" ? "[correction]" : s.kind === "new_source" ? "[new-source]" : "[tip]";
  const label = s.target?.ref_label ? inlineSafe(s.target.ref_label) : "";
  const subject = label || inlineSafe(s.body).slice(0, 60) || "(no description)";
  return `${prefix} ${subject}`.slice(0, 120);
}

export function buildIssue(
  s: Submission,
  dedupeHash: string,
  sub?: string,
  notifyUsers?: string[],
  attachmentKeys?: string[],
): IssueDraft {
  const lines: string[] = [];

  if (s.target && s.target.ref_kind !== "general") {
    const label = s.target.ref_label ? ` — ${inlineSafe(s.target.ref_label)}` : "";
    lines.push(
      `**Concerns:** \`${inlineSafe(s.target.ref_kind)}\` \`${inlineSafe(s.target.ref_id)}\`${label}`,
    );
  }
  if (s.page_url) lines.push(`**From page:** ${s.page_url}`);
  lines.push("");
  lines.push("**Submission:**");
  lines.push(fence(s.body));
  if (s.evidence_url) {
    lines.push("");
    lines.push(`**Cited evidence:** ${s.evidence_url}`);
  }
  if (attachmentKeys && attachmentKeys.length > 0) {
    lines.push("");
    lines.push("**Attachments** _(retrieve via `wrangler r2 object get SUBMISSION_ATTACHMENTS <key>`)_:");
    for (const key of attachmentKeys) {
      lines.push(`- \`${inlineSafe(key)}\``);
    }
  }
  lines.push("");
  lines.push("---");
  const authAttr = sub ? `authenticated (sub: \`${inlineSafe(sub)}\`); ` : "";
  lines.push(
    `_Submitted via the public form; Turnstile-verified; ${authAttr}**unverified** — triage before ` +
      "acting. A submission is a proposal, never evidence._",
  );
  lines.push(submissionMarker(dedupeHash));

  const assignees = notifyUsers && notifyUsers.length > 0 ? notifyUsers.slice(0, 10) : undefined;
  return { title: titleText(s), body: lines.join("\n"), labels: SUBMISSION_LABELS, assignees };
}

/** Stable input for the dedupe hash: the target + the normalized body. */
export function dedupeInput(s: Submission): string {
  const ref = s.target ? `${s.target.ref_kind}:${s.target.ref_id}` : "";
  return `${ref}\n${s.body.trim().toLowerCase()}`;
}

/** Hex SHA-256 over Web Crypto — the dedupe hash's digest (paired with `dedupeInput`). */
export async function sha256Hex(input: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
