"""Live-data connectors for the hydrology subsystem.

Each connector is a pure, synchronous function ``fn(settings, ...) -> pydantic``
that fetches from an external service through :func:`_cache.cached_get` — which
adds on-disk caching, TTL, an offline mode, and a committed-fixture fallback so
tests and CI never touch the network.
"""

from __future__ import annotations

from bosc.hydrology.connectors._cache import HydroOfflineError, cached_get

__all__ = ["HydroOfflineError", "cached_get"]
