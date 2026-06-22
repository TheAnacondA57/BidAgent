from rip_agent.config import Settings
from rip_agent.evaluation.judge import JudgeClient
from rip_agent.generation.llm import LLMClient


def _judge_with_fixed_response(response_text: str) -> JudgeClient:
    llm_client = LLMClient(settings=Settings(), completion_fn=lambda *, model, messages: response_text)
    return JudgeClient(settings=Settings(), llm_client=llm_client)


def test_score_parses_plain_number() -> None:
    judge = _judge_with_fixed_response("0.8")

    assert judge.score([]) == 0.8


def test_score_parses_number_within_sentence() -> None:
    judge = _judge_with_fixed_response("Score : 1")

    assert judge.score([]) == 1.0


def test_score_clamps_out_of_range_values() -> None:
    judge = _judge_with_fixed_response("5")

    assert judge.score([]) == 1.0


def test_score_defaults_to_zero_when_unparseable() -> None:
    judge = _judge_with_fixed_response("je ne sais pas")

    assert judge.score([]) == 0.0
