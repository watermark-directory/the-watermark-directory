# Ashville · Pickaway (ashville) — subdivision meeting-records registry

Per-site registry of Ashville · Pickaway's meeting-holding bodies (townships, municipalities, meeting-holding special districts) and **where each publishes its minutes/agendas online**. Scaffolded empty by `watermark onboard ashville` (#1524); read per active site by `watermark.civic` (`registry_path`). This peer slug-scopes under `subdivisions/ashville/`; Lima (the reference build) keeps the flat legacy path.

## Source

Hand-curated, not connector-generated. **Grounded** fields (`name`/`type`/`governing_body`/`meeting_schedule`/`office`) are transcribed **verbatim** from a committed Ashville · Pickaway-area county-published roster named in `meta.grounded_sources` (`grounded_from` per body) — never from outside knowledge. **Discovered** fields (`publishing.*`) are a live-web finding with their own `publishing.discovered:` provenance, folded in BY HAND from `watermark --site ashville subdivisions discover` (read-only; it never rewrites this file).

## Known gaps & caveats

- **Scaffolded empty** — enumerate the county's bodies before promotion. An empty registry is honest, never a finding of "publishes nothing."
- `publishing.platform: unknown` = *not yet looked*, never *publishes nothing*; a null `records_url` is never evidence of withholding.
- An empty/seeded registry does **not** flip the `record` readiness domain live (#1220) — it rises only when meetings are actually ingested and summarized.

## Populate

Enumerate bodies by hand from a committed roster, then `watermark --site ashville subdivisions discover` and fold the confirmed platforms in. See `docs/onboarding.md` and `src/watermark/civic/CLAUDE.md`.
