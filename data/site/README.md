# Site configuration

Committed configuration consumed by the site generator (`bosc.site`) when it stages
the browsable MkDocs tree. This is **input config**, not generated output — the
generated `web/` and `site/` trees are git-ignored and regenerable.

## Files

| File | What |
|---|---|
| `exhibits.yaml` | The curated **Exhibits** allowlist — which source PDFs (and page-range slices of large bundles) get published on the site. Edit here to add/remove an exhibit; page-range slices mean a full bundle is never republished wholesale. |

See [`data/README.md`](../README.md) (Publishing) for the build/serve/deploy flow.
