"""NASA POWER climate normals as a committed hydrology reference.

The live pull is :func:`bosc.hydrology.connectors.nasa_power.fetch_climatology`; this
module persists its result to ``data/reference/hydrology/nasa-power-climatology.yaml``
and loads it back, mirroring :mod:`bosc.hydrology.maumee` and
:mod:`bosc.hydrology.floodplain`. The committed table is what the offline-
deterministic hydrology report reads, so the doc never depends on a live API call.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from bosc.config import Settings, get_settings
from bosc.hydrology.connectors.nasa_power import NasaPowerClimatology
from bosc.sites import active_profile


def _reference_path(settings: Settings) -> Path:
    # Per-site (#326): Lima keeps the legacy un-slugged path; a new site slug-scopes it.
    return settings.data_dir / active_profile(settings).climatology_relpath


def write_climatology(clim: NasaPowerClimatology, *, settings: Settings | None = None) -> Path:
    """Persist a climatology to the committed reference YAML (deterministic)."""
    settings = settings or get_settings()
    path = _reference_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "meta": {
            "subject": "NASA POWER climate normals — Lima loop point",
            "source": "NASA POWER (AWS Open Data s3://nasa-power), climatology point API",
            "title": clim.source_title,
            "point": {"latitude": clim.latitude, "longitude": clim.longitude},
            "elevation_m": clim.elevation_m,
        },
        "climatology": clim.model_dump(mode="json"),
    }
    path.write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8"
    )
    return path


def load_climatology(*, settings: Settings | None = None) -> NasaPowerClimatology | None:
    """Load the committed NASA POWER climatology, or ``None`` if absent."""
    settings = settings or get_settings()
    path = _reference_path(settings)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    block = data.get("climatology")
    if not block:
        return None
    return NasaPowerClimatology.model_validate(block)
