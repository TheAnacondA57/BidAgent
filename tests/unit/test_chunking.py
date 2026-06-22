from rip_agent.config import Settings
from rip_agent.ingestion.chunking import chunk_document
from rip_agent.schemas.document import Document


def _doc(raw_text: str) -> Document:
    return Document(id="doc-1", source_path="contrat.pdf", title="contrat", raw_text=raw_text)


def _fake_split(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """Word-based stand-in for split_by_tokens, so these tests exercise
    chunk_document's section/position logic without a real tiktoken call.
    """
    words = text.split()
    if len(words) <= max_tokens:
        return [text]

    step = max_tokens - overlap_tokens
    pieces = []
    for start in range(0, len(words), step):
        pieces.append(" ".join(words[start : start + max_tokens]))
        if start + max_tokens >= len(words):
            break
    return pieces


def _fake_count(text: str) -> int:
    return len(text.split())


def test_chunk_document_splits_by_section() -> None:
    doc = _doc("# Article 1\ncontenu un\n\n# Article 2\ncontenu deux")

    chunks = chunk_document(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    assert [c.section_title for c in chunks] == ["Article 1", "Article 2"]
    assert all(c.document_id == "doc-1" for c in chunks)
    assert all(c.document_source_path == "contrat.pdf" for c in chunks)
    assert [c.position for c in chunks] == [0, 1]


def test_chunk_document_falls_back_to_fixed_size_with_overlap() -> None:
    long_body = "# Article 1\n" + " ".join(f"mot{i}" for i in range(250))
    doc = _doc(long_body)
    settings = Settings(chunk_max_tokens=100, chunk_overlap_tokens=20)

    chunks = chunk_document(doc, settings=settings, split_fn=_fake_split, token_counter=_fake_count)

    assert len(chunks) > 1
    assert all(c.section_title == "Article 1" for c in chunks)
    assert all(c.token_count <= 100 for c in chunks)
    # overlap: le dernier mot du premier chunk doit réapparaître dans le second
    assert chunks[0].text.split()[-1] in chunks[1].text.split()


def test_chunk_document_handles_text_without_headers() -> None:
    doc = _doc("juste du texte sans titre de section")

    chunks = chunk_document(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    assert len(chunks) == 1
    assert chunks[0].section_title is None
