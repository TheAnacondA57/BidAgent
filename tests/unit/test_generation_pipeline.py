from rip_agent.config import Settings
from rip_agent.generation.llm import LLMClient
from rip_agent.generation.pipeline import GenerationPipeline
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk


def _retrieved(chunk_id: str, document_id: str = "d1", section_title: str | None = "Article 2") -> RetrievedChunk:
    chunk = Chunk(id=chunk_id, document_id=document_id, text="texte", section_title=section_title, position=0, token_count=2)
    return RetrievedChunk(chunk=chunk)


def _pipeline_with_fixed_answer(answer_text: str) -> GenerationPipeline:
    llm_client = LLMClient(settings=Settings(), completion_fn=lambda *, model, messages: answer_text)
    return GenerationPipeline(settings=Settings(), llm_client=llm_client)


def test_run_extracts_citations_from_answer_text() -> None:
    pipeline = _pipeline_with_fixed_answer("Le contrat dure 25 ans [abcdef01].")

    answer = pipeline.run("Quelle est la durée ?", [_retrieved("abcdef01")])

    assert answer.refused is False
    assert answer.text == "Le contrat dure 25 ans [abcdef01]."
    assert len(answer.citations) == 1
    assert answer.citations[0].chunk_id == "abcdef01"
    assert answer.citations[0].source_doc == "d1"
    assert answer.citations[0].source_section == "Article 2"


def test_run_detects_refusal_and_drops_citations() -> None:
    pipeline = _pipeline_with_fixed_answer("REFUS: le contexte ne contient pas l'information demandée.")

    answer = pipeline.run("Question hors corpus", [_retrieved("abcdef01")])

    assert answer.refused is True
    assert answer.citations == []


def test_run_ignores_citation_ids_not_in_retrieved_chunks() -> None:
    pipeline = _pipeline_with_fixed_answer("Réponse citant [abcdef01] et [00000000].")

    answer = pipeline.run("Question", [_retrieved("abcdef01")])

    assert [c.chunk_id for c in answer.citations] == ["abcdef01"]
