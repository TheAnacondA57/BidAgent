from collections.abc import Callable
from pathlib import Path

from rip_agent.config import Settings, get_settings
from rip_agent.ingestion.embedder import Embedder
from rip_agent.ingestion.node_store import NodeStore
from rip_agent.ingestion.parser import parse_pdf
from rip_agent.ingestion.tree import build_document_tree
from rip_agent.schemas.document import Document, DocumentNode, IngestReport
from rip_agent.telemetry import get_tracer

_tracer = get_tracer(__name__)


class TreeIngestPipeline:
    """Orchestrates parse -> build_document_tree -> embed leaves -> store in doc_nodes.

    Only leaf nodes are embedded; section nodes hold the aggregated text used
    during context expansion and do not need an embedding.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        embedder: Embedder | None = None,
        node_store: NodeStore | None = None,
        parse_pdf_fn: Callable[..., Document] = parse_pdf,
        build_tree_fn: Callable[..., list[DocumentNode]] = build_document_tree,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedder = embedder or Embedder(self._settings)
        self._node_store = node_store or NodeStore(self._settings)
        self._parse_pdf = parse_pdf_fn
        self._build_tree = build_tree_fn

    def run(self, paths: list[Path]) -> IngestReport:
        with _tracer.start_as_current_span("tree_ingestion") as span:
            span.set_attribute("ingestion.document_count", len(paths))

            documents_processed = 0
            chunks_inserted = 0
            failed_paths: list[str] = []

            self._node_store.ensure_schema()

            for path in paths:
                with _tracer.start_as_current_span("tree_ingestion.document") as doc_span:
                    doc_span.set_attribute("ingestion.source_path", str(path))
                    try:
                        document = self._parse_pdf(path, settings=self._settings)
                        nodes = self._build_tree(document, settings=self._settings)
                        leaves = [n for n in nodes if n.node_type == "leaf"]
                        embeddings_array = self._embedder.embed([n.text for n in leaves])
                        leaf_embeddings = {
                            leaf.id: vec for leaf, vec in zip(leaves, embeddings_array, strict=True)
                        }
                        self._node_store.insert_nodes(nodes, leaf_embeddings)
                    except Exception:
                        doc_span.set_attribute("ingestion.failed", True)
                        failed_paths.append(str(path))
                        continue

                    doc_span.set_attribute("ingestion.node_count", len(nodes))
                    doc_span.set_attribute("ingestion.leaf_count", len(leaves))
                    documents_processed += 1
                    chunks_inserted += len(leaves)

            span.set_attribute("ingestion.chunks_inserted", chunks_inserted)
            span.set_attribute("ingestion.failed_count", len(failed_paths))

        return IngestReport(
            documents_processed=documents_processed,
            chunks_inserted=chunks_inserted,
            failed_paths=failed_paths,
        )
