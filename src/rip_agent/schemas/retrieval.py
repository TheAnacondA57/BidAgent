from pydantic import BaseModel

from rip_agent.schemas.document import Chunk


class RetrievalQuery(BaseModel):
    question: str
    top_k_dense: int | None = None
    top_k_bm25: int | None = None


class RetrievedChunk(BaseModel):
    chunk: Chunk
    dense_score: float | None = None
    bm25_score: float | None = None
    fused_score: float = 0.0
