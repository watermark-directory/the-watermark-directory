// Tier A integration test for the /api/submit Pages Function (functions/api/submit.ts):
// drive the exported `onRequestPost` end-to-end with a faked Env + a stubbed `fetch`, so
// the full request path (kill switch → validate → rate-limit → Turnstile → GitHub-App JWT
// → dedupe → file issue → private contact store) is exercised offline, no wrangler, no
// network, no real issues filed. Pure `_lib` logic is unit-tested separately
// (submitContact.test.ts et al.); this covers the wiring those leave out.

import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { dedupeInput, submissionMarker } from "../../functions/api/_lib/issue";
import { windowKey } from "../../functions/api/_lib/ratelimit";
import { onRequestPost } from "../../functions/api/submit";
import {
  type FetchRoute,
  fakeKV,
  generatePkcs8Pem,
  jsonResponse,
  postJson,
  routingFetch,
} from "./_routeHarness";

const SUBMIT_URL = "https://bosc.test/api/submit";
const GITHUB_API_BASE = "https://gh.test"; // exercises the GITHUB_API_BASE seam
const ISSUE_URL = "https://github.com/goedelsoup/bosc/issues/123";

let privateKey: string;
beforeAll(async () => {
  privateKey = await generatePkcs8Pem();
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function submitEnv(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    SUBMISSIONS_ENABLED: "true",
    TURNSTILE_SECRET_KEY: "1x0000000000000000000000000000000AA",
    TIPS_APP_ID: "12345",
    TIPS_APP_PRIVATE_KEY: privateKey,
    GITHUB_OWNER: "goedelsoup",
    GITHUB_REPO: "bosc",
    GITHUB_API_BASE,
    ...overrides,
  };
}

const validSubmission = (extra: Record<string, unknown> = {}) => ({
  kind: "tip",
  body: "A culvert behind the plant discharges into the creek after rain.",
  turnstile_token: "tok",
  ...extra,
});

const turnstileRoute = (success: boolean): FetchRoute => ({
  test: (url) => url.pathname === "/turnstile/v0/siteverify",
  respond: () => jsonResponse(200, { success }),
});

// GitHub App auth + issue routes. `issuesOnGet` lets a test seed an existing open
// submission (the dedupe path); default is "no open submissions".
function githubRoutes(issuesOnGet: Array<{ html_url: string; body: string }> = []): FetchRoute[] {
  return [
    {
      test: (url) => url.pathname.endsWith("/installation"),
      respond: () => jsonResponse(200, { id: 42 }),
    },
    {
      test: (url) => url.pathname.endsWith("/access_tokens"),
      respond: () => jsonResponse(201, { token: "ghs_test" }),
    },
    {
      test: (url, m) => url.pathname.endsWith("/issues") && m === "GET",
      respond: () => jsonResponse(200, issuesOnGet),
    },
    {
      test: (url, m) => url.pathname.endsWith("/issues") && m === "POST",
      respond: () => jsonResponse(201, { html_url: ISSUE_URL }),
    },
  ];
}

async function sha256Hex(input: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

describe("/api/submit route", () => {
  it("503s when the kill switch is off", async () => {
    vi.stubGlobal("fetch", routingFetch([]));
    const res = await onRequestPost({ request: postJson(SUBMIT_URL, validSubmission()), env: {} } as never);
    expect(res.status).toBe(503);
  });

  it("500s when secrets are missing", async () => {
    vi.stubGlobal("fetch", routingFetch([]));
    const res = await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission()),
      env: { SUBMISSIONS_ENABLED: "true" },
    } as never);
    expect(res.status).toBe(500);
  });

  it("400s on invalid JSON before any external call", async () => {
    const fetchStub = routingFetch([]);
    vi.stubGlobal("fetch", fetchStub);
    const request = new Request(SUBMIT_URL, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: "{ not json",
    });
    const res = await onRequestPost({ request, env: submitEnv() } as never);
    expect(res.status).toBe(400);
    expect(fetchStub.calls).toHaveLength(0);
  });

  it("400s when the payload fails allowlist validation", async () => {
    vi.stubGlobal("fetch", routingFetch([]));
    const res = await onRequestPost({
      request: postJson(SUBMIT_URL, { kind: "tip" }), // no body, no token
      env: submitEnv(),
    } as never);
    expect(res.status).toBe(400);
  });

  it("403s and never reaches GitHub when Turnstile fails", async () => {
    const fetchStub = routingFetch([turnstileRoute(false), ...githubRoutes()]);
    vi.stubGlobal("fetch", fetchStub);
    const res = await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission()),
      env: submitEnv(),
    } as never);
    expect(res.status).toBe(403);
    expect(fetchStub.calls.some((c) => c.url.includes("/installation"))).toBe(false);
  });

  it("files an issue and returns 201 on the happy path (honoring GITHUB_API_BASE)", async () => {
    const fetchStub = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", fetchStub);
    const res = await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission()),
      env: submitEnv(),
    } as never);
    expect(res.status).toBe(201);
    expect(await res.json()).toEqual({ issue_url: ISSUE_URL, deduped: false });
    expect(
      fetchStub.calls.some((c) => c.url.startsWith(GITHUB_API_BASE) && c.url.endsWith("/installation")),
    ).toBe(true);
  });

  it("dedupes against an open submission carrying the same marker (200, no new issue)", async () => {
    const submission = validSubmission();
    const hash = await sha256Hex(dedupeInput(submission as never));
    const existing = {
      html_url: "https://github.com/goedelsoup/bosc/issues/7",
      body: `x ${submissionMarker(hash)} y`,
    };
    const fetchStub = routingFetch([turnstileRoute(true), ...githubRoutes([existing])]);
    vi.stubGlobal("fetch", fetchStub);

    const res = await onRequestPost({ request: postJson(SUBMIT_URL, submission), env: submitEnv() } as never);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ issue_url: existing.html_url, deduped: true });
    // The POST that would open a *new* issue must not have fired.
    expect(fetchStub.calls.some((c) => c.method === "POST" && c.url.endsWith("/issues"))).toBe(false);
  });

  it("drops a foreign-origin page_url (keeps a same-origin one)", async () => {
    const issuePost = (stub: ReturnType<typeof routingFetch>) =>
      stub.calls.find((c) => c.method === "POST" && c.url.endsWith("/issues"));

    const foreign = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", foreign);
    await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission({ page_url: "https://evil.test/phish" })),
      env: submitEnv(),
    } as never);
    expect(issuePost(foreign)?.body).not.toContain("evil.test");
    expect(issuePost(foreign)?.body).not.toContain("From page");
    vi.unstubAllGlobals();

    const same = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", same);
    await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission({ page_url: "https://bosc.test/network/x" })),
      env: submitEnv(),
    } as never);
    expect(issuePost(same)?.body).toContain("https://bosc.test/network/x");
  });

  it("429s (before Turnstile) when the per-IP window is exhausted", async () => {
    const fixedMs = 1_750_000_000_000;
    vi.spyOn(Date, "now").mockReturnValue(fixedMs);
    const ip = "203.0.113.9";
    const kv = fakeKV({ [windowKey(ip, Math.floor(fixedMs / 1000), 3600)]: "5" }); // default max = 5
    const fetchStub = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", fetchStub);

    const request = postJson(SUBMIT_URL, validSubmission(), { "CF-Connecting-IP": ip });
    const res = await onRequestPost({ request, env: submitEnv({ RATE_LIMIT: kv }) } as never);
    expect(res.status).toBe(429);
    expect(res.headers.get("Retry-After")).toBeTruthy();
    expect(fetchStub.calls.some((c) => c.url.includes("/siteverify"))).toBe(false);
  });

  it('treats RATE_LIMIT_MAX="0" as block-all (not the default 5) (#588)', async () => {
    const fixedMs = 1_750_000_000_000;
    vi.spyOn(Date, "now").mockReturnValue(fixedMs);
    const ip = "203.0.113.10";
    const kv = fakeKV({}); // no prior submissions
    const fetchStub = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", fetchStub);

    const request = postJson(SUBMIT_URL, validSubmission(), { "CF-Connecting-IP": ip });
    const res = await onRequestPost({
      request,
      env: submitEnv({ RATE_LIMIT: kv, RATE_LIMIT_MAX: "0" }),
    } as never);
    expect(res.status).toBe(429); // 0 allowed ⇒ first submission already over
    expect(fetchStub.calls.some((c) => c.url.includes("/siteverify"))).toBe(false);
  });

  it("stores submitter contact in the private KV, never in the public issue", async () => {
    const kv = fakeKV();
    const fetchStub = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", fetchStub);

    const res = await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission({ contact: "tipster@example.com" })),
      env: submitEnv({ SUBMISSION_CONTACT: kv }),
    } as never);
    expect(res.status).toBe(201);

    const stored = kv.store.get("contact:123"); // issue number parsed from ISSUE_URL
    expect(stored).toBeTruthy();
    expect(JSON.parse(stored as string).contact).toBe("tipster@example.com");
    const issuePost = fetchStub.calls.find((c) => c.method === "POST" && c.url.endsWith("/issues"));
    expect(issuePost?.body).not.toContain("tipster@example.com");
  });

  it("files normally when no contact KV is bound (contact silently skipped)", async () => {
    const fetchStub = routingFetch([turnstileRoute(true), ...githubRoutes()]);
    vi.stubGlobal("fetch", fetchStub);
    const res = await onRequestPost({
      request: postJson(SUBMIT_URL, validSubmission({ contact: "tipster@example.com" })),
      env: submitEnv(), // no SUBMISSION_CONTACT binding
    } as never);
    expect(res.status).toBe(201);
  });
});
