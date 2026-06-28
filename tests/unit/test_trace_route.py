from contextlib import contextmanager

from fastapi.testclient import TestClient

from rip_agent.api.deps import get_rag_pipeline
from rip_agent.api.main import app
from rip_agent.schemas.generation import Answer, Citation


class _FakePipeline:
    def answer(self, question: str) -> Answer:
        return Answer(
            text="La durée est de 25 ans.",
            citations=[Citation(chunk_id="c1", source_doc="contrat.pdf", source_section="Art. 3")],
            refused=False,
        )


class _RefusingPipeline:
    def answer(self, question: str) -> Answer:
        return Answer(text="REFUS: hors contexte.", citations=[], refused=True)


@contextmanager
def _override(pipeline):
    app.dependency_overrides[get_rag_pipeline] = lambda: pipeline
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def test_query_trace_returns_answer_and_spans() -> None:
    with _override(_FakePipeline()) as client:
        r = client.post("/query/trace", json={"question": "Durée ?"})
    assert r.status_code == 200
    data = r.json()
    assert data["answer"]["text"] == "La durée est de 25 ans."
    assert isinstance(data["spans"], list)
    assert isinstance(data["total_ms"], float)


def test_query_trace_contains_rag_request_span() -> None:
    with _override(_FakePipeline()) as client:
        r = client.post("/query/trace", json={"question": "Durée ?"})
    names = {s["name"] for s in r.json()["spans"]}
    assert "rag_request" in names


def test_query_trace_spans_have_required_fields() -> None:
    with _override(_FakePipeline()) as client:
        r = client.post("/query/trace", json={"question": "Test ?"})
    for span in r.json()["spans"]:
        assert "name" in span
        assert "span_id" in span
        assert "start_ms" in span
        assert "duration_ms" in span
        assert isinstance(span["attributes"], dict)


def test_query_trace_refused_answer_propagated() -> None:
    with _override(_RefusingPipeline()) as client:
        r = client.post("/query/trace", json={"question": "PIB mondial ?"})
    assert r.status_code == 200
    assert r.json()["answer"]["refused"] is True


def test_root_serves_html() -> None:
    with TestClient(app) as client:
        r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "RIP-Agent" in r.text
