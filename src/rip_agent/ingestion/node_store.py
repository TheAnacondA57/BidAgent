from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from typing import Any

import numpy as np

from rip_agent.config import Settings, get_settings
from rip_agent.db import default_connection_factory
from rip_agent.schemas.document import DocumentNode

_SCHEMA_SQL_TEMPLATE = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS doc_nodes (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL,
    document_source_path TEXT NOT NULL,
    parent_id UUID REFERENCES doc_nodes(id),
    node_type TEXT NOT NULL CHECK (node_type IN ('section', 'leaf')),
    header_level INT NOT NULL,
    section_title TEXT,
    text TEXT NOT NULL,
    position INT NOT NULL,
    token_count INT NOT NULL,
    embedding VECTOR({embedding_dim}),
    text_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('french', text)) STORED
);

CREATE INDEX IF NOT EXISTS doc_nodes_leaf_emb_idx
    ON doc_nodes USING hnsw (embedding vector_cosine_ops)
    WHERE node_type = 'leaf' AND embedding IS NOT NULL;
CREATE INDEX IF NOT EXISTS doc_nodes_tsv_idx ON doc_nodes USING gin (text_tsv);
CREATE INDEX IF NOT EXISTS doc_nodes_parent_idx ON doc_nodes (parent_id);
"""

_INSERT_SQL = """
INSERT INTO doc_nodes
    (id, document_id, document_source_path, parent_id, node_type, header_level,
     section_title, text, position, token_count, embedding)
VALUES
    (%(id)s, %(document_id)s, %(document_source_path)s, %(parent_id)s, %(node_type)s,
     %(header_level)s, %(section_title)s, %(text)s, %(position)s, %(token_count)s, %(embedding)s)
ON CONFLICT (id) DO NOTHING
"""


class NodeStore:
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

    def insert_nodes(
        self,
        nodes: Sequence[DocumentNode],
        leaf_embeddings: dict[str, np.ndarray],
    ) -> None:
        """Nodes must be in topological order (parents before children) to satisfy
        the self-referencing FK constraint on parent_id.
        """
        rows = [
            {
                "id": node.id,
                "document_id": node.document_id,
                "document_source_path": node.document_source_path,
                "parent_id": node.parent_id,
                "node_type": node.node_type,
                "header_level": node.header_level,
                "section_title": node.section_title,
                "text": node.text,
                "position": node.position,
                "token_count": node.token_count,
                "embedding": leaf_embeddings[node.id].tolist() if node.id in leaf_embeddings else None,
            }
            for node in nodes
        ]
        with self._connection_factory() as conn:
            with conn.cursor() as cur:
                cur.executemany(_INSERT_SQL, rows)
