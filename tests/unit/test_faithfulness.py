from rip_agent.evaluation.metrics.faithfulness import build_faithfulness_prompt, compute_faithfulness
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk


class FakeJudge:
    def __init__(self, score: float) -> None:
        self._score = score
        self.received_messages: list[dict[str, str]] | None = None

    def score(self, messages: list[dict[str, str]]) -> float:
        self.received_messages = messages
        return self._score


def _retrieved(chunk_id: str, text: str) -> RetrievedChunk:
    chunk = Chunk(id=chunk_id, document_id="d1", document_source_path="contrat.pdf", text=text, position=0, token_count=2)
    return RetrievedChunk(chunk=chunk)


def test_build_faithfulness_prompt_includes_context_and_answer() -> None:
    chunks = [_retrieved("c1", "Le contrat dure 25 ans.")]

    messages = build_faithfulness_prompt("Réponse à vérifier", chunks)

    user_content = messages[-1]["content"]
    assert "[c1] Le contrat dure 25 ans." in user_content
    assert "Réponse à vérifier" in user_content


def test_compute_faithfulness_delegates_to_judge() -> None:
    judge = FakeJudge(score=0.6)
    chunks = [_retrieved("c1", "Le contrat dure 25 ans.")]

    result = compute_faithfulness("Réponse", chunks, judge)

    assert result == 0.6
    assert judge.received_messages is not None
