from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_dsn: str = "postgresql://rip_agent:rip_agent@localhost:5432/rip_agent"

    llamaparse_api_key: str = ""

    embedding_model_name: str = "intfloat/multilingual-e5-large"

    litellm_model: str = "anthropic/claude-sonnet-4-6"
    litellm_judge_model: str = "anthropic/claude-sonnet-4-6"
    anthropic_api_key: str = ""

    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 100

    retrieval_top_k_dense: int = 10
    retrieval_top_k_bm25: int = 10
    retrieval_rrf_k: int = 60

    otel_exporter_endpoint: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
