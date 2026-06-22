from rip_agent.tokenization import count_tokens, split_by_tokens


def test_count_tokens_counts_real_tokens() -> None:
    assert count_tokens("Bonjour le monde") > 0
    assert count_tokens("") == 0


def test_split_by_tokens_returns_single_piece_when_under_budget() -> None:
    assert split_by_tokens("petit texte", max_tokens=100, overlap_tokens=10) == ["petit texte"]


def test_split_by_tokens_splits_with_overlap_and_respects_budget() -> None:
    text = " ".join(f"mot{i}" for i in range(300))

    pieces = split_by_tokens(text, max_tokens=50, overlap_tokens=10)

    assert len(pieces) > 1
    assert all(count_tokens(piece) <= 50 for piece in pieces)
