"""Structured logging setup, wired to :mod:`structlog`."""

from __future__ import annotations

import logging
import os
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from watermark.config import Settings

_configured = False
_tracing_configured = False


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog + stdlib logging once per process."""
    global _configured
    if _configured:
        return

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _inject_otel_context,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )
    _configured = True


def _inject_otel_context(
    logger: Any, method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Structlog processor: inject OTel trace_id/span_id when a span is active."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
    except ImportError:
        pass
    return event_dict


def configure_tracing(settings: Settings) -> None:
    """Initialize the OTel TracerProvider exporting to Honeycomb.

    No-ops when ``settings.otel_enabled`` is false, so the default path
    (``WATERMARK_OTEL_ENABLED`` unset) adds zero overhead.
    """
    global _tracing_configured
    if _tracing_configured or not settings.otel_enabled:
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.resource import ResourceAttributes

    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: "watermark-backend",
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: settings.otel_environment,
            "watermark.site": settings.site,
        }
    )
    exporter = OTLPSpanExporter(
        endpoint="https://api.honeycomb.io/v1/traces",
        headers={"x-honeycomb-team": settings.honeycomb_api_key},
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    if not settings.otel_trace_content:
        os.environ.setdefault("TRACELOOP_TRACE_CONTENT", "false")
    AnthropicInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    _tracing_configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
