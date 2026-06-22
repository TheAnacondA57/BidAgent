from collections.abc import Callable

from rip_agent.schemas.retrieval import RetrievedChunk
from rip_agent.tokenization import count_tokens


def select_within_budget(
    chunks: list[RetrievedChunk],
    max_tokens: int,
    token_counter: Callable[[str], int] = count_tokens,
) -> list[RetrievedChunk]:
    """Greedily keeps the best-ranked chunks (already sorted by fused_score)
    until adding the next one would exceed `max_tokens`. Always keeps at
    least the first chunk, even if it alone exceeds the budget, so a tight
    budget never produces an empty context.
    """
    selected: list[RetrievedChunk] = []
    used_tokens = 0
    for result in chunks:
        chunk_tokens = token_counter(result.chunk.text)
        if selected and used_tokens + chunk_tokens > max_tokens:
            break
        selected.append(result)
        used_tokens += chunk_tokens
    return selected
