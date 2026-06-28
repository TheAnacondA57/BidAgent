import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.node_store import NodeStore
from rip_agent.schemas.document import DocumentNode


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


def _section(node_id: str, parent_id: str | None = None) -> DocumentNode:
    return DocumentNode(
        id=node_id,
        document_id="doc-1",
        document_source_path="f.pdf",
        parent_id=parent_id,
        node_type="section",
        header_level=1,
        section_title="Titre",
        text="Texte de section",
        position=0,
        token_count=3,
    )


def _leaf(node_id: str, parent_id: str | None = None) -> DocumentNode:
    return DocumentNode(
        id=node_id,
        document_id="doc-1",
        document_source_path="f.pdf",
        parent_id=parent_id,
        node_type="leaf",
        header_level=0,
        section_title=None,
        text="texte de feuille",
        position=1,
        token_count=3,
    )


def test_ensure_schema_creates_doc_nodes_table_with_correct_dim() -> None:
    conn = FakeConnection()
    store = NodeStore(settings=Settings(embedding_dim=512), connection_factory=lambda: conn)

    store.ensure_schema()

    assert any("VECTOR(512)" in sql for sql in conn.executed_sql)
    assert any("doc_nodes" in sql for sql in conn.executed_sql)


def test_ensure_schema_creates_parent_id_index() -> None:
    conn = FakeConnection()
    store = NodeStore(settings=Settings(), connection_factory=lambda: conn)

    store.ensure_schema()

    assert any("doc_nodes_parent_idx" in sql for sql in conn.executed_sql)


def test_insert_nodes_section_has_null_embedding() -> None:
    conn = FakeConnection()
    store = NodeStore(settings=Settings(), connection_factory=lambda: conn)
    section = _section("sec-1")

    store.insert_nodes([section], leaf_embeddings={})

    _, rows = conn.cursor_calls[0]
    assert rows[0]["embedding"] is None


def test_insert_nodes_leaf_gets_its_embedding() -> None:
    conn = FakeConnection()
    store = NodeStore(settings=Settings(), connection_factory=lambda: conn)
    leaf = _leaf("leaf-1", parent_id="sec-1")
    emb = np.array([0.1, 0.2, 0.3])

    store.insert_nodes([leaf], leaf_embeddings={"leaf-1": emb})

    _, rows = conn.cursor_calls[0]
    assert rows[0]["embedding"] == [0.1, 0.2, 0.3]


def test_insert_nodes_preserves_parent_id_and_node_type() -> None:
    conn = FakeConnection()
    store = NodeStore(settings=Settings(), connection_factory=lambda: conn)
    section = _section("sec-1")
    leaf = _leaf("leaf-1", parent_id="sec-1")

    store.insert_nodes([section, leaf], leaf_embeddings={"leaf-1": np.zeros(3)})

    _, rows = conn.cursor_calls[0]
    sec_row = next(r for r in rows if r["id"] == "sec-1")
    leaf_row = next(r for r in rows if r["id"] == "leaf-1")

    assert sec_row["node_type"] == "section"
    assert sec_row["parent_id"] is None
    assert leaf_row["node_type"] == "leaf"
    assert leaf_row["parent_id"] == "sec-1"


def test_insert_nodes_sends_all_nodes_in_one_executemany() -> None:
    conn = FakeConnection()
    store = NodeStore(settings=Settings(), connection_factory=lambda: conn)
    nodes = [_section("s1"), _leaf("l1", "s1"), _leaf("l2", "s1")]
    embeddings = {"l1": np.zeros(3), "l2": np.ones(3)}

    store.insert_nodes(nodes, leaf_embeddings=embeddings)

    assert len(conn.cursor_calls) == 1
    _, rows = conn.cursor_calls[0]
    assert len(rows) == 3
