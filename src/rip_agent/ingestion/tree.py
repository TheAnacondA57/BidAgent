import re
import uuid
from collections.abc import Callable

from rip_agent.config import Settings, get_settings
from rip_agent.schemas.document import Document, DocumentNode
from rip_agent.tokenization import count_tokens, split_by_tokens

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def _find_direct_children(text: str, min_level: int) -> list[re.Match]:
    # Among headers at level >= min_level, only return those at the minimum
    # level found — avoids treating nested sub-headers as siblings.
    all_headers = list(_HEADER_RE.finditer(text))
    candidates = [m for m in all_headers if len(m.group(1)) >= min_level]
    if not candidates:
        return []
    min_found = min(len(m.group(1)) for m in candidates)
    return [m for m in candidates if len(m.group(1)) == min_found]


def build_document_tree(
    document: Document,
    settings: Settings | None = None,
    split_fn: Callable[[str, int, int], list[str]] = split_by_tokens,
    token_counter: Callable[[str], int] = count_tokens,
) -> list[DocumentNode]:
    """Returns all DocumentNodes forming the document tree, in topological order
    (parents always precede their children) so the list is safe to insert
    row-by-row into a table with a self-referencing FK constraint.
    """
    settings = settings or get_settings()
    nodes: list[DocumentNode] = []
    position = 0

    def make_leaves(text: str, parent_id: str | None) -> None:
        nonlocal position
        text = text.strip()
        if not text:
            return
        for piece in split_fn(text, settings.chunk_max_tokens, settings.chunk_overlap_tokens):
            nodes.append(
                DocumentNode(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    document_source_path=document.source_path,
                    parent_id=parent_id,
                    node_type="leaf",
                    header_level=0,
                    section_title=None,
                    text=piece,
                    position=position,
                    token_count=token_counter(piece),
                )
            )
            position += 1

    def parse_block(text: str, parent_id: str | None, min_level: int) -> None:
        nonlocal position
        direct_children = _find_direct_children(text, min_level)

        preamble_end = direct_children[0].start() if direct_children else len(text)
        make_leaves(text[:preamble_end], parent_id)

        for i, match in enumerate(direct_children):
            level = len(match.group(1))
            title = match.group(2).strip()
            body_start = match.end()
            body_end = direct_children[i + 1].start() if i + 1 < len(direct_children) else len(text)
            body = text[body_start:body_end].strip()

            section_text = f"{'#' * level} {title}\n\n{body}".strip()
            section_id = str(uuid.uuid4())

            nodes.append(
                DocumentNode(
                    id=section_id,
                    document_id=document.id,
                    document_source_path=document.source_path,
                    parent_id=parent_id,
                    node_type="section",
                    header_level=level,
                    section_title=title,
                    text=section_text,
                    position=position,
                    token_count=token_counter(section_text),
                )
            )
            position += 1

            parse_block(body, section_id, level + 1)

    parse_block(document.raw_text, None, 1)
    return nodes
