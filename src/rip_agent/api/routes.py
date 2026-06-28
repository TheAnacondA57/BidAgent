from fastapi import APIRouter, Depends
from opentelemetry.trace import format_span_id

from rip_agent.api.deps import get_rag_pipeline
from rip_agent.rag.pipeline import RAGPipeline
from rip_agent.schemas.api import QueryRequest, SpanData, TraceResponse
from rip_agent.schemas.generation import Answer
from rip_agent.telemetry import get_spans_for_trace, get_tracer

router = APIRouter()
_tracer = get_tracer(__name__)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/query", response_model=Answer)
def query(request: QueryRequest, rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)) -> Answer:
    return rag_pipeline.answer(request.question)


@router.post("/query/trace", response_model=TraceResponse)
def query_with_trace(
    request: QueryRequest, rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
) -> TraceResponse:
    with _tracer.start_as_current_span("rag_request") as root_span:
        trace_id = root_span.get_span_context().trace_id
        answer = rag_pipeline.answer(request.question)

    raw_spans = get_spans_for_trace(trace_id)
    t_origin = min((s.start_time or 0 for s in raw_spans), default=0)

    spans = [
        SpanData(
            name=s.name,
            span_id=format_span_id(s.context.span_id),
            parent_span_id=format_span_id(s.parent.span_id) if s.parent else None,
            start_ms=((s.start_time or 0) - t_origin) / 1_000_000,
            duration_ms=((s.end_time or 0) - (s.start_time or 0)) / 1_000_000,
            attributes={
                k: v
                for k, v in (s.attributes or {}).items()
                if isinstance(v, (str, int, float, bool))
            },
        )
        for s in sorted(raw_spans, key=lambda x: x.start_time or 0)
    ]

    total_ms = next(
        (s.duration_ms for s in spans if s.name == "rag_request"),
        max((s.start_ms + s.duration_ms for s in spans), default=0.0),
    )

    return TraceResponse(answer=answer, spans=spans, total_ms=total_ms)
