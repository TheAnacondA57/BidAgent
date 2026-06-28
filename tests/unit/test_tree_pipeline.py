from pathlib import Path

import numpy as np

from rip_agent.config import Settings
from rip_agent.ingestion.embedder import Embedder
from rip_agent.ingestion.tree_pipeline import TreeIngestPipeline
from rip_agent.schemas.document import Document, DocumentNode


class FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool) -> np.ndarray:
        return np.zeros((len(texts), 4))


class FakeNodeStore:
    def __init__(self) -> None:
        self.schema_ensured = False
        self.inserted: list[tuple[list[DocumentNode], dict]] = []

    def ensure_schema(self) -> None:
        self.schema_ensured = True

    def insert_nodes(self, nodes: list[DocumentNode], leaf_embeddings: dict) -> None:
        self.inserted.append((nodes, leaf_embeddings))


def _fake_parse_pdf(path: Path, settings: Settings) -> Document:
    if "broken" in str(path):
        raise ValueError("PDF illisible")
    return Document(
        id=str(path), source_path=str(path), title=path.stem,
        raw_text="# Article 1\ncontenu de l'article",
    )


def _fake_build_tree(document: Document, settings: Settings) -> list[DocumentNode]:
    section = DocumentNode(
        id=f"{document.id}-sec",
        document_id=document.id,
        document_source_path=document.source_path,
        parent_id=None,
        node_type="section",
        header_level=1,
        section_title="Article 1",
        text="# Article 1\ncontenu de l'article",
        position=0,
        token_count=5,
    )
    leaf = DocumentNode(
        id=f"{document.id}-leaf",
        document_id=document.id,
        document_source_path=document.source_path,
        parent_id=section.id,
        node_type="leaf",
        header_level=0,
        section_title=None,
        text="contenu de l'article",
        position=1,
        token_count=3,
    )
    return [section, leaf]


def test_run_ingests_documents_and_only_embeds_leaves() -> None:
    store = FakeNodeStore()
    pipeline = TreeIngestPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        node_store=store,
        parse_pdf_fn=_fake_parse_pdf,
        build_tree_fn=_fake_build_tree,
    )

    report = pipeline.run([Path("doc1.pdf"), Path("doc2.pdf")])

    assert report.documents_processed == 2
    assert report.chunks_inserted == 2  # 1 leaf per document
    assert report.failed_paths == []
    assert store.schema_ensured is True
    assert len(store.inserted) == 2


def test_run_leaf_embeddings_keyed_by_leaf_id() -> None:
    store = FakeNodeStore()
    pipeline = TreeIngestPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        node_store=store,
        parse_pdf_fn=_fake_parse_pdf,
        build_tree_fn=_fake_build_tree,
    )

    pipeline.run([Path("doc1.pdf")])

    nodes, leaf_embeddings = store.inserted[0]
    leaf_ids = {n.id for n in nodes if n.node_type == "leaf"}
    section_ids = {n.id for n in nodes if n.node_type == "section"}

    assert set(leaf_embeddings.keys()) == leaf_ids
    assert not any(sid in leaf_embeddings for sid in section_ids)


def test_run_collects_failed_paths_without_stopping_batch() -> None:
    store = FakeNodeStore()
    pipeline = TreeIngestPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        node_store=store,
        parse_pdf_fn=_fake_parse_pdf,
        build_tree_fn=_fake_build_tree,
    )

    report = pipeline.run([Path("doc1.pdf"), Path("broken.pdf"), Path("doc2.pdf")])

    assert report.documents_processed == 2
    assert report.failed_paths == ["broken.pdf"]


def test_run_inserts_all_nodes_including_sections() -> None:
    store = FakeNodeStore()
    pipeline = TreeIngestPipeline(
        settings=Settings(),
        embedder=Embedder(settings=Settings(), model=FakeModel()),
        node_store=store,
        parse_pdf_fn=_fake_parse_pdf,
        build_tree_fn=_fake_build_tree,
    )

    pipeline.run([Path("doc1.pdf")])

    nodes, _ = store.inserted[0]
    node_types = {n.node_type for n in nodes}
    assert node_types == {"section", "leaf"}
