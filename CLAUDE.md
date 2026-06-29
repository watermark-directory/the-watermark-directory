# CLAUDE.md — guidance for agents working in this repo

Project BOSC is an **agentic research platform** that deconstructs public-records
source documents (degraded scans, OCR PDFs) into reviewed structured data and
runs Claude-driven analysis over it. Spun out from Periplus.

## Architecture

Three-stage pipeline under `src/watermark/pipeline/`: **ingest → extract → analyze**.
The `src/watermark/agent/` layer wraps the Claude Agent SDK and exposes in-process
tools so the agent inspects real data. Entry point is the `bosc` Typer CLI
(`src/watermark/cli.py`).

A second subsystem, `src/watermark/hydrology/`, runs water-balance / stormwater models
of the Lima municipal loop. `src/watermark/hydrology/connectors/` pulls **live public
data** (USGS NWIS, NOAA Atlas-14, EPA ECHO) through `_cache.cached_get` — on-disk
cache + TTL + offline/committed-fixture fallback, so tests never hit the network.
A new connector is a pure sync `fn(..., settings) -> pydantic` in that dir, with a
committed fixture under `tests/fixtures/hydrology/<connector>/`. External-data
pulls land as committed reference datasets under `data/reference/<source>/` and
are regenerable via a `bosc` subcommand (e.g. `watermark npdes` → the EPA ECHO Maumee
NPDES inventory; columns are selected by ECHO **ObjectName**, never by index).

The **public site** is built in two tiers. The Python data tier (`src/watermark/site/`)
emits a typed **content bundle** — JSON feeds + a manifest with a `CONTRACT_VERSION`,
Pydantic models in `watermark.site.feeds`, written by `watermark export`. The presentation tier lives
in **`web/`**: an Astro + MDX static site that reads that bundle at build time
(Epic #54). It's pure Node (npm, no uv/LFS) and builds against the committed
`web/sample-bundle/` fixture offline; deck.gl map/graph visualizations are the
only React islands. The frontend is structured as **the BOSC network** (Epic #308):
one build hosting a network of watershed-point sites — Lima (the live reference build)
is physically re-rooted under **`/bosc`** so future sites are clean siblings, with
cross-cutting pages (about, wiki, ask, search, the `/network/*` hub) global at the root
and a topbar switcher (`src/lib/sites.ts`) between them. Charts are a hand-rolled SVG
library (`src/lib/charts.ts` + `components/charts/`) — indigo encodes data, the evidence
palette only encodes evidence. The legacy Python SSG was retired at the parity cutover —
the Astro `web/` is now the sole presentation tier. Production is
**Cloudflare Pages** (`.github/workflows/pages.yml` + `web/wrangler.toml`,
where the `web/functions/api/*` Pages Functions — `/api/submit`, `/api/ask` —
also deploy), **not** GitHub Pages: that deploy was never flipped and Cloudflare
supersedes it. See
`web/README.md` for the architecture; **don't edit `docs/**` to fix the new
site's cross-links** — they're rewritten at build time (`web/src/lib/rehype-doc-links.ts`,
base-aware: Lima routes get the `/bosc` prefix, network-global ones don't), keeping the
`docs/**` source canonical. After a base/`LINK_MAP` change, clear
`node_modules/.astro` (Astro caches markdown rehype output there).

The **investigative-method layer** is the methodology the platform's analysis and
prose are held to: `.claude/skills/` carries six abstract, agent-discoverable
skills (evidentiary-discipline is the spine; the rest defer to it), and
`docs/investigative-method/` carries the candidate agent system prompt plus the
`ENRICHMENT.md` that binds those skills to this repo's artifacts (the `[verified]`/
`[inference]`/`[reference]`/`[open]` tag vocabulary, the `EntityGraph`,
`ProvenancedValue`, `docs/legal/`, the corpus audit). Wiring it into the in-app
`watermark.agent` research agent is deferred follow-up; the skills are usable by
repo-working agents now.

## Conventions

- **Tooling:** mise manages the toolchain (Python 3.11, uv, node 24, git-lfs);
  `Brewfile` is the fallback. uv for envs/deps, ruff for lint+format, mypy
  `strict`, pytest. mise is a **monorepo**: backend tasks run at the repo root
  (`mise run check` — the gate to run before declaring done — plus `test`/`lint`/
  `types`/`fmt`/`dev`/`export`), the `web/` Astro project's tasks are namespaced
  (`mise run //web:check`, `//web:dev`, `//web:test`, …), and
  `mise run ci` runs the whole-repo gate (both `check`s). A bare task name runs the
  project you're standing in. The frontend is its own Node toolchain; it doesn't touch uv.
- **Markdown lint:** `markdown` is a **separate required CI check** (alongside `check`).
  Any PR that adds or edits `.md` files triggers it. Run `npx markdownlint-cli2` locally
  before pushing — common failures: missing blank line before a list (`MD032`), multiple
  consecutive blank lines (`MD012`). Config and ignores live in `.markdownlint-cli2.yaml`
  (generated docs like `docs/HYDROLOGY.md` and `data/research/*/**` are excluded).
- **CI / path filtering:** `.github/workflows/ci.yml` is split into two halves
  gated by a `changes` job — the Python `check` job (ruff/format/mypy/pytest) runs
  only when the backend tree changed (`src/`, `tests/`, `data/`, `pyproject.toml`,
  `uv.lock`, …), the Astro `web` job runs only when `web/` changed, and a
  `mise.toml`/`ci.yml` edit runs both. `check` is the one **required** status check
  on `main` (`.github/config/index.ts` `requiredChecks`), so filtering is done at
  the **job** level, not with a trigger-level `paths:` filter — a skipped job
  reports success and satisfies the gate, whereas a path-filtered-away workflow
  would leave that required check stuck "pending" and block the PR. Don't add a
  top-level `paths:` to this workflow.
- **Python 3.11+**, `from __future__ import annotations` at the top of modules.
- **Config:** never read `os.environ` directly — go through `watermark.config.get_settings()`.
  Settings are `WATERMARK_`-prefixed; the model default is `claude-opus-4-8`, bulk
  extraction uses `claude-sonnet-4-6`.
- **Site axis (the BOSC network):** the platform hosts a network of watershed-point
  sites (Lima today; Fort Wayne/Defiance/… queued — #323/#308). Per-site values are
  **not** baked in: they live on a `SiteProfile` in `watermark.sites` (the Python peer of
  `web/src/lib/sites.ts`), selected by `WATERMARK_SITE` (`Settings.site`, default
  `lima`) or the global `watermark --site <slug>` flag. `Settings` fills the per-site config
  knobs (`PROFILE_SETTINGS_FIELDS`: `nwis_sites`, `rsei_fips`, `eia861_utility_number`,
  the GIS URLs, …) from the active profile unless a knob is set explicitly (env/`.env`/
  kwarg still win); deeper hydrology/grid/rsei constants read `watermark.sites.active_profile(settings)`.
  **Add a site by registering a profile in `watermark.sites.SITES`; never re-hardcode a
  Lima/Allen-County value.** Profile `*_relpath`s are relative to `settings.data_dir`,
  and `bosc-`-prefixed reference/extracted filenames are Lima-specific by convention — a
  new site supplies its own paths. (The `--site` callback writes `WATERMARK_SITE` to the env
  before the first `get_settings()`; that's the one sanctioned `os.environ` write.)
  Onboard a registered site with `watermark onboard <slug>` (`watermark.onboard`; runbook
  `docs/onboarding.md`): it scaffolds the per-site data dirs, runs the portable reach
  connectors (per-site point outputs are slug-scoped so Lima is never clobbered; basin-level
  outputs stay shared), and prints a **blocking review checklist** — promotion to
  `live`/`selectable` in `web/src/lib/sites.ts` stays a manual, parity-gated edit.
  **Registered ≠ selectable, and a thin peer is still engageable** (#781/#782): a
  non-reference `/network/<site>` page **degrades, doesn't break** — the frontend
  readiness layer (`web/src/lib/readiness.ts`, the peer of `watermark.sites.is_reference_site`)
  classifies each section `available|locked` from the bundle's `manifest.json` feed counts,
  locks the thin ones, and surfaces a needs/leads board instead. Chrome is **two-tier by the
  current path** — site-level tabs when standing on a site (locked tabs render non-navigable),
  network tabs otherwise; a non-`selectable` site gets registry-only locked tabs. So **never
  fake a value to make a partial site look complete** — let it lock and ask for the source.
  Onboarding only needs the verifiable knobs; the page is useful before parity. (Leads are a
  per-site `leads` bundle feed, #796 — Lima's live in `data/site/leads.yaml`, a peer ships its own.)
- **Models:** structured extractions are validated with the Pydantic models in
  `watermark.models`. Scan transcriptions may be **approximate**, written `~12345`
  in YAML; `ApproxInt`/`_coerce_number` handle that — preserve the marker in
  source data, don't silently drop it.
- **CLI options:** a `typer.Option` default trips ruff `B008` when the parameter
  is annotated `Path` (but not for `bool`/`int`/`float`); type the option `str`
  and convert to `Path` in the body.

## Data discipline (important)

- `data/documents/**` is raw, immutable, and **versioned via Git LFS** for large
  binaries (see `.gitattributes`). Add new scan/PDF types to LFS tracking.
  The `history/` sub-tree is for secondary/reference sources (public-domain books,
  surveys) and nests **by site** (`history/allen-oh/`, `history/allen-in/`, …) so
  books for different watershed points don't collide. All claims from `history/`
  sources are tagged `[reference]`, never `[verified]`.
- `data/extracted/**` is the committed, reviewed artifact and what tests run on.
- `data/reference/**` is committed **authoritative data from outside sources**
  (EPA ECHO, USGS/NOAA, parcels). Each folder carries a `README.md` naming its
  source and gaps; raw API responses stay cached under `data/cache/` (git-ignored)
  so the committed CSV/YAML is regenerable.
- When transcribing figures: dollar totals/subtotals are high-confidence; mark
  uncertain quantities `~`. **Never fabricate line items or sources.** Prefer
  omission over invention. Cite source page/file.
- **Chain of custody — the corpus is litigation evidence.** Never alter a source
  byte under `data/documents/**`, and don't rename or "fix" malformed/typo'd
  source filenames in place: keep the as-received name and record the canonical
  name + a **content-verified** date (text layer or OCR, *not* the filename or
  outside knowledge) in a non-destructive alias manifest — see
  `data/extracted/commissioners/minutes/filename-map.yaml`. Removing a source
  file is only OK when it's a checksum-verified byte-identical duplicate — e.g. the
  commissioners' meeting record is now connector-sourced under
  `data/documents/commissioners/meetings/`, the legacy `minutes/raw/` tree retired
  under exactly this rule (`data/extracted/commissioners/meetings/cutover-reconciliation.yaml`).
  Captured
  third-party web evidence may embed secrets/tokens — that's evidence, not a leak
  to redact. The standing completeness audit is
  `data/extracted/legal/corpus-completeness-audit.md`.

## What "extract" must achieve

The reference target is `data/extracted/aedg/roundabouts.*.opc.yaml`: the six Tetra
Tech OPC estimates at 0-based PDF pages **317 (summary), 318-327 (detail)** of
`data/documents/aedg/PRR-01-bundle.ocr.pdf` (printed sheets `pdf_page` 318-328).
The extracted tree **mirrors `data/documents/` by collection** — an artifact lands
under the same first-level collection as its source (`recorder/`, `oepa/`, `aedg/`).

The extract stage is **implemented as a hybrid, profile-driven read**
(`watermark.pipeline.extract`): OCR text layer (pypdf, hint only) + 300 DPI render
(pypdfium2) → resolve a format `Profile` (`watermark.profiles`, auto-detected from the
OCR text or `--profile`) → forced-tool-use vision extraction
(`watermark.agent.extractor.StructuredExtractor`) → Pydantic-validated, contractor-
agnostic `Estimate` (dynamic `sections` + `markups`) with provenance
(`PageExtraction`). The OCR text layer is badly garbled (e.g. `$109,307.69` →
`$108.307.89`); **never trust its digits — figures come from the image.**

**Generality (important):** the extract entrypoint is not tied to one contractor.
`extract_page(doc, i, kind="opc", profile="auto", detail=...)` dispatches by
document kind, and within OPC by `Profile` (Tetra Tech is profile #1; `generic`
is the fallback). The `Estimate` model and `analyze.reconcile_estimate` are
format-agnostic — section taxonomy and markup rate come from the data/profile,
**not hardcoded**. Add a contractor by registering a `Profile`; don't add fixed
section fields. `bosc extract --detail` adds per-section `LineItem`s (rolled up
by `reconcile_estimate`). `Number` (`models._coerce_number_keep`) preserves
int-vs-float for quantities/rates and tolerates the `~` marker. `bosc reconcile`
(legacy `OPCSummary`, 25% convention) still covers the assembled summary artifact.
