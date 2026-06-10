# `.github/config` — repository configuration as code (Pulumi)

This Pulumi project manages the GitHub configuration of the **`bosc`** repository
declaratively: repository settings and branch protection for `main`. Change the
config by editing [`index.ts`](index.ts) and running `pulumi up` (locally or via
the [`repo-config` workflow](../workflows/repo-config.yml)) — not by clicking
around in the GitHub UI.

## What it manages

- **Repository settings** (`github.Repository` `"bosc"`) — description,
  visibility, features (issues / projects / wiki), and the merge-button policy.
  The resource is `protect`ed and `retainOnDelete`, so Pulumi will **never delete
  the repo**, even on `pulumi destroy` or if the resource is removed from the
  program.
- **Branch protection** (`github.BranchProtection` `"main"`) — requires the
  `check` CI job to pass, optionally requires the branch be up to date, blocks
  force-pushes and deletions, requires conversation resolution, and routes all
  changes through a pull request. Required approvals and admin-enforcement are
  tunable via stack config (defaults: 0 approvals, admins not enforced — suited
  to a solo maintainer).

## Stack config (`Pulumi.prod.yaml`, committed — no secrets)

| Key | Default | Meaning |
| --- | --- | --- |
| `github:owner` | `goedelsoup` | GitHub owner / org |
| `repo` | `bosc` | repository name |
| `requiredApprovals` | `0` | approving reviews required on `main` |
| `enforceAdmins` | `false` | also apply protection to admins |
| `requireUpToDate` | `true` | branch must be current before merge |

The GitHub **token** is never committed. Supply it via the `GITHUB_TOKEN`
environment variable — a PAT or GitHub App token with **Administration: write**
on the repo. (The default Actions `GITHUB_TOKEN` is *not* sufficient for branch
protection or repo settings.)

## Prerequisites

- Node.js LTS (managed by mise) — run `npm install` in this directory.
- The Pulumi CLI and a state backend: Pulumi Cloud (`PULUMI_ACCESS_TOKEN`) or a
  local file backend (`pulumi login --local`).

## Bootstrap (one-time)

The repository already exists, so adopt it into Pulumi state before the first
apply — otherwise Pulumi tries to *create* a repo named `bosc` and fails:

```bash
cd .github/config
npm install
pulumi stack init prod            # or: pulumi stack select prod
export GITHUB_TOKEN=...           # admin-scoped PAT / App token
pulumi import github:index/repository:Repository bosc bosc
pulumi preview                    # review: should show only the new BranchProtection
pulumi up
```

## Everyday use

```bash
cd .github/config
# edit index.ts ...
pulumi preview     # see the diff
pulumi up          # apply
```

## CI

[`../workflows/repo-config.yml`](../workflows/repo-config.yml) runs `pulumi
preview` on pull requests that touch this directory (commenting the plan on the
PR) and `pulumi up` when those changes land on `main`. It needs:

- **`PULUMI_ACCESS_TOKEN`** (secret) — Pulumi Cloud token for state.
- **`GH_ADMIN_TOKEN`** (secret) — PAT / App token with **Administration: write**
  (the provider token; the default `GITHUB_TOKEN` can't manage protection).
- **`PULUMI_STACK`** (Actions *variable*) — fully-qualified stack name, e.g.
  `your-pulumi-org/bosc-repo-config/prod`.
