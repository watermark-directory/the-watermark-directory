"""Live NWIS smoke test — deselected by default. Run with: pytest -m network."""

from __future__ import annotations

import pytest

from watermark.config import Settings
from watermark.hydrology.connectors import nwis


@pytest.mark.network
def test_live_ottawa_at_lima_discharge() -> None:
    settings = Settings(hydro_offline=False)
    readings = nwis.fetch_streamflow(sites=["04187100"], settings=settings)
    discharge = next(r for r in readings if r.parameter_cd == nwis.DISCHARGE_CFS)
    assert discharge.value is not None
    assert 1.0 < discharge.value < 5000.0  # plausible Ottawa-at-Lima range (cfs)
