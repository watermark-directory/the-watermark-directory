"""Tests for the EPA RSEI per-county reduction (`bosc rsei`)."""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

from bosc import rsei
from bosc.config import Settings
from bosc.rsei import RseiFacility, RseiInventory
from bosc.site.rsei import render_rsei

REPO_ROOT = Path(__file__).resolve().parents[1]


def _gdls(**kw: object) -> RseiFacility:
    base: dict[str, object] = {
        "facility_id": "GD1",
        "facility_number": "1",
        "name": "GENERAL DYNAMICS LAND SYSTEMS",
        "parent_name": "GENERAL DYNAMICS",
        "fips": "39003",
    }
    base.update(kw)
    return RseiFacility(**base)  # type: ignore[arg-type]


def test_render_rsei_zero_score_gdls_does_not_divide_by_zero() -> None:
    """#617: a GDLS facility reporting pounds but a zero modeled Score must not crash
    the corridor highlight (which divides by Score for the cancer share)."""
    inv = RseiInventory(
        meta={},
        county_fips="39003",
        county_name="Allen",
        facilities=[_gdls(score=0.0, cancer_score=0.0, pounds=1234.0)],
    )
    md = render_rsei(inv)  # must not raise ZeroDivisionError
    # The score-ranked corridor highlight is omitted when there's no score to rank by.
    assert "cancer-driven" not in md


def test_render_rsei_scored_gdls_renders_highlight() -> None:
    """The corridor highlight renders (with the cancer share) when Score is non-zero."""
    inv = RseiInventory(
        meta={},
        county_fips="39003",
        county_name="Allen",
        facilities=[_gdls(score=200.0, cancer_score=150.0)],
    )
    md = render_rsei(inv)
    assert "cancer-driven" in md
    assert "75% cancer-driven" in md  # 100 * 150 / 200


def _write_gz(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="latin-1", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _seed_tables(settings: Settings) -> None:
    """Write a tiny self-consistent RSEI table set into the (offline) cache."""
    base = settings.rsei_cache_dir / settings.rsei_version / "data_tables"
    _write_gz(
        base / "media.csv.gz",
        [
            {"Media": "1", "MediaCode": "1"},  # air
            {"Media": "3", "MediaCode": "3"},  # direct water
        ],
    )
    _write_gz(
        base / "chemical.csv.gz",
        [
            {
                "ChemicalNumber": "100",
                "Chemical": "Nickel and nickel compounds",
                "CASStandard": "7440-02-0",
                "ToxicityCategory": "Carcinogen",
            },
            {
                "ChemicalNumber": "200",
                "Chemical": "Toluene",
                "CASStandard": "108-88-3",
                "ToxicityCategory": "Non-carcinogen",
            },
        ],
    )
    _write_gz(
        base / "facility.csv.gz",
        [
            {
                "FacilityID": "ACME1",
                "FacilityNumber": "1",
                "FacilityName": "ACME FORGE",
                "ParentName": "ACME CORP",
                "FederalFacilityFlag": "",
                "Latitude": "40.7",
                "Longitude": "-84.1",
                "Street": "1 MAIN ST",
                "City": "LIMA",
                "State": "OH",
                "FIPS": "39003",
                "NPDESPermit": "OH0001234",
                "NAICS1": "331110",
                "DerivedNAICS": "0",
                "SIC1": "3462",
                "DerivedSIC": "0",
                "WaterReleases": "1",
            },
            {
                "FacilityID": "OTHER",
                "FacilityNumber": "2",
                "FacilityName": "OUT OF COUNTY",
                "ParentName": "X",
                "FederalFacilityFlag": "",
                "Latitude": "0",
                "Longitude": "0",
                "Street": "",
                "City": "",
                "State": "OH",
                "FIPS": "39999",
                "NPDESPermit": "NA",
                "NAICS1": "0",
                "DerivedNAICS": "0",
                "SIC1": "0",
                "DerivedSIC": "0",
                "WaterReleases": "0",
            },
        ],
    )
    _write_gz(
        base / "submission.csv.gz",
        [
            {
                "SubmissionNumber": "S1",
                "FacilityNumber": "1",
                "ChemicalNumber": "100",
                "SubmissionYear": "2000",
            },
            {
                "SubmissionNumber": "S2",
                "FacilityNumber": "1",
                "ChemicalNumber": "200",
                "SubmissionYear": "2001",
            },
            {
                "SubmissionNumber": "S9",
                "FacilityNumber": "2",
                "ChemicalNumber": "100",
                "SubmissionYear": "2000",
            },
        ],
    )
    _write_gz(
        base / "release.csv.gz",
        [
            {
                "ReleaseNumber": "R1",
                "SubmissionNumber": "S1",
                "Media": "1",
                "PoundsReleased": "100",
            },
            {
                "ReleaseNumber": "R2",
                "SubmissionNumber": "S2",
                "Media": "3",
                "PoundsReleased": "50",
            },  # reported pounds, no modeled element
            {
                "ReleaseNumber": "R9",
                "SubmissionNumber": "S9",
                "Media": "1",
                "PoundsReleased": "999",
            },
        ],
    )
    _write_gz(
        base / "elements.csv.gz",
        [
            {
                "ElementNumber": "1",
                "ReleaseNumber": "R1",
                "Score": "1000",
                "CScore": "900",
                "NCScore": "100",
                "Hazard": "5000",
            },
            {
                "ElementNumber": "2",
                "ReleaseNumber": "R9",
                "Score": "777",
                "CScore": "777",
                "NCScore": "0",
                "Hazard": "1234",
            },  # out-of-county; must be dropped
        ],
    )


def test_build_inventory_joins_and_rolls_up(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "data", rsei_offline=True)
    _seed_tables(settings)

    inv = rsei.build_inventory(settings)

    # Only the in-county facility survives.
    assert inv.county_fips == "39003"
    assert [f.facility_number for f in inv.facilities] == ["1"]
    f = inv.facilities[0]

    # Pounds sum across both releases; Score only from the modeled element.
    assert f.pounds == 150.0
    assert f.score == 1000.0
    assert f.cancer_score == 900.0
    assert f.noncancer_score == 100.0
    assert f.hazard == 5000.0

    # Media split + provenance fields.
    assert f.pounds_by_media == {"air": 100.0, "water": 50.0}
    assert f.npdes_permit == "OH0001234"
    assert f.naics == "331110" and f.sic == "3462"  # NAICS1/SIC1, not the "0" Derived*
    assert f.water_releases is True

    # Per-year series spans both report years.
    assert [y.year for y in f.years] == [2000, 2001]
    assert {y.year: y.pounds for y in f.years} == {2000: 100.0, 2001: 50.0}

    # Top chemical is the modeled (scored) Nickel, ahead of unscored Toluene.
    assert f.top_chemicals[0].chemical.startswith("Nickel")
    assert f.top_chemicals[0].toxicity_category == "Carcinogen"

    assert inv.meta["scored_facility_count"] == 1


def test_committed_inventory_loads() -> None:
    """The committed Allen County inventory loads and has the expected shape."""
    inv = rsei.load_inventory(Settings().reference_dir)
    assert inv is not None, "data/reference/rsei/inventory.yaml is missing"
    assert inv.county_fips == "39003"
    assert len(inv.facilities) >= 40
    # Ranked descending by Score.
    scores = [f.score for f in inv.facilities]
    assert scores == sorted(scores, reverse=True)
    # The JSMC / GDLS defense footprint is present and scored.
    gdls = next((f for f in inv.facilities if "GENERAL DYNAMICS" in f.name.upper()), None)
    assert gdls is not None and gdls.score > 0
    assert gdls.parent_name == "GENERAL DYNAMICS"
