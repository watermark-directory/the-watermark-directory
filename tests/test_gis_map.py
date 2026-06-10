"""GIS map (imagery P5): dated Esri Wayback aerial layers on the site map."""

from __future__ import annotations

import re

from bosc.config import Settings
from bosc.site.gismap import _WAYBACK, render_gis_map


def test_map_has_dated_wayback_layers() -> None:
    md = render_gis_map(Settings().gis_findings_path)

    # One Wayback tile layer per curated release, each with its real releaseNum + label.
    assert md.count("wayback.maptiles.arcgis.com") == len(_WAYBACK)
    for label, rel in _WAYBACK:
        assert f"/tile/{rel}/" in md
        assert f'"Aerial {label}"' in md

    # The current Esri aerial + OSM base layers survive; no template placeholders leak.
    assert '"Aerial (Esri, current)"' in md and '"Street (OSM)"' in md
    assert "__WAYBACK" not in md

    # Dated aerials are listed newest-first in the layer control.
    order = re.findall(r'"Aerial (20\d\d-\d\d)"', md)
    assert order == sorted(order, reverse=True)
