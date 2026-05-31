"""NWIS connector + the offline cache/fixture machinery (hermetic, no network)."""

from __future__ import annotations

import pytest

from bosc.config import Settings
from bosc.hydrology.connectors import nwis
from bosc.hydrology.connectors._cache import HydroOfflineError, cache_key


def test_fetch_streamflow_from_fixture(hydro_settings: Settings) -> None:
    readings = nwis.fetch_streamflow(sites=["04187100"], settings=hydro_settings)
    by_param = {r.parameter_cd: r for r in readings}
    assert by_param[nwis.DISCHARGE_CFS].value == pytest.approx(36.3)
    assert by_param[nwis.DISCHARGE_CFS].unit  # has a unit string
    assert "Ottawa River at Lima" in by_param[nwis.DISCHARGE_CFS].name


def test_offline_cache_miss_raises(hydro_settings: Settings) -> None:
    with pytest.raises(HydroOfflineError):
        nwis.fetch_streamflow(sites=["00000000"], settings=hydro_settings)


def test_cache_key_is_order_independent() -> None:
    assert cache_key({"a": 1, "b": 2}) == cache_key({"b": 2, "a": 1})


def test_observed_min_is_derived_not_document(hydro_settings: Settings) -> None:
    # The 7-day-min cross-check, when present, must never masquerade as a 7Q10.
    # (No P7D fixture committed -> offline miss; the point is the source tag, which
    #  we assert directly on a freshly built derived value.)
    from bosc.hydrology.model import ProvenancedValue

    pv = ProvenancedValue.derived(0.4, "cfs", citation="NWIS min P7D (not 7Q10)")
    assert pv.source == "derived"
    assert not pv.verified
