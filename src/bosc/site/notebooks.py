"""Export the marimo methodology notebooks to self-contained WASM apps.

Mission goal (5): teach the methodology through articles linked to runnable
notebooks. Each registered notebook reads a **committed, read-only** corpus
artifact (bundled into its ``public/`` folder) and is exported with
``marimo export html-wasm`` to a static, backend-free app the site serves directly.

Heavy + optional, like the SWMM engine: if marimo isn't installed the export is
**skipped gracefully** (the default ``bosc site build`` never runs it — only
``--notebooks`` does), and the Methodology page says how to enable it. WASM can't run
``pyswmm``/``pypdfium2`` (no wasm wheels), so registered notebooks must stick to the
pure-Python artifacts (OPC financials, entity graph, economics baseline).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from bosc.logging import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class NotebookSpec:
    """A methodology notebook + the committed artifact it reads (bundled read-only)."""

    slug: str
    title: str
    blurb: str
    notebook: str  # repo-relative path to the marimo .py
    artifact: str  # repo-relative committed artifact copied into public/
    public_name: str  # filename the notebook fetches from public/


@dataclass
class NotebookExport:
    """Result of attempting one notebook export."""

    spec: NotebookSpec
    available: bool  # the WASM app was exported into the site
    url: str | None  # site-relative path to the app, when available


# The committed registry. Each entry must read a WASM-safe artifact (no pyswmm/pdfium).
_NOTEBOOKS: list[NotebookSpec] = [
    NotebookSpec(
        slug="opc-scenario",
        title="Reading a degraded OPC scan into structured data",
        blurb=(
            "A reactive view of the six Tetra Tech Opinion-of-Probable-Cost "
            "sub-estimates extracted from scanned exhibit pages — the financial "
            "reconciliation behind the roadwork numbers."
        ),
        notebook="notebooks/opc_scenario.py",
        artifact="data/extracted/aedg/roundabouts.summary.opc.yaml",
        public_name="roundabouts.summary.opc.yaml",
    ),
]


def marimo_available() -> bool:
    """True if the ``marimo`` CLI is on PATH (the export tool)."""
    return shutil.which("marimo") is not None


def _export_one(spec: NotebookSpec, repo_root: Path, out_root: Path) -> NotebookExport:
    """Export one notebook to ``out_root/<slug>`` as a WASM app; never raises."""
    nb = repo_root / spec.notebook
    artifact = repo_root / spec.artifact
    if not nb.is_file() or not artifact.is_file():
        log.warning("site.notebooks.missing", slug=spec.slug, notebook=str(nb))
        return NotebookExport(spec=spec, available=False, url=None)
    # Bundle the committed artifact read-only next to the notebook (chain of custody:
    # a copy, never the source) so the WASM app fetches it from public/.
    public = nb.parent / "public"
    public.mkdir(parents=True, exist_ok=True)
    shutil.copy2(artifact, public / spec.public_name)

    dst = out_root / spec.slug
    try:
        proc = subprocess.run(
            ["marimo", "export", "html-wasm", str(nb), "-o", str(dst), "--mode", "run"],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log.warning("site.notebooks.export_failed", slug=spec.slug, error=str(exc).splitlines()[0])
        return NotebookExport(spec=spec, available=False, url=None)
    if proc.returncode != 0 or not (dst / "index.html").is_file():
        log.warning(
            "site.notebooks.export_failed",
            slug=spec.slug,
            code=proc.returncode,
            stderr=(proc.stderr or "").splitlines()[-1:],
        )
        return NotebookExport(spec=spec, available=False, url=None)
    log.info("site.notebooks.exported", slug=spec.slug)
    return NotebookExport(spec=spec, available=True, url=f"notebooks/{spec.slug}/index.html")


def export_notebooks(repo_root: Path, web_dir: Path, *, enabled: bool) -> list[NotebookExport]:
    """Export every registered notebook into ``web_dir/notebooks`` (graceful skip).

    Returns one :class:`NotebookExport` per registered notebook (``available=False``
    when disabled or marimo is absent), so the Methodology page can list them either way.
    """
    if not enabled or not marimo_available():
        if enabled:
            log.info("site.notebooks.unavailable", reason="marimo not on PATH")
        return [NotebookExport(spec=s, available=False, url=None) for s in _NOTEBOOKS]
    out_root = web_dir / "notebooks"
    out_root.mkdir(parents=True, exist_ok=True)
    return [_export_one(s, repo_root, out_root) for s in _NOTEBOOKS]


def render_notebooks_page(exports: list[NotebookExport], *, enabled: bool) -> str:
    """Render ``notebooks.md`` — the Methodology notebook index."""
    lines = [
        "# Methodology — interactive notebooks",
        "",
        "Each notebook reads a committed, read-only corpus artifact and runs entirely "
        "in your browser (marimo + WebAssembly — no backend). They are the runnable "
        "companions to the [methodology](docs/methodology.md) write-ups: inspect the "
        "real data behind a claim, change an input, watch it recompute.",
        "",
    ]
    any_available = any(e.available for e in exports)
    if not any_available:
        note = (
            "Notebooks are not in this build. Regenerate with `bosc site build "
            "--notebooks` (requires `marimo`: `uv sync --extra docs`)."
            if not enabled
            else "Notebook export was requested but `marimo` is not installed "
            "(`uv sync --extra docs`)."
        )
        lines += [f'!!! note "Not exported"\n    {note}', ""]
    for e in exports:
        lines += [f"## {e.spec.title}", "", e.spec.blurb, ""]
        if e.available and e.url:
            lines += [f"[Open the notebook →]({e.url})", ""]
        else:
            lines += [f"*Source: `{e.spec.notebook}` — build with `--notebooks` to publish.*", ""]
    return "\n".join(lines)
