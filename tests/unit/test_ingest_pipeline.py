from pathlib import Path

import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.embedder import Embedder
from rip_agent.ingestion.pipeline import IngestPipeline
from rip_agent.schemas.document import Chunk, Document


class FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool) -> np.ndarray:
        return np.zeros((len(texts), 2))


class FakeStore:
    def __init__(self) -> None:
        self.schema_ensured = False
        self.inserted: list[tuple[list[Chunk], np.ndarray]] = []

    def ensure_schema(self) -> None:
        self.schema_ensured = True

    def insert_chunks(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        self.inserted.append((chunks, embeddings))


def _fake_parse_pdf(path: Path, settings: Settings) -> Document:
    if "broken" in str(path):
        raise ValueError("PDF illisible")
    return Document(id=str(path), source_path=str(path), title=path.stem, raw_text="# Article 1\ntexte")


def _fake_chunk_document(document: Document, settings: Settings) -> list[Chunk]:
    return [
        Chunk(
            id=f"{document.id}-0",
            document_id=document.id,
            text=document.raw_text,
            section_title="Article 1",
            position=0,
            token_count=2,
        )
    ]


def test_run_ingests_each_document_and_reports_counts() -> None:
    store = FakeStore()
    pipeline = IngestPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        store=store,
        parse_pdf_fn=_fake_parse_pdf,
        chunk_document_fn=_fake_chunk_document,
    )

    report = pipeline.run([Path("doc1.pdf"), Path("doc2.pdf")])

    assert report.documents_processed == 2
    assert report.chunks_inserted == 2
    assert report.failed_paths == []
    assert store.schema_ensured is True
    assert len(store.inserted) == 2


def test_run_collects_failed_paths_without_stopping_the_batch() -> None:
    store = FakeStore()
    pipeline = IngestPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        store=store,
        parse_pdf_fn=_fake_parse_pdf,
        chunk_document_fn=_fake_chunk_document,
    )

    report = pipeline.run([Path("doc1.pdf"), Path("broken.pdf")])

    assert report.documents_processed == 1
    assert report.failed_paths == ["broken.pdf"]
