from fastapi import APIRouter, Depends

from rip_agent.api.deps import get_rag_pipeline
from rip_agent.rag.pipeline import RAGPipeline
from rip_agent.schemas.api import QueryRequest
from rip_agent.schemas.generation import Answer

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/query", response_model=Answer)
def query(request: QueryRequest, rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)) -> Answer:
    return rag_pipeline.answer(request.question)
