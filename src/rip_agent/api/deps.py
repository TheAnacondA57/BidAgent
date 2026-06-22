from functools import lru_cache

from rip_agent.config import get_settings
from rip_agent.rag.pipeline import RAGPipeline


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline(get_settings())
