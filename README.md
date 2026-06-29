# Watermark Directory

**An agentic research platform for investigating public infrastructure programs
through their paper trails.** It deconstructs degraded public-records documents —
scanned cost estimates, NPDES permits, meeting minutes, deed filings — into
reviewed, structured data, then runs Claude-driven analysis across the result.

The subject is a network of watershed-point sites in the Ohio River basin, each
paired to a specific data-center construction program and its documented impact
on water infrastructure. Lima, OH (American Sugar Creek, Allen County) is the
live reference build; 18 additional sites span the Maumee, Great Miami, Little
Miami, and Scioto basins.

The corpus is treated as **litigation evidence**. Nothing is guessed; nothing
is invented. Every number either reads off a scanned page or returns from an
official database. Uncertain scan transcriptions are marked `~` rather than
presented as exact. All claims carry `[verified]`, `[inference]`, `[reference]`,
or `[open]` tags throughout the extracted data.

---

## What it does

### Document pipeline

Three-stage pipeline in `src/watermark/pipeline/`:

```
ingest  →  extract  →  analyze
```

**`watermark ingest`** — walks `data/documents/`, inventories source files by
collection (`aedg/`, `oepa/`, `recorder/`, …), emits a manifest.

**`watermark extract <doc_id> --kind <kind> --pdf-page <N>`** — hybrid vision
read: OCR text layer (pypdf, hint only; its digits are unreliable on degraded
scans) + 300 DPI render (pypdfium2) → profile auto-detection from OCR text →
forced tool-use Claude call that reads figures off the *image* →
Pydantic-validated structured YAML written to `data/extracted/`. Supports
`--detail` for per-section line items (item number, description, quantity,
unit, rate, extended amount) that are immediately cross-checked against section
subtotals. A contractor-agnostic `Estimate` model with dynamic `sections`, `markups`,
construction subtotal, and total dispatches by document `--kind` and contractor
`--profile`; adding a new contractor is a `Profile` registration, not a model
change.

**`watermark reconcile`** — deterministic arithmetic check: section roll-ups,
markup rates, totals. Surfaces transcription errors and budgeting discrepancies
without any model call.

### Research agent

**`watermark research run`** runs a Claude Agent SDK loop over the extracted
corpus, backed by 18 in-process MCP tools that expose real committed data:

| Tool group | Tools |
|---|---|
| Corpus | `list_documents`, `list_extractions`, `read_extraction`, `retrieve_corpus` |
| Estimates | `reconcile_summary`, `reconcile_estimate`, `program_overview` |
| Record | `timeline`, `entities` |
| Hydrology | `hydrology_balance`, `stormwater_runoff`, `hydrology_scenario`, `storm_plan_inventory`, `sanitary_basis`, `tier1_swmm` |
| OEPA | `discover_oepa_permits`, `fetch_oepa_permit` |
| Research | `report_novel_finding` |

Tools resolve per the active `--site`; off the Lima reference build they serve
the active site's own corpus or return an honest "not yet available" notice
rather than silently falling through to Lima's data.

**`watermark research run --recipe site-onboard`** is a structured first-pass
that directs the agent across six coverage areas: NPDES/permit profile,
GIS/parcels, water-grid data, facility/RSEI toxics, economic ledger, and
hypothesis assessment. It discovers and fetches new OEPA DAM permit PDFs
automatically.

**`watermark research publish`** promotes agent findings to GitHub issues with
standardized labels (`kind/area/status` taxonomy).

### Hydrology and water balance

`src/watermark/hydrology/` runs water-balance and stormwater models of the
municipal loop. Connectors pull live public data:

| Source | What |
|---|---|
| USGS NWIS | Streamflow, 7Q10 low-flow |
| NOAA Atlas-14 | Rainfall frequency (DDF curves) |
| EPA ECHO | NPDES permit inventory, DMRs |
| NASA POWER | Surface met data for ET calculation |
| EIA-861 | Utility service territory and sales |
| PJM | LMP, interchange, generation |

All connectors use an on-disk cache with TTL and committed-fixture fallback,
so `mise run test` never hits the network.

### Reference datasets

`data/reference/` holds authoritative external data that is committed,
regenerable, and documented with source and gaps:

+ `echo/` — EPA ECHO NPDES discharger inventory (Maumee basin)
+ `hydrology/` — USGS flow and NOAA rainfall reference values
+ `rsei/` — EPA RSEI facility toxics scores
+ `economics/` — EIA utility baseline, USASpending federal outlays
+ `periplus/` — parcel geometry, road-corridor GIS

### Site network

19 sites registered across four basins:

| Basin | Sites |
|---|---|
| Maumee | Lima, Findlay, Fort Wayne, Van Wert, Toledo, Defiance, Bryan, Ottawa |
| Great Miami | Urbana, Springfield, Hamilton·Middletown, Troy·Piqua, Sidney, Greenville |
| Little Miami | Xenia, Wilmington |
| Scioto | New Albany, Columbus |
| (multi) | Wright-Patterson AFB |

Each site is a `SiteProfile` in `watermark.sites.SITES`, carrying all per-site
knobs (USGS gages, county FIPS, GIS URLs, EIA utility number, output relpaths).
The frontend registry mirrors it in `web/src/lib/sites.ts`. Onboard a new
site with `watermark onboard <slug>` (see [docs/onboarding.md](docs/onboarding.md)).
Registered ≠ live: promotion to `selectable` in the frontend is a manual,
parity-gated edit.

### Public site

The site is built in two tiers. The **data tier** (`watermark.site`,
`watermark export`) emits a typed content bundle — JSON feeds + a `manifest.json`
with a `CONTRACT_VERSION` — from the extracted corpus. The **presentation tier**
(`web/`) is an Astro + MDX static site that reads that bundle at build time.
deck.gl map/graph visualizations are the only React islands; charts are a
hand-rolled SVG library (`web/src/lib/charts.ts`). Cloudflare Pages hosts
it; Pages Functions (`/api/submit`, `/api/ask`) deploy alongside. The frontend
classifies each section `available|locked` from feed counts in the manifest, so
a thin site degrades gracefully rather than breaking. See
[web/README.md](web/README.md).

---

## Data layout

```
data/
  documents/    Raw originals, exactly as received — never edited (Git LFS for PDFs)
                  aedg/          engineering cost estimates
                  oepa/<site>/   Ohio EPA NPDES permits & fact sheets
                  recorder/      property deeds & recorder filings
                  commissioners/ county commission minutes
                  idem/<site>/   Indiana IDEM permit docs
                  legal/         web captures & legal exhibits
  extracted/    Reviewed, structured YAML — the committed, durable artifact
  reference/    Authoritative external datasets (each with a README + source)
  catalog/      Pydantic-validated data catalog (watermark catalog check in CI)
  hypotheses/   Per-site hypothesis store (boom-origin × site)
  research/     Agent finding manifests and leads (data/research/<site>/)
  site/         Export feeds and bundle (data/site/bundle/ — built by watermark export)
  cache/        Regenerable API responses — git-ignored
```

Cloning requires Git LFS (`git lfs install`) for the full source documents.
Without it, `data/documents/` contains lightweight pointer files.

---

## Quickstart

```bash
mise install          # Python 3.11, uv, node 24, git-lfs
mise run setup        # uv sync --extra dev + git lfs install
cp .env.example .env  # set ANTHROPIC_API_KEY

watermark ingest
watermark reconcile roundabouts.summary.opc.yaml   # no API key needed
watermark --site lima research run --recipe site-onboard
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for the full task reference and
[CONTRIBUTING.md](CONTRIBUTING.md) for data conventions and the contribution
workflow.
