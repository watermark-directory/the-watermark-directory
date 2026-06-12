# `deploy/` — Cloudflare deployment infrastructure (Pulumi)

A dedicated Pulumi stack for the BOSC site's **Cloudflare** resources — kept separate
from the GitHub repo-config stack ([`.github/config`](../.github/config)) because they
have different providers and credentials (a Cloudflare API token vs a GitHub admin
token), different lifecycles, and a different blast radius. Change the config by editing
[`index.ts`](index.ts) and running `pulumi up` (locally or via the
[`deploy-infra` workflow](../.github/workflows/deploy-infra.yml)).

## What it manages

The two **underlying** Cloudflare resources the public submissions endpoint
([#74](https://github.com/goedelsoup/bosc/issues/74), see
[`docs/submissions-api.md`](../docs/submissions-api.md)) depends on:

- **`cloudflare.WorkersKvNamespace`** — the KV namespace backing the per-IP rate limiter
  (Phase 5). Bind its id as `RATE_LIMIT` in `frontend/wrangler.toml` to turn rate
  limiting on.
- **`cloudflare.TurnstileWidget`** — the Turnstile widget guarding the form. Exports the
  public site key and the (sensitive) secret key.

**Not** managed here: the **Pages project** itself. It is wrangler-deployed
([`pages.yml`](../.github/workflows/pages.yml)) with its env/bindings in
[`frontend/wrangler.toml`](../frontend/wrangler.toml); managing that config in both Pulumi
and wrangler would drift on every deploy. Pulumi owns the deploy-independent resources its
config references.

## Outputs → where they go

`pulumi up` exports the values the rest of the seam wires in:

| Output | Wire it into |
| --- | --- |
| `rateLimitKvNamespaceId` | `frontend/wrangler.toml` → `[[kv_namespaces]]` `id` (RATE_LIMIT) |
| `turnstileSiteKey` | the `PUBLIC_TURNSTILE_SITE_KEY` build var |
| `turnstileSecretKey` | the `TURNSTILE_SECRET_KEY` Function secret (`pulumi stack output turnstileSecretKey --show-secrets`) |

## Stack config (`Pulumi.prod.yaml`, committed — no secrets)

| Key | Default | Meaning |
| --- | --- | --- |
| `cloudflareAccountId` | *(required, unset)* | Cloudflare account that owns the resources |
| `siteDomains` | `["bosc.pages.dev"]` | domains the Turnstile widget may serve on |

The Cloudflare **token** is never committed. Supply it via the `CLOUDFLARE_API_TOKEN`
env var (or the `cloudflare:apiToken` Pulumi secret) — scoped to **Workers KV Storage:
Edit** + **Turnstile: Edit**.

## Prerequisites

- Node.js LTS (managed by mise) — run `npm install` in this directory.
- The Pulumi CLI and a state backend: Pulumi Cloud (`PULUMI_ACCESS_TOKEN`) or a local
  file backend (`pulumi login --local`).

## Bootstrap (one-time)

```bash
cd deploy
npm install
pulumi stack init prod                         # or: pulumi stack select prod
pulumi config set bosc-deploy:cloudflareAccountId <account-id>
export CLOUDFLARE_API_TOKEN=...                # KV + Turnstile edit scope
pulumi preview                                 # the KV namespace + Turnstile widget
pulumi up
pulumi stack output                            # read the ids/keys to wire in
pulumi stack output turnstileSecretKey --show-secrets
```

## CI

[`../.github/workflows/deploy-infra.yml`](../.github/workflows/deploy-infra.yml) runs
`pulumi preview` on PRs that touch this directory (commenting the plan) and `pulumi up`
on `main`. It needs:

- **`PULUMI_ACCESS_TOKEN`** (secret) — Pulumi Cloud token for state.
- **`CLOUDFLARE_API_TOKEN`** (secret) — the provider token (KV + Turnstile edit).
- **`DEPLOY_PULUMI_STACK`** (Actions *variable*) — fully-qualified stack name, e.g.
  `your-pulumi-org/bosc-deploy/prod`.

`DEPLOY_PULUMI_STACK` doubles as the on-switch: the job is gated on it, so until it's set
the workflow is **skipped** (not failed) on PRs that touch this directory. Set the
variable and the two secrets together to activate it.
