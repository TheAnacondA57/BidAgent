import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.embedder import Embedder


class FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool) -> np.ndarray:
        return np.array([[float(len(t)), 0.0] for t in texts])


def test_embed_delegates_to_injected_model() -> None:
    embedder = Embedder(settings=Settings(), model=FakeModel())

    vectors = embedder.embed(["ab", "abcd"])

    assert vectors.shape == (2, 2)
    assert vectors[0][0] == 2.0
    assert vectors[1][0] == 4.0


def test_model_property_does_not_reload_when_injected() -> None:
    fake = FakeModel()
    embedder = Embedder(settings=Settings(), model=fake)

    assert embedder.model is fake
