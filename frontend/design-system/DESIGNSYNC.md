# DesignSync — Watermark Design System ↔ this repo

This directory is the in-repo **mirror** of the **Watermark Design System** Claude Design
project, and the `localDir` for two-way [DesignSync](https://claude.ai/design). The Claude
Design project is the **source of truth**; this mirror is what's version-controlled with the
code and what pushes/pulls go through.

| | |
|---|---|
| **Project** | Watermark Design System |
| **Project ID** | `dbe30a08-547c-442e-b4ac-81492fa5570f` |
| **localDir** | `frontend/design-system` |
| **Config** | [`designsync.json`](./designsync.json) — `synced` / `pending` / `generated` manifest |
| **Skill** | `/watermark-design` (`.claude/skills/watermark-design/`) routes agents here |

The design language (the doctrine) is in [`readme.md`](./readme.md) and [`SKILL.md`](./SKILL.md);
the tokens are in [`tokens/`](./tokens/) and [`styles.css`](./styles.css).

## Connector

Sync runs through the **claude_design** MCP connector (the `DesignSync` tool). It needs design
scopes on the claude.ai login. If a fresh session reports it's unauthorized, run **`/design-login`**
(grants `user:design:read` / `user:design:write`). Verify with `DesignSync list_projects` — the
Watermark project should appear.

## Pull (design → code)

When the design system changes upstream, bring the changes into the mirror:

1. `DesignSync { method: "list_files", projectId }` → diff the paths/structure against this dir.
2. For each **changed** path, `DesignSync { method: "get_file", projectId, path }` → write the
   content into `frontend/design-system/<path>`. (Only fetch what changed — `get_file` pulls
   content into context.)
3. Move any newly-mirrored paths from `pending` → `synced` in `designsync.json`.

## Push (code → design)

When you edit the design system **here** (tokens, a component, a card) and want it upstream:

1. Edit the file(s) under `frontend/design-system/`.
2. `DesignSync { method: "finalize_plan", projectId, writes: ["<paths…>"], localDir:
   "frontend/design-system" }` → returns a `planId`. (The user reviews the exact write list.)
3. `DesignSync { method: "write_files", projectId, planId, files: [{ path: "<project path>",
   localPath: "<path under localDir>" }] }` — contents are read from disk and **never enter model
   context**. Up to 256 files per call.

**Discipline (from the DesignSync tool + the `/design-sync` skill):** sync **incrementally, one
component at a time — never a wholesale replace.** New preview cards carry a first-line
`<!-- @dsCard group="…" -->` marker; the app compiles `_ds_manifest.json` from those (don't author
`_ds_*` by hand — they're in `generated`).

## Token reconciliation — the next pass (NOT done yet)

The live site (`frontend/src/styles/site.css`) currently re-declares the palette under `--bosc-*`
names with values identical to the design system's `--*` tokens. To make the design system actually
**drive** the site, the next pass will `@import "../../design-system/tokens/colors.css"` (etc.) into
`site.css` and redefine each `--bosc-*` as an alias of its DS token. The map:

| site.css (`--bosc-*`) | design-system token | notes |
|---|---|---|
| `--bosc-ink` | `--ink` | |
| `--bosc-muted` | `--ink-muted` | |
| `--bosc-faint` | `--ink-faint` | |
| `--bosc-chart-faint` | `--ink-ghost` | |
| `--bosc-forest`, `--bosc-link`, `--bosc-verified` | `--forest` (`--ev-verified-fg`) | the one signal |
| `--bosc-bg` | `--bone-surface` | |
| `--bosc-page` | `--bone-page` | |
| `--bosc-surface`, `--bosc-rail-bg` | `--bone-raised` | |
| `--bosc-rule` | `--line-hair` | the hairline |
| `--bosc-inference` | `--ev-inference-fg` | |
| `--bosc-open`, `--bosc-filename` | `--ev-open-fg` | |
| `--bosc-danger` | `--ev-gap-fg` | oxblood |
| `--bosc-sans` | `--font-sans` | |
| `--bosc-mono` | `--font-mono` | |
| **`--bosc-forest-dark` (`#155539`)** | — | **no DS token** — add `--forest-deep` upstream, or keep local |
| **`--bosc-ink-green` (`#3a4a3e`)** | — | **no DS token** (≈ `--ink-prose` `#3a4036`) — reconcile upstream or keep local |

That pass needs `npm run build` + a visual check, so it's deliberately separate from this setup.

## Scope status

- **Synced now:** the foundations — `tokens/*`, `styles.css`, `readme.md`, `SKILL.md`.
- **Pending (pull incrementally):** `components/**`, `ui_kits/**`, `guidelines/**`, `assets/brand/**`
  (brand binaries already live in `frontend/public/`). The Astro `.astro`/`.tsx` components in
  `frontend/src/components/` are the *implementations* of these `.jsx` specs — reconcile per
  component, not by file copy.
- **Never mirror:** `_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json` (`generated`).
