from collections import namedtuple

import numpy as np

from rip_agent.config import Settings
from rip_agent.retrieval.dense import dense_search

_Column = namedtuple("Column", ["name"])
_COLUMNS = ["id", "document_id", "text", "section_title", "position", "token_count", "score"]


class FakeCursor:
    def __init__(self, rows: list[tuple], calls: list[tuple[str, dict]]) -> None:
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
        self.calls: list[tuple[str, dict]] = []

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._rows, self.calls)


def test_dense_search_maps_rows_to_retrieved_chunks() -> None:
    fake_conn = FakeConnection(rows=[("c1", "d1", "texte article 1", "Article 1", 0, 3, 0.87)])

    results = dense_search(
        np.array([0.1, 0.2, 0.3]),
        top_k=5,
        settings=Settings(),
        connection_factory=lambda: fake_conn,
    )

    assert len(results) == 1
    assert results[0].chunk.id == "c1"
    assert results[0].dense_score == 0.87
    assert results[0].bm25_score is None
    assert results[0].fused_score == 0.0


def test_dense_search_formats_embedding_as_pgvector_literal() -> None:
    fake_conn = FakeConnection(rows=[])

    dense_search(
        np.array([0.1, 0.2]),
        top_k=3,
        settings=Settings(),
        connection_factory=lambda: fake_conn,
    )

    sql, params = fake_conn.calls[0]
    assert params["query_embedding"] == "[0.1,0.2]"
    assert params["top_k"] == 3
    assert "::vector" in sql
