# The public document allowlist

`published-documents.yaml` is the **default-deny** gate that decides which source
documents the **public** site may serve (epic #274 / #280). It is the demand-side peer of
`exhibits.yaml`: where exhibits are a handful of curated downloads, this governs the whole
`/api/doc` byte path.

## The model: dev-full, public allowlist-gated

The object store (R2) holds the **entire** corpus, and in **dev / preview** the `/api/doc`
Function serves all of it so the viewer works on everything. On the **public** production
site, `/api/doc` serves a file **only** if this allowlist clears it. Nothing is public by
default. The same flag is carried on every `DocumentItem.published` in the content bundle,
so the catalog UI and the server-side gate always agree (both derive from this file).

## What's allowed

A rel is public if it matches **any** rule, or is a curated exhibit:

- **`collections:`** — whole `data/documents/<slug>` trees (matched on the first path
  segment).
- **`globs:`** — `fnmatch` patterns over the `data/documents` rel.
- **`documents:`** — exact rels.
- **Exhibits** (`exhibits.yaml`) are **auto-included** — they're already published
  downloads, so the existing links keep working without restating them here.

## The discipline (load-bearing)

Chain of custody holds: the source bytes are immutable and the store serves them
verbatim. The public gate is **not** byte redaction — it is *exposure control*. A rel is
added to this file **only after a completed
[document publication review](../../docs/legal/document-publication-review.md)** (#281)
has confirmed the document carries no material that shouldn't be republished (personal
PII, sealed/NDA'd content). **Every public entry must be traceable to that review** —
record the reviewer + date with the entry. Captured third-party web evidence may embed
secrets/tokens — that is *evidence*, not a leak to redact (see the root `CLAUDE.md`); the
allowlist, not deletion, is how such a document is kept off the public surface.

When in doubt, leave it out: omission is default-deny, and dev/preview still serve it.
