from rip_agent.generation.context import select_within_budget
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk


def _word_count(text: str) -> int:
    return len(text.split())


def _retrieved(chunk_id: str, text: str) -> RetrievedChunk:
    chunk = Chunk(id=chunk_id, document_id="d1", document_source_path="contrat.pdf", text=text, position=0, token_count=0)
    return RetrievedChunk(chunk=chunk)


def test_select_within_budget_keeps_chunks_until_budget_exhausted() -> None:
    chunks = [_retrieved("c1", "un deux trois"), _retrieved("c2", "quatre cinq"), _retrieved("c3", "six")]

    selected = select_within_budget(chunks, max_tokens=4, token_counter=_word_count)

    assert [r.chunk.id for r in selected] == ["c1"]


def test_select_within_budget_keeps_first_chunk_even_if_it_exceeds_budget() -> None:
    chunks = [_retrieved("c1", "un deux trois quatre cinq")]

    selected = select_within_budget(chunks, max_tokens=2, token_counter=_word_count)

    assert [r.chunk.id for r in selected] == ["c1"]


def test_select_within_budget_returns_all_when_under_budget() -> None:
    chunks = [_retrieved("c1", "un deux"), _retrieved("c2", "trois quatre")]

    selected = select_within_budget(chunks, max_tokens=100, token_counter=_word_count)

    assert [r.chunk.id for r in selected] == ["c1", "c2"]
