from typing import Literal

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    source_path: str
    title: str
    raw_text: str
    metadata: dict[str, str] = Field(default_factory=dict)


class Chunk(BaseModel):
    id: str
    document_id: str
    document_source_path: str = ""
    text: str
    section_title: str | None = None
    position: int
    token_count: int


class DocumentNode(BaseModel):
    """Node in the hierarchical document tree.

    section nodes aggregate the full text of their subtree (header + all descendants).
    leaf nodes are token-bounded chunks of direct text content, ready for embedding.
    header_level is 1–6 for section nodes and 0 for leaf nodes.
    """

    id: str
    document_id: str
    document_source_path: str
    parent_id: str | None
    node_type: Literal["section", "leaf"]
    header_level: int
    section_title: str | None
    text: str
    position: int
    token_count: int


class IngestReport(BaseModel):
    documents_processed: int
    chunks_inserted: int
    failed_paths: list[str] = Field(default_factory=list)
