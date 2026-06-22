# CLAUDE.md — guidance for agents working in this repo

Project BOSC is an **agentic research platform** that deconstructs public-records
source documents (degraded scans, OCR PDFs) into reviewed structured data and
runs Claude-driven analysis over it. Spun out from Periplus.

## Architecture

Three-stage pipeline under `src/bosc/pipeline/`: **ingest → extract → analyze**.
The `src/bosc/agent/` layer wraps the Claude Agent SDK and exposes in-process
tools so the agent inspects real data. Entry point is the `bosc` Typer CLI
(`src/bosc/cli.py`).

A second subsystem, `src/bosc/hydrology/`, runs water-balance / stormwater models
of the Lima municipal loop. `src/bosc/hydrology/connectors/` pulls **live public
data** (USGS NWIS, NOAA Atlas-14, EPA ECHO) through `_cache.cached_get` — on-disk
cache + TTL + offline/committed-fixture fallback, so tests never hit the network.
A new connector is a pure sync `fn(..., settings) -> pydantic` in that dir, with a
committed fixture under `tests/fixtures/hydrology/<connector>/`. External-data
pulls land as committed reference datasets under `data/reference/<source>/` and
are regenerable via a `bosc` subcommand (e.g. `bosc npdes` → the EPA ECHO Maumee
NPDES inventory; columns are selected by ECHO **ObjectName**, never by index).

The **public site** is built in two tiers. The Python data tier (`src/bosc/site/`)
emits a typed **content bundle** — JSON feeds + a manifest with a `CONTRACT_VERSION`,
Pydantic models in `bosc.site.feeds`, written by `bosc export`. The presentation tier lives
in **`frontend/`**: an Astro + MDX static site that reads that bundle at build time
(Epic #54). It's pure Node (npm, no uv/LFS) and builds against the committed
`frontend/sample-bundle/` fixture offline; deck.gl map/graph visualizations are the
only React islands. The frontend is structured as **the BOSC network** (Epic #308):
one build hosting a network of watershed-point sites — Lima (the live reference build)
is physically re-rooted under **`/bosc`** so future sites are clean siblings, with
cross-cutting pages (about, wiki, ask, search, the `/network/*` hub) global at the root
and a topbar switcher (`src/lib/sites.ts`) between them. Charts are a hand-rolled SVG
library (`src/lib/charts.ts` + `components/charts/`) — indigo encodes data, the evidence
palette only encodes evidence. The legacy Python SSG was retired at the parity cutover —
the Astro `frontend/` is now the sole presentation tier. Production is
**Cloudflare Pages** (`.github/workflows/pages.yml` + `frontend/wrangler.toml`,
where the `frontend/functions/api/*` Pages Functions — `/api/submit`, `/api/ask` —
also deploy), **not** GitHub Pages: that deploy was never flipped and Cloudflare
supersedes it. See
`frontend/README.md` for the architecture; **don't edit `docs/**` to fix the new
site's cross-links** — they're rewritten at build time (`frontend/src/lib/rehype-doc-links.ts`,
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
`bosc.agent` research agent is deferred follow-up; the skills are usable by
repo-working agents now.

## Conventions

- **Tooling:** mise manages the toolchain (Python 3.11, uv, node 24, git-lfs);
  `Brewfile` is the fallback. uv for envs/deps, ruff for lint+format, mypy
  `strict`, pytest. Run `mise run check` before declaring done. The `frontend/`
  site is its own Node toolchain (`mise run frontend` = `npm ci && npm run check
  && npm run build`); it doesn't touch uv.
- **CI / path filtering:** `.github/workflows/ci.yml` is split into two halves
  gated by a `changes` job — the Python `check` job (ruff/format/mypy/pytest) runs
  only when the backend tree changed (`src/`, `tests/`, `data/`, `pyproject.toml`,
  `uv.lock`, …), the Astro `frontend` job runs only when `frontend/` changed, and a
  `mise.toml`/`ci.yml` edit runs both. `check` is the one **required** status check
  on `main` (`.github/config/index.ts` `requiredChecks`), so filtering is done at
  the **job** level, not with a trigger-level `paths:` filter — a skipped job
  reports success and satisfies the gate, whereas a path-filtered-away workflow
  would leave that required check stuck "pending" and block the PR. Don't add a
  top-level `paths:` to this workflow.
- **Python 3.11+**, `from __future__ import annotations` at the top of modules.
- **Config:** never read `os.environ` directly — go through `bosc.config.get_settings()`.
  Settings are `BOSC_`-prefixed; the model default is `claude-opus-4-8`, bulk
  extraction uses `claude-sonnet-4-6`.
- **Site axis (the BOSC network):** the platform hosts a network of watershed-point
  sites (Lima today; Fort Wayne/Defiance/… queued — #323/#308). Per-site values are
  **not** baked in: they live on a `SiteProfile` in `bosc.sites` (the Python peer of
  `frontend/src/lib/sites.ts`), selected by `BOSC_SITE` (`Settings.site`, default
  `lima`) or the global `bosc --site <slug>` flag. `Settings` fills the per-site config
  knobs (`PROFILE_SETTINGS_FIELDS`: `nwis_sites`, `rsei_fips`, `eia861_utility_number`,
  the GIS URLs, …) from the active profile unless a knob is set explicitly (env/`.env`/
  kwarg still win); deeper hydrology/grid/rsei constants read `bosc.sites.active_profile(settings)`.
  **Add a site by registering a profile in `bosc.sites.SITES`; never re-hardcode a
  Lima/Allen-County value.** Profile `*_relpath`s are relative to `settings.data_dir`,
  and `bosc-`-prefixed reference/extracted filenames are Lima-specific by convention — a
  new site supplies its own paths. (The `--site` callback writes `BOSC_SITE` to the env
  before the first `get_settings()`; that's the one sanctioned `os.environ` write.)
  Onboard a registered site with `bosc onboard <slug>` (`bosc.onboard`; runbook
  `docs/onboarding.md`): it scaffolds the per-site data dirs, runs the portable reach
  connectors (per-site point outputs are slug-scoped so Lima is never clobbered; basin-level
  outputs stay shared), and prints a **blocking review checklist** — promotion to
  `live`/`selectable` in `frontend/src/lib/sites.ts` stays a manual, parity-gated edit.
- **Models:** structured extractions are validated with the Pydantic models in
  `bosc.models`. Scan transcriptions may be **approximate**, written `~12345`
  in YAML; `ApproxInt`/`_coerce_number` handle that — preserve the marker in
  source data, don't silently drop it.
- **CLI options:** a `typer.Option` default trips ruff `B008` when the parameter
  is annotated `Path` (but not for `bool`/`int`/`float`); type the option `str`
  and convert to `Path` in the body.

## Data discipline (important)

- `data/documents/**` is raw, immutable, and **versioned via Git LFS** for large
  binaries (see `.gitattributes`). Add new scan/PDF types to LFS tracking.
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
(`bosc.pipeline.extract`): OCR text layer (pypdf, hint only) + 300 DPI render
(pypdfium2) → resolve a format `Profile` (`bosc.profiles`, auto-detected from the
OCR text or `--profile`) → forced-tool-use vision extraction
(`bosc.agent.extractor.StructuredExtractor`) → Pydantic-validated, contractor-
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
