from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from typing import Any

import numpy as np

from rip_agent.config import Settings, get_settings
from rip_agent.db import default_connection_factory
from rip_agent.schemas.document import Chunk

_SCHEMA_SQL_TEMPLATE = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL,
    document_source_path TEXT NOT NULL,
    text TEXT NOT NULL,
    section_title TEXT,
    position INT NOT NULL,
    token_count INT NOT NULL,
    embedding VECTOR({embedding_dim}) NOT NULL,
    text_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('french', text)) STORED
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_text_tsv_idx ON chunks USING gin (text_tsv);
"""

_INSERT_SQL = """
INSERT INTO chunks (id, document_id, document_source_path, text, section_title, position, token_count, embedding)
VALUES (%(id)s, %(document_id)s, %(document_source_path)s, %(text)s, %(section_title)s, %(position)s, %(token_count)s, %(embedding)s)
ON CONFLICT (id) DO NOTHING
"""


class PgVectorStore:
    """Owns the `chunks` table: schema (vector column + generated tsvector for BM25)
    and inserts. `connection_factory` can be injected to test SQL generation without
    a real Postgres instance.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        connection_factory: Callable[[], AbstractContextManager[Any]] | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._connection_factory = connection_factory or default_connection_factory(
            self._settings.postgres_dsn
        )

    def ensure_schema(self) -> None:
        sql = _SCHEMA_SQL_TEMPLATE.format(embedding_dim=self._settings.embedding_dim)
        with self._connection_factory() as conn:
            conn.execute(sql)

    def insert_chunks(self, chunks: Sequence[Chunk], embeddings: np.ndarray) -> None:
        rows = [
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "document_source_path": chunk.document_source_path,
                "text": chunk.text,
                "section_title": chunk.section_title,
                "position": chunk.position,
                "token_count": chunk.token_count,
                "embedding": embeddings[i].tolist(),
            }
            for i, chunk in enumerate(chunks)
        ]
        with self._connection_factory() as conn:
            with conn.cursor() as cur:
                cur.executemany(_INSERT_SQL, rows)
