from collections.abc import Callable
from pathlib import Path

from rip_agent.config import Settings, get_settings
from rip_agent.ingestion.chunking import chunk_document
from rip_agent.ingestion.embedder import Embedder
from rip_agent.ingestion.parser import parse_pdf
from rip_agent.ingestion.store import PgVectorStore
from rip_agent.schemas.document import Chunk, Document, IngestReport
from rip_agent.telemetry import get_tracer

_tracer = get_tracer(__name__)


class IngestPipeline:
    """Orchestrates parse -> chunk -> embed -> store for a batch of PDFs.

    `parse_pdf_fn`/`chunk_document_fn` are injectable so tests can run the
    orchestration logic without a real LlamaParse call or embedding model.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        embedder: Embedder | None = None,
        store: PgVectorStore | None = None,
        parse_pdf_fn: Callable[..., Document] = parse_pdf,
        chunk_document_fn: Callable[..., list[Chunk]] = chunk_document,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedder = embedder or Embedder(self._settings)
        self._store = store or PgVectorStore(self._settings)
        self._parse_pdf = parse_pdf_fn
        self._chunk_document = chunk_document_fn

    def run(self, paths: list[Path]) -> IngestReport:
        with _tracer.start_as_current_span("ingestion") as span:
            span.set_attribute("ingestion.document_count", len(paths))

            documents_processed = 0
            chunks_inserted = 0
            failed_paths: list[str] = []

            self._store.ensure_schema()

            for path in paths:
                with _tracer.start_as_current_span("ingestion.document") as doc_span:
                    doc_span.set_attribute("ingestion.source_path", str(path))
                    try:
                        document = self._parse_pdf(path, settings=self._settings)
                        chunks = self._chunk_document(document, settings=self._settings)
                        embeddings = self._embedder.embed([chunk.text for chunk in chunks])
                        self._store.insert_chunks(chunks, embeddings)
                    except Exception:
                        doc_span.set_attribute("ingestion.failed", True)
                        failed_paths.append(str(path))
                        continue

                    doc_span.set_attribute("ingestion.chunk_count", len(chunks))
                    documents_processed += 1
                    chunks_inserted += len(chunks)

            span.set_attribute("ingestion.chunks_inserted", chunks_inserted)
            span.set_attribute("ingestion.failed_count", len(failed_paths))

        return IngestReport(
            documents_processed=documents_processed,
            chunks_inserted=chunks_inserted,
            failed_paths=failed_paths,
        )
