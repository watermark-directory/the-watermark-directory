# CLAUDE.md — `bosc.site`

The static-site generator: stages a MkDocs source tree under `web/`, which `mkdocs
build` turns into `site/`. Defers to the root [`CLAUDE.md`](../../../CLAUDE.md).

- **`web/` and `site/` are git-ignored and fully regenerable — this package is the
  source of truth.** Never hand-edit the generated output; change the generator.
- `build.py` **wipes `web/`** then mirrors the curated `docs/` markdown + the whole
  `data/extracted/` tree at **repo-relative paths**, so existing cross-links resolve
  unchanged. Preserve that path mirroring when adding pages.
- Generated content is built **from committed corpus data** (`corpus`, `entities`,
  `timeline`, `people`, `candidates`, `exhibits`) — don't fabricate records or links.
- Exhibits are driven by [`data/site/exhibits.yaml`](../../../data/site/README.md)
  (page-range slices, never whole bundles). Static assets live in `assets/`
  (`extra.css`, `mermaid-init.js`).
- Deployment is **manual** (`workflow_dispatch`) — the site is an unlisted draft.
