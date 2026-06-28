from collections import namedtuple

import numpy as np

from rip_agent.config import Settings
from rip_agent.retrieval.tree_dense import tree_dense_search

_Column = namedtuple("Column", ["name"])
_COLUMNS = ["id", "document_id", "document_source_path", "text", "section_title", "position", "token_count", "score"]


class FakeCursor:
    def __init__(self, rows: list[tuple], calls: list) -> None:
        self.description = [_Column(name=name) for name in _COLUMNS]
        self._rows = rows
        self._calls = calls

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def execute(self, sql: str, params: dict) -> None:
        self._calls.append((sql, params))

    def fetchall(self) -> list[tuple]:
        return self._rows


class FakeConnection:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows
        self.calls: list[tuple] = []

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._rows, self.calls)


def test_tree_dense_search_maps_rows_to_retrieved_chunks() -> None:
    rows = [("leaf-1", "doc-1", "contrat.pdf", "texte de la feuille", "Article 1", 0, 3, 0.92)]
    conn = FakeConnection(rows)

    results = tree_dense_search(
        np.array([0.1, 0.2, 0.3]),
        top_k=5,
        settings=Settings(),
        connection_factory=lambda: conn,
    )

    assert len(results) == 1
    assert results[0].chunk.id == "leaf-1"
    assert results[0].dense_score == 0.92
    assert results[0].bm25_score is None
    assert results[0].fused_score == 0.0


def test_tree_dense_search_formats_embedding_as_pgvector_literal() -> None:
    conn = FakeConnection([])

    tree_dense_search(
        np.array([0.1, 0.2, 0.3]),
        top_k=5,
        settings=Settings(),
        connection_factory=lambda: conn,
    )

    _, params = conn.calls[0]
    assert params["query_embedding"] == "[0.1,0.2,0.3]"
    assert params["top_k"] == 5


def test_tree_dense_search_queries_doc_nodes_leaf_with_embedding_filter() -> None:
    conn = FakeConnection([])

    tree_dense_search(np.zeros(3), top_k=5, settings=Settings(), connection_factory=lambda: conn)

    sql, _ = conn.calls[0]
    assert "doc_nodes" in sql
    assert "node_type = 'leaf'" in sql
    assert "embedding IS NOT NULL" in sql


def test_tree_dense_search_returns_empty_on_no_match() -> None:
    conn = FakeConnection([])

    results = tree_dense_search(np.zeros(3), top_k=5, settings=Settings(), connection_factory=lambda: conn)

    assert results == []
