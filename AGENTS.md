# AGENTS.md

Orientation for automated agents working in this repo. For project architecture,
read [CLAUDE.md](CLAUDE.md). This file is the execution contract — the conventions
and sharp edges for agentic runs (research and task-execution alike).

## Gate before declaring done

```bash
mise run check
```

This runs ruff lint + format check + mypy strict + pytest. A change is not done
until `check` is green. For changes that touch `frontend/`, also run
`mise run //frontend:check`.

## Checkout

Always use `lfs: false` when checking out this repo. `data/documents/` contains
~5.4 GB of Git LFS source documents — smudging them fills the disk and is
unnecessary for almost all automated work.

## Environment

```bash
uv sync --extra dev    # install all deps including dev extras
uv run bosc ...        # all CLI commands go through uv run
```

Python 3.11. Settings are read via `watermark.config.get_settings()` — never read
`os.environ` directly. All settings are `WATERMARK_`-prefixed.

## Data discipline (important)

- `data/documents/**` is **immutable evidence** — never modify, rename, or delete
  any file here. The research workflow has a hard chain-of-custody check that aborts
  if any source byte is touched.
- `data/extracted/**` is the reviewed artifact. Changes require a cited source.
- `data/reference/**` is committed authoritative external data. Changes must be
  regenerable from a documented connector.
- `data/research/**` is the output directory for `bosc research run` — commit the
  whole directory as produced.

## Research tasks

Research runs write to `data/research/<slug>/`. Commit the output directory:

```bash
git add data/research/
git commit -m "research: <topic>"
```

The `findings.md` and `manifest.yaml` inside are the reviewable artifacts.

## Custom PR description

The Orlop agent harness sets `$AGENT_PR_BODY_FILE` to a temp file path. Write a
markdown PR body there before the process exits and the harness will use it as the
PR description. If the file is absent or empty, the harness generates a default body
from the issue title and body.

## Stuck / blocked

Exit with a non-zero status code. The harness catches it, adds `agent:needs-human`
to the issue, and stops — a human will review and unblock. Never silently swallow
errors that prevent the task from being completed correctly.

## Site axis

The network hosts multiple watershed-point sites. Per-site values live on
`SiteProfile` in `watermark.sites` — never hard-code a Lima/Allen-County value.
Select a site with `--site <slug>` or `WATERMARK_SITE=<slug>`. The default site
is `lima`.
