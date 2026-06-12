import * as pulumi from "@pulumi/pulumi";
import * as cloudflare from "@pulumi/cloudflare";

// ---------------------------------------------------------------------------
// Cloudflare resources for the submissions seam (Epic #56)
// ---------------------------------------------------------------------------
// The two *underlying* Cloudflare resources the public submissions endpoint (#74)
// depends on, declared as code: the Turnstile widget that guards the form, and the
// Workers KV namespace that backs the per-IP rate limiter (Phase 5).
//
// Deliberately NOT here: the **Pages project** itself. It is wrangler-deployed
// (`.github/workflows/pages.yml`) and its env/bindings live in `frontend/wrangler.toml`;
// managing that config in both Pulumi and wrangler would fight on every deploy. Pulumi
// owns the stable, deploy-independent resources, and their ids/keys (the stack outputs
// below) are what the wrangler.toml binding + the Cloudflare env reference.
//
// Auth: the default Cloudflare provider reads `CLOUDFLARE_API_TOKEN` from the env. This
// module is only invoked when `cloudflareAccountId` is configured (see index.ts), so the
// GitHub-only stack never needs a Cloudflare token.

export interface CloudflareInputs {
  /** Cloudflare account that owns the resources. */
  accountId: string;
  /** Domains the Turnstile widget may be served on (e.g. the Pages domain). */
  domains: string[];
  /** Turnstile widget mode: "managed" | "non-interactive" | "invisible". */
  widgetMode: string;
}

export interface CloudflareOutputs {
  /** KV namespace id → `frontend/wrangler.toml` `[[kv_namespaces]]` `id` (RATE_LIMIT). */
  rateLimitKvNamespaceId: pulumi.Output<string>;
  /** Public Turnstile site key → the `PUBLIC_TURNSTILE_SITE_KEY` build var. */
  turnstileSiteKey: pulumi.Output<string>;
  /** Secret Turnstile key → the `TURNSTILE_SECRET_KEY` Function secret (sensitive). */
  turnstileSecretKey: pulumi.Output<string>;
}

export function provisionCloudflare(opts: CloudflareInputs): CloudflareOutputs {
  // Per-IP rate-limit store for the submissions Function (Phase 5). Bind its id as
  // RATE_LIMIT in wrangler.toml to turn rate limiting on; until then it sits unused.
  const rateLimitKv = new cloudflare.WorkersKvNamespace("submissions-ratelimit", {
    accountId: opts.accountId,
    title: "bosc-submissions-ratelimit",
  });

  // Turnstile widget guarding the public form. `secret` is flagged sensitive by the
  // provider, so it stays a Pulumi secret output.
  const widget = new cloudflare.TurnstileWidget("submissions-turnstile", {
    accountId: opts.accountId,
    name: "bosc-submissions",
    domains: opts.domains,
    mode: opts.widgetMode,
  });

  return {
    rateLimitKvNamespaceId: rateLimitKv.id,
    turnstileSiteKey: widget.sitekey,
    turnstileSecretKey: widget.secret,
  };
}
