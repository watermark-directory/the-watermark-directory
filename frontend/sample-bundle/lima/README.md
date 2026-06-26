# `sample-bundle/` — committed content-bundle fixture

A **minimal, trimmed snapshot** of the real content bundle (`bosc export` →
`data/site/bundle/`), committed so `npm run build` and offline UI work need zero
Python or Git-LFS. The full bundle's `feeds/**` are git-ignored by design (they
churn and `documents` availability depends on local LFS) — this fixture is the
small, stable stand-in.

It carries a few authentic rows per feed (real shapes, not mocks) across every
section's feeds (records, timeline, entities, relationships, people, places,
meetings, exhibits, documents, hydrology-scenarios, concepts, rsei, geo). Schemas
are **not** duplicated here — the canonical `schemas/*.schema.json` live under
`data/site/bundle/`, and bundle schema validation is issue #62.

**Build against the real bundle instead** of this fixture:

```sh
bosc export                       # writes data/site/bundle/ (the loader prefers it)
# or point anywhere:
BOSC_BUNDLE_DIR=/path/to/bundle npm run build
```

**Refresh this fixture** after a contract change (run from the repo root):

```sh
bosc export --out /tmp/bundle
# then re-trim /tmp/bundle into this directory (a handful of rows per feed)
```
