// POST /api/attach — pre-upload endpoint for submission file attachments (#243).
// A submitter uploads a file here before calling /api/submit; the returned key is
// included in the submission payload as attachment_keys[]. The key is referenced (not
// embedded) from the triage GitHub issue. See docs/submissions-api.md.
//
// Flow: kill switch → rate limit → parse multipart → validate MIME + size → R2 put → { key }
//
// Abuse model:
//   - Declared Content-Type must be in the allowlist.
//   - Magic-byte sniffing: if the file has a recognizable signature, it must match the
//     declared type. text/plain has no magic bytes and is trusted as declared.
//   - Files are stored with Content-Disposition: attachment and the declared (allowlisted)
//     Content-Type, so they are never executed as HTML/script by a browser.
//   - The key embeds a UUID — capability-based access; no serving endpoint (maintainer
//     retrieves via `wrangler r2 object get SUBMISSION_ATTACHMENTS <key>`).

import { intEnv } from "./_lib/env";
import { json, requireEnabled } from "./_lib/http";
import { DEFAULT_RATE_LIMIT, enforceRateLimit, type KVLike } from "./_lib/ratelimit";
import {
  ATTACH_MAX_BYTES,
  ATTACH_MIME_ALLOWLIST,
  type R2Like,
  attachmentKey,
  detectMime,
  sanitizeFilename,
} from "./_lib/attachments";

interface Env {
  /** Shared kill switch with /api/submit. */
  SUBMISSIONS_ENABLED?: string;
  /** R2 bucket for attachment storage. Absent ⇒ 503. */
  SUBMISSION_ATTACHMENTS?: R2Like;
  /** Per-file size cap in bytes; defaults to ATTACH_MAX_BYTES (10 MB). */
  ATTACH_MAX_BYTES?: string;
  /** Shared rate-limit KV from /api/submit (optional). */
  RATE_LIMIT?: KVLike;
  RATE_LIMIT_MAX?: string;
  RATE_LIMIT_WINDOW_SEC?: string;
}

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

  if (!env.SUBMISSION_ATTACHMENTS) {
    return json(503, { error: "attachment storage is not configured" });
  }

  const remoteip = request.headers.get("CF-Connecting-IP") ?? undefined;
  if (env.RATE_LIMIT && remoteip) {
    const blocked = await enforceRateLimit(
      env.RATE_LIMIT,
      `attach:${remoteip}`,
      Math.floor(Date.now() / 1000),
      {
        max: intEnv(env.RATE_LIMIT_MAX, DEFAULT_RATE_LIMIT.max),
        windowSec: Math.max(60, intEnv(env.RATE_LIMIT_WINDOW_SEC, DEFAULT_RATE_LIMIT.windowSec)),
      },
      "too many uploads — please try again later",
    );
    if (blocked) return blocked;
  }

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return json(400, { error: "expected multipart/form-data with a 'file' field" });
  }

  const entry = formData.get("file");
  if (!entry || typeof entry === "string") {
    return json(400, { error: "missing file field" });
  }
  const file = entry as File;

  const maxBytes = intEnv(env.ATTACH_MAX_BYTES, ATTACH_MAX_BYTES);
  if (file.size === 0) return json(400, { error: "file is empty" });
  if (file.size > maxBytes) {
    return json(413, { error: `file exceeds ${Math.round(maxBytes / 1024 / 1024)} MB limit` });
  }

  // Content-type check: declared type must be in the allowlist.
  const declaredType = (file.type || "application/octet-stream").split(";")[0].trim().toLowerCase();
  if (!ATTACH_MIME_ALLOWLIST.includes(declaredType as (typeof ATTACH_MIME_ALLOWLIST)[number])) {
    return json(415, { error: "file type not allowed" });
  }

  // Magic-byte check: if the content has a recognizable signature, it must agree with
  // the declared type. text/plain has no magic bytes and is trusted as-declared.
  const bytes = new Uint8Array(await file.arrayBuffer());
  const detected = detectMime(bytes);
  if (detected !== null && detected !== declaredType) {
    return json(415, { error: "file content does not match declared type" });
  }

  const uuid = crypto.randomUUID();
  const isoDate = new Date().toISOString().slice(0, 10);
  const filename = file.name ? sanitizeFilename(file.name) : "attachment";
  const key = attachmentKey(isoDate, uuid, filename);

  try {
    await env.SUBMISSION_ATTACHMENTS.put(key, bytes.buffer as ArrayBuffer, {
      httpMetadata: {
        contentType: declaredType,
        contentDisposition: `attachment; filename="${filename}"`,
      },
    });
  } catch (e) {
    console.error("attach: R2 put failed", e);
    return json(502, { error: "failed to store attachment — please try again" });
  }

  return json(201, { key });
};
