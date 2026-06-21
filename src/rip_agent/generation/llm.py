from typing import Protocol

from rip_agent.config import Settings, get_settings


class CompletionFn(Protocol):
    def __call__(self, *, model: str, messages: list[dict[str, str]]) -> str: ...


def _default_completion_fn(*, model: str, messages: list[dict[str, str]]) -> str:
    import litellm

    response = litellm.completion(model=model, messages=messages)
    return response.choices[0].message.content


class LLMClient:
    """Thin LiteLLM wrapper: a single provider today, but every call goes
    through this one seam so multi-model routing can be added later without
    touching the generation/evaluation modules that depend on it.

    `completion_fn` can be injected to bypass the real LLM call in tests.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        model: str | None = None,
        completion_fn: CompletionFn | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._model = model or self._settings.litellm_model
        self._completion_fn = completion_fn or _default_completion_fn

    def complete(self, messages: list[dict[str, str]]) -> str:
        return self._completion_fn(model=self._model, messages=messages)
