"""POI resolve funnel: parcel-id (exact) + address (geocode → parcel, proposal), offline."""

from __future__ import annotations

import pytest

from watermark.config import Settings
from watermark.connectors import OfflineError
from watermark.poi.connectors.census_geocoder import geocode_address
from watermark.poi.model import POICandidate
from watermark.poi.resolve import resolve_candidate, resolve_value


def test_geocode_address_offline(poi_offline_settings: Settings) -> None:
    m = geocode_address("3640 Spencerville Road, Lima, OH", settings=poi_offline_settings)
    assert m is not None
    assert m.lon == pytest.approx(-84.1764, abs=0.01)
    assert m.lat == pytest.approx(40.7227, abs=0.01)
    assert "SPENCERVILLE" in m.matched_address and "LIMA" in m.matched_address


def test_resolve_parcel_id_is_exact_and_auto_mergeable(poi_offline_settings: Settings) -> None:
    r = resolve_value("parcel-id", "36-0100-03-002.000", settings=poi_offline_settings)
    assert r.method == "parcel-id"
    assert r.confidence == "high"
    assert r.auto_mergeable is True  # exact id is the only auto-merge path
    assert r.parcel_no == "36010003002000"
    assert r.parcel is not None and r.parcel.owner


def test_resolve_address_is_a_proposal(poi_offline_settings: Settings) -> None:
    r = resolve_value("address", "3640 Spencerville Road, Lima, OH", settings=poi_offline_settings)
    assert r.method == "geocode+parcel-at-point"
    assert r.confidence == "medium"
    assert r.auto_mergeable is False  # geocoding is fuzzy → confirm before merging
    assert r.point is not None
    assert r.matched_address is not None and "SPENCERVILLE" in r.matched_address
    assert r.parcel_no == "46040202001000"
    assert r.parcel is not None and "SPENCERVILLE" in (r.parcel.situs_address or "")


def test_geocode_match_carries_state(poi_offline_settings: Settings) -> None:
    # The match now exposes its USPS state (addressComponents.state) for the guard (#621).
    m = geocode_address("3640 Spencerville Road, Lima, OH", settings=poi_offline_settings)
    assert m is not None and m.state == "OH"


def test_resolve_address_rejects_wrong_state(poi_offline_settings: Settings) -> None:
    # The same OH geocode, but against a site whose state is IN: an unconstrained geocoder
    # can match another state, so a cross-state point is rejected before becoming a lead (#621).
    in_site = poi_offline_settings.model_copy(
        update={"gnis_default_state": "IN", "eia_state": "IN"}
    )
    r = resolve_value("address", "3640 Spencerville Road, Lima, OH", settings=in_site)
    assert r.method == "unresolved"
    assert r.confidence == "none"
    assert r.parcel is None
    assert "wrong-state" in (r.note or "")


def test_resolve_candidate_dispatches(poi_offline_settings: Settings) -> None:
    cand = POICandidate(
        kind="parcel-id", value="36-0100-03-002.000", normalized="36010003002000", occurrences=1
    )
    r = resolve_candidate(cand, settings=poi_offline_settings)
    assert r.parcel_no == "36010003002000" and r.auto_mergeable


def test_resolve_offline_miss_raises(poi_offline_settings: Settings) -> None:
    # An address with no committed geocoder fixture must fail loudly (hermetic).
    with pytest.raises(OfflineError):
        resolve_value("address", "1 Nowhere Street, Nowhere, OH", settings=poi_offline_settings)
