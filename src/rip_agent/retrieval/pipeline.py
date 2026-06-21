from collections.abc import Callable

import numpy as np

from rip_agent.config import Settings, get_settings
from rip_agent.ingestion.embedder import Embedder
from rip_agent.retrieval.bm25 import bm25_search
from rip_agent.retrieval.dense import dense_search
from rip_agent.retrieval.hybrid import fuse
from rip_agent.schemas.retrieval import RetrievalQuery, RetrievedChunk
from rip_agent.telemetry import get_tracer

_tracer = get_tracer(__name__)


class RetrievalPipeline:
    """Orchestrates bm25_search + dense_search + fuse for a single question.

    `bm25_search_fn`/`dense_search_fn`/`fuse_fn` are injectable so tests can
    run the orchestration logic without a real Postgres instance or embedding model.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        embedder: Embedder | None = None,
        bm25_search_fn: Callable[..., list[RetrievedChunk]] = bm25_search,
        dense_search_fn: Callable[..., list[RetrievedChunk]] = dense_search,
        fuse_fn: Callable[[list[RetrievedChunk], list[RetrievedChunk], int], list[RetrievedChunk]] = fuse,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedder = embedder or Embedder(self._settings)
        self._bm25_search = bm25_search_fn
        self._dense_search = dense_search_fn
        self._fuse = fuse_fn

    def run(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        top_k_bm25 = query.top_k_bm25 or self._settings.retrieval_top_k_bm25
        top_k_dense = query.top_k_dense or self._settings.retrieval_top_k_dense

        with _tracer.start_as_current_span("retrieval") as span:
            span.set_attribute("retrieval.question", query.question)

            bm25_results = self._bm25_search(query.question, top_k_bm25, settings=self._settings)

            query_embedding: np.ndarray = self._embedder.embed([query.question])[0]
            dense_results = self._dense_search(query_embedding, top_k_dense, settings=self._settings)

            fused = self._fuse(dense_results, bm25_results, self._settings.retrieval_rrf_k)

            span.set_attribute("retrieval.bm25_count", len(bm25_results))
            span.set_attribute("retrieval.dense_count", len(dense_results))
            span.set_attribute("retrieval.fused_count", len(fused))

        return fused
