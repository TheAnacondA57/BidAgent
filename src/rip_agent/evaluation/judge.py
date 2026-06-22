import re

from rip_agent.config import Settings, get_settings
from rip_agent.generation.llm import LLMClient

_SCORE_RE = re.compile(r"(\d+(?:\.\d+)?)")


class JudgeClient:
    """Wraps LLMClient pinned to the judge model and parses a 0-1 score out of
    its response. Judge prompts instruct the model to answer with a single
    number, so this is the one place that interprets that convention.
    """

    def __init__(self, settings: Settings | None = None, llm_client: LLMClient | None = None) -> None:
        self._settings = settings or get_settings()
        self._llm_client = llm_client or LLMClient(self._settings, model=self._settings.litellm_judge_model)

    def score(self, messages: list[dict[str, str]]) -> float:
        raw = self._llm_client.complete(messages)
        match = _SCORE_RE.search(raw)
        if not match:
            return 0.0
        return max(0.0, min(1.0, float(match.group(1))))
