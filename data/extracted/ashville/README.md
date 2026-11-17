# Ashville · Pickaway (ashville) — extractions

Per-site onboarding tree for the Ashville · Pickaway watershed point (basin: scioto), scaffolded by `watermark onboard ashville` (#326). Values come from the portable onboard connectors keyed to this site's `SiteProfile` in `watermark.sites` — nothing here is fabricated; regenerate, don't hand-edit.

## Source

`watermark onboard ashville` over the Ashville · Pickaway `SiteProfile` — the ingest→extract corpus pipeline over this site's source documents.

## Known gaps & caveats

- Onboarding seed — **review every value against a cited source before promotion** (`web/packages/core/src/sites.ts` `status`/`selectable`, parity-gated).
- County/City parcel & zoning GIS is jurisdiction-specific and is **not** populated by the portable reach connectors — it needs a per-jurisdiction connector (see `docs/onboarding.md`).

## Regenerate

`watermark onboard ashville`  (or the per-connector commands: `derive-low-flows`, `nasa-power --write`, etc.)
