from pydantic import BaseModel

from rip_agent.schemas.generation import Answer


class QueryRequest(BaseModel):
    question: str


class SpanData(BaseModel):
    name: str
    span_id: str
    parent_span_id: str | None
    start_ms: float
    duration_ms: float
    attributes: dict[str, str | int | float | bool]


class TraceResponse(BaseModel):
    answer: Answer
    spans: list[SpanData]
    total_ms: float
