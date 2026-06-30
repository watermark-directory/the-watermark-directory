"""OpenTelemetry tracing helpers for the agent layer."""

from __future__ import annotations

import functools
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

import opentelemetry.trace

tracer = opentelemetry.trace.get_tracer(__name__)

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


def traced_tool(fn: F) -> F:
    """Wrap an async MCP tool function in a ``tool.<name>`` span."""

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        with tracer.start_as_current_span(f"tool.{fn.__name__}") as span:
            span.set_attribute("tool.name", fn.__name__)
            return await fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
