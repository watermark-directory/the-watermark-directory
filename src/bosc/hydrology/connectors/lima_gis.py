"""City of Lima, Ohio GIS — zoning connector.

Pulls the **"Current Lima Zoning"** polygon layer from the City of Lima's public
**ArcGIS REST** server (folder ``CitywideMaps/Lima_Zoning``, layer 6). Each zoning
polygon carries a ``ZONING`` district label and a ``PARCEL_NO`` — so zoning joins
to a parcel by id, no spatial query needed. The server is anonymous (no token),
serves ``f=json``, and the layer's ``maxRecordCount`` is 10,000.

Scope caveat (important): this layer covers **Lima city limits only**. Parcels in
unincorporated Allen County (e.g. the American Township corridor) are *not* in it —
a lookup there returning ``None`` means "outside the city," not "unzoned."

Two ways in:

* :func:`zoning_for_parcel` — the district for one parcel number (deed ids like
  ``36-0100-03-002.000`` are normalized to the dashless ``PARCEL_NO``);
* :func:`zoning_districts` — the district catalog (each code + its polygon count),
  via a server-side ``groupBy`` statistics query.

Values are passed through **verbatim** from the service; ``None`` means the service
returned no value. Reuses the shared connector cache/offline/fixture machinery;
synchronous (``httpx``). Mirrors :mod:`bosc.hydrology.connectors.allen_gis`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import httpx
import yaml
from pydantic import BaseModel, ConfigDict

from bosc.config import Settings, get_settings
from bosc.hydrology.connectors._cache import cached_get
from bosc.hydrology.connectors.allen_gis import normalize_parcel_id
from bosc.logging import get_logger

log = get_logger(__name__)

_PAGE_SIZE = 10000  # the layer's maxRecordCount


class LimaGisError(RuntimeError):
    """The ArcGIS service returned an error object (bad field, bad where, ...)."""


class ZoningRecord(BaseModel):
    """One zoning polygon's attributes, as returned by the City of Lima GIS."""

    model_config = ConfigDict(extra="forbid")

    object_id: int | None
    parcel_no: str | None  # PARCEL_NO (dashless, joins to the county CAMA layer)
    zoning: str | None  # ZONING district label, verbatim

    @classmethod
    def from_attrs(cls, a: dict[str, Any]) -> ZoningRecord:
        return cls(
            object_id=_i(a.get("OBJECTID")),
            parcel_no=_s(a.get("PARCEL_NO")),
            zoning=_s(a.get("ZONING")),
        )


class ZoningDistrict(BaseModel):
    """One zoning district and how many polygons carry it (the catalog row)."""

    model_config = ConfigDict(extra="forbid")

    code: str  # the ZONING label, verbatim
    polygon_count: int


def _s(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _i(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _query(params: dict[str, Any], *, settings: Settings) -> dict[str, Any]:
    """Run (or replay) one ArcGIS ``/query`` request; return the parsed JSON."""
    query = {"f": "json", "returnGeometry": "false", **params}

    def fetch() -> Any:
        log.info("lima_gis.fetch", where=params.get("where"), offset=params.get("resultOffset"))
        resp = httpx.get(
            f"{settings.lima_zoning_url}/query",
            params=query,
            timeout=settings.hydro_request_timeout_s,
        )
        resp.raise_for_status()
        return resp.json()

    payload = cast("dict[str, Any]", cached_get("lima_gis", query, fetch, settings=settings))
    if "error" in payload:
        raise LimaGisError(f"ArcGIS error: {payload['error']}")
    return payload


def query_zoning(
    where: str,
    *,
    max_records: int | None = None,
    settings: Settings | None = None,
) -> list[ZoningRecord]:
    """Every zoning polygon matching ``where``, paged to completion."""
    settings = settings or get_settings()
    records: list[ZoningRecord] = []
    offset = 0
    while True:
        page = _query(
            {
                "where": where,
                "outFields": "OBJECTID,PARCEL_NO,ZONING",
                "resultOffset": offset,
                "resultRecordCount": _PAGE_SIZE,
                "orderByFields": "OBJECTID",
            },
            settings=settings,
        )
        features = page.get("features") or []
        records.extend(ZoningRecord.from_attrs(f.get("attributes", {})) for f in features)
        if max_records is not None and len(records) >= max_records:
            return records[:max_records]
        if not page.get("exceededTransferLimit") or not features:
            return records
        offset += len(features)


def zoning_for_parcel(parcel_no: str, *, settings: Settings | None = None) -> ZoningRecord | None:
    """The zoning district for one parcel; ``None`` if outside Lima city limits."""
    settings = settings or get_settings()
    normalized = normalize_parcel_id(parcel_no)
    matches = query_zoning(f"PARCEL_NO='{normalized}'", settings=settings)
    return matches[0] if matches else None


def zoning_districts(*, settings: Settings | None = None) -> list[ZoningDistrict]:
    """The zoning-district catalog: each ``ZONING`` code and its polygon count.

    Uses a server-side ``groupBy`` statistics query so the whole catalog comes back
    in one request rather than paging every polygon.
    """
    settings = settings or get_settings()
    stats = [
        {"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "n"}
    ]
    page = _query(
        {
            "where": "1=1",
            "outFields": "ZONING",
            "groupByFieldsForStatistics": "ZONING",
            "outStatistics": json.dumps(stats),
        },
        settings=settings,
    )
    districts = [
        ZoningDistrict(code=str(a.get("ZONING") or "").strip(), polygon_count=int(a.get("n") or 0))
        for a in (f.get("attributes", {}) for f in page.get("features") or [])
        if _s(a.get("ZONING"))
    ]
    return sorted(districts, key=lambda d: (-d.polygon_count, d.code))


def write_zoning_districts(districts: list[ZoningDistrict], out_dir: Path) -> Path:
    """Write the zoning-district catalog to one YAML file with provenance ``meta``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "zoning-districts.yaml"
    doc = {
        "meta": {
            "subject": "City of Lima, Ohio zoning districts (catalog)",
            "source": "City of Lima GIS — ArcGIS REST, CitywideMaps/Lima_Zoning, layer 6 'Current Lima Zoning'",
            "source_url": (
                "https://colgis.cityhall.lima.oh.us/server/rest/services/"
                "CitywideMaps/Lima_Zoning/MapServer/6"
            ),
            "district_count": len(districts),
            "polygon_total": sum(d.polygon_count for d in districts),
            "caveats": [
                "Values are verbatim from the City of Lima GIS.",
                "Coverage is Lima CITY LIMITS ONLY; unincorporated Allen County parcels "
                "(e.g. the American Township corridor) are not in this layer.",
                "polygon_count counts zoning polygons, not distinct parcels (a parcel may "
                "carry more than one polygon).",
            ],
        },
        "districts": [d.model_dump() for d in districts],
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
