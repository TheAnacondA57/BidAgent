from fastapi.testclient import TestClient

from rip_agent.api.deps import get_rag_pipeline
from rip_agent.api.main import app
from rip_agent.schemas.generation import Answer, Citation


class FakeRAGPipeline:
    def __init__(self, answer: Answer) -> None:
        self._answer = answer
        self.received_question: str | None = None

    def answer(self, question: str) -> Answer:
        self.received_question = question
        return self._answer


def test_health_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer_from_rag_pipeline() -> None:
    expected = Answer(
        text="Le contrat dure 25 ans [c1].",
        citations=[Citation(chunk_id="c1", source_doc="contrat.pdf", source_section="Article 2")],
        refused=False,
    )
    fake_pipeline = FakeRAGPipeline(expected)
    app.dependency_overrides[get_rag_pipeline] = lambda: fake_pipeline
    client = TestClient(app)

    try:
        response = client.post("/query", json={"question": "Quelle est la durée du contrat ?"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == expected.model_dump()
    assert fake_pipeline.received_question == "Quelle est la durée du contrat ?"
