"""POI discover: corpus place-reference extraction + store-coverage flags."""

from __future__ import annotations

from pathlib import Path

from bosc.config import Settings
from bosc.hydrology.connectors.allen_gis import scan_parcel_ids
from bosc.poi.discover import _default_roots, discover_candidates


def test_discover_parcel_ids_and_coverage(poi_settings: Settings, tmp_path: Path) -> None:
    # One campus parcel (covered by the seed POI) and a fabricated one (not covered).
    (tmp_path / "doc.md").write_text(
        "Parcel 36-0100-03-002.000 was conveyed; cf. 99-9999-99-999.999 elsewhere.\n",
        encoding="utf-8",
    )
    cands = discover_candidates(roots=[tmp_path], settings=poi_settings)
    parcels = {c.normalized: c for c in cands if c.kind == "parcel-id"}

    assert set(parcels) == {"36010003002000", "99999999999999"}
    assert parcels["36010003002000"].covered is True  # a campus parcel, in the store
    assert parcels["99999999999999"].covered is False  # fabricated, not in the store
    assert any("doc.md" in cite for cite in parcels["36010003002000"].citations)


def test_discover_address_extraction(poi_settings: Settings, tmp_path: Path) -> None:
    (tmp_path / "m.md").write_text("The plant at 2801 Centerville Road, Lima.\n", encoding="utf-8")
    cands = discover_candidates(roots=[tmp_path], settings=poi_settings)
    addrs = [c for c in cands if c.kind == "address"]

    assert any(c.normalized == "2801 CENTERVILLE ROAD" for c in addrs)
    assert all(not c.covered for c in addrs)  # only parcel-ids are coverage-checked


def test_discover_matches_scan_parcel_ids(poi_settings: Settings) -> None:
    # Divergence guard: discover's parcel set must equal allen_gis.scan_parcel_ids
    # over the same roots (the two parcel regexes mirror each other).
    roots = _default_roots(poi_settings)
    scan = set(scan_parcel_ids(*roots))
    disc = {c.value for c in discover_candidates(settings=poi_settings) if c.kind == "parcel-id"}
    assert disc == scan and scan  # same canonical parcel set, non-empty


def test_discover_corpus_marks_campus_covered(poi_settings: Settings) -> None:
    cands = discover_candidates(settings=poi_settings)
    by_norm = {c.normalized: c for c in cands if c.kind == "parcel-id"}

    # The campus parcels are cited in the corpus and covered by the seed composite POI…
    campus = by_norm.get("36010003002000")
    assert campus is not None and campus.covered is True
    # …and there is an uncovered worklist (other parcels cited but not yet POIs).
    assert any(not c.covered for c in by_norm.values())
