import * as pulumi from "@pulumi/pulumi";
import * as cloudflare from "@pulumi/cloudflare";

// ---------------------------------------------------------------------------
// Cloudflare deployment infrastructure for the BOSC site (Epic #56)
// ---------------------------------------------------------------------------
// A dedicated Pulumi stack, separate from the GitHub repo-config stack
// (../.github/config): different provider + credentials (CLOUDFLARE_API_TOKEN vs a
// GitHub admin token), different lifecycle, different blast radius.
//
// Manages the two *underlying* Cloudflare resources the public submissions endpoint
// (#74) depends on: the Turnstile widget guarding the form, and the Workers KV namespace
// backing the per-IP rate limiter (Phase 5).
//
// Deliberately NOT here: the **Pages project** itself. It is wrangler-deployed
// (../.github/workflows/pages.yml) with its env/bindings in ../frontend/wrangler.toml;
// managing that config in both Pulumi and wrangler would fight on every deploy. Pulumi
// owns the stable, deploy-independent resources, and their ids/keys (the stack outputs
// below) are what the wrangler.toml binding + the Cloudflare env reference.
//
// Auth: the default Cloudflare provider reads `CLOUDFLARE_API_TOKEN` from the env (or the
// `cloudflare:apiToken` secret). The account is required config (see README).

const config = new pulumi.Config();

// Cloudflare account that owns the resources (required — set out of band):
//   pulumi config set bosc-deploy:cloudflareAccountId <account-id>
const accountId = config.require("cloudflareAccountId");

// Domains the Turnstile widget may be served on (the Pages domain). Committed default in
// Pulumi.prod.yaml; override with `pulumi config set --path siteDomains[0] <domain>`.
const siteDomains = config.getObject<string[]>("siteDomains") ?? ["bosc.pages.dev"];

// Per-IP rate-limit store for the submissions Function (Phase 5). Bind its id as
// RATE_LIMIT in frontend/wrangler.toml to turn rate limiting on; until then it sits idle.
const rateLimitKv = new cloudflare.WorkersKvNamespace("submissions-ratelimit", {
    accountId,
    title: "bosc-submissions-ratelimit",
});

// Turnstile widget guarding the public form. `secret` is flagged sensitive by the
// provider, so it stays a Pulumi secret output.
const turnstile = new cloudflare.TurnstileWidget("submissions-turnstile", {
    accountId,
    name: "bosc-submissions",
    domains: siteDomains,
    mode: "managed",
});

// ---------------------------------------------------------------------------
// Outputs — wire these into the rest of the seam (see README + docs/submissions-api.md)
// ---------------------------------------------------------------------------
/** KV namespace id → `frontend/wrangler.toml` `[[kv_namespaces]]` `id` (RATE_LIMIT). */
export const rateLimitKvNamespaceId = rateLimitKv.id;
/** Public Turnstile site key → the `PUBLIC_TURNSTILE_SITE_KEY` build var. */
export const turnstileSiteKey = turnstile.sitekey;
/** Secret Turnstile key → the `TURNSTILE_SECRET_KEY` Function secret (a secret output). */
export const turnstileSecretKey = turnstile.secret;
