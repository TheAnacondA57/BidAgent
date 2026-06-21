from rip_agent.config import Settings
from rip_agent.generation.llm import LLMClient


def test_complete_delegates_to_injected_completion_fn() -> None:
    calls = []

    def fake_completion_fn(*, model: str, messages: list[dict[str, str]]) -> str:
        calls.append((model, messages))
        return "réponse factice"

    client = LLMClient(settings=Settings(litellm_model="anthropic/claude-sonnet-4-6"), completion_fn=fake_completion_fn)

    result = client.complete([{"role": "user", "content": "question"}])

    assert result == "réponse factice"
    assert calls == [("anthropic/claude-sonnet-4-6", [{"role": "user", "content": "question"}])]


def test_explicit_model_overrides_settings_default() -> None:
    calls = []

    def fake_completion_fn(*, model: str, messages: list[dict[str, str]]) -> str:
        calls.append(model)
        return ""

    client = LLMClient(settings=Settings(), model="anthropic/claude-haiku-4-5", completion_fn=fake_completion_fn)
    client.complete([])

    assert calls == ["anthropic/claude-haiku-4-5"]
