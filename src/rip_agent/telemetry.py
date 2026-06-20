from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace import Tracer

from rip_agent.config import get_settings

_initialized = False


def setup_telemetry(service_name: str) -> None:
    global _initialized
    if _initialized:
        return

    settings = get_settings()
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))

    if settings.otel_exporter_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint)
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _initialized = True


def get_tracer(name: str) -> Tracer:
    return trace.get_tracer(name)
