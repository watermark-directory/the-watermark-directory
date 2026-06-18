# Document publication review — the pre-publication checklist

The gate that keeps the public document surface **default-deny honest** (epic #274 / C2).
The object store holds the entire corpus, and dev/preview serve all of it — but a source
document becomes **public** only after this review passes and its rel is added to
[`published-documents.yaml`](../../data/site/published-documents.yaml). Default-deny: when
in doubt, leave it out.

This is **exposure control, not redaction.** Source bytes are immutable
chain-of-custody evidence — this review never mutates a source file. A document that
can't be published as-is simply stays off the allowlist (or a clearly-labeled redacted
*derivative* is published as a separate exhibit, never overwriting the original).

## Scope

Run the review **per collection or glob** before adding it to the allowlist. A collection
is only as publishable as its least-publishable member, so a sweep that turns up a single
gating document means the collection is added by narrower rule (specific rels / a tighter
glob), not wholesale.

## The checklist

For each document (or a representative sweep of the collection):

### 1. Personal PII sweep

- [ ] No government identifiers — SSNs, driver's license, passport, tax IDs.
- [ ] No financial account numbers (bank/routing, full card numbers).
- [ ] No personal contact info for private individuals — home addresses, personal
      phone/email (officials acting in their official capacity are public).
- [ ] No wet-ink **signatures** of private individuals (an official's signature on a
      public instrument is public record; a private party's may not be).
- [ ] Nothing concerning **minors**.
- [ ] No health/medical information.

### 2. Provenance & status

- [ ] The bytes are genuinely **public record** — not a custodian copy held under an NDA
      or protective order. (The corpus contains the Bistrozzi ↔ County mutual NDA; a
      document obtained *subject to* such an instrument is **not** publishable here even
      though it's in the evidence corpus.)
- [ ] Not under seal, protective order, or an active confidentiality designation.
- [ ] Captured third-party web evidence may legitimately embed tokens/secrets — that is
      **evidence, not a leak to redact** (see the root `CLAUDE.md`). It does **not** gate
      publication; only *personal PII* and *legal status* (above) do.

### 3. Disposition

- [ ] **Publish** — add the rel/glob to `published-documents.yaml` with the reviewer note
      below.
- [ ] **Hold** — leave off the allowlist (default-deny; still dev/preview-viewable).
- [ ] **Redacted derivative** — if there's public value, publish a clearly-labeled
      redacted *copy* as a separate exhibit; never overwrite the source byte.

## Recording the review

Record the outcome alongside the allowlist entry so every public document is traceable to
a completed review:

```yaml
# in published-documents.yaml
documents:
  - rel: recorder/bistrozzi-deeds/202508130008300.pdf
    review: { by: "<reviewer>", date: 2026-06-17, result: publish }
```

> The C1 allowlist loader accepts a bare list of rels today; the per-entry `review`
> metadata above is the record-keeping convention this checklist requires. Keep the
> reviewer + date so a public entry is never anonymous.

## See also

- [`published-documents.yaml`](../../data/site/published-documents.yaml) — the allowlist
  this review gates, and its
  [README](../../data/site/published-documents.README.md).
- [`corpus-completeness-audit.md`](../../data/extracted/legal/corpus-completeness-audit.md)
  — the standing audit of what the corpus contains and what's missing.
- The root `CLAUDE.md` "Data discipline" section — chain of custody and the
  "evidence, not a leak to redact" rule.
