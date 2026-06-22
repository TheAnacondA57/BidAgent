from typing import Any

from rip_agent.schemas.document import Chunk


def chunk_from_row(row: dict[str, Any]) -> Chunk:
    """Builds a Chunk from a `chunks` table row, shared by bm25.py and dense.py
    since both query the same table and need the same mapping.
    """
    return Chunk(
        id=row["id"],
        document_id=row["document_id"],
        document_source_path=row["document_source_path"],
        text=row["text"],
        section_title=row["section_title"],
        position=row["position"],
        token_count=row["token_count"],
    )
