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

## Token reconciliation

### Colors — done (the design system drives the palette)

`site.css` `@import`s `tokens/colors.css` and aliases each `--bosc-*` color to its design-system
token, so a color edit pulled via DesignSync now propagates to the live site. Values were
identical → **zero visual change**. The map:

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
| **`--bosc-forest-dark` (`#155539`)** | — | **no DS token** — add `--forest-deep` upstream, or keep local |
| **`--bosc-ink-green` (`#3a4a3e`)** | — | **no DS token** (≈ `--ink-prose` `#3a4036`) — reconcile upstream or keep local |

`--bosc-sans` / `--bosc-mono` stay **literal** — the site's font stacks carry extra fallbacks
(Roboto/Helvetica/Arial; SF Mono/Consolas) that `--font-sans` / `--font-mono` don't.

### Type & spacing — tokens available; the site has diverged

`site.css` also `@import`s `tokens/typography.css` + `tokens/spacing.css`, so the type/spacing token
layer (`--font-*`, `--fs-*`, `--lh-*`, `--ls-*`, `--sp-*`, `--pad-*`, `--bw-*`, `--ease`, `--dur`,
`--lift`, `--ring-focus`, …) is **available** to adopt. Two exact-match doctrinal values now come
from the DS (zero change): the focus ring → `var(--ring-focus)`, the hover lift → `var(--lift)`.

The rest is **not** auto-applied — the production sheet has **diverged** from the DS scale, so each
row below is a reconciliation **decision** (align the site to the DS, *or* update the DS to the
as-built values — possibly the first DesignSync push):

| area | site (as-built) | design-system | the decision |
|---|---|---|---|
| transitions | `0.12s ease` (≈40 rules) | `--dur 0.15s` + `--ease cubic-bezier(.4,0,.2,1)` | adopt DS timing, or set the DS to `0.12s ease` |
| active-tab underline | `inset 0 -3px 0 var(--bosc-bg)` (bone) | `--underline-active: inset 0 -3px 0 currentColor` | the site colors it bone, not `currentColor` |
| type scale | arbitrary `rem`/`px` (`0.78rem`, `10.5px`, `11px`, …) | `--fs-*` (52/40/36/24/20/18/16/14/13/12/11/10) | adopt `--fs-*` (visual changes — needs review) |
| spacing scale | inline `rem`/`px` paddings/gaps | `--sp-*` (4px) + `--pad-*` / `--gap-*` | adopt `--sp-*` (visual changes — needs review) |
| fonts | richer fallback stacks | fewer fallbacks | push the richer stacks to the DS, then alias |

Adopting the scales is a **visual-change refactor** (the as-built values aren't on the DS scale), so
it needs `npm run build` + a visual pass — out of scope for token availability.

## Scope status

- **Synced now:** the foundations — `tokens/*`, `styles.css`, `readme.md`, `SKILL.md`.
- **Colors:** the design system **drives** the live palette (done). **Type + spacing tokens are
  imported/available**; adopting the scales (+ the divergences above) is a pending, visual-review
  decision.
- **Pending (pull incrementally):** `components/**`, `ui_kits/**`, `guidelines/**`, `assets/brand/**`
  (brand binaries already live in `frontend/public/`). The Astro `.astro`/`.tsx` components in
  `frontend/src/components/` are the *implementations* of these `.jsx` specs — reconcile per
  component, not by file copy.
- **Never mirror:** `_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json` (`generated`).
