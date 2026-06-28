from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Tracer

from rip_agent.config import get_settings

_initialized = False
_span_store: InMemorySpanExporter | None = None


def setup_telemetry(service_name: str) -> None:
    global _initialized, _span_store
    if _initialized:
        return

    settings = get_settings()
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))

    if settings.otel_exporter_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint)
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))

    _span_store = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(_span_store))

    trace.set_tracer_provider(provider)
    _initialized = True


def get_spans_for_trace(trace_id: int) -> list[ReadableSpan]:
    if _span_store is None:
        return []
    return [s for s in _span_store.get_finished_spans() if s.context.trace_id == trace_id]


def get_tracer(name: str) -> Tracer:
    return trace.get_tracer(name)
