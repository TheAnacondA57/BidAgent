from rip_agent.retrieval.hybrid import fuse
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk


def _chunk(chunk_id: str) -> Chunk:
    return Chunk(id=chunk_id, document_id="d1", text=f"texte {chunk_id}", position=0, token_count=2)


def _retrieved(chunk_id: str, dense_score: float | None = None, bm25_score: float | None = None) -> RetrievedChunk:
    return RetrievedChunk(chunk=_chunk(chunk_id), dense_score=dense_score, bm25_score=bm25_score)


def test_fuse_ranks_chunk_found_in_both_lists_highest() -> None:
    dense = [_retrieved("c1", dense_score=0.9), _retrieved("c2", dense_score=0.5)]
    bm25 = [_retrieved("c2", bm25_score=0.8), _retrieved("c1", bm25_score=0.3)]

    fused = fuse(dense, bm25, k=60)

    assert [r.chunk.id for r in fused] == ["c1", "c2"]
    assert fused[0].fused_score == 1 / 61 + 1 / 62


def test_fuse_keeps_score_from_the_list_a_chunk_appears_in() -> None:
    dense = [_retrieved("c1", dense_score=0.9)]
    bm25 = [_retrieved("c2", bm25_score=0.8)]

    fused = fuse(dense, bm25, k=60)
    by_id = {r.chunk.id: r for r in fused}

    assert by_id["c1"].dense_score == 0.9
    assert by_id["c1"].bm25_score is None
    assert by_id["c2"].bm25_score == 0.8
    assert by_id["c2"].dense_score is None


def test_fuse_merges_scores_for_chunk_present_in_both_lists() -> None:
    dense = [_retrieved("c1", dense_score=0.9)]
    bm25 = [_retrieved("c1", bm25_score=0.7)]

    fused = fuse(dense, bm25, k=60)

    assert fused[0].dense_score == 0.9
    assert fused[0].bm25_score == 0.7
