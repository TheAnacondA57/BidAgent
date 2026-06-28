import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.embedder import Embedder
from rip_agent.retrieval.tree_pipeline import TreeRetrievalPipeline
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievalQuery, RetrievedChunk


class FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool) -> np.ndarray:
        return np.zeros((len(texts), 2))


def _retrieved(chunk_id: str, fused_score: float = 0.0) -> RetrievedChunk:
    chunk = Chunk(id=chunk_id, document_id="d1", text="texte", position=0, token_count=1)
    return RetrievedChunk(chunk=chunk, fused_score=fused_score)


def test_run_calls_bm25_dense_fuse_expand_in_order() -> None:
    call_order: list[str] = []

    def fake_bm25(question: str, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        call_order.append("bm25")
        return [_retrieved("bm25-1")]

    def fake_dense(query_embedding: np.ndarray, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        call_order.append("dense")
        return [_retrieved("dense-1")]

    def fake_fuse(
        dense: list[RetrievedChunk], bm25: list[RetrievedChunk], k: int
    ) -> list[RetrievedChunk]:
        call_order.append("fuse")
        return dense + bm25

    def fake_expand(fused: list[RetrievedChunk], settings: Settings | None = None) -> list[RetrievedChunk]:
        call_order.append("expand")
        return fused

    pipeline = TreeRetrievalPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=fake_bm25,
        dense_search_fn=fake_dense,
        fuse_fn=fake_fuse,
        expand_fn=fake_expand,
    )

    results = pipeline.run(RetrievalQuery(question="durée du contrat ?"))

    assert call_order == ["bm25", "dense", "fuse", "expand"]
    assert len(results) == 2


def test_run_passes_correct_top_k_to_search_functions() -> None:
    received: dict[str, int] = {}

    def fake_bm25(question: str, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        received["bm25"] = top_k
        return []

    def fake_dense(query_embedding: np.ndarray, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        received["dense"] = top_k
        return []

    pipeline = TreeRetrievalPipeline(
        settings=Settings(retrieval_top_k_bm25=7, retrieval_top_k_dense=12),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=fake_bm25,
        dense_search_fn=fake_dense,
        fuse_fn=lambda d, b, k: [],
        expand_fn=lambda chunks, settings=None: chunks,
    )

    pipeline.run(RetrievalQuery(question="question"))

    assert received["bm25"] == 7
    assert received["dense"] == 12


def test_run_uses_query_top_k_over_settings_default() -> None:
    received: dict[str, int] = {}

    def fake_bm25(question: str, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        received["bm25"] = top_k
        return []

    def fake_dense(query_embedding: np.ndarray, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        received["dense"] = top_k
        return []

    pipeline = TreeRetrievalPipeline(
        settings=Settings(retrieval_top_k_bm25=20, retrieval_top_k_dense=20),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=fake_bm25,
        dense_search_fn=fake_dense,
        fuse_fn=lambda d, b, k: [],
        expand_fn=lambda chunks, settings=None: chunks,
    )

    pipeline.run(RetrievalQuery(question="?", top_k_bm25=3, top_k_dense=5))

    assert received["bm25"] == 3
    assert received["dense"] == 5


def test_run_passes_fused_results_to_expand() -> None:
    fused_received: list[RetrievedChunk] = []
    fused_chunks = [_retrieved("leaf-1", 0.9), _retrieved("leaf-2", 0.4)]

    def fake_expand(chunks: list[RetrievedChunk], settings: Settings | None = None) -> list[RetrievedChunk]:
        fused_received.extend(chunks)
        return chunks

    pipeline = TreeRetrievalPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=lambda q, k, settings: [],
        dense_search_fn=lambda e, k, settings: [],
        fuse_fn=lambda d, b, k: fused_chunks,
        expand_fn=fake_expand,
    )

    pipeline.run(RetrievalQuery(question="?"))

    assert len(fused_received) == 2
    assert [r.chunk.id for r in fused_received] == ["leaf-1", "leaf-2"]


def test_tree_retrieval_pipeline_satisfies_rag_pipeline_contract() -> None:
    """TreeRetrievalPipeline must expose run(RetrievalQuery) -> list[RetrievedChunk]."""
    pipeline = TreeRetrievalPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=lambda q, k, settings: [],
        dense_search_fn=lambda e, k, settings: [],
        fuse_fn=lambda d, b, k: [],
        expand_fn=lambda chunks, settings=None: [],
    )

    result = pipeline.run(RetrievalQuery(question="test"))
    assert isinstance(result, list)
