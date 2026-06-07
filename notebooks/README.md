# notebooks/ — marimo investigation + proof-of-concept

**Status: research spike, not wired into `bosc site build`.** This directory is a
self-contained unit exploring whether to integrate [marimo](https://marimo.io)
reactive notebooks into the BOSC site for scenario demos, lessons, and
exploration. Nothing here is published by the site yet.

- [`marimo-integration-investigation.md`](marimo-integration-investigation.md) —
  the full findings: deployment-mode fit (static GitHub Pages → `marimo export
  html-wasm`), Pyodide package coverage (the `pyswmm`/`pypdfium2` blocker),
  integration architecture, alternatives, and a phased recommendation.
- [`opc_scenario.py`](opc_scenario.py) — a working POC notebook over the six
  Tetra Tech OPC roundabout estimates: a contingency-% slider + intersection
  multiselect that re-derives the modeled program total live in the browser.

## Data discipline (read this before running)

`public/` is **git-ignored on purpose.** The notebook reads a read-only *copy* of
a committed corpus artifact bundled at export time; the original under
`data/extracted/**` is the single source of truth and the chain-of-custody
record. Never commit a second copy here — see [`.gitignore`](.gitignore). The
notebook only ever reads; it never writes back to the corpus.

## Run it locally

```sh
# from the repo root
uv pip install marimo            # not a project dependency yet — see the writeup
mkdir -p notebooks/public
cp data/extracted/aedg/roundabouts.summary.opc.yaml notebooks/public/
uv run marimo edit notebooks/opc_scenario.py     # interactive editor
# or: uv run marimo run notebooks/opc_scenario.py # read-only app
```

## Export to a static (WASM) page

This is the mode that fits the static site — a browser-only Pyodide bundle, no
backend:

```sh
uv run marimo export html-wasm notebooks/opc_scenario.py \
  --mode run --output notebooks/_site
# serve to verify: python -m http.server -d notebooks/_site
```

**Export gotcha (from the POC):** the exporter copies sibling files from the
notebook's directory into the bundle. Keep `notebooks/` clean (only the `.py`
notebook + its `public/` payload) or prune the bundle afterward, so stray files
(e.g. a `CLAUDE.md`) don't ship to the public site. A real integration should
export from a per-notebook subdir or a temp staging dir.
