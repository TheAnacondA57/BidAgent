import re
import uuid
from collections.abc import Callable

from rip_agent.config import Settings, get_settings
from rip_agent.schemas.document import Chunk, Document
from rip_agent.tokenization import count_tokens, split_by_tokens

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def _split_sections(raw_text: str) -> list[tuple[str | None, str]]:
    """Split markdown text into (section_title, section_body) pairs based on headers."""
    matches = list(_HEADER_RE.finditer(raw_text))
    if not matches:
        return [(None, raw_text)]

    sections: list[tuple[str | None, str]] = []
    if matches[0].start() > 0:
        sections.append((None, raw_text[: matches[0].start()]))

    for i, match in enumerate(matches):
        title = match.group(2).strip()
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        sections.append((title, raw_text[body_start:body_end].strip()))

    return sections


def chunk_document(
    document: Document,
    settings: Settings | None = None,
    split_fn: Callable[[str, int, int], list[str]] = split_by_tokens,
    token_counter: Callable[[str], int] = count_tokens,
) -> list[Chunk]:
    """Chunk a document by markdown section, falling back to fixed-size token
    windows with overlap for sections that exceed `chunk_max_tokens`.

    `split_fn`/`token_counter` are injectable so tests can run the section/
    position logic without a real tiktoken call.
    """
    settings = settings or get_settings()

    chunks: list[Chunk] = []
    position = 0
    for title, body in _split_sections(document.raw_text):
        if not body.strip():
            continue
        for piece in split_fn(body, settings.chunk_max_tokens, settings.chunk_overlap_tokens):
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    document_source_path=document.source_path,
                    text=piece,
                    section_title=title,
                    position=position,
                    token_count=token_counter(piece),
                )
            )
            position += 1

    return chunks
