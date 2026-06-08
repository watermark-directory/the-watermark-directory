"""The methodology-notebook wiring degrades gracefully: disabled (or marimo absent)
yields an unexported list and a Methodology page that says how to enable it — the
default build never depends on marimo.
"""

from __future__ import annotations

from pathlib import Path

from bosc.site.notebooks import export_notebooks, render_notebooks_page

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_disabled_export_is_graceful(tmp_path: Path) -> None:
    exports = export_notebooks(REPO_ROOT, tmp_path / "web", enabled=False)
    assert exports, "registry should still list the notebooks"
    assert all(not e.available for e in exports)
    # No notebook output dir is created when disabled.
    assert not (tmp_path / "web" / "notebooks").exists()


def test_render_notebooks_page_unexported() -> None:
    exports = export_notebooks(REPO_ROOT, Path("/nonexistent"), enabled=False)
    page = render_notebooks_page(exports, enabled=False)
    assert "interactive notebooks" in page.lower()
    assert "--notebooks" in page  # tells the reader how to publish them
    # Each registered notebook is listed by title.
    for e in exports:
        assert e.spec.title in page
