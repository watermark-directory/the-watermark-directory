// POST /api/submit — the public tips/corrections endpoint (Epic #56 / #74).
// A Cloudflare Pages Function colocated with the static site, so the form posts
// same-origin. See docs/submissions-api.md for the contract and the chain-of-custody
// invariant: a submission only ever opens a labeled, inert GitHub issue.
//
// Flow: kill switch → parse + allowlist-validate → same-origin page_url → per-IP
// rate-limit (soft, if a KV namespace is bound) → verify Turnstile → mint the
// issues-only App token → dedupe vs open submissions → create the issue.

import { intEnv } from "./_lib/env";
import { fileIssueAsApp } from "./_lib/github";
import { json, parseJsonBody, requireEnabled } from "./_lib/http";
import { buildIssue, dedupeInput, sha256Hex } from "./_lib/issue";
import { DEFAULT_RATE_LIMIT, enforceRateLimit, type KVLike } from "./_lib/ratelimit";
import { validateSubmission } from "./_lib/schema";
import { verifyTurnstile } from "./_lib/turnstile";

interface Env {
  /** On/kill switch — anything but "true" disables the endpoint. */
  SUBMISSIONS_ENABLED?: string;
  TURNSTILE_SECRET_KEY?: string;
  TIPS_APP_ID?: string;
  TIPS_APP_PRIVATE_KEY?: string;
  /** Default to this repo; overridable for forks/tests. */
  GITHUB_OWNER?: string;
  GITHUB_REPO?: string;
  /** Override the GitHub API host (local dev mock). Absent ⇒ api.github.com. */
  GITHUB_API_BASE?: string;
  /** Optional KV namespace for per-IP rate limiting; absent ⇒ rate limiting off. */
  RATE_LIMIT?: KVLike;
  RATE_LIMIT_MAX?: string;
  RATE_LIMIT_WINDOW_SEC?: string;
  /**
   * Optional KV namespace for the **private** submitter-contact channel (#242), keyed by
   * issue number. Absent ⇒ the optional contact field is simply not retained (the public
   * issue is unaffected — contact never lands there).
   */
  SUBMISSION_CONTACT?: KVLike;
  /** Override the contact retention TTL (seconds); default below bounds PII retention. */
  CONTACT_TTL_SEC?: string;
}

// Submitter contact is PII — keep it only as long as triage plausibly needs it, then let
// KV expire it. 180 days by default; operator-overridable via CONTACT_TTL_SEC.
const DEFAULT_CONTACT_TTL_SEC = 60 * 60 * 24 * 180;

// Minimal Pages-Functions context (avoids a dep on @cloudflare/workers-types; the
// runtime supplies request + env). Only POST is exported, so other verbs get 405.
interface RequestContext {
  request: Request;
  env: Env;
}

export const onRequestPost = async (ctx: RequestContext): Promise<Response> => {
  const { request, env } = ctx;

  const disabled = requireEnabled(env.SUBMISSIONS_ENABLED, () =>
    json(503, { error: "submissions are not enabled" }),
  );
  if (disabled) return disabled;
  if (!env.TURNSTILE_SECRET_KEY || !env.TIPS_APP_ID || !env.TIPS_APP_PRIVATE_KEY)
    return json(500, { error: "endpoint is misconfigured" });

  const body = await parseJsonBody(request);
  if (!body.ok) return body.response;

  const parsed = validateSubmission(body.value);
  if (!parsed.ok) return json(400, { error: parsed.error });
  const submission = parsed.value;

  // page_url is an auto-filled convenience; drop (don't reject) a foreign-origin one.
  if (submission.page_url) {
    try {
      if (new URL(submission.page_url).host !== new URL(request.url).host) submission.page_url = undefined;
    } catch {
      submission.page_url = undefined;
    }
  }

  const remoteip = request.headers.get("CF-Connecting-IP") ?? undefined;

  // Rate-limit early — before spending a Turnstile verification — when a KV namespace
  // is bound and we have an IP. Soft + fail-open (Turnstile is the primary gate).
  if (env.RATE_LIMIT && remoteip) {
    const blocked = await enforceRateLimit(
      env.RATE_LIMIT,
      remoteip,
      Math.floor(Date.now() / 1000),
      {
        max: intEnv(env.RATE_LIMIT_MAX, DEFAULT_RATE_LIMIT.max),
        windowSec: Math.max(60, intEnv(env.RATE_LIMIT_WINDOW_SEC, DEFAULT_RATE_LIMIT.windowSec)),
      },
      "too many submissions — please try again later",
    );
    if (blocked) return blocked;
  }

  const human = await verifyTurnstile(submission.turnstile_token, env.TURNSTILE_SECRET_KEY, remoteip);
  if (!human) return json(403, { error: "verification failed — please retry the challenge" });

  try {
    const dedupeHash = await sha256Hex(dedupeInput(submission));
    const issue = buildIssue(submission, dedupeHash);
    const result = await fileIssueAsApp({
      appId: env.TIPS_APP_ID,
      privateKey: env.TIPS_APP_PRIVATE_KEY,
      owner: env.GITHUB_OWNER ?? "watermark-directory",
      repo: env.GITHUB_REPO ?? "the-watermark-directory",
      issue,
      dedupeHash,
      apiBase: env.GITHUB_API_BASE,
    });

    // Optional submitter contact (#242) → the PRIVATE store, keyed by issue number; never
    // the public issue (buildIssue ignores it). Best-effort: a missing binding or a write
    // error must not fail the submission (the tip is what matters) and never leaks contact.
    if (submission.contact && env.SUBMISSION_CONTACT) {
      const issueNo = result.url.match(/\/(\d+)(?:[?#].*)?$/)?.[1];
      if (issueNo) {
        const ttl = Math.max(60, Number(env.CONTACT_TTL_SEC) || DEFAULT_CONTACT_TTL_SEC);
        try {
          await env.SUBMISSION_CONTACT.put(
            `contact:${issueNo}`,
            JSON.stringify({
              contact: submission.contact,
              kind: submission.kind,
              dedupe: dedupeHash,
              deduped: result.deduped,
              at: new Date().toISOString(),
            }),
            { expirationTtl: ttl },
          );
        } catch (e) {
          console.error("contact store failed (submission still filed):", e);
        }
      }
    }

    return json(result.deduped ? 200 : 201, { issue_url: result.url, deduped: result.deduped });
  } catch (e) {
    console.error("submission failed:", e);
    return json(502, { error: "could not file the submission — please try again later" });
  }
};
