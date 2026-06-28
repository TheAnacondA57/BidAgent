from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from rip_agent.config import Settings, get_settings
from rip_agent.db import default_connection_factory
from rip_agent.retrieval._shared import chunk_from_row, rows_from_cursor
from rip_agent.schemas.retrieval import RetrievedChunk

_BM25_SQL = """
WITH q AS (
    SELECT to_tsquery('french', string_agg(lexeme, ' | ')) AS tsq
    FROM unnest(to_tsvector('french', %(question)s))
)
SELECT id, document_id, document_source_path, text, section_title, position, token_count,
       ts_rank_cd(text_tsv, q.tsq) AS score
FROM chunks, q
WHERE q.tsq IS NOT NULL AND text_tsv @@ q.tsq
ORDER BY score DESC
LIMIT %(top_k)s
"""


def bm25_search(
    question: str,
    top_k: int,
    settings: Settings | None = None,
    connection_factory: Callable[[], AbstractContextManager[Any]] | None = None,
) -> list[RetrievedChunk]:
    """Lexical search over the `text_tsv` column (French) using ts_rank_cd.

    `connection_factory` can be injected to test the query/mapping without a
    real Postgres instance.
    """
    settings = settings or get_settings()
    connection_factory = connection_factory or default_connection_factory(settings.postgres_dsn)

    with connection_factory() as conn:
        with conn.cursor() as cur:
            cur.execute(_BM25_SQL, {"question": question, "top_k": top_k})
            rows = rows_from_cursor(cur)

    return [
        RetrievedChunk(chunk=chunk_from_row(row), bm25_score=row["score"])
        for row in rows
    ]
