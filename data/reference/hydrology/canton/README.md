# Canton · Stark (canton) — hydrology connector outputs

Per-site onboarding tree for the Canton · Stark watershed point (basin: muskingum), scaffolded by `watermark onboard canton` (#326). Values come from the portable onboard connectors keyed to this site's `SiteProfile` in `watermark.sites` — nothing here is fabricated; regenerate, don't hand-edit.

## Source

`watermark onboard canton` over the Canton · Stark `SiteProfile` — USGS NWIS (7Q10) · NOAA Atlas-14 (corridor DDF) · USDA NRCS SSURGO (dominant HSG) · NASA-POWER (climatology).

## Known gaps & caveats

- Onboarding seed — **review every value against a cited source before promotion** (`web/packages/core/src/sites.ts` `status`/`selectable`, parity-gated).
- County/City parcel & zoning GIS is jurisdiction-specific and is **not** populated by the portable reach connectors — it needs a per-jurisdiction connector (see `docs/onboarding.md`).

## Regenerate

`watermark onboard canton`  (or the per-connector commands: `derive-low-flows`, `nasa-power --write`, etc.)
