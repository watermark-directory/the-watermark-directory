// Lambda handler: GitHub webhook → AUTH_PREFS lookup → SES email dispatch (#938 E1).
//
// Triggered by an API Gateway (Lambda URL) receiving `issues.opened` events from the
// GitHub webhook on the `watermark-directory/the-watermark-directory` repository.
//
// Flow:
//   1. Verify the GitHub webhook signature (X-Hub-Signature-256).
//   2. Parse the issue labels to determine notification category.
//   3. Enumerate AUTH_PREFS KV (via Cloudflare REST API) for subscribers matching
//      the category + a site that matches the issue's site label.
//   4. Send an immediate SES email for each `immediate`-frequency subscriber.
//   5. Increment a `digest:pending:<sub>` counter for `daily` subscribers
//      (flushed by a separate EventBridge-triggered digest Lambda, future work).
//   6. On first successful delivery, note `email_verified: true` is set by the
//      subscriber's own prefs write path — the Lambda doesn't touch that field.
//
// Required environment variables (set in Lambda console / Pulumi secrets):
//   GITHUB_WEBHOOK_SECRET       — shared secret used to verify X-Hub-Signature-256
//   CLOUDFLARE_API_TOKEN        — CF API token with KV read/write permission
//   CLOUDFLARE_ACCOUNT_ID       — Cloudflare account ID
//   AUTH_PREFS_NAMESPACE_ID     — the AUTH_PREFS KV namespace ID
//   SES_FROM_ADDRESS            — verified SES sender address
//   SITE_URL                    — base URL for unsubscribe links (e.g. https://watermarkdirectory.org)
//   UNSUB_SECRET                — shared HMAC secret (same as Pages Function UNSUB_SECRET)

import {
  type APIGatewayProxyEventV2,
  type APIGatewayProxyResultV2,
  type ScheduledEvent,
} from "aws-lambda";
import { createHmac, timingSafeEqual } from "crypto";
import { SESClient, SendEmailCommand } from "@aws-sdk/client-ses";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface IssueEvent {
  action: string;
  issue: {
    number: number;
    title: string;
    html_url: string;
    labels: Array<{ name: string }>;
  };
  repository: {
    full_name: string;
  };
}

interface UserPrefs {
  notifications?: {
    sites?: string[];
    categories?: string[];
    frequency?: "immediate" | "daily";
    email_verified?: boolean;
  };
}

type NotifCategory = "tip" | "correction" | "new_source" | "hypothesis";

const CATEGORY_LABELS: Record<string, NotifCategory> = {
  "[tip]": "tip",
  "[correction]": "correction",
  "[new-source]": "new_source",
  hypothesis: "hypothesis",
};

// ---------------------------------------------------------------------------
// GitHub webhook signature verification
// ---------------------------------------------------------------------------

function verifySignature(secret: string, body: string, signature: string): boolean {
  const expected = `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;
  try {
    return timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Cloudflare KV REST API helpers
// ---------------------------------------------------------------------------

async function cfKvListKeys(
  token: string,
  accountId: string,
  namespaceId: string,
  prefix: string,
): Promise<string[]> {
  const url = `https://api.cloudflare.com/client/v4/accounts/${accountId}/storage/kv/namespaces/${namespaceId}/keys?prefix=${encodeURIComponent(prefix)}&limit=1000`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`CF KV list failed: ${res.status}`);
  const data = (await res.json()) as {
    result?: Array<{ name: string }>;
    success?: boolean;
  };
  return (data.result ?? []).map((k) => k.name);
}

async function cfKvGetValue(
  token: string,
  accountId: string,
  namespaceId: string,
  key: string,
): Promise<string | null> {
  const url = `https://api.cloudflare.com/client/v4/accounts/${accountId}/storage/kv/namespaces/${namespaceId}/values/${encodeURIComponent(key)}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`CF KV get failed: ${res.status}`);
  return res.text();
}

async function cfKvPutValue(
  token: string,
  accountId: string,
  namespaceId: string,
  key: string,
  value: string,
): Promise<void> {
  const url = `https://api.cloudflare.com/client/v4/accounts/${accountId}/storage/kv/namespaces/${namespaceId}/values/${encodeURIComponent(key)}`;
  const res = await fetch(url, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "text/plain" },
    body: value,
  });
  if (!res.ok) throw new Error(`CF KV put failed: ${res.status}`);
}

// ---------------------------------------------------------------------------
// Unsubscribe token (mirrors _lib/unsub.ts for the Lambda side)
// ---------------------------------------------------------------------------

const TOKEN_TTL_SEC = 30 * 24 * 60 * 60;

function base64urlEncode(buf: Buffer): string {
  return buf.toString("base64url");
}

function base64urlEncodeStr(s: string): string {
  return base64urlEncode(Buffer.from(s, "utf8"));
}

function signUnsubToken(sub: string, category: string, secret: string): string {
  const exp = Math.floor(Date.now() / 1000) + TOKEN_TTL_SEC;
  const message = `${sub}|${category}|${exp}`;
  const sig = createHmac("sha256", secret).update(message).digest("base64url");
  return [base64urlEncodeStr(sub), base64urlEncodeStr(category), String(exp), sig].join(".");
}

// ---------------------------------------------------------------------------
// SES email dispatch
// ---------------------------------------------------------------------------

const ses = new SESClient({});

async function sendNotificationEmail(params: {
  toEmail: string;
  sub: string;
  category: string;
  issue: IssueEvent["issue"];
  siteUrl: string;
  unsubSecret: string;
  fromAddress: string;
}): Promise<void> {
  const { toEmail, sub, category, issue, siteUrl, unsubSecret, fromAddress } = params;
  const unsubToken = signUnsubToken(sub, category, unsubSecret);
  const unsubUrl = `${siteUrl}/account/unsubscribe?token=${unsubToken}`;

  const categoryLabel: Record<string, string> = {
    tip: "New tip",
    correction: "Correction submitted",
    new_source: "New source added",
    hypothesis: "Hypothesis update",
  };

  const subject = `[Watermark] ${categoryLabel[category] ?? "Update"}: ${issue.title}`;

  const body = `A new ${category.replace("_", " ")} has been posted to the Watermark Directory.

Issue: ${issue.title}
Link: ${issue.html_url}

---
To stop receiving these emails, click: ${unsubUrl}
To manage all notification preferences, visit: ${siteUrl}/account
`;

  await ses.send(
    new SendEmailCommand({
      Source: fromAddress,
      Destination: { ToAddresses: [toEmail] },
      Message: {
        Subject: { Data: subject, Charset: "UTF-8" },
        Body: { Text: { Data: body, Charset: "UTF-8" } },
      },
    }),
  );
}

// ---------------------------------------------------------------------------
// Main handler (webhook + scheduled digest trigger stub)
// ---------------------------------------------------------------------------

export const handler = async (
  event: APIGatewayProxyEventV2 | ScheduledEvent,
): Promise<APIGatewayProxyResultV2 | void> => {
  const env = {
    GITHUB_WEBHOOK_SECRET: process.env.GITHUB_WEBHOOK_SECRET ?? "",
    CLOUDFLARE_API_TOKEN: process.env.CLOUDFLARE_API_TOKEN ?? "",
    CLOUDFLARE_ACCOUNT_ID: process.env.CLOUDFLARE_ACCOUNT_ID ?? "",
    AUTH_PREFS_NAMESPACE_ID: process.env.AUTH_PREFS_NAMESPACE_ID ?? "",
    SES_FROM_ADDRESS: process.env.SES_FROM_ADDRESS ?? "",
    SITE_URL: process.env.SITE_URL ?? "",
    UNSUB_SECRET: process.env.UNSUB_SECRET ?? "",
  };

  // EventBridge scheduled event — daily digest flush (stubbed; TODO: #938 follow-up).
  if ("source" in event && event.source === "aws.events") {
    console.log("Daily digest trigger received — digest dispatch not yet implemented.");
    return;
  }

  // Fail closed: all required env vars must be present before touching secrets.
  const missing = Object.entries(env)
    .filter(([, value]) => !value)
    .map(([key]) => key);
  if (missing.length) {
    console.error("Notify Lambda missing required env vars", missing);
    return { statusCode: 500, body: "notification service misconfigured" };
  }

  // API Gateway webhook event.
  const webhookEvent = event as APIGatewayProxyEventV2;
  const body = webhookEvent.body ?? "";
  const ghEvent = webhookEvent.headers?.["x-github-event"];
  const signature = webhookEvent.headers?.["x-hub-signature-256"] ?? "";

  if (!verifySignature(env.GITHUB_WEBHOOK_SECRET, body, signature)) {
    return { statusCode: 401, body: "invalid signature" };
  }

  if (ghEvent !== "issues") {
    return { statusCode: 200, body: "ignored" };
  }

  let parsed: IssueEvent;
  try {
    parsed = JSON.parse(body) as IssueEvent;
  } catch {
    return { statusCode: 400, body: "invalid JSON" };
  }

  if (parsed.action !== "opened") {
    return { statusCode: 200, body: "ignored" };
  }

  const labelNames = parsed.issue.labels.map((l) => l.name);

  // Determine notification category from labels.
  const category = Object.entries(CATEGORY_LABELS).find(([label]) =>
    labelNames.includes(label),
  )?.[1];

  // Determine site from a `site:<slug>` label.
  const siteSlug = labelNames.find((l) => l.startsWith("site:"))?.slice(5) ?? null;

  if (!category) {
    return { statusCode: 200, body: "no matching category label" };
  }
  if (!siteSlug) {
    return { statusCode: 200, body: "no matching site label" };
  }

  // Enumerate AUTH_PREFS subscribers.
  const keys = await cfKvListKeys(
    env.CLOUDFLARE_API_TOKEN,
    env.CLOUDFLARE_ACCOUNT_ID,
    env.AUTH_PREFS_NAMESPACE_ID,
    "prefs:",
  );

  let sent = 0;
  let digest = 0;

  for (const key of keys) {
    const raw = await cfKvGetValue(
      env.CLOUDFLARE_API_TOKEN,
      env.CLOUDFLARE_ACCOUNT_ID,
      env.AUTH_PREFS_NAMESPACE_ID,
      key,
    ).catch(() => null);
    if (!raw) continue;

    let prefs: UserPrefs;
    try {
      prefs = JSON.parse(raw) as UserPrefs;
    } catch {
      continue;
    }

    const notif = prefs.notifications;
    if (!notif) continue;

    // Check category subscription.
    if (!notif.categories?.includes(category)) continue;

    // Check site subscription.
    if (siteSlug && notif.sites?.length && !notif.sites.includes(siteSlug)) continue;

    // The KV key is `prefs:<sub>`.
    const sub = key.slice("prefs:".length);

    if (notif.frequency === "daily") {
      // Increment digest counter (flushed by scheduled Lambda).
      const digestKey = `digest:pending:${sub}`;
      const current = Number(
        (await cfKvGetValue(
          env.CLOUDFLARE_API_TOKEN,
          env.CLOUDFLARE_ACCOUNT_ID,
          env.AUTH_PREFS_NAMESPACE_ID,
          digestKey,
        ).catch(() => null)) ?? "0",
      );
      await cfKvPutValue(
        env.CLOUDFLARE_API_TOKEN,
        env.CLOUDFLARE_ACCOUNT_ID,
        env.AUTH_PREFS_NAMESPACE_ID,
        digestKey,
        String(current + 1),
      ).catch((e: unknown) => console.error("digest increment failed", sub, e));
      digest++;
      continue;
    }

    // Immediate dispatch. The user's email lives in Cognito, not in KV — the prefs
    // record doesn't store it. We skip users whose prefs don't have email_verified
    // as a light guard; the from-address bounce handling covers the rest.
    if (!notif.email_verified) continue;

    // The subscriber's email lives in Cognito, not in KV. Until AdminGetUser is
    // wired here, log and skip without counting as sent (#938 follow-up).
    console.log(`TODO: send immediate email to sub=${sub} category=${category}`);
  }

  console.log(`Dispatched: ${sent} immediate, ${digest} queued for digest`);
  return { statusCode: 200, body: JSON.stringify({ sent, digest }) };
};
