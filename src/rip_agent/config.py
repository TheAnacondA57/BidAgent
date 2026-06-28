from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_dsn: str = "postgresql://rip_agent:rip_agent@localhost:5432/rip_agent"

    llamaparse_api_key: str = ""

    embedding_model_name: str = "intfloat/multilingual-e5-large"
    embedding_dim: int = 1024

    litellm_model: str = "openai/gpt-4o"
    litellm_judge_model: str = "openai/gpt-4o"
    openai_api_key: str = ""

    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 100

    retrieval_top_k_dense: int = 20
    retrieval_top_k_bm25: int = 20
    retrieval_rrf_k: int = 60

    generation_context_max_tokens: int = 12000

    use_tree_retrieval: bool = False

    otel_exporter_endpoint: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
