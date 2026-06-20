import re
import uuid

from rip_agent.config import Settings, get_settings
from rip_agent.schemas.document import Chunk, Document

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def _count_tokens(text: str) -> int:
    return len(text.split())


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


def _split_fixed(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """Fallback split for an oversized section: fixed-size windows with overlap."""
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


def chunk_document(document: Document, settings: Settings | None = None) -> list[Chunk]:
    """Chunk a document by markdown section, falling back to fixed-size windows
    with overlap for sections that exceed `chunk_max_tokens`.
    """
    settings = settings or get_settings()

    chunks: list[Chunk] = []
    position = 0
    for title, body in _split_sections(document.raw_text):
        if not body.strip():
            continue
        for piece in _split_fixed(body, settings.chunk_max_tokens, settings.chunk_overlap_tokens):
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    text=piece,
                    section_title=title,
                    position=position,
                    token_count=_count_tokens(piece),
                )
            )
            position += 1

    return chunks
