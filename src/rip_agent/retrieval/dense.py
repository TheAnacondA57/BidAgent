from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import numpy as np

from rip_agent.config import Settings, get_settings
from rip_agent.db import default_connection_factory
from rip_agent.retrieval._shared import chunk_from_row, format_vector, rows_from_cursor
from rip_agent.schemas.retrieval import RetrievedChunk

_DENSE_SQL = """
SELECT id, document_id, document_source_path, text, section_title, position, token_count,
       1 - (embedding <=> %(query_embedding)s::vector) AS score
FROM chunks
ORDER BY embedding <=> %(query_embedding)s::vector
LIMIT %(top_k)s
"""


def dense_search(
    query_embedding: np.ndarray,
    top_k: int,
    settings: Settings | None = None,
    connection_factory: Callable[[], AbstractContextManager[Any]] | None = None,
) -> list[RetrievedChunk]:
    """Cosine similarity search over the `embedding` column.

    `connection_factory` can be injected to test the query/mapping without a
    real Postgres instance.
    """
    settings = settings or get_settings()
    connection_factory = connection_factory or default_connection_factory(settings.postgres_dsn)

    with connection_factory() as conn:
        with conn.cursor() as cur:
            cur.execute(
                _DENSE_SQL,
                {"query_embedding": format_vector(query_embedding), "top_k": top_k},
            )
            rows = rows_from_cursor(cur)

    return [
        RetrievedChunk(chunk=chunk_from_row(row), dense_score=row["score"])
        for row in rows
    ]
