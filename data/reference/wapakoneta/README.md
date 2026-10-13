# Wapakoneta (wapakoneta) — reference data

Per-site onboarding tree for the Wapakoneta watershed point (basin: maumee), scaffolded by `watermark onboard wapakoneta` (#326). Values come from the portable onboard connectors keyed to this site's `SiteProfile` in `watermark.sites` — nothing here is fabricated; regenerate, don't hand-edit.

## Source

`watermark onboard wapakoneta` over the Wapakoneta `SiteProfile` — per-site authored reference inputs + per-jurisdiction connectors (site geometry, parcels/zoning).

## Known gaps & caveats

- Onboarding seed — **review every value against a cited source before promotion** (`web/packages/core/src/sites.ts` `status`/`selectable`, parity-gated).
- County/City parcel & zoning GIS is jurisdiction-specific and is **not** populated by the portable reach connectors — it needs a per-jurisdiction connector (see `docs/onboarding.md`).

## Regenerate

`watermark onboard wapakoneta`  (or the per-connector commands: `derive-low-flows`, `nasa-power --write`, etc.)
