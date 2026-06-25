"""Small shared helpers for the connectors (#601)."""

from __future__ import annotations

from typing import Any, overload


@overload
def to_float(value: Any) -> float | None: ...
@overload
def to_float(value: Any, default: float) -> float: ...
def to_float(value: Any, default: float | None = None) -> float | None:
    """Parse ``value`` to ``float``; return ``default`` (``None`` unless given) on a
    ``TypeError``/``ValueError``. The one home for the connectors' numeric coercion —
    callers that want a non-optional float pass an explicit ``default``."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
