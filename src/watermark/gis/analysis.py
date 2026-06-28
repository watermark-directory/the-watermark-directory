"""Spectral-index analysis — NDVI / NDWI over a tracking-site AOI (imagery P4).

Compute a normalized-difference index from a scene's band COGs clipped to the AOI:

* **NDVI** = (NIR - red) / (NIR + red) — vegetation; year-over-year drops flag land
  disturbance (grading, clearing) on a tracked site.
* **NDWI** = (green - NIR) / (green + NIR) — open water; the **water fraction** (pixels
  above a threshold) is the measurement that feeds the off-stream reservoir water budget
  once the reservoir is a tracked POI.

Pixels are verbatim (windowed clip, native CRS — :func:`watermark.gis.raster.clip_asset`); the
index is a **derived** float32 raster, tagged as such in the sidecar. The bands per
``(collection, index)`` come from a small table — not hardcoded into the math.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import numpy as np
import rasterio
import yaml
from pydantic import BaseModel, ConfigDict

from watermark.config import Settings, get_settings
from watermark.gis.imagery import Scene
from watermark.gis.raster import clip_asset
from watermark.gis.sites import TrackingSite
from watermark.logging import get_logger

log = get_logger(__name__)

Index = Literal["ndvi", "ndwi"]

# (collection -> index -> (band_a, band_b)) for the formula (a - b) / (a + b).
# NDVI = (NIR - red); NDWI = (green - NIR).
_BANDS: dict[str, dict[str, tuple[str, str]]] = {
    "sentinel-2-l2a": {"ndvi": ("B08", "B04"), "ndwi": ("B03", "B08")},
    "landsat-c2-l2": {"ndvi": ("nir08", "red"), "ndwi": ("green", "nir08")},
}
_WATER_THRESHOLD = 0.0  # NDWI > 0 ≈ open water (McFeeters)


class IndexResult(BaseModel):
    """A computed index raster + its summary statistics and provenance."""

    model_config = ConfigDict(extra="forbid")

    site_id: str
    collection: str
    scene_id: str
    index: Index
    acquired: str | None
    retrieved_at: str
    epsg: int | None
    width: int
    height: int
    path: str
    sidecar: str
    sha256: str
    valid_fraction: float  # fraction of pixels with a defined index
    mean: float | None  # mean index over valid pixels
    water_fraction: float | None  # NDWI: fraction of valid pixels above threshold


def compute_index(
    scene: Scene,
    site: TrackingSite,
    *,
    index: Index,
    out_dir: Path | None = None,
    settings: Settings | None = None,
) -> IndexResult:
    """Compute NDVI/NDWI for a scene over the site AOI → a derived GeoTIFF + stats."""
    settings = settings or get_settings()
    out_dir = out_dir if out_dir is not None else (settings.reference_dir / "imagery")
    bands = _BANDS.get(scene.collection, {}).get(index)
    if bands is None:
        raise ValueError(f"no {index} band mapping for collection {scene.collection!r}")
    a_key, b_key = bands

    a_arr, profile, epsg, _ = clip_asset(scene, site, a_key, settings=settings)
    b_arr, _, _, _ = clip_asset(scene, site, b_key, settings=settings)
    a = np.asarray(a_arr[0], dtype="float32")
    b = np.asarray(b_arr[0], dtype="float32")
    if a.shape != b.shape:
        raise ValueError(f"band shape mismatch {a.shape} vs {b.shape} for {index}")

    denom = a + b
    with np.errstate(divide="ignore", invalid="ignore"):
        ndi = np.where(denom != 0, (a - b) / denom, np.nan).astype("float32")

    valid = np.isfinite(ndi)
    valid_fraction = float(valid.mean()) if ndi.size else 0.0
    mean = float(np.nanmean(ndi)) if bool(valid.any()) else None
    water_fraction: float | None = None
    if index == "ndwi" and bool(valid.any()):
        water_fraction = float((ndi[valid] > _WATER_THRESHOLD).mean())

    height, width = int(ndi.shape[0]), int(ndi.shape[1])
    out_profile = dict(profile)
    out_profile.update(dtype="float32", count=1, nodata=float("nan"))
    date = (scene.acquired or "unknown")[:10]
    dest = out_dir / site.id / scene.collection
    dest.mkdir(parents=True, exist_ok=True)
    tif_path = dest / f"{date}.{index}.tif"
    with rasterio.open(tif_path, "w", **out_profile) as out:
        out.write(ndi, 1)

    sidecar_path = dest / f"{tif_path.name}.yaml"
    result = IndexResult(
        site_id=site.id,
        collection=scene.collection,
        scene_id=scene.scene_id,
        index=index,
        acquired=scene.acquired,
        retrieved_at=datetime.now(UTC).isoformat(),
        epsg=epsg,
        width=width,
        height=height,
        path=str(tif_path),
        sidecar=str(sidecar_path),
        sha256=_sha256(tif_path),
        valid_fraction=round(valid_fraction, 4),
        mean=round(mean, 4) if mean is not None else None,
        water_fraction=round(water_fraction, 4) if water_fraction is not None else None,
    )
    _write_sidecar(result, site, (a_key, b_key), sidecar_path)
    log.info("imagery.index", site=site.id, scene=scene.scene_id, index=index, path=str(tif_path))
    return result


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_sidecar(
    result: IndexResult, site: TrackingSite, bands: tuple[str, str], path: Path
) -> None:
    formula = "(NIR - red)/(NIR + red)" if result.index == "ndvi" else "(green - NIR)/(green + NIR)"
    doc = {
        "meta": {
            "subject": f"AOI {result.index.upper()} index (derived)",
            "site": {"id": site.id, "name": site.name},
            "collection": result.collection,
            "scene_id": result.scene_id,
            "index": result.index,
            "formula": f"{formula} from bands {bands[0]}, {bands[1]}",
            "acquired": result.acquired,
            "retrieved_at": result.retrieved_at,
            "crs": f"EPSG:{result.epsg}" if result.epsg else None,
            "width": result.width,
            "height": result.height,
            "valid_fraction": result.valid_fraction,
            "mean": result.mean,
            "water_fraction": result.water_fraction,
            "sha256": result.sha256,
            "tool": "watermark imagery index",
            "source": "derived",
            "caveats": [
                "A derived index, not raw radiance: computed from the cited band COGs.",
                "water_fraction is NDWI > 0 (McFeeters open-water heuristic) — a screen, "
                "not a validated water mask; confirm against high-res imagery.",
            ],
        }
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
