from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    source_doc: str
    source_section: str | None = None


class Answer(BaseModel):
    text: str
    citations: list[Citation] = Field(default_factory=list)
    refused: bool = False
