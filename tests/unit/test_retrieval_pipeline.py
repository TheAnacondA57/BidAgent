import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.embedder import Embedder
from rip_agent.retrieval.pipeline import RetrievalPipeline
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievalQuery, RetrievedChunk


class FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool) -> np.ndarray:
        return np.zeros((len(texts), 2))


def _retrieved(chunk_id: str) -> RetrievedChunk:
    chunk = Chunk(id=chunk_id, document_id="d1", text="texte", position=0, token_count=1)
    return RetrievedChunk(chunk=chunk)


def test_run_calls_bm25_and_dense_with_resolved_top_k_then_fuses() -> None:
    calls: dict[str, tuple] = {}

    def fake_bm25(question: str, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        calls["bm25"] = (question, top_k)
        return [_retrieved("bm25-1")]

    def fake_dense(query_embedding: np.ndarray, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        calls["dense"] = (top_k,)
        return [_retrieved("dense-1")]

    def fake_fuse(dense: list[RetrievedChunk], bm25: list[RetrievedChunk], k: int) -> list[RetrievedChunk]:
        calls["fuse"] = (len(dense), len(bm25), k)
        return dense + bm25

    pipeline = RetrievalPipeline(
        settings=Settings(retrieval_top_k_bm25=5, retrieval_top_k_dense=8, retrieval_rrf_k=60),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=fake_bm25,
        dense_search_fn=fake_dense,
        fuse_fn=fake_fuse,
    )

    results = pipeline.run(RetrievalQuery(question="durée du contrat ?"))

    assert calls["bm25"] == ("durée du contrat ?", 5)
    assert calls["dense"] == (8,)
    assert calls["fuse"] == (1, 1, 60)
    assert [r.chunk.id for r in results] == ["dense-1", "bm25-1"]


def test_run_uses_query_top_k_over_settings_default() -> None:
    calls: dict[str, tuple] = {}

    def fake_bm25(question: str, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        calls["bm25_top_k"] = top_k
        return []

    def fake_dense(query_embedding: np.ndarray, top_k: int, settings: Settings) -> list[RetrievedChunk]:
        calls["dense_top_k"] = top_k
        return []

    pipeline = RetrievalPipeline(
        settings=Settings(retrieval_top_k_bm25=5, retrieval_top_k_dense=8),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        bm25_search_fn=fake_bm25,
        dense_search_fn=fake_dense,
        fuse_fn=lambda dense, bm25, k: [],
    )

    pipeline.run(RetrievalQuery(question="question", top_k_bm25=1, top_k_dense=2))

    assert calls["bm25_top_k"] == 1
    assert calls["dense_top_k"] == 2
