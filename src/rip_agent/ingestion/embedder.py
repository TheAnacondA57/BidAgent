from typing import Any, Protocol

import numpy as np

from rip_agent.config import Settings, get_settings


class EmbeddingModel(Protocol):
    def encode(self, texts: list[str], normalize_embeddings: bool) -> Any: ...


class Embedder:
    """Loads the SentenceTransformers model once and embeds batches of text.

    `model` can be injected to bypass the real (heavy) model load in tests.
    """

    def __init__(self, settings: Settings | None = None, model: EmbeddingModel | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = model

    @property
    def model(self) -> EmbeddingModel:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._settings.embedding_model_name)
        return self._model

    def embed(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True))
