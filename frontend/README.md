# `frontend/` — the redesigned BOSC site (Astro + MDX)

Tier 2 of the two-tier site refactor ([Epic #54](https://github.com/goedelsoup/bosc/issues/54)).
An in-repo [Astro](https://astro.build) + MDX app that reads the committed
**content bundle** (the typed JSON feeds the Python data tier emits, Epic #53)
at build time and renders the site as static HTML.

This is **built alongside** the legacy Python SSG (`bosc site build` → `site/`).
Both stay live until the new site reaches parity. Production is **Cloudflare Pages**
([`pages.yml`](../.github/workflows/pages.yml) + [`wrangler.toml`](wrangler.toml), where
the [`functions/`](functions/) Pages Functions deploy too), **not** GitHub Pages — that
deploy was never flipped and Cloudflare supersedes it; the public cutover to this app
is parity-gated.

## Toolchain

Node is pinned via mise (`node = "24"` in [`mise.toml`](../mise.toml)); `mise install`
gets it. Without mise, use any Node 24.x. Dependencies are locked in
`package-lock.json` — use `npm ci` for reproducible installs.

## Develop

```sh
cd frontend
npm ci            # or: npm install   (first time / after dep changes)
npm run dev       # dev server with HMR  → http://localhost:4321
npm run check     # astro check (types + template diagnostics)
npm run build     # static build         → dist/
npm run preview   # serve the built dist/ locally
```

From the repo root, `mise run frontend` runs `npm ci && npm run check && npm run build`.

In CI, the `frontend` job in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
does the same against the sample bundle (pure Node — no uv/LFS). It's path-filtered:
a `changes` gate runs it only when `frontend/` changed, so a backend-only PR skips
it (and a frontend-only PR skips the Python `check` job). Don't add a trigger-level
`paths:` filter to that workflow — `check` is a required status check, and skipping
the *workflow* would leave it stuck pending; skipping a *job* via the gate reports
success instead.

## How the content bundle is resolved

`src/lib/bundle.ts` reads the bundle at build time. It picks the **first**
directory that contains a `manifest.json`:

1. **`$BOSC_BUNDLE_DIR`** — explicit override (absolute or relative to CWD).
2. **`../data/site/bundle`** — the real bundle, present after `bosc export`.
3. **`./sample-bundle`** — the committed minimal fixture (the default in a fresh
   checkout and in CI; see [`sample-bundle/README.md`](sample-bundle/README.md)).

So a plain `npm run build` works with zero Python (it uses the fixture). To build
the full site against real data:

```sh
bosc export                                   # → data/site/bundle/  (the loader then prefers it)
# or point anywhere:
BOSC_BUNDLE_DIR=/path/to/bundle npm run build
```

Read `manifest.json` first, then feeds it lists:

```ts
import { loadManifest, loadFeed } from "../lib/bundle";
const manifest = loadManifest();
const records = loadFeed<RecordItem[]>("records");
```

The bundle contract (manifest shape, feed list, schemas, provenance) is documented
in [`data/site/bundle/README.md`](../data/site/bundle/README.md).

## Information architecture

The site is a four-section header, each with a minimal per-section table of
contents (the IA lives in `src/lib/nav.ts` — the single source of truth for the
header tabs, the TOC rail, and the search index):

- **A. Home / About** (`/`) — landing, disclaimer, corpus at a glance, methodology
- **B. The BOSC site** (`/site/`) — documents, records, timeline, exhibits, people & places, legal
- **C. The Maumee watershed** (`/watershed/`) — hydrology, watershed map, imagery, RSEI/toxics
- **D. Wiki** (`/wiki/`) — entity & concept pages

## Search

Dependency-free, zero-CDN. A build-time endpoint (`src/pages/search-index.json.ts`
→ `/search-index.json`) emits one entry per section area and per bundle row; the
vanilla client matcher (`src/scripts/search.ts`) does an all-terms substring
match, title hits first. Ported from the legacy site's `search.js` — no lunr, no
external host needed.

## Interactive maps & the entity graph (deck.gl)

The map/graph visualizations (Epic #55) are **React islands** — the only React in
the app — mounted `client:only` so their JS (deck.gl + MapLibre, ~heavy) loads
**only** on those pages; the rest of the site stays zero-framework. Each island
has a **server-rendered no-JS fallback** (a legend + feature table, or the entity
list) that doubles as a plain data view.

- **Corridor map** (`/watershed/map`, [#71](https://github.com/goedelsoup/bosc/issues/71)) — `src/components/islands/CorridorMap.tsx`, deck.gl `GeoJsonLayer`s over a MapLibre basemap with dated Esri Wayback aerials. Styled **entirely from the feed** (`color`/`role`/`radius`); the data is the geo feeds merged by the `/feeds/geo/corridor-map.geojson` endpoint.
- **Entity graph** (`/wiki/graph`, [#73](https://github.com/goedelsoup/bosc/issues/73)) — `src/components/islands/EntityGraph.tsx`, a deck.gl `OrthographicView` over nodes/edges laid out at build time by `d3-force` (`/feeds/graph.json`, deterministic). Click a node → its wiki page; entity pages deep-link `/wiki/graph#<slug>` to focus a neighborhood.

The islands are build-verified (bundle, mount, endpoint fetch); a quick **browser
visual pass** is still worth doing (WebGL rendering isn't covered by `astro check`).
The watershed map (`/watershed/map`) and the before/during/after imagery slider
(`/watershed/imagery`, [#72](https://github.com/goedelsoup/bosc/issues/72)) ship too —
`ImagerySlider.tsx` over the `geo/imagery` Wayback feed, against the committed
watershed-boundary + AOI geometry feeds.

## Narrative content (the `docs/` collection)

The project's prose (DOSSIER, methodology, HYDROLOGY, ECONOMICS, the bigger
picture, legal analyses…) is surfaced via an Astro **content collection** sourced
from the repo-root `docs/` **as-is** ([#69](https://github.com/goedelsoup/bosc/issues/69)).

**Single-source decision:** `docs/` stays at the repo root and is **not** moved or
edited — it's also the legacy Python SSG's input and general repo documentation.
The frontend reads it with a `glob` loader over `../docs` (`src/content.config.ts`),
publishing only the curated set in `src/lib/narrative.ts`, rendered at `/docs/<slug>`.

Because the source links target the *legacy* `web/docs/` layout, a build-time
rehype plugin (`src/lib/rehype-doc-links.ts`) rewrites them without touching the
source: intra-narrative links → `/docs/<slug>`, known legacy pages → their new-IA
route (`src/lib/narrative.ts` `LINK_MAP`), and any other in-repo file (the corpus,
not-yet-migrated pages) → its GitHub source — so cross-links resolve in both tiers.

> Note: editing `astro.config.ts`-imported modules (the rehype plugin / its data)
> requires clearing `node_modules/.vite` to bust Astro's config bundle cache; a
> fresh `npm ci` in CI is unaffected.

## Evidence tags

`src/components/EvidenceTag.astro` renders the corpus's inline confidence markers
(`[verified]` / `[inference]` / `[open]` / `[filename]`) as tinted pills; derive
the kind from a citation with `evidenceKind()` in `src/lib/feeds.ts`.

## Layout

```
frontend/
  astro.config.ts      # MDX + React integrations; static output; rehype link
                       #   rewriter for the docs collection; site/base from env
  src/
    content.config.ts  # the docs/ narrative content collection (glob over ../docs)
    lib/
      bundle.ts          # build-time bundle reader (resolve dir, manifest, feeds, hasFeed)
      feeds.ts           # TS shapes for the feed rows + evidenceKind()
      nav.ts             # the 4-section IA + per-section TOC (single source of truth)
      search.ts          # build-time search-index assembly over the bundle
      site.ts            # site constants + withBase() base-path helper
      narrative.ts       # which docs/ files are published + the legacy→IA link map
      rehype-doc-links.ts # build-time rewriter for in-repo links inside docs/
      geo.ts / graph.ts  # build-time geo merge + deterministic d3-force graph layout
      geoStyle.ts        # client-safe geo types/colors (shared with the islands)
    components/          # Header (tabs + search), SectionToc rail, EvidenceTag pill
      islands/           # CorridorMap + EntityGraph — the only React (deck.gl)
    layouts/Base.astro   # the app shell (header + TOC rail + content + footer)
    scripts/             # search.ts + toc.ts — dependency-free client scripts
    styles/site.css      # shell styling (indigo chrome, evidence pills)
    pages/
      index.astro         # Section A (Home / About)
      site/               # Section B — documents, records, timeline, people/places, legal
      watershed/          # Section C — hydrology, RSEI, the corridor map
      wiki/               # Section D — entities, concepts, the entity graph
      docs/               # the migrated narrative collection (/docs/<slug>)
      about.mdx           # the About page (MDX)
      search-index.json.ts # build-time search endpoint
      feeds/              # build-time data endpoints (geojson, graph.json) for the islands
  sample-bundle/        # committed minimal bundle fixture (offline/CI build input)
```

## Status / roadmap

In: the scaffold ([#63](https://github.com/goedelsoup/bosc/issues/63)), the app
shell ([#64](https://github.com/goedelsoup/bosc/issues/64)), and all four content
sections:

- **A. Home / About** ([#65](https://github.com/goedelsoup/bosc/issues/65)) — disclaimer, corpus-at-a-glance, doors.
- **B. The BOSC site** ([#66](https://github.com/goedelsoup/bosc/issues/66)) — documents catalog, per-kind record pages, the timeline, exhibits, people/place profiles, legal history.
- **C. The Maumee watershed** ([#67](https://github.com/goedelsoup/bosc/issues/67)) — the water-balance/scenario dashboard, the geo-layer inventory + DeckGL mount point, an imagery slider, and RSEI. The DeckGL map itself is E3.3 (#72).
- **D. Wiki** ([#68](https://github.com/goedelsoup/bosc/issues/68)) — entity pages (graph neighborhood + backlinks), concept pages, and the `[[wiki-link]]` resolver over the new `concepts` feed (a Python data-tier addition — `data/concepts/*.md`, contract `1.1.0`). The interactive entity-graph viz is E3.4 (#73).

Plus the **deck.gl visualization layer** (Epic #55): the corridor map
([#71](https://github.com/goedelsoup/bosc/issues/71)) and the entity graph
([#73](https://github.com/goedelsoup/bosc/issues/73)).

Plus the narrative content collection
([#69](https://github.com/goedelsoup/bosc/issues/69)) — **Epic #54 is complete**.

Remaining for the redesign: flipping the parity-gated Pages deploy to this app
(the watershed map + imagery slider, #72, have shipped).
