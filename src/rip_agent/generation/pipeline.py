import re
from collections.abc import Callable

from rip_agent.config import Settings, get_settings
from rip_agent.generation.context import select_within_budget
from rip_agent.generation.llm import LLMClient
from rip_agent.generation.prompts import REFUSAL_PREFIX, build_answer_prompt
from rip_agent.schemas.generation import Answer, Citation
from rip_agent.schemas.retrieval import RetrievedChunk
from rip_agent.telemetry import get_tracer

_tracer = get_tracer(__name__)
_CITATION_RE = re.compile(r"\[([0-9a-fA-F-]{8,})\]")


class GenerationPipeline:
    """Builds the prompt, calls the LLM once, and parses the answer into
    citations + a refusal flag.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
        select_chunks_fn: Callable[[list[RetrievedChunk], int], list[RetrievedChunk]] = select_within_budget,
    ) -> None:
        self._settings = settings or get_settings()
        self._llm_client = llm_client or LLMClient(self._settings)
        self._select_chunks = select_chunks_fn

    def run(self, question: str, chunks: list[RetrievedChunk]) -> Answer:
        with _tracer.start_as_current_span("generation") as span:
            span.set_attribute("generation.question", question)

            chunks = self._select_chunks(chunks, self._settings.generation_context_max_tokens)
            span.set_attribute("generation.context_chunk_count", len(chunks))

            messages = build_answer_prompt(question, chunks)
            text = self._llm_client.complete(messages)

            refused = text.strip().startswith(REFUSAL_PREFIX)
            citations = [] if refused else self._extract_citations(text, chunks)

            span.set_attribute("generation.refused", refused)
            span.set_attribute("generation.citation_count", len(citations))

        return Answer(text=text, citations=citations, refused=refused)

    @staticmethod
    def _extract_citations(text: str, chunks: list[RetrievedChunk]) -> list[Citation]:
        chunks_by_id = {result.chunk.id: result.chunk for result in chunks}
        cited_ids = dict.fromkeys(_CITATION_RE.findall(text))

        return [
            Citation(
                chunk_id=chunk_id,
                source_doc=chunks_by_id[chunk_id].document_source_path,
                source_section=chunks_by_id[chunk_id].section_title,
            )
            for chunk_id in cited_ids
            if chunk_id in chunks_by_id
        ]
