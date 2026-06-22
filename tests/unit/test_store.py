import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.store import PgVectorStore
from rip_agent.schemas.document import Chunk


class FakeCursor:
    def __init__(self, calls: list) -> None:
        self._calls = calls

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def executemany(self, sql: str, rows: list[dict]) -> None:
        self._calls.append((sql, rows))


class FakeConnection:
    def __init__(self) -> None:
        self.executed_sql: list[str] = []
        self.cursor_calls: list[tuple[str, list[dict]]] = []

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def execute(self, sql: str) -> None:
        self.executed_sql.append(sql)

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.cursor_calls)


def test_ensure_schema_creates_vector_column_with_configured_dim() -> None:
    fake_conn = FakeConnection()
    store = PgVectorStore(settings=Settings(embedding_dim=384), connection_factory=lambda: fake_conn)

    store.ensure_schema()

    assert any("VECTOR(384)" in sql for sql in fake_conn.executed_sql)
    assert any("tsvector" in sql for sql in fake_conn.executed_sql)


def test_insert_chunks_sends_one_row_per_chunk() -> None:
    fake_conn = FakeConnection()
    store = PgVectorStore(settings=Settings(), connection_factory=lambda: fake_conn)
    chunks = [
        Chunk(id="c1", document_id="d1", document_source_path="contrat.pdf", text="texte 1", section_title="Article 1", position=0, token_count=2),
        Chunk(id="c2", document_id="d1", document_source_path="contrat.pdf", text="texte 2", section_title="Article 1", position=1, token_count=2),
    ]
    embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])

    store.insert_chunks(chunks, embeddings)

    assert len(fake_conn.cursor_calls) == 1
    _, rows = fake_conn.cursor_calls[0]
    assert len(rows) == 2
    assert rows[0]["id"] == "c1"
    assert rows[0]["document_source_path"] == "contrat.pdf"
    assert rows[0]["embedding"] == [0.1, 0.2]
    assert rows[1]["embedding"] == [0.3, 0.4]
