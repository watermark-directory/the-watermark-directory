# `sample-bundle/` — the committed, per-site offline fixtures

Each subdirectory is one network site's **trimmed content bundle** — the committed fixture the
Astro build reads offline (CI, zero-Python). The frontend resolves a site's bundle by registry
slug (`bundleFor(slug)` in `src/lib/bundle.ts`), so the fixtures are keyed the same way:

```
sample-bundle/
  lima/                 # the Lima reference site (WATERMARK_SITE default)
    manifest.json
    feeds/**
    README.md           # how this fixture is trimmed + refreshed
```

A new site adds its own `sample-bundle/<slug>/` (e.g. `fort-wayne/`, #741). The real,
full bundles are generated per-site by `watermark --site <slug> export` →
`data/site/bundles/<slug>/` (git-ignored) and take precedence over these fixtures when present.

See `lima/README.md` for how a fixture is trimmed from the real export and the drift guard
(`tests/test_site_bundle.py::test_frontend_sample_bundle_tracks_the_export_contract`).
