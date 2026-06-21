from rip_agent.config import Settings
from rip_agent.rag.pipeline import RAGPipeline
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.generation import Answer
from rip_agent.schemas.retrieval import RetrievalQuery, RetrievedChunk


class FakeRetrievalPipeline:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self.chunks = chunks
        self.received_query: RetrievalQuery | None = None

    def run(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        self.received_query = query
        return self.chunks


class FakeGenerationPipeline:
    def __init__(self, answer: Answer) -> None:
        self._answer = answer
        self.received_args: tuple | None = None

    def run(self, question: str, chunks: list[RetrievedChunk]) -> Answer:
        self.received_args = (question, chunks)
        return self._answer


def test_answer_passes_retrieved_chunks_to_generation() -> None:
    chunk = Chunk(id="c1", document_id="d1", text="texte", position=0, token_count=1)
    retrieved = [RetrievedChunk(chunk=chunk)]
    expected_answer = Answer(text="réponse", citations=[], refused=False)

    retrieval_pipeline = FakeRetrievalPipeline(retrieved)
    generation_pipeline = FakeGenerationPipeline(expected_answer)

    pipeline = RAGPipeline(
        settings=Settings(),
        retrieval_pipeline=retrieval_pipeline,
        generation_pipeline=generation_pipeline,
    )

    answer = pipeline.answer("Quelle est la durée du contrat ?")

    assert answer is expected_answer
    assert retrieval_pipeline.received_query.question == "Quelle est la durée du contrat ?"
    assert generation_pipeline.received_args == ("Quelle est la durée du contrat ?", retrieved)
