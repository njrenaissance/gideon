"""OpenTelemetry setup for on-premise observability.

All telemetry data stays on-premise. No data leaves the host.

Usage — Traces and Spans
~~~~~~~~~~~~~~~~~~~~~~~~

A **trace** is a complete request lifecycle (e.g. an API call from start
to finish). A **span** is a unit of work within a trace (e.g. a database
query, an LLM call). Spans nest to form a tree.

To add custom spans in any module::

    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)

    async def ingest_document(doc):
        with tracer.start_as_current_span("ingest_document") as span:
            span.set_attribute("document.id", doc.id)
            span.set_attribute("document.type", doc.content_type)

            with tracer.start_as_current_span("extract_text"):
                text = await extract(doc)

            with tracer.start_as_current_span("embed_chunks"):
                chunks = await embed(text)

            span.set_attribute("document.chunk_count", len(chunks))

FastAPI requests are automatically traced via FastAPIInstrumentor
(configured in main.py).

Usage — Metrics
~~~~~~~~~~~~~~~

Use the module-level ``meter`` to create counters, histograms, etc.::

    from app.core.telemetry import meter

    doc_counter = meter.create_counter(
        "opencase.documents.ingested",
        description="Number of documents ingested",
    )
    doc_counter.add(1, {"matter_id": matter.id})
"""

import logging

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from app.core.config import Settings

logger = logging.getLogger(__name__)

_tracer_provider: TracerProvider | None = None

# Global meter for creating metrics instruments across the application.
meter = metrics.get_meter("opencase")


def setup_telemetry(settings: Settings) -> TracerProvider | None:
    """Configure OpenTelemetry tracing and metrics.

    Returns the TracerProvider if enabled, None otherwise.
    Idempotent: repeated calls return the cached provider.
    """
    global _tracer_provider  # noqa: PLW0603

    if not settings.otel.enabled:
        logger.info("OpenTelemetry disabled")
        return None

    if _tracer_provider is not None:
        return _tracer_provider

    resource = Resource.create(
        {
            "service.name": settings.otel.service_name,
            "service.version": settings.app_version,
        }
    )

    # Tracing
    sampler = TraceIdRatioBased(settings.otel.sample_rate)
    provider = TracerProvider(resource=resource, sampler=sampler)

    if settings.otel.exporter == "console":
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer_provider = provider

    # Metrics
    if settings.otel.exporter == "console":
        metric_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=60000,
        )
        meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(meter_provider)

    logger.info(
        "OpenTelemetry enabled: exporter=%s, service=%s",
        settings.otel.exporter,
        settings.otel.service_name,
    )
    return provider
