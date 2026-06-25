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
from bosc.poi.connectors.gnis import find_feature
from bosc.poi.model import POICandidate

Method = Literal["parcel-id", "geocode+parcel-at-point", "geocode-only", "gnis", "unresolved"]
Confidence = Literal["high", "medium", "low", "none"]

_GEOHASH_B32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def _geohash(lat: float, lon: float, precision: int = 9) -> str:
    """A standard geohash of a point — the fallback identity key for a non-parcel place."""
    lat_lo, lat_hi, lon_lo, lon_hi = -90.0, 90.0, -180.0, 180.0
    out: list[str] = []
    ch = bit = 0
    even = True
    while len(out) < precision:
        if even:
            mid = (lon_lo + lon_hi) / 2
            ch = (ch << 1) | 1 if lon >= mid else ch << 1
            lon_lo, lon_hi = (mid, lon_hi) if lon >= mid else (lon_lo, mid)
        else:
            mid = (lat_lo + lat_hi) / 2
            ch = (ch << 1) | 1 if lat >= mid else ch << 1
            lat_lo, lat_hi = (mid, lat_hi) if lat >= mid else (lat_lo, mid)
        even = not even
        bit += 1
        if bit == 5:
            out.append(_GEOHASH_B32[ch])
            ch = bit = 0
    return "".join(out)


class Resolution(BaseModel):
    """The outcome of funnelling one candidate toward a canonical parcel."""

    model_config = ConfigDict(extra="forbid")

    kind: str  # the candidate kind (parcel-id | address | coord | feature)
    value: str  # the input value
    method: Method
    confidence: Confidence
    parcel_no: str | None  # canonical PARCEL_NO when resolved to a parcel
    parcel: Parcel | None  # the resolved parcel's CAMA attributes
    point: tuple[float, float] | None  # (lon, lat) when geocoded
    matched_address: str | None  # the geocoder's / GNIS normalized name
    auto_mergeable: bool  # True only for an exact parcel-id resolution
    fallback_key: str | None = None  # non-parcel identity (gnis-<id> | geo-<geohash>)
    note: str | None = None

    @property
    def key(self) -> str | None:
        """The canonical blocking key: the parcel number, else the non-parcel fallback."""
        return self.parcel_no or self.fallback_key


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
    if kind in ("feature", "name"):
        return _resolve_feature(value, settings)
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
    # Wrong-state guard (#621): the geocoder is unconstrained, so an under-qualified
    # address can match another state entirely. Reject a cross-state match before it
    # enters the funnel as a lead. The site's state is the profile's geo anchor
    # (gnis_default_state, else eia_state); skip the check only if neither is set.
    site_state = settings.gnis_default_state or settings.eia_state
    if match.state and site_state and match.state.upper() != site_state.upper():
        return _unresolved(
            "address",
            value,
            f"geocoded to {match.state}, outside the site state {site_state} — wrong-state match",
        )
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
            fallback_key=f"geo-{_geohash(match.lat, match.lon)}",
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


def _resolve_feature(value: str, settings: Settings) -> Resolution:
    """A named feature (river, water body, landform) → GNIS point + ``gnis-<id>`` key."""
    feature = find_feature(value, settings=settings)
    if feature is None:
        return _unresolved("feature", value, "no GNIS match")
    where = f"{feature.county} Co, {feature.state}" if feature.county else feature.state
    return Resolution(
        kind="feature",
        value=value,
        method="gnis",
        confidence="medium",
        parcel_no=None,  # a feature has no parcel — identity is the GNIS id
        parcel=None,
        point=(feature.lon, feature.lat),
        matched_address=f"{feature.name} ({feature.feature_class}, {where})",
        auto_mergeable=False,
        fallback_key=feature.key,
        note="GNIS feature (no parcel) — a proposal; confirm before merging",
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
