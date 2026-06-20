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
    text: str
    section_title: str | None = None
    position: int
    token_count: int
