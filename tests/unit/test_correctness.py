from rip_agent.evaluation.metrics.correctness import build_correctness_prompt, compute_correctness


class FakeJudge:
    def __init__(self, score: float) -> None:
        self._score = score
        self.received_messages: list[dict[str, str]] | None = None

    def score(self, messages: list[dict[str, str]]) -> float:
        self.received_messages = messages
        return self._score


def test_build_correctness_prompt_includes_question_and_answers() -> None:
    messages = build_correctness_prompt("Durée ?", "25 ans", "Le contrat dure 25 ans.")

    user_content = messages[-1]["content"]
    assert "Durée ?" in user_content
    assert "25 ans" in user_content
    assert "Le contrat dure 25 ans." in user_content


def test_compute_correctness_delegates_to_judge() -> None:
    judge = FakeJudge(score=0.9)

    result = compute_correctness("Durée ?", "25 ans", "Le contrat dure 25 ans.", judge)

    assert result == 0.9
    assert judge.received_messages is not None
