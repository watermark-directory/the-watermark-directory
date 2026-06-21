"""Allen County GIS parcel connector: ArcGIS parsing, date decode, offline replay."""

from __future__ import annotations

import pytest

from bosc.config import Settings
from bosc.hydrology.connectors import allen_gis
from bosc.hydrology.connectors._cache import HydroOfflineError


def test_fetch_parcel_from_fixture(hydro_settings: Settings) -> None:
    p = allen_gis.fetch_parcel("36-0100-03-001.000", settings=hydro_settings)
    assert p is not None
    assert p.parcel_no == "36010003001000"
    assert p.owner == "PATRICK DARLENE S TRUSTEE"
    assert p.situs_address == "N COLE ST"  # HOUSENO blank, dir+street+desc joined
    assert p.acres == pytest.approx(70.62)
    assert p.last_sale_date == "2020-12-21"  # decoded from the M(M)DDYYYY int
    # OWNADR2 already has city/state/zip — not duplicated.
    assert p.owner_address == "N COLE ST LIMA OH 45807"


def test_fetch_parcel_no_match_returns_none(hydro_settings: Settings) -> None:
    assert allen_gis.fetch_parcel("00-0000-00-000.000", settings=hydro_settings) is None


def test_normalize_parcel_id() -> None:
    assert allen_gis.normalize_parcel_id("36-0100-03-002.000") == "36010003002000"
    assert allen_gis.normalize_parcel_id("36010003002000") == "36010003002000"


def test_parse_parcel_date() -> None:
    assert allen_gis._parse_parcel_date(2252008) == "2008-02-25"  # M DD YYYY
    assert allen_gis._parse_parcel_date(8011994) == "1994-08-01"
    assert allen_gis._parse_parcel_date(12312020) == "2020-12-31"  # MM DD YYYY
    assert allen_gis._parse_parcel_date(0) is None
    assert allen_gis._parse_parcel_date(None) is None
    assert allen_gis._parse_parcel_date(99999999) is None  # invalid month/day


def test_scan_parcel_ids(tmp_path) -> None:  # type: ignore[no-untyped-def]
    (tmp_path / "deed.yaml").write_text(
        "parcel_ids:\n  - 36-0100-03-002.000\n  - 46-1300-04-001.005\n"
        "legal_description: Part of 36-1200-02-001.001; not a parcel 12-3.\n",
        encoding="utf-8",
    )
    ids = allen_gis.scan_parcel_ids(tmp_path)
    assert ids == ["36-0100-03-002.000", "36-1200-02-001.001", "46-1300-04-001.005"]


def test_offline_unfetched_parcel_raises(hydro_settings: Settings) -> None:
    with pytest.raises(HydroOfflineError):
        allen_gis.fetch_parcel("99-9999-99-999.999", settings=hydro_settings)


def _seed_primes(settings: Settings) -> list[tuple[str, list[str]]]:
    from bosc.candidates import load_defense_contractors

    dcl = load_defense_contractors(settings.entities_dir)
    assert dcl is not None
    return [(d.name, d.patterns) for d in dcl.defense_contractors]


def test_defense_owner_scan_finds_no_prime_owner(hydro_settings: Settings) -> None:
    # No Allen County parcel is owned by a DoD prime in its own name — the local
    # defense footprint is federally held, not prime-owned.
    hits = allen_gis.defense_owner_scan(_seed_primes(hydro_settings), settings=hydro_settings)
    assert hits == {}


def test_army_controlled_defense_land(hydro_settings: Settings) -> None:
    parcels = allen_gis.army_controlled_defense_land(settings=hydro_settings)
    assert len(parcels) == 5  # the JSMC / Lima Army Tank Plant cluster (Buckeye/Reed)
    by_no = {p.parcel_no: p for p in parcels}
    tank_plant = by_no["46110004005000"]  # 1151 Buckeye Rd
    assert tank_plant.owner == "UNITED STATES"
    assert tank_plant.acres == pytest.approx(133.78)
    assert "BUCKEYE" in (tank_plant.situs_address or "")
    assert all(p.tax_district == "L35" for p in parcels)


def test_decode_land_use_modes() -> None:
    # leading_int parses the numeric code out of Ohio's "<code>: <label>" StateLUC strings;
    # int (Lima's path) is unchanged.
    assert allen_gis._decode_land_use("511: Res-Custom Code", "leading_int") == 511
    assert allen_gis._decode_land_use("110: Agr-CAUV-Vacant Land", "leading_int") == 110
    assert allen_gis._decode_land_use(None, "leading_int") is None
    assert allen_gis._decode_land_use("n/a", "leading_int") is None
    assert allen_gis._decode_land_use("340", "int") == 340  # Lima's bare-code path, unchanged


def test_findlay_statewide_parcel_partial(hydro_settings: Settings) -> None:
    """Findlay's parcels come from the OGRIP Ohio statewide layer (Hancock-scoped, #237): a
    partial, owner-redacted catalog. id/situs/land-use/acreage decode by field name; owner, value,
    and sale are honestly absent. Replaying the committed fixture also proves the scoped request
    (``... AND County='Hancock'``) hashes to the recorded cache key — the zero-drift guard."""
    fs = hydro_settings.model_copy(update={"site": "findlay"})
    p = allen_gis.fetch_parcel("010001025254", settings=fs)
    assert p is not None
    assert p.parcel_no == "010001025254"
    assert p.land_use_code == 511  # "511: Res-Custom Code" -> leading_int decode
    assert p.acres == pytest.approx(5.01)
    assert p.situs_address == "199  COUNTY RD 140   NORTH BALTIMORE 45872"
    assert p.owner is None  # owner-name-redacted in the public statewide view
    assert p.owner_address == "JOHNSON CHARLES W & JOY M NORTH BALTIMORE 45872"  # the mailing label
    assert p.market_total_value is None and p.last_sale_date is None  # fields absent in this layer


def test_owner_search_refuses_on_owner_redacted_layer(hydro_settings: Settings) -> None:
    """A parcel layer with no owner field refuses owner search cleanly (never a malformed query)."""
    fs = hydro_settings.model_copy(update={"site": "findlay"})
    with pytest.raises(allen_gis.AllenGisError, match="no owner-name field"):
        allen_gis.parcels_by_owner("JOHNSON", settings=fs)


def test_dedupe_keeps_first_per_parcel_no() -> None:
    a = allen_gis.Parcel.from_attrs({"PARCEL_NO": "1", "OWNNAM1": "A"})
    dup = allen_gis.Parcel.from_attrs({"PARCEL_NO": "1", "OWNNAM1": "A2"})
    b = allen_gis.Parcel.from_attrs({"PARCEL_NO": "2", "OWNNAM1": "B"})
    out = allen_gis._dedupe([a, dup, b])
    assert [p.parcel_no for p in out] == ["1", "2"]
    assert out[0].owner == "A"  # first row wins
