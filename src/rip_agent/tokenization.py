from functools import lru_cache


@lru_cache
def _get_encoding():  # type: ignore[no-untyped-def]
    import tiktoken

    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Real token count via tiktoken (cl100k_base).

    There's no public offline tokenizer for Claude, so this is used as a
    consistent approximation everywhere a token budget matters (chunking,
    context assembly) rather than mixing ad-hoc heuristics.
    """
    return len(_get_encoding().encode(text))


def split_by_tokens(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """Splits `text` into windows of at most `max_tokens` real tokens, each
    overlapping the previous window by `overlap_tokens` tokens.
    """
    encoding = _get_encoding()
    token_ids = encoding.encode(text)
    if len(token_ids) <= max_tokens:
        return [text]

    step = max_tokens - overlap_tokens
    pieces = []
    for start in range(0, len(token_ids), step):
        window = token_ids[start : start + max_tokens]
        pieces.append(encoding.decode(window))
        if start + max_tokens >= len(token_ids):
            break
    return pieces
