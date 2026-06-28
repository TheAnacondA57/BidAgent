from typing import Any, Protocol

import numpy as np

from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievalQuery, RetrievedChunk


def chunk_from_row(row: dict[str, Any]) -> Chunk:
    return Chunk(
        id=row["id"],
        document_id=row["document_id"],
        document_source_path=row["document_source_path"],
        text=row["text"],
        section_title=row["section_title"],
        position=row["position"],
        token_count=row["token_count"],
    )


def rows_from_cursor(cur: Any) -> list[dict[str, Any]]:
    columns = [col.name for col in cur.description]
    return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


def format_vector(embedding: np.ndarray) -> str:
    """pgvector text input format, e.g. '[0.1,0.2,0.3]'."""
    return "[" + ",".join(repr(float(x)) for x in embedding) + "]"


class RetrievalPipelineProtocol(Protocol):
    def run(self, query: RetrievalQuery) -> list[RetrievedChunk]: ...
