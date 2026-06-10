import * as pulumi from "@pulumi/pulumi";
import * as github from "@pulumi/github";

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
// Runtime labels — the research GitHub App's vocabulary (Epic 5)
// ---------------------------------------------------------------------------
// The App tags everything it opens so proposed work is inert until a human
// triages it: `agent-proposed` (provenance) + `needs-triage` (not yet actioned)
// on each proposed issue, and `research-run` on the run's PR. Declaring them here
// (rather than clicking in the UI) keeps the App's contract reproducible. Pulumi
// manages only these labels; pre-existing repo labels are untouched.
const runtimeLabels = [
    {
        name: "agent-proposed",
        color: "8957e5", // purple — ties to the `automation` label
        description: "Opened by the research agent (GitHub App); provenance marker.",
    },
    {
        name: "needs-triage",
        color: "fbca04", // yellow — needs a human's attention
        description: "Agent-proposed and inert until a maintainer triages it.",
    },
    {
        name: "research-run",
        color: "0e8a16", // green — marks a research-run PR
        description: "A PR (or issue) produced by a `bosc research run`.",
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
// Outputs
// ---------------------------------------------------------------------------
export const repository = repo.fullName;
export const repositoryUrl = repo.htmlUrl;
export const protectedBranch = mainProtection.pattern;
export const runtimeLabelNames = runtimeLabels.map((l) => l.name);
