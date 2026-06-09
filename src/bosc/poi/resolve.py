"""Resolve POI candidates to a canonical Allen County parcel — the dedup funnel.

Take a candidate and funnel it to a parcel:

* a **parcel id** normalizes directly and is looked up in CAMA — *exact*, high
  confidence, the only auto-merge-eligible path;
* an **address** is geocoded (US Census) and then snapped to the containing parcel via
  ``allen_gis.parcel_at_point`` — a **proposal** (medium/low confidence), because
  geocoding is fuzzy (an under-qualified address can match the wrong place).

Confidence + ``auto_mergeable`` encode the merge-strictness decision (only an exact
parcel-id match auto-merges; geocoded matches are human-confirmed). The merge/blocking
across candidates is a later increment — this resolves one candidate at a time.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from bosc.config import Settings, get_settings
from bosc.hydrology.connectors.allen_gis import (
    Parcel,
    fetch_parcel,
    normalize_parcel_id,
    parcel_at_point,
)
from bosc.poi.connectors.census_geocoder import geocode_address
from bosc.poi.model import POICandidate

Method = Literal["parcel-id", "geocode+parcel-at-point", "geocode-only", "unresolved"]
Confidence = Literal["high", "medium", "low", "none"]


class Resolution(BaseModel):
    """The outcome of funnelling one candidate toward a canonical parcel."""

    model_config = ConfigDict(extra="forbid")

    kind: str  # the candidate kind (parcel-id | address | coord)
    value: str  # the input value
    method: Method
    confidence: Confidence
    parcel_no: str | None  # canonical PARCEL_NO when resolved
    parcel: Parcel | None  # the resolved parcel's CAMA attributes
    point: tuple[float, float] | None  # (lon, lat) when geocoded
    matched_address: str | None  # the geocoder's normalized address
    auto_mergeable: bool  # True only for an exact parcel-id resolution
    note: str | None = None


def resolve_candidate(candidate: POICandidate, *, settings: Settings | None = None) -> Resolution:
    """Resolve a discovered :class:`POICandidate` to a parcel."""
    return resolve_value(candidate.kind, candidate.value, settings=settings)


def resolve_value(kind: str, value: str, *, settings: Settings | None = None) -> Resolution:
    """Resolve a raw ``(kind, value)`` to a parcel via the funnel."""
    settings = settings or get_settings()
    if kind == "parcel-id":
        return _resolve_parcel_id(value, settings)
    if kind == "address":
        return _resolve_address(value, settings)
    if kind == "coord":
        return _resolve_coord(value, settings)
    return _unresolved(kind, value, "unsupported candidate kind")


def _resolve_parcel_id(value: str, settings: Settings) -> Resolution:
    norm = normalize_parcel_id(value)
    parcel = fetch_parcel(norm, settings=settings)
    return Resolution(
        kind="parcel-id",
        value=value,
        method="parcel-id",
        confidence="high" if parcel else "medium",
        parcel_no=parcel.parcel_no if parcel else norm,
        parcel=parcel,
        point=None,
        matched_address=None,
        auto_mergeable=True,  # exact id is the only auto-merge path
        note=None if parcel else "parcel id not found in CAMA — verify the id",
    )


def _resolve_address(value: str, settings: Settings) -> Resolution:
    match = geocode_address(value, settings=settings)
    if match is None:
        return _unresolved("address", value, "no geocoder match")
    point = (match.lon, match.lat)
    parcel = parcel_at_point(match.lon, match.lat, settings=settings)
    if parcel is None:
        return Resolution(
            kind="address",
            value=value,
            method="geocode-only",
            confidence="low",
            parcel_no=None,
            parcel=None,
            point=point,
            matched_address=match.matched_address,
            auto_mergeable=False,
            note="geocoded but no containing parcel (out of county / bad match?)",
        )
    return Resolution(
        kind="address",
        value=value,
        method="geocode+parcel-at-point",
        confidence="medium",
        parcel_no=parcel.parcel_no,
        parcel=parcel,
        point=point,
        matched_address=match.matched_address,
        auto_mergeable=False,  # a proposal — geocoding is fuzzy
        note="geocode → parcel is a proposal; confirm before merging",
    )


def _resolve_coord(value: str, settings: Settings) -> Resolution:
    try:
        lon_s, lat_s = value.split(",", 1)
        lon, lat = float(lon_s), float(lat_s)
    except ValueError:
        return _unresolved("coord", value, "expected 'lon,lat'")
    parcel = parcel_at_point(lon, lat, settings=settings)
    if parcel is None:
        return _unresolved("coord", value, "no containing parcel at point")
    return Resolution(
        kind="coord",
        value=value,
        method="geocode+parcel-at-point",
        confidence="medium",
        parcel_no=parcel.parcel_no,
        parcel=parcel,
        point=(lon, lat),
        matched_address=None,
        auto_mergeable=False,
        note="point → parcel is a proposal; confirm before merging",
    )


def _unresolved(kind: str, value: str, note: str) -> Resolution:
    return Resolution(
        kind=kind,
        value=value,
        method="unresolved",
        confidence="none",
        parcel_no=None,
        parcel=None,
        point=None,
        matched_address=None,
        auto_mergeable=False,
        note=note,
    )
