"""AERMET/AERMAP preprocessing connectors: offline fixture replay + emitters (#1179)."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import httpx
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from watermark.air.connectors import aermap, aermet, igra, isd, ned
from watermark.air.connectors._cache import AirOfflineError
from watermark.config import Settings

# --- ISD surface ---------------------------------------------------------------------


def test_isd_surface_offline(air_settings: Settings) -> None:
    surf = isd.fetch_surface(settings=air_settings)

    assert surf.station_id == "725330-14827"
    assert surf.call_sign == "KFWA"
    assert surf.latitude == pytest.approx(40.978, abs=0.001)
    assert surf.longitude == pytest.approx(-85.195, abs=0.001)
    assert surf.elevation_m == pytest.approx(250.0)
    assert surf.year == 2023
    assert 0 < surf.coverage_fraction() < 0.01  # a few fixture hours of 8760

    first = surf.observations[0]
    assert first.time == "2023-01-01T00:00:00Z"
    assert first.wind_dir_deg == 180
    assert first.wind_speed_ms == pytest.approx(5.0)
    assert first.air_temp_c == pytest.approx(-1.1)
    assert first.dew_point_c == pytest.approx(-4.5)
    assert first.ceiling_m == 22000
    assert first.sea_level_pressure_hpa == pytest.approx(1015.2)
    # Raw ISHD text is passed through verbatim for the AERMET surface input.
    assert surf.raw_ishd.strip().splitlines()[0].startswith("0100725330")


def test_isd_missing_sentinels_become_none(air_settings: Settings) -> None:
    surf = isd.fetch_surface(settings=air_settings)
    last = surf.observations[-1]  # the all-nines sentinel line
    assert last.wind_dir_deg is None
    assert last.wind_speed_ms is None
    assert last.air_temp_c is None
    assert last.ceiling_m is None
    assert last.sea_level_pressure_hpa is None


def test_isd_offline_unfetched_station_raises(air_settings: Settings) -> None:
    with pytest.raises(AirOfflineError) as exc:
        isd.fetch_surface(station="999999-99999", year=2023, settings=air_settings)
    assert "isd" in str(exc.value)


def test_isd_bad_station_raises() -> None:
    with pytest.raises(ValueError, match="USAF-WBAN"):
        isd.fetch_surface(station="notastation", settings=Settings())


def _obs(
    time: str, *, wind: float | None = 3.0, temp: float | None = 10.0
) -> isd.SurfaceObservation:
    return isd.SurfaceObservation(
        time=time,
        wind_dir_deg=180,
        wind_speed_ms=wind,
        air_temp_c=temp,
        dew_point_c=None,
        ceiling_m=None,
        sea_level_pressure_hpa=None,
    )


def _series(year: int, observations: list[isd.SurfaceObservation]) -> isd.SurfaceSeries:
    return isd.SurfaceSeries(
        station_id="725330-14827",
        usaf="725330",
        wban="14827",
        call_sign="KFWA",
        latitude=40.978,
        longitude=-85.195,
        elevation_m=250.0,
        year=year,
        observations=observations,
        raw_ishd="",
    )


def _every_hour(year: int, *, skip_months: tuple[int, ...] = ()) -> list[isd.SurfaceObservation]:
    start = datetime(year, 1, 1)
    hours = (datetime(year + 1, 1, 1) - start) // timedelta(hours=1)
    stamps = (start + timedelta(hours=h) for h in range(hours))
    return [_obs(t.strftime("%Y-%m-%dT%H:51:00Z")) for t in stamps if t.month not in skip_months]


def test_isd_coverage_counts_distinct_hours_not_observations() -> None:
    # AQ-07's reproduction: 9000 obs stamped in the SAME hour (METAR + SPECI specials) used
    # to report 102.7% "coverage". It is one covered hour.
    surf = _series(2023, [_obs("2023-03-01T12:00:00Z")] * 9000)
    cov = surf.coverage()
    assert cov.covered_hours == 1
    assert cov.fraction < 0.001
    assert surf.coverage_fraction() == cov.fraction


def test_isd_coverage_uses_the_years_real_hour_count() -> None:
    cov = _series(2024, _every_hour(2024)).coverage()  # leap year
    assert cov.hours == 8784
    assert cov.covered_hours == 8784
    assert cov.fraction == 1.0
    assert [q.hours for q in cov.quarters] == [2184, 2184, 2208, 2208]
    assert _series(2023, []).coverage().hours == 8760


def test_isd_coverage_ignores_hours_without_wind_and_temperature() -> None:
    surf = _series(
        2023,
        [
            _obs("2023-01-01T00:00:00Z", wind=None),  # all-nines wind
            _obs("2023-01-01T01:00:00Z", temp=None),  # all-nines temperature
            _obs("2023-01-01T02:00:00Z"),
            _obs("2022-12-31T23:00:00Z"),  # boundary hour from the previous year
        ],
    )
    assert surf.coverage().covered_hours == 1


def test_isd_coverage_reports_a_gapped_quarter_the_annual_figure_hides() -> None:
    # Missing all of February: 91.9% annual recovery clears 90%, but Q1 does not.
    cov = _series(2023, _every_hour(2023, skip_months=(2,))).coverage()
    assert cov.fraction > isd.COVERAGE_FLOOR
    assert not cov.meets_floor
    assert [q.quarter for q in cov.short_quarters] == [1]
    assert cov.quarters[0].fraction == pytest.approx(1488 / 2160, abs=0.001)  # Jan + Mar = 62 days


@pytest.mark.parametrize(("q1_hours", "short"), [(1943, True), (1944, False)])
def test_isd_coverage_floor_uses_the_unrounded_fraction(q1_hours: int, short: bool) -> None:
    # 1943/2160 = 89.95%, which rounds to 0.900 for display but is below the 90% floor.
    every = _every_hour(2023)
    q1 = [o for o in every if o.time[5:7] in ("01", "02", "03")]
    rest = [o for o in every if o.time[5:7] not in ("01", "02", "03")]
    cov = _series(2023, q1[:q1_hours] + rest).coverage()
    assert cov.quarters[0].hours == 2160
    assert cov.quarters[0].fraction == 0.9  # rounded display value, identical at both counts
    assert ([q.quarter for q in cov.short_quarters] == [1]) is short
    assert cov.meets_floor is not short


def test_aermet_refuses_below_the_recovery_floor(air_settings: Settings, tmp_path: Path) -> None:
    ua = igra.fetch_upperair(settings=air_settings)
    surf = _series(2023, _every_hour(2023, skip_months=(2,)))
    out = tmp_path / "aermet"
    with pytest.raises(aermet.InsufficientMetCoverageError, match="Q1"):
        aermet.write_aermet_inputs(surf, ua, out_dir=out, site_label="lima")
    assert not out.exists()  # refused before writing anything

    staged = aermet.write_aermet_inputs(
        surf, ua, out_dir=out, site_label="lima", allow_incomplete=True
    )
    assert staged.coverage_override is True
    runstream = Path(staged.runstream_path).read_text()
    assert "BELOW the 90% per-quarter recovery floor" in runstream
    assert "SCREENING ONLY" in runstream


def test_aermet_stages_a_fully_recovered_year(air_settings: Settings, tmp_path: Path) -> None:
    ua = igra.fetch_upperair(settings=air_settings)
    inputs = aermet.write_aermet_inputs(
        _series(2023, _every_hour(2023)), ua, out_dir=tmp_path, site_label="lima"
    )
    assert inputs.coverage_override is False
    assert inputs.surface_coverage_fraction == 1.0
    runstream = Path(inputs.runstream_path).read_text()
    assert "** Surface recovery: 8760/8760 h (100.0%)" in runstream
    assert "BELOW" not in runstream


# --- IGRA upper air ------------------------------------------------------------------


def test_igra_upperair_offline(air_settings: Settings) -> None:
    ua = igra.fetch_upperair(settings=air_settings)

    assert ua.station_id == "USM00072426"
    assert ua.latitude == pytest.approx(40.978, abs=0.001)
    assert ua.longitude == pytest.approx(-85.195, abs=0.001)
    # The fixture payload is already year-filtered (what fetch() caches): all soundings 2023.
    assert {s.time[:4] for s in ua.soundings} == {"2023"}
    assert len(ua.soundings) == 4

    s0 = ua.soundings[0]
    assert s0.time == "2023-01-01T00:00:00Z"
    assert s0.release_time == "00:00"
    assert s0.n_levels == 4
    lev = s0.levels[0]
    assert lev.pressure_hpa == pytest.approx(1013.0)
    assert lev.height_m == 250
    assert lev.temperature_c == pytest.approx(1.5)
    assert lev.dewpoint_depression_c == pytest.approx(2.0)
    assert lev.wind_dir_deg == 270
    assert lev.wind_speed_ms == pytest.approx(3.5)


def test_igra_filter_year_drops_other_years() -> None:
    header_2022 = "#USM00072426 2022 01 01 00 0000    1 x        x         409780 -0851950"
    header_2023 = "#USM00072426 2023 06 15 12 1200    1 x        x         409780 -0851950"
    level = "21 -9999 101300A  250A   15A   50   20    270    35"
    text = "\n".join([header_2022, level, header_2023, level])
    filtered = igra._filter_year(text, 2023)
    assert "2023" in filtered
    assert "2022" not in filtered


def test_igra_offline_unfetched_station_raises(air_settings: Settings) -> None:
    with pytest.raises(AirOfflineError):
        igra.fetch_upperair(station="USM00099999", year=2023, settings=air_settings)


# --- NED terrain ---------------------------------------------------------------------


def test_ned_terrain_offline(air_settings: Settings) -> None:
    dom = ned.fetch_terrain(settings=air_settings)
    assert dom.source == "fixture DEM (offline)"
    assert dom.epsg == 4326
    assert dom.width > 0 and dom.height > 0
    assert dom.bbox[0] < dom.center_lon < dom.bbox[2]

    pts = ned.sample_points(dom, [("REC1", dom.center_lat, dom.center_lon), ("OUT", 10.0, 10.0)])
    assert pts[0].elevation_m is not None and pts[0].elevation_m > 0
    assert pts[1].elevation_m is None  # outside the DEM domain


def _ramp_dem(path: Path, *, width: int = 8, height: int = 6) -> tuple[float, float, float]:
    """A synthetic Area-referenced DEM whose value is ``10*col + row`` at each pixel centre."""
    west, north, cell = -84.0, 41.0, 0.01
    rows, cols = np.mgrid[0:height, 0:width]
    data = (10.0 * cols + rows).astype("float32")
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(west, north, cell, cell),
    ) as dst:
        dst.write(data, 1)
    return west, north, cell


def test_ned_bilinear_samples_pixel_centres(tmp_path: Path) -> None:
    # AQ-22: a pixel's value belongs to its centre. Sampling exactly at the centre of pixel
    # (row 2, col 3) must return that pixel's value, not a blend half a pixel south-east.
    path = tmp_path / "ramp.tif"
    west, north, cell = _ramp_dem(path)

    def centre(row: float, col: float) -> tuple[float, float]:
        return north - (row + 0.5) * cell, west + (col + 0.5) * cell  # (lat, lon)

    dom = ned.TerrainDomain(
        center_lat=0.0,
        center_lon=0.0,
        bbox=(west, north - 6 * cell, west + 8 * cell, north),
        epsg=4326,
        width=8,
        height=6,
        cell_size_deg=cell,
        dem_path=str(path),
        source="test",
    )
    pts = [
        ("C23", *centre(2, 3)),
        ("MID", *centre(2.5, 3.25)),  # between centres: analytically 10*3.25 + 2.5
        ("FIRST", *centre(0, 0)),
        ("LAST", *centre(5, 7)),
        ("RING", north - 0.25 * cell, west + 0.25 * cell),  # outer half-pixel: no 4 neighbours
    ]
    got = {p.id: p.elevation_m for p in ned.sample_points(dom, pts)}
    assert got["C23"] == pytest.approx(32.0)
    assert got["MID"] == pytest.approx(35.0)
    assert got["FIRST"] == pytest.approx(0.0)
    assert got["LAST"] == pytest.approx(75.0)
    assert got["RING"] is None


def _live_ned_settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path, air_offline=False)


def test_ned_json_error_body_is_not_cached(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # AQ-21: ArcGIS reports a failed exportImage as HTTP 200 + JSON. It must raise, naming the
    # endpoint's message, and leave nothing at the cache key to be served on the next run.
    settings = _live_ned_settings(tmp_path)
    body = {"error": {"code": 400, "message": "Unable to complete operation.", "details": ["x"]}}

    def fake_get(url: str, **_: object) -> httpx.Response:
        return httpx.Response(200, json=body, request=httpx.Request("GET", url))

    monkeypatch.setattr(ned.httpx, "get", fake_get)
    with pytest.raises(ned.NedExportError, match="Unable to complete operation"):
        ned.fetch_terrain(center_lat=40.7, center_lon=-84.1, settings=settings)
    cache = settings.air_cache_dir / "ned"
    assert not any(cache.glob("*")) if cache.exists() else True


def test_ned_truncated_tiff_is_not_cached(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _live_ned_settings(tmp_path)

    def fake_get(url: str, **_: object) -> httpx.Response:
        return httpx.Response(200, content=b"II*\x00garbage", request=httpx.Request("GET", url))

    monkeypatch.setattr(ned.httpx, "get", fake_get)
    with pytest.raises(ned.NedExportError, match="unreadable GeoTIFF"):
        ned.fetch_terrain(center_lat=40.7, center_lon=-84.1, settings=settings)
    cache = settings.air_cache_dir / "ned"
    assert not any(cache.glob("*")) if cache.exists() else True


def test_ned_non_object_json_body_keeps_the_excerpt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A JSON body that is not an object (a list) must not crash the diagnostic path.
    settings = _live_ned_settings(tmp_path)

    def fake_get(url: str, **_: object) -> httpx.Response:
        return httpx.Response(200, json=["service busy"], request=httpx.Request("GET", url))

    monkeypatch.setattr(ned.httpx, "get", fake_get)
    with pytest.raises(ned.NedExportError, match="service busy"):
        ned.fetch_terrain(center_lat=40.7, center_lon=-84.1, settings=settings)
    cache = settings.air_cache_dir / "ned"
    assert not any(cache.glob("*")) if cache.exists() else True


def test_ned_corrupt_later_block_is_not_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The first tile decodes (so a one-pixel probe would pass); the last tile does not.
    settings = _live_ned_settings(tmp_path)
    src = tmp_path / "tiled.tif"
    with rasterio.open(
        src,
        "w",
        driver="GTiff",
        width=64,
        height=64,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(-84.2, 40.8, 0.001, 0.001),
        tiled=True,
        blockxsize=16,
        blockysize=16,
        compress="deflate",
    ) as dst:
        dst.write(np.arange(64 * 64, dtype="float32").reshape(64, 64), 1)
    with rasterio.open(src) as s:
        off = int(s.get_tag_item("BLOCK_OFFSET_3_3", "TIFF", bidx=1))
        size = int(s.get_tag_item("BLOCK_SIZE_3_3", "TIFF", bidx=1))
    body = bytearray(src.read_bytes())
    body[off : off + size] = b"\xff" * size
    corrupt = tmp_path / "corrupt.tif"
    corrupt.write_bytes(bytes(body))
    with rasterio.open(corrupt) as s:
        s.read(1, window=((0, 1), (0, 1)))  # the first block is intact

    def fake_get(url: str, **_: object) -> httpx.Response:
        return httpx.Response(200, content=bytes(body), request=httpx.Request("GET", url))

    monkeypatch.setattr(ned.httpx, "get", fake_get)
    with pytest.raises(ned.NedExportError, match="unreadable GeoTIFF"):
        ned.fetch_terrain(center_lat=40.7, center_lon=-84.1, settings=settings)
    cache = settings.air_cache_dir / "ned"
    assert not any(cache.glob("*")) if cache.exists() else True


def test_ned_valid_geotiff_is_cached_and_reused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _live_ned_settings(tmp_path)
    src = tmp_path / "src.tif"
    _ramp_dem(src)
    calls: list[str] = []

    def fake_get(url: str, **_: object) -> httpx.Response:
        calls.append(url)
        return httpx.Response(200, content=src.read_bytes(), request=httpx.Request("GET", url))

    monkeypatch.setattr(ned.httpx, "get", fake_get)
    first = ned.fetch_terrain(center_lat=40.7, center_lon=-84.1, settings=settings)
    again = ned.fetch_terrain(center_lat=40.7, center_lon=-84.1, settings=settings)
    assert first.source == "USGS 3DEP ImageServer"
    assert again.source == "USGS 3DEP ImageServer (cached)"
    assert len(calls) == 1


def test_ned_offline_miss_raises(air_settings: Settings) -> None:
    with pytest.raises(AirOfflineError):
        ned.fetch_terrain(center_lat=0.0, center_lon=0.0, settings=air_settings)


# --- AERMET emitter ------------------------------------------------------------------


def test_aermet_emitter_stages_inputs(air_settings: Settings, tmp_path: Path) -> None:
    surf = isd.fetch_surface(settings=air_settings)
    ua = igra.fetch_upperair(settings=air_settings)
    # The fixture is a handful of hours — far below the recovery floor — so stage it as a
    # screening run (the floor itself is exercised by the coverage tests below).
    inputs = aermet.write_aermet_inputs(
        surf, ua, out_dir=tmp_path, site_label="lima", allow_incomplete=True
    )

    assert inputs.surface_station == "725330-14827"
    assert inputs.upperair_station == "USM00072426"
    assert inputs.start_date == "2023-01-01"
    assert inputs.n_soundings == 4

    runstream = Path(inputs.runstream_path).read_text()
    assert "SURFACE" in runstream and "ISHD" in runstream
    assert "UPPERAIR" in runstream and "IGRA" in runstream
    assert "MERGE" in runstream
    # METPREP surface characteristics stay a commented template — never fabricated met.
    assert "** METPREP" in runstream
    assert "\nMETPREP" not in runstream
    # The surface file is the raw ISHD, byte-for-byte.
    assert Path(inputs.surface_path).read_text(encoding="latin-1") == surf.raw_ishd


def test_aermet_utc_offset_override(air_settings: Settings, tmp_path: Path) -> None:
    surf = isd.fetch_surface(settings=air_settings)
    ua = igra.fetch_upperair(settings=air_settings)
    inputs = aermet.write_aermet_inputs(
        surf, ua, out_dir=tmp_path, site_label="lima", utc_offset=5, allow_incomplete=True
    )
    assert inputs.utc_offset == 5


# --- AERMAP emitter ------------------------------------------------------------------


def test_aermap_build_offline(air_settings: Settings, tmp_path: Path) -> None:
    outputs = aermap.build_aermap(out_dir=tmp_path, site_label="lima", settings=air_settings)

    assert outputs.n_points == 1
    assert outputs.utm_epsg == 32617  # Lima UTM 17N, profile-filled
    assert outputs.dem_source == "fixture DEM (offline)"
    assert outputs.elevations[0].elevation_m is not None

    # Exact control-file lines — malformed formatting (missing DATATYPE/RUNORNOT, a bad
    # ANCHORXY, or a dropped pathway prefix) must fail the test, not just a keyword search.
    control = Path(outputs.control_path).read_text().splitlines()
    assert "CO DATATYPE  NED" in control
    assert "CO DATAFILE  47ab9dcd154a7e01.tif" in control
    assert "CO ANCHORXY  237399.8 4514549.0 237399.8 4514549.0 17 0" in control
    assert "CO RUNORNOT  RUN" in control
    assert "SO LOCATION  REC1  POINT  237399.8 4514549.0" in control
    assert "RE DISCCART  237399.8 4514549.0" in control

    elev_doc = Path(outputs.elevations_path).read_text()
    assert "[derived]" in elev_doc
    assert "aermap" in elev_doc
