from rip_agent.config import Settings, get_settings
from rip_agent.generation.pipeline import GenerationPipeline
from rip_agent.retrieval.pipeline import RetrievalPipeline
from rip_agent.schemas.generation import Answer
from rip_agent.schemas.retrieval import RetrievalQuery


class RAGPipeline:
    """Single entry point composing retrieval + generation.

    Used by both the API and the evaluation harness so they exercise the
    exact same path — the harness measures what the API actually serves.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        retrieval_pipeline: RetrievalPipeline | None = None,
        generation_pipeline: GenerationPipeline | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._retrieval_pipeline = retrieval_pipeline or RetrievalPipeline(self._settings)
        self._generation_pipeline = generation_pipeline or GenerationPipeline(self._settings)

    def answer(self, question: str) -> Answer:
        chunks = self._retrieval_pipeline.run(RetrievalQuery(question=question))
        return self._generation_pipeline.run(question, chunks)
