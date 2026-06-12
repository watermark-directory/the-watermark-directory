import * as pulumi from "@pulumi/pulumi";
import * as github from "@pulumi/github";
import { provisionCloudflare, type CloudflareOutputs } from "./cloudflare";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
// The GitHub *owner* and *token* are provider-level settings, supplied out of
// band: `github:owner` is committed in Pulumi.<stack>.yaml; the token comes from
// the GITHUB_TOKEN env var (or the `github:token` secret) and is never committed.
const config = new pulumi.Config();

// Repository this stack manages.
const repoName = config.get("repo") ?? "bosc";

// Branch-protection knobs, surfaced as stack config so the policy can be tuned
// without editing code. With the research GitHub App in play (Epic 5), `main`
// requires one approving review *and* a CODEOWNERS review, so the App — which is
// not a repo admin — cannot approve or merge its own research PRs. `enforceAdmins`
// stays false so the solo human maintainer (a repo admin, and a code owner) can
// still merge their own work; GitHub forbids approving one's own PR, and admin
// override is the escape hatch for that.
const requiredApprovals = config.getNumber("requiredApprovals") ?? 1;
const requireCodeOwnerReviews = config.getBoolean("requireCodeOwnerReviews") ?? true;
const enforceAdmins = config.getBoolean("enforceAdmins") ?? false;
const requireUpToDate = config.getBoolean("requireUpToDate") ?? true;

// Status-check contexts that must pass before `main` can be updated. "check" is
// the job id in .github/workflows/ci.yml, which is also its reported check name.
const requiredChecks = ["check"];

// ---------------------------------------------------------------------------
// Repository settings
// ---------------------------------------------------------------------------
// `bosc` already exists, so adopt it rather than recreate. One-time bootstrap,
// run before the first `pulumi up` (see README):
//
//   pulumi import github:index/repository:Repository bosc bosc
//
// The declared state below mirrors the live repo as of adoption (only the
// description is added); change a field here and `pulumi up` reconciles it.
// `protect` + `retainOnDelete` ensure Pulumi never deletes the GitHub repo.
const repo = new github.Repository(
    "bosc",
    {
        name: repoName,
        description:
            "Project BOSC — an agentic research platform for ingesting, " +
            "extracting, and analyzing public-records source documents.",
        visibility: "public",
        hasIssues: true,
        hasProjects: true,
        hasWiki: true,
        // Merge-button policy. Mirrors the repo's current settings; tighten as
        // desired (e.g. squash-only + deleteBranchOnMerge) and `pulumi up`.
        allowSquashMerge: true,
        allowMergeCommit: true,
        allowRebaseMerge: true,
        allowAutoMerge: false,
        deleteBranchOnMerge: false,
    },
    {
        protect: true,
        retainOnDelete: true,
    },
);

// ---------------------------------------------------------------------------
// Branch protection — the default branch
// ---------------------------------------------------------------------------
// A brand-new resource (the repo currently has no protection), so `pulumi up`
// creates it cleanly. Requires CI to pass and blocks force-push / deletion of
// `main`. Including the pull-request-reviews block requires changes to land via
// a PR even when zero approvals are required.
const mainProtection = new github.BranchProtection("main", {
    repositoryId: repo.nodeId,
    pattern: "main",
    enforceAdmins: enforceAdmins,
    requiredStatusChecks: [
        {
            strict: requireUpToDate,
            contexts: requiredChecks,
        },
    ],
    requiredPullRequestReviews: [
        {
            requiredApprovingReviewCount: requiredApprovals,
            dismissStaleReviews: true,
            requireCodeOwnerReviews: requireCodeOwnerReviews,
        },
    ],
    requireConversationResolution: true,
    allowsForcePushes: false,
    allowsDeletions: false,
});

// ---------------------------------------------------------------------------
// Runtime labels — the automation vocabulary (research App, Epic 5 + submissions
// seam, Epic 4)
// ---------------------------------------------------------------------------
// Everything the automation opens is tagged so proposed work is inert until a human
// triages it: a provenance marker (`agent-proposed` for the research App,
// `submission` for the public tips form) + `needs-triage` (not yet actioned) on each
// proposed issue, and `research-run` on a research run's PR. Declaring them here
// (rather than clicking in the UI) keeps the contract reproducible. Pulumi manages
// only these labels; pre-existing repo labels are untouched.
const runtimeLabels = [
    {
        name: "agent-proposed",
        color: "8957e5", // purple — ties to the `automation` label
        description: "Opened by the research agent (GitHub App); provenance marker.",
    },
    {
        name: "needs-triage",
        color: "fbca04", // yellow — needs a human's attention
        description: "Proposed (by the research agent or the public form) and inert until a maintainer triages it.",
    },
    {
        name: "research-run",
        color: "0e8a16", // green — marks a research-run PR
        description: "A PR (or issue) produced by a `bosc research run`.",
    },
    {
        name: "submission",
        color: "1d76db", // blue — a public tips/corrections submission (cf. agent-proposed)
        description: "Opened via the public submissions form (tip/correction); provenance marker.",
    },
];
for (const label of runtimeLabels) {
    new github.IssueLabel(label.name, {
        repository: repoName,
        name: label.name,
        color: label.color,
        description: label.description,
    });
}

// ---------------------------------------------------------------------------
// Cloudflare resources — the submissions seam (Epic #56), OPT-IN
// ---------------------------------------------------------------------------
// The submissions endpoint's Turnstile widget + rate-limit KV namespace, as code.
// Provisioned ONLY when `cloudflareAccountId` is set (and the provider has a
// CLOUDFLARE_API_TOKEN), so the GitHub-only `pulumi up` — and the repo-config workflow
// without a Cloudflare token — keep working untouched. The Pages *project* is
// deliberately not managed here (it's wrangler-deployed); see cloudflare.ts.
//   pulumi config set bosc-repo-config:cloudflareAccountId <account-id>
//   pulumi config set --path bosc-repo-config:siteDomains[0] bosc.pages.dev   # optional
const cloudflareAccountId = config.get("cloudflareAccountId");
const siteDomains = config.getObject<string[]>("siteDomains") ?? ["bosc.pages.dev"];

let cloudflareResources: CloudflareOutputs | undefined;
if (cloudflareAccountId) {
    cloudflareResources = provisionCloudflare({
        accountId: cloudflareAccountId,
        domains: siteDomains,
        widgetMode: "managed",
    });
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
export const repository = repo.fullName;
export const repositoryUrl = repo.htmlUrl;
export const protectedBranch = mainProtection.pattern;
export const runtimeLabelNames = runtimeLabels.map((l) => l.name);

// Cloudflare outputs (undefined until `cloudflareAccountId` is configured). The KV id
// goes into frontend/wrangler.toml; the Turnstile keys into the Cloudflare env / build
// (turnstileSecretKey is a secret — read with `pulumi stack output --show-secrets`).
export const rateLimitKvNamespaceId = cloudflareResources?.rateLimitKvNamespaceId;
export const turnstileSiteKey = cloudflareResources?.turnstileSiteKey;
export const turnstileSecretKey = cloudflareResources?.turnstileSecretKey;
