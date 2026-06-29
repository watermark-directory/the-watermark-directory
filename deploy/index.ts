import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as cloudflare from "@pulumi/cloudflare";

// ---------------------------------------------------------------------------
// Deployment infrastructure for the BOSC site (Epic #56 / submissions #240)
// ---------------------------------------------------------------------------
// A dedicated Pulumi stack, separate from the GitHub repo-config stack
// (../.github/config): different providers + credentials, lifecycle, blast radius.
//
// It owns the deploy-independent resources the public submissions endpoint (#74)
// depends on, plus — when a custom domain is set — the AWS↔Cloudflare exchange that
// puts the Pages site on a Route53-hosted name:
//
//   • Workers KV namespace      — per-IP rate limiter store (Phase 5).
//   • Turnstile widget          — guards the public form.
//   • Pages custom domain       — attaches `siteDomain` to the wrangler-deployed
//                                 `bosc` Pages project (the Cloudflare side).
//   • Route53 CNAME             — points `siteDomain` at `<project>.pages.dev`
//                                 (the AWS side); Cloudflare validates via it and
//                                 issues the edge cert.
//
// Deliberately NOT here: the **Pages project** itself. It is wrangler-deployed
// (../.github/workflows/pages.yml) with its env/bindings in ../web/wrangler.toml;
// managing that config in both Pulumi and wrangler would fight on every deploy. Pulumi
// owns the stable resources its config references; PagesDomain only *attaches* to the
// existing project by name, so the two don't drift.
//
// State + auth (see README):
//   • Backend  — self-managed **S3** (`pulumi login s3://…`); secrets via **awskms**.
//   • Cloudflare — default provider reads `CLOUDFLARE_API_TOKEN` (KV + Turnstile +
//     Pages-domain edit).
//   • AWS — standard credential chain (env / OIDC role); only used when `siteDomain`
//     + `route53ZoneId` are set, so the KV/Turnstile-only path needs no AWS creds.

const config = new pulumi.Config();

// Cloudflare account that owns the resources (required — set out of band):
//   pulumi config set bosc-deploy:cloudflareAccountId <account-id>
const accountId = config.require("cloudflareAccountId");

// The wrangler-deployed Pages project a custom domain attaches to.
const pagesProject = config.get("pagesProject") ?? "bosc";

// The custom subdomain for the live site, e.g. "bosc.example.org" — LATE-BOUND.
// Until it's set, the stack manages only KV + Turnstile and the site stays on
// <project>.pages.dev. Decided shape (#240): a **subdomain CNAME** in Route53, because
// a bare apex can't point cross-provider at pages.dev (CNAME illegal at apex; a Route53
// ALIAS only targets AWS resources). Set it when the name is chosen:
//   pulumi config set bosc-deploy:siteDomain bosc.example.org
const siteDomain = config.get("siteDomain");

// The Route53 hosted-zone id that owns `siteDomain` (required to manage the CNAME here;
// omit to attach the Pages domain but create the DNS record by hand):
//   pulumi config set bosc-deploy:route53ZoneId Z0123456789ABCDEFGHIJ
const route53ZoneId = config.get("route53ZoneId");

// Domains the Turnstile widget may be served on. The custom domain is folded in
// automatically; bosc.pages.dev is kept so preview deploys still validate.
const previewDomains = config.getObject<string[]>("siteDomains") ?? ["bosc.pages.dev"];
const turnstileDomains = Array.from(new Set([...(siteDomain ? [siteDomain] : []), ...previewDomains]));

// --- Deploy-independent Cloudflare resources -------------------------------

// Per-IP rate-limit store for the submissions Function (Phase 5). Bind its id as
// RATE_LIMIT in web/wrangler.toml to turn rate limiting on; until then it sits idle.
const rateLimitKv = new cloudflare.WorkersKvNamespace("submissions-ratelimit", {
    accountId,
    title: "bosc-submissions-ratelimit",
});

// Turnstile widget guarding the public form. `secret` is flagged sensitive by the
// provider, so it stays a Pulumi secret output.
const turnstile = new cloudflare.TurnstileWidget("submissions-turnstile", {
    accountId,
    name: "bosc-submissions",
    domains: turnstileDomains,
    mode: "managed",
});

// --- The custom-domain exchange (only when siteDomain is set) ---------------

// Cloudflare side: register the hostname with the Pages project. This tells Cloudflare
// to expect the domain and to issue a cert once the DNS validates.
const pagesDomain = siteDomain
    ? new cloudflare.PagesDomain("site-domain", {
          accountId,
          projectName: pagesProject,
          name: siteDomain,
      })
    : undefined;

// AWS side: the Route53 CNAME that points the subdomain at the Pages project. Created
// only when the zone id is also supplied; `dependsOn` so Cloudflare is expecting the
// domain before DNS resolves to it.
const route53Record =
    siteDomain && route53ZoneId
        ? new aws.route53.Record(
              "site-cname",
              {
                  zoneId: route53ZoneId,
                  name: siteDomain,
                  type: "CNAME",
                  ttl: 300,
                  records: [`${pagesProject}.pages.dev`],
              },
              { dependsOn: pagesDomain ? [pagesDomain] : [] },
          )
        : undefined;

// ---------------------------------------------------------------------------
// Outputs — wire these into the rest of the seam (see README + docs/submissions-api.md)
// ---------------------------------------------------------------------------
/** KV namespace id → `web/wrangler.toml` `[[kv_namespaces]]` `id` (RATE_LIMIT). */
export const rateLimitKvNamespaceId = rateLimitKv.id;
/** Public Turnstile site key → the `PUBLIC_TURNSTILE_SITE_KEY` build var. */
export const turnstileSiteKey = turnstile.sitekey;
/** Secret Turnstile key → the `TURNSTILE_SECRET_KEY` Function secret (a secret output). */
export const turnstileSecretKey = turnstile.secret;
/** The live site URL once the custom domain validates (else the pages.dev default). */
export const siteUrl = siteDomain ? `https://${siteDomain}` : `https://${pagesProject}.pages.dev`;
/** Cloudflare's validation status for the custom domain ("active" once the cert issues). */
export const siteDomainStatus = pagesDomain ? pagesDomain.status : pulumi.output("not-configured");
/** The Route53 record FQDN, when Pulumi manages the DNS side. */
export const route53RecordFqdn = route53Record ? route53Record.fqdn : pulumi.output("not-managed");
