from rip_agent.config import Settings
from rip_agent.ingestion.tree import build_document_tree
from rip_agent.schemas.document import Document


def _doc(raw_text: str) -> Document:
    return Document(id="doc-1", source_path="contrat.pdf", title="contrat", raw_text=raw_text)


def _fake_split(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text]
    step = max_tokens - overlap_tokens
    pieces = []
    for start in range(0, len(words), step):
        pieces.append(" ".join(words[start : start + max_tokens]))
        if start + max_tokens >= len(words):
            break
    return pieces


def _fake_count(text: str) -> int:
    return len(text.split())


def test_flat_text_produces_only_leaves() -> None:
    doc = _doc("pas de titre juste du texte brut")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    assert all(n.node_type == "leaf" for n in nodes)
    assert all(n.parent_id is None for n in nodes)
    assert all(n.header_level == 0 for n in nodes)


def test_single_section_produces_section_then_leaf() -> None:
    doc = _doc("# Article 1\ncontenu de l'article")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    sections = [n for n in nodes if n.node_type == "section"]
    leaves = [n for n in nodes if n.node_type == "leaf"]

    assert len(sections) == 1
    assert len(leaves) == 1
    assert sections[0].section_title == "Article 1"
    assert sections[0].header_level == 1
    assert leaves[0].parent_id == sections[0].id


def test_nested_sections_form_correct_parent_chain() -> None:
    doc = _doc("# H1\ntext a\n\n## H2\ntext b\n\n## H2bis\ntext c")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    by_title = {n.section_title: n for n in nodes if n.node_type == "section"}
    h1, h2, h2bis = by_title["H1"], by_title["H2"], by_title["H2bis"]

    assert h1.parent_id is None
    assert h2.parent_id == h1.id
    assert h2bis.parent_id == h1.id


def test_h2_is_not_treated_as_sibling_of_h3() -> None:
    doc = _doc("# H1\n\n## H2\ntext b\n\n### H3\ntext c")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    by_title = {n.section_title: n for n in nodes if n.node_type == "section"}
    assert by_title["H3"].parent_id == by_title["H2"].id
    assert by_title["H2"].parent_id == by_title["H1"].id


def test_section_text_aggregates_all_descendant_content() -> None:
    doc = _doc("# H1\npreamble\n\n## H2\ndetail")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    h1 = next(n for n in nodes if n.node_type == "section" and n.header_level == 1)
    assert "preamble" in h1.text
    assert "detail" in h1.text
    assert "H2" in h1.text


def test_topological_order_parents_always_before_children() -> None:
    doc = _doc("# H1\n\n## H2\n\n### H3\nfeuille")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    id_to_index = {n.id: i for i, n in enumerate(nodes)}
    for node in nodes:
        if node.parent_id is not None:
            assert id_to_index[node.parent_id] < id_to_index[node.id]


def test_deeply_nested_leaf_has_direct_section_as_parent() -> None:
    doc = _doc("# H1\n\n## H2\n\n### H3\ncontenu profond")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    leaves = [n for n in nodes if n.node_type == "leaf"]
    h3 = next(n for n in nodes if n.node_type == "section" and n.header_level == 3)

    assert len(leaves) == 1
    assert leaves[0].parent_id == h3.id


def test_preamble_before_first_header_has_no_parent() -> None:
    doc = _doc("intro sans titre\n\n# Article 1\ncorps")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    parentless = [n for n in nodes if n.node_type == "leaf" and n.parent_id is None]
    assert len(parentless) == 1
    assert "intro" in parentless[0].text


def test_long_leaf_text_is_split_with_overlap() -> None:
    long_body = "# S\n" + " ".join(f"mot{i}" for i in range(20))
    doc = _doc(long_body)
    settings = Settings(chunk_max_tokens=5, chunk_overlap_tokens=1)

    nodes = build_document_tree(doc, settings=settings, split_fn=_fake_split, token_counter=_fake_count)
    leaves = [n for n in nodes if n.node_type == "leaf"]

    assert len(leaves) > 1
    assert all(len(leaf.text.split()) <= 5 for leaf in leaves)
    # overlap: last word of first leaf reappears in second leaf
    assert leaves[0].text.split()[-1] in leaves[1].text.split()


def test_all_node_ids_are_unique() -> None:
    doc = _doc("# A\ntexte\n\n## B\nplus\n\n## C\nfin")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    ids = [n.id for n in nodes]
    assert len(ids) == len(set(ids))


def test_empty_document_produces_no_nodes() -> None:
    doc = _doc("")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    assert nodes == []


def test_document_id_and_source_path_are_propagated_to_all_nodes() -> None:
    doc = _doc("# H1\ntexte")
    nodes = build_document_tree(doc, settings=Settings(), split_fn=_fake_split, token_counter=_fake_count)

    assert all(n.document_id == "doc-1" for n in nodes)
    assert all(n.document_source_path == "contrat.pdf" for n in nodes)
