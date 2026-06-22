from rip_agent.schemas.retrieval import RetrievedChunk


def compute_hit(chunks: list[RetrievedChunk], source_doc: str) -> bool:
    """True if any retrieved chunk comes from the expected source document."""
    return any(result.chunk.document_source_path == source_doc for result in chunks)


def aggregate_hit_rate(hits: list[bool]) -> float:
    if not hits:
        return 0.0
    return sum(hits) / len(hits)
