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
// without editing code. Defaults suit a small / solo public repo.
const requiredApprovals = config.getNumber("requiredApprovals") ?? 0;
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
            requireCodeOwnerReviews: false,
        },
    ],
    requireConversationResolution: true,
    allowsForcePushes: false,
    allowsDeletions: false,
});

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
export const repository = repo.fullName;
export const repositoryUrl = repo.htmlUrl;
export const protectedBranch = mainProtection.pattern;
