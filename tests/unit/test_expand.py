from collections import namedtuple

from rip_agent.config import Settings
from rip_agent.retrieval.expand import expand_to_parent, fetch_parents
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk

_Column = namedtuple("Column", ["name"])
_PARENT_COLUMNS = [
    "leaf_id", "id", "document_id", "document_source_path",
    "text", "section_title", "position", "token_count",
]


def _chunk(chunk_id: str, text: str = "texte") -> Chunk:
    return Chunk(
        id=chunk_id, document_id="d1", document_source_path="f.pdf",
        text=text, section_title=None, position=0, token_count=1,
    )


def _retrieved(chunk_id: str, fused_score: float = 0.0) -> RetrievedChunk:
    return RetrievedChunk(chunk=_chunk(chunk_id), fused_score=fused_score)


class FakeCursor:
    def __init__(self, rows: list[tuple], calls: list) -> None:
        self.description = [_Column(name=n) for n in _PARENT_COLUMNS]
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


# ── fetch_parents ─────────────────────────────────────────────────────────────

def test_fetch_parents_returns_empty_for_no_leaf_ids() -> None:
    result = fetch_parents([], settings=Settings(), connection_factory=lambda: FakeConnection([]))
    assert result == {}


def test_fetch_parents_maps_leaf_id_to_parent_chunk() -> None:
    rows = [("leaf-1", "parent-1", "d1", "f.pdf", "contexte large", "Article 1", 0, 3)]
    conn = FakeConnection(rows)

    result = fetch_parents(["leaf-1"], settings=Settings(), connection_factory=lambda: conn)

    assert "leaf-1" in result
    parent = result["leaf-1"]
    assert parent.id == "parent-1"
    assert parent.text == "contexte large"
    assert parent.section_title == "Article 1"


def test_fetch_parents_passes_leaf_ids_as_param() -> None:
    conn = FakeConnection([])

    fetch_parents(["leaf-1", "leaf-2"], settings=Settings(), connection_factory=lambda: conn)

    _, params = conn.calls[0]
    assert params["leaf_ids"] == ["leaf-1", "leaf-2"]


def test_fetch_parents_uses_cte_joining_doc_nodes() -> None:
    conn = FakeConnection([])

    fetch_parents(["leaf-1"], settings=Settings(), connection_factory=lambda: conn)

    sql, _ = conn.calls[0]
    assert "doc_nodes" in sql
    assert "parent_id" in sql


# ── expand_to_parent ──────────────────────────────────────────────────────────

def test_expand_replaces_leaf_with_its_parent() -> None:
    parent = _chunk("parent-1", text="texte agrégé de la section")
    fake_fetch = lambda leaf_ids, **_: {"leaf-1": parent}

    results = expand_to_parent([_retrieved("leaf-1", fused_score=0.5)], fetch_parents_fn=fake_fetch)

    assert len(results) == 1
    assert results[0].chunk.id == "parent-1"
    assert results[0].chunk.text == "texte agrégé de la section"
    assert results[0].fused_score == 0.5


def test_expand_returns_leaf_unchanged_when_no_parent() -> None:
    fake_fetch = lambda leaf_ids, **_: {}

    result = expand_to_parent([_retrieved("leaf-1", fused_score=0.7)], fetch_parents_fn=fake_fetch)

    assert len(result) == 1
    assert result[0].chunk.id == "leaf-1"


def test_expand_deduplicates_leaves_sharing_same_parent() -> None:
    parent = _chunk("parent-1", text="section complète")
    fake_fetch = lambda leaf_ids, **_: {"leaf-1": parent, "leaf-2": parent}

    results = expand_to_parent(
        [_retrieved("leaf-1", fused_score=0.9), _retrieved("leaf-2", fused_score=0.4)],
        fetch_parents_fn=fake_fetch,
    )

    assert len(results) == 1
    assert results[0].chunk.id == "parent-1"
    assert results[0].fused_score == 0.9


def test_expand_keeps_highest_score_when_deduplicating() -> None:
    parent = _chunk("parent-1")
    fake_fetch = lambda leaf_ids, **_: {"leaf-1": parent, "leaf-2": parent}

    results = expand_to_parent(
        [_retrieved("leaf-1", fused_score=0.3), _retrieved("leaf-2", fused_score=0.8)],
        fetch_parents_fn=fake_fetch,
    )

    assert results[0].fused_score == 0.8


def test_expand_output_is_sorted_by_fused_score_descending() -> None:
    parent_a = _chunk("parent-a")
    parent_b = _chunk("parent-b")
    fake_fetch = lambda leaf_ids, **_: {"leaf-1": parent_a, "leaf-2": parent_b}

    results = expand_to_parent(
        [_retrieved("leaf-1", fused_score=0.6), _retrieved("leaf-2", fused_score=0.9)],
        fetch_parents_fn=fake_fetch,
    )

    scores = [r.fused_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_expand_mixes_expanded_and_non_expanded() -> None:
    parent = _chunk("parent-1")
    fake_fetch = lambda leaf_ids, **_: {"leaf-1": parent}

    results = expand_to_parent(
        [_retrieved("leaf-1", fused_score=0.8), _retrieved("leaf-2", fused_score=0.5)],
        fetch_parents_fn=fake_fetch,
    )

    ids = [r.chunk.id for r in results]
    assert "parent-1" in ids
    assert "leaf-2" in ids
