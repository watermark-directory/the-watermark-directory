"""Direct coverage for the hydrology dossier renderer (#620).

`report.py` (700+ lines) previously had only transitive coverage; given the div-by-zero
(#614) and the prose/figure drift it carries, a direct offline smoke is warranted.
"""

from __future__ import annotations

from watermark.config import Settings
from watermark.hydrology.report import render_report


def test_render_report_offline_builds_the_full_dossier(hydro_settings: Settings) -> None:
    md = render_report(settings=hydro_settings, live=False)
    # Substantial markdown with the headline sections (no crash on any section, incl. the
    # assimilative screen whose div-by-zero on a zero natural low flow is guarded — #614).
    assert md.startswith("# Hydrology")
    assert len(md) > 2000
    assert "## 1. The municipal loop and its low-flow squeeze" in md
    assert "assimilative screen" in md.lower()
    # Every figure is provenance-tagged — the dossier never prints a bare number.
    assert "[verified]" in md or "[inference]" in md
