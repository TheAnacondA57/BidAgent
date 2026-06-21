from rip_agent.generation.prompts import REFUSAL_PREFIX, build_answer_prompt
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk


def test_build_answer_prompt_includes_chunk_ids_and_question() -> None:
    chunk = Chunk(id="c1", document_id="d1", text="durée de 25 ans", section_title="Article 2", position=0, token_count=4)
    chunks = [RetrievedChunk(chunk=chunk)]

    messages = build_answer_prompt("Quelle est la durée du contrat ?", chunks)

    assert messages[0]["role"] == "system"
    assert REFUSAL_PREFIX in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "[c1]" in messages[1]["content"]
    assert "Article 2" in messages[1]["content"]
    assert "durée de 25 ans" in messages[1]["content"]
    assert "Quelle est la durée du contrat ?" in messages[1]["content"]


def test_build_answer_prompt_handles_no_chunks() -> None:
    messages = build_answer_prompt("Question sans contexte", [])

    assert "Question sans contexte" in messages[1]["content"]
