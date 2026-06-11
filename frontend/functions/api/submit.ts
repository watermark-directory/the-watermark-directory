// POST /api/submit — the public tips/corrections endpoint (Epic #56 / #74).
// A Cloudflare Pages Function colocated with the static site, so the form posts
// same-origin. See docs/submissions-api.md for the contract and the chain-of-custody
// invariant: a submission only ever opens a labeled, inert GitHub issue.
//
// Flow: kill switch → parse + allowlist-validate → same-origin page_url → verify
// Turnstile → mint the issues-only App token → create the issue.

import { createIssueAsApp } from "./_lib/github";
import { buildIssue, dedupeInput } from "./_lib/issue";
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
}

// Minimal Pages-Functions context (avoids a dep on @cloudflare/workers-types; the
// runtime supplies request + env). Only POST is exported, so other verbs get 405.
interface RequestContext {
  request: Request;
  env: Env;
}

const json = (status: number, data: unknown): Response =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } });

async function sha256Hex(input: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export const onRequestPost = async (ctx: RequestContext): Promise<Response> => {
  const { request, env } = ctx;

  if (env.SUBMISSIONS_ENABLED !== "true") return json(503, { error: "submissions are not enabled" });
  if (!env.TURNSTILE_SECRET_KEY || !env.TIPS_APP_ID || !env.TIPS_APP_PRIVATE_KEY)
    return json(500, { error: "endpoint is misconfigured" });

  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    return json(400, { error: "invalid JSON" });
  }

  const parsed = validateSubmission(raw);
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
  const human = await verifyTurnstile(submission.turnstile_token, env.TURNSTILE_SECRET_KEY, remoteip);
  if (!human) return json(403, { error: "verification failed — please retry the challenge" });

  try {
    const dedupeHash = await sha256Hex(dedupeInput(submission));
    const issue = buildIssue(submission, dedupeHash);
    const url = await createIssueAsApp({
      appId: env.TIPS_APP_ID,
      privateKey: env.TIPS_APP_PRIVATE_KEY,
      owner: env.GITHUB_OWNER ?? "goedelsoup",
      repo: env.GITHUB_REPO ?? "bosc",
      issue,
    });
    return json(201, { issue_url: url });
  } catch (e) {
    console.error("submission failed:", e);
    return json(502, { error: "could not file the submission — please try again later" });
  }
};
