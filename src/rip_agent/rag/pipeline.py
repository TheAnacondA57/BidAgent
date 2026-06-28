from rip_agent.config import Settings, get_settings
from rip_agent.generation.pipeline import GenerationPipeline
from rip_agent.retrieval._shared import RetrievalPipelineProtocol
from rip_agent.retrieval.pipeline import RetrievalPipeline
from rip_agent.schemas.generation import Answer
from rip_agent.schemas.retrieval import RetrievalQuery


class RAGPipeline:
    """Single entry point composing retrieval + generation.

    Accepts any retrieval pipeline that satisfies RetrievalPipelineProtocol
    (RetrievalPipeline or TreeRetrievalPipeline). Used by both the API and the
    evaluation harness so they exercise the exact same path.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        retrieval_pipeline: RetrievalPipelineProtocol | None = None,
        generation_pipeline: GenerationPipeline | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        if retrieval_pipeline is not None:
            self._retrieval_pipeline = retrieval_pipeline
        elif self._settings.use_tree_retrieval:
            from rip_agent.retrieval.tree_pipeline import TreeRetrievalPipeline
            self._retrieval_pipeline = TreeRetrievalPipeline(self._settings)
        else:
            self._retrieval_pipeline = RetrievalPipeline(self._settings)
        self._generation_pipeline = generation_pipeline or GenerationPipeline(self._settings)

    def answer(self, question: str) -> Answer:
        chunks = self._retrieval_pipeline.run(RetrievalQuery(question=question))
        return self._generation_pipeline.run(question, chunks)
