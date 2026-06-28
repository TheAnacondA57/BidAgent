from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from rip_agent.config import Settings, get_settings
from rip_agent.db import default_connection_factory
from rip_agent.retrieval._shared import chunk_from_row, rows_from_cursor
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk

_FETCH_PARENTS_SQL = """
WITH leaf_parents AS (
    SELECT id AS leaf_id, parent_id
    FROM doc_nodes
    WHERE id = ANY(%(leaf_ids)s) AND parent_id IS NOT NULL
)
SELECT lp.leaf_id,
       n.id, n.document_id, n.document_source_path, n.text,
       n.section_title, n.position, n.token_count
FROM leaf_parents lp
JOIN doc_nodes n ON n.id = lp.parent_id
"""


def fetch_parents(
    leaf_ids: list[str],
    settings: Settings | None = None,
    connection_factory: Callable[[], AbstractContextManager[Any]] | None = None,
) -> dict[str, Chunk]:
    """Returns {leaf_id: parent_chunk} for every leaf that has a parent node."""
    if not leaf_ids:
        return {}

    settings = settings or get_settings()
    connection_factory = connection_factory or default_connection_factory(settings.postgres_dsn)

    with connection_factory() as conn:
        with conn.cursor() as cur:
            cur.execute(_FETCH_PARENTS_SQL, {"leaf_ids": leaf_ids})
            rows = rows_from_cursor(cur)

    return {row["leaf_id"]: chunk_from_row(row) for row in rows}


def expand_to_parent(
    leaf_results: list[RetrievedChunk],
    fetch_parents_fn: Callable[..., dict[str, Chunk]] = fetch_parents,
    settings: Settings | None = None,
    connection_factory: Callable[[], AbstractContextManager[Any]] | None = None,
) -> list[RetrievedChunk]:
    """Replaces each leaf with its parent section node.

    When multiple leaves share a parent, they are merged into one result
    keeping the highest fused_score. Leaves without a parent are returned unchanged.
    """
    parent_map = fetch_parents_fn(
        [r.chunk.id for r in leaf_results],
        settings=settings,
        connection_factory=connection_factory,
    )

    merged: dict[str, RetrievedChunk] = {}
    for result in leaf_results:
        parent = parent_map.get(result.chunk.id)
        replacement = parent if parent is not None else result.chunk
        key = replacement.id
        if key not in merged or result.fused_score > merged[key].fused_score:
            merged[key] = result.model_copy(update={"chunk": replacement})

    return sorted(merged.values(), key=lambda r: r.fused_score, reverse=True)
