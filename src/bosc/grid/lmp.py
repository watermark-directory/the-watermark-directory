"""PJM Data Miner 2 zonal day-ahead LMP connector (#121, #124).

The live source for the campus's energy-price signal: PJM Data Miner 2's
``da_hrl_lmps`` feed (day-ahead hourly locational marginal price), reduced to a
**zonal period mean** that replaces the transcribed ``$35/MWh`` placeholder carried on
each :class:`bosc.sites.SiteProfile` (``lmp_usd_mwh``). Zonal because a site's pricing
zone is the right granularity for a screening view — LMP is nodal and time-varying; the
zone annual mean is "bracket, don't overclaim," not a bus-specific or peak-hour price.

Data discipline (the shared connector contract): a pure sync ``fn(..., settings) ->
pydantic`` over :func:`bosc.connectors.cached_get`, reusing the **econ** cache / offline
/ fixtures (the other grid connectors do). The PJM **subscription key** is read from
``settings.pjm_api_key`` (``BOSC_PJM_API_KEY``) and sent only as the live request's
``Ocp-Apim-Subscription-Key`` header — **never** in the cache key or a committed fixture.
Offline replays the committed fixture; an offline miss raises naming the key to record.

The zone is addressed by its **pnode_id** (the stable numeric id; the ``pnode_name``
filter is not honored server-side): AEP = ``8445784``, ATSI = ``116013753`` — carried per
site on the profile (``lmp_pnode_id`` / ``lmp_pnode_name``).
"""

from __future__ import annotations

from typing import Any, cast

import httpx
from pydantic import BaseModel, ConfigDict

from bosc.config import Settings, get_settings
from bosc.connectors import cached_get
from bosc.logging import get_logger

log = get_logger(__name__)

# Latest full calendar year — a reproducible annual window (8760 day-ahead hours per zone).
_PERIOD_START = "2025-01-01 00:00"
_PERIOD_END = "2025-12-31 23:59"
_ROW_COUNT = 9000  # >= 8760 hours/year, so one request returns the full window


class PjmLmpError(RuntimeError):
    """PJM Data Miner 2 returned an error, non-JSON, or no usable LMP rows."""


class ZonalLmp(BaseModel):
    """One PJM zone's day-ahead LMP, reduced to a period mean."""

    model_config = ConfigDict(extra="forbid")

    zone: str  # the pricing-zone name (e.g. "AEP", "ATSI")
    pnode_id: int  # the zone's PJM pricing-node id
    period_start: str
    period_end: str
    n_hours: int  # day-ahead hours with a price in the window
    mean_da_lmp_usd_mwh: float  # mean total day-ahead LMP ($/MWh) over the window


def _reduce(
    rows: list[dict[str, Any]], *, zone: str, pnode_id: int, start: str, end: str
) -> dict[str, Any]:
    """Reduce ``da_hrl_lmps`` rows to a zonal mean day-ahead LMP (the cached payload)."""
    vals = [r["total_lmp_da"] for r in rows if r.get("total_lmp_da") is not None]
    if not vals:
        raise PjmLmpError(
            f"PJM da_hrl_lmps returned no day-ahead LMP for pnode_id={pnode_id} {start}..{end}"
        )
    return {
        "zone": zone,
        "pnode_id": pnode_id,
        "period_start": start,
        "period_end": end,
        "n_hours": len(vals),
        "mean_da_lmp_usd_mwh": round(sum(vals) / len(vals), 4),
    }


def fetch_zonal_lmp(
    *,
    pnode_id: int,
    zone: str,
    start: str = _PERIOD_START,
    end: str = _PERIOD_END,
    settings: Settings | None = None,
) -> ZonalLmp:
    """One PJM zone's day-ahead LMP over ``[start, end]``, reduced to a period mean (cached)."""
    settings = settings or get_settings()
    # The cache key carries the request shape but NEVER the subscription key.
    params = {
        "connector": "pjm_lmp",
        "route": "da_hrl_lmps",
        "pnode_id": pnode_id,
        "start": start,
        "end": end,
    }

    def fetch() -> Any:
        log.info("pjm_lmp.fetch", pnode_id=pnode_id, zone=zone, start=start, end=end)
        if not settings.pjm_api_key:
            raise PjmLmpError(
                "no BOSC_PJM_API_KEY set — a PJM Data Miner 2 subscription key is required for "
                "live LMP pulls (offline replays committed fixtures)"
            )
        resp = httpx.get(
            f"{settings.pjm_base_url}/da_hrl_lmps",
            params={
                "rowCount": _ROW_COUNT,
                "startRow": 1,
                "datetime_beginning_ept": f"{start}to{end}",
                "type": "ZONE",
                "pnode_id": pnode_id,
                "fields": "datetime_beginning_ept,pnode_name,total_lmp_da",
                "format": "json",
            },
            headers={"Ocp-Apim-Subscription-Key": settings.pjm_api_key},
            timeout=settings.econ_request_timeout_s,
        )
        if resp.status_code in (401, 403):
            raise PjmLmpError(
                f"PJM Data Miner 2 rejected the subscription key (HTTP {resp.status_code})"
            )
        resp.raise_for_status()
        try:
            body = resp.json()
        except ValueError as exc:
            raise PjmLmpError(f"PJM da_hrl_lmps returned non-JSON: {resp.text[:80]!r}") from exc
        rows = (body or {}).get("items") if isinstance(body, dict) else body
        return _reduce(rows or [], zone=zone, pnode_id=pnode_id, start=start, end=end)

    payload = cast(
        "dict[str, Any]",
        cached_get(
            "pjm_lmp",
            params,
            fetch,
            cache_dir=settings.econ_cache_dir,
            offline=settings.econ_offline,
            fixtures_dir=settings.econ_fixtures_dir,
        ),
    )
    return ZonalLmp.model_validate(payload)
