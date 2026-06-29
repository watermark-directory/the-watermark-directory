"""POI curate: scaffold a merge group into a data/entities/poi/ profile (depth=located)."""

from __future__ import annotations

from pathlib import Path

import pytest

from watermark.config import Settings
from watermark.hydrology.connectors.allen_gis import Parcel
from watermark.poi.curate import CurateError, scaffold_from_group, write_profile
from watermark.poi.merge import MergeGroup, MergeMember
from watermark.poi.store import parse_poi


def _group() -> MergeGroup:
    parcel = Parcel.from_attrs(
        {
            "PARCEL_NO": "11111111111111",
            "OWNNAM1": "TEST OWNER",
            "HOUSENO": "100",
            "STREET": "MAIN",
            "ST_DESC": "ST",
            "ACRES": "5.0",
        }
    )
    members = [
        MergeMember(
            kind="parcel-id",
            value="11-1111-11-111.111",
            citations=["data/extracted/a.yaml", "data/extracted/b.yaml"],
            method="parcel-id",
            confidence="high",
            auto_mergeable=True,
        )
    ]
    return MergeGroup(
        parcel_no="11111111111111",
        parcel=parcel,
        members=members,
        has_exact_id=True,
        covered=False,
        status="auto",
    )


def test_scaffold_from_group() -> None:
    front, body = scaffold_from_group(_group(), asof="2026-06-09")
    assert front.kind == "parcel"
    assert front.depth == "located"  # scaffolds at located; human promotes
    assert front.slug == "parcel-11111111111111"
    assert front.parcels == ["11-1111-11-111.111"]  # deed format, as cited
    assert front.name == "100 MAIN ST"  # CAMA situs
    assert front.location is not None
    assert front.location.method == "parcel-cama" and front.location.confidence == "high"
    assert front.location.bbox is None  # no AOI until promoted to watched
    assert [sf.type for sf in front.surface_forms] == ["parcel-id"]
    assert front.surface_forms[0].resolved_parcel == "11111111111111"
    assert [r.role for r in front.relationships] == ["owner"]
    assert front.relationships[0].entity == "TEST OWNER"
    assert set(front.citations) == {"data/extracted/a.yaml", "data/extracted/b.yaml"}
    assert "11-1111-11-111.111" in body


def test_write_profile_roundtrips(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)
    front, body = scaffold_from_group(_group(), asof="2026-06-09")
    path = write_profile(front, body, settings=settings)
    assert path == tmp_path / "entities" / "poi" / "parcel-11111111111111.md"

    parsed = parse_poi(path)  # the written frontmatter must re-validate
    assert parsed.front.name == "100 MAIN ST"
    assert parsed.front.depth == "located"
    assert parsed.front.parcels == ["11-1111-11-111.111"]
    assert parsed.front.surface_forms[0].resolved_parcel == "11111111111111"
    assert parsed.tracked is False  # located, not watched


def test_write_profile_refuses_overwrite(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)
    front, body = scaffold_from_group(_group(), asof="2026-06-09")
    write_profile(front, body, settings=settings)
    with pytest.raises(CurateError):
        write_profile(front, body, settings=settings)  # exists, no force
    write_profile(front, body, settings=settings, force=True)  # force overwrites
