from rip_agent.schemas.retrieval import RetrievedChunk


def fuse(dense: list[RetrievedChunk], bm25: list[RetrievedChunk], k: int) -> list[RetrievedChunk]:
    """Reciprocal Rank Fusion: combines two ranked lists into one, scoring each
    chunk by the sum of 1/(k + rank) over the lists it appears in.
    """
    merged: dict[str, RetrievedChunk] = {}

    def add(results: list[RetrievedChunk]) -> None:
        for rank, result in enumerate(results, start=1):
            chunk_id = result.chunk.id
            existing = merged.get(chunk_id)
            contribution = 1.0 / (k + rank)

            if existing is None:
                merged[chunk_id] = result.model_copy(update={"fused_score": contribution})
                continue

            merged[chunk_id] = existing.model_copy(
                update={
                    "fused_score": existing.fused_score + contribution,
                    "dense_score": existing.dense_score if existing.dense_score is not None else result.dense_score,
                    "bm25_score": existing.bm25_score if existing.bm25_score is not None else result.bm25_score,
                }
            )

    add(dense)
    add(bm25)

    return sorted(merged.values(), key=lambda result: result.fused_score, reverse=True)
