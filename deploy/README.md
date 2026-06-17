# `deploy/` — site deployment infrastructure (Pulumi)

A dedicated Pulumi stack for the BOSC site's deployment resources — kept separate from the
GitHub repo-config stack ([`.github/config`](../.github/config)) because they have
different providers and credentials, lifecycles, and blast radius. Change the config by
editing [`index.ts`](index.ts) and running `pulumi up` (locally or via the
[`deploy-infra` workflow](../.github/workflows/deploy-infra.yml)).

Two providers: **Cloudflare** (the KV namespace + Turnstile widget + the Pages
custom-domain attach) and **AWS** (the Route53 record — only when a custom domain is set).

## What it manages

The underlying resources the public submissions endpoint
([#74](https://github.com/goedelsoup/bosc/issues/74) / epic
[#240](https://github.com/goedelsoup/bosc/issues/240), see
[`docs/submissions-api.md`](../docs/submissions-api.md)) depends on:

- **`cloudflare.WorkersKvNamespace`** — the KV namespace backing the per-IP rate limiter
  (Phase 5). Bind its id as `RATE_LIMIT` in `frontend/wrangler.toml` to turn rate
  limiting on.
- **`cloudflare.TurnstileWidget`** — the Turnstile widget guarding the form. Exports the
  public site key and the (sensitive) secret key. Serves on the custom domain + the
  pages.dev preview.

When `siteDomain` is set (the late-bound custom subdomain), it also owns the
**Route53↔Cloudflare exchange** that puts the Pages site on the Route53-hosted name:

- **`cloudflare.PagesDomain`** — attaches `siteDomain` to the `bosc` Pages project (the
  Cloudflare side: "expect this hostname, issue a cert once DNS validates").
- **`aws.route53.Record`** — a CNAME `siteDomain` → `bosc.pages.dev` (the AWS side).
  Decided shape ([#240](https://github.com/goedelsoup/bosc/issues/240)): a **subdomain**,
  because a bare apex can't point cross-provider at pages.dev (a CNAME is illegal at the
  apex, and a Route53 ALIAS only targets AWS resources). For an apex you'd move DNS to
  Cloudflare or add a redirect — neither is wired here.

**Not** managed here: the **Pages project** itself. It is wrangler-deployed
([`pages.yml`](../.github/workflows/pages.yml)) with its env/bindings in
[`frontend/wrangler.toml`](../frontend/wrangler.toml); managing that config in both Pulumi
and wrangler would drift on every deploy. `PagesDomain` only *attaches* to the existing
project by name, so the two don't fight.

> **CAA note:** if the Route53 zone carries `CAA` records, they must permit Cloudflare's
> CA (currently Google Trust Services / Let's Encrypt) or the edge cert won't issue.

## Outputs → where they go

`pulumi up` exports the values the rest of the seam wires in:

| Output | Wire it into |
| --- | --- |
| `rateLimitKvNamespaceId` | `frontend/wrangler.toml` → `[[kv_namespaces]]` `id` (RATE_LIMIT) |
| `turnstileSiteKey` | the `PUBLIC_TURNSTILE_SITE_KEY` **build** repo variable (public) |
| `turnstileSecretKey` | the `TURNSTILE_SECRET_KEY` Function secret (`pulumi stack output turnstileSecretKey --show-secrets`) |
| `siteUrl` | the `PAGES_SITE_URL` repo variable for the build |
| `siteDomainStatus` | watch for `active` — Cloudflare validated the domain + issued the cert |
| `route53RecordFqdn` | sanity-check the managed DNS record |

## Stack config (`Pulumi.prod.yaml`, committed — no secrets)

| Key | Default | Meaning |
| --- | --- | --- |
| `cloudflareAccountId` | *(required, unset)* | Cloudflare account that owns the resources |
| `pagesProject` | `bosc` | the wrangler-deployed Pages project a custom domain attaches to |
| `siteDomain` | *(unset)* | the live subdomain, e.g. `bosc.example.org` — **late-bound** |
| `route53ZoneId` | *(unset)* | the Route53 hosted-zone id that owns `siteDomain` |
| `siteDomains` | `["bosc.pages.dev"]` | preview hostnames for Turnstile (custom domain folded in automatically) |

Until `siteDomain` is set the stack manages KV + Turnstile only and the site stays on
`bosc.pages.dev` — so it's **ready to go with the domain as the single late-bound value**.

Provider auth: the Cloudflare **token** is never committed — supply it via
`CLOUDFLARE_API_TOKEN` (or the `cloudflare:apiToken` Pulumi secret), scoped to **Workers
KV Storage: Edit** + **Turnstile: Edit** + **Pages: Edit** (the last for the domain
attach). AWS uses the standard credential chain (env / an OIDC role) and is only exercised
when `siteDomain` + `route53ZoneId` are set.

## Prerequisites

- Node.js LTS (managed by mise) — run `npm install` in this directory (installs
  `@pulumi/cloudflare` **and** `@pulumi/aws`).
- The Pulumi CLI + the **S3 state backend** in the project's AWS account
  (`pulumi login s3://<bucket>/bosc-deploy`); Pulumi locks within the bucket, so no
  DynamoDB table is needed. Secrets are encrypted with **awskms** (a small KMS key), not a
  shared passphrase. A local `pulumi login --local` still works for dry runs.

## Bootstrap (one-time)

```bash
# 0. Once per account: a state bucket + a KMS key for secret encryption.
aws s3api create-bucket --bucket <bucket> --region <region>
KMS_ARN=$(aws kms create-key --description bosc-pulumi-secrets --query KeyMetadata.Arn --output text)

cd deploy
npm install
pulumi login s3://<bucket>/bosc-deploy
pulumi stack init prod --secrets-provider "awskms://${KMS_ARN}"
pulumi config set bosc-deploy:cloudflareAccountId <account-id>
export CLOUDFLARE_API_TOKEN=...                # KV + Turnstile + Pages edit scope
pulumi preview                                 # KV + Turnstile (no domain yet)
pulumi up
pulumi stack output                            # read the ids/keys to wire in
pulumi stack output turnstileSecretKey --show-secrets

# Later, once the domain is chosen — the Route53↔Cloudflare exchange:
pulumi config set bosc-deploy:siteDomain   bosc.example.org
pulumi config set bosc-deploy:route53ZoneId Z0123456789ABC
pulumi up                                      # PagesDomain + the Route53 CNAME
pulumi stack output siteDomainStatus           # poll until "active"
```

## CI

[`../.github/workflows/deploy-infra.yml`](../.github/workflows/deploy-infra.yml) runs
`pulumi preview` on PRs that touch this directory (commenting the plan) and `pulumi up`
on `main`. It needs:

- **`CLOUDFLARE_API_TOKEN`** (secret) — the Cloudflare provider token (KV + Turnstile +
  Pages edit).
- **`DEPLOY_AWS_ROLE_ARN`** (variable) — an AWS IAM role assumed via **OIDC** (no static
  keys), with access to the S3 state bucket, the awskms key, and Route53 for the zone.
- **`PULUMI_BACKEND_URL`** (variable) — `s3://<bucket>/bosc-deploy`.
- **`DEPLOY_AWS_REGION`** (variable, optional) — defaults to `us-east-1`.
- **`DEPLOY_PULUMI_STACK`** (variable) — the S3-backend stack name, just `prod`.

`DEPLOY_PULUMI_STACK` doubles as the on-switch: the job is gated on it, so until it's set
the workflow is **skipped** (not failed) on PRs that touch this directory. Set it with the
AWS role + backend URL + the Cloudflare secret together to activate it.
