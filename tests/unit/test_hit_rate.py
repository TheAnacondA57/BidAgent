from rip_agent.evaluation.metrics.hit_rate import aggregate_hit_rate, compute_hit
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.retrieval import RetrievedChunk


def _retrieved(document_source_path: str) -> RetrievedChunk:
    chunk = Chunk(id="c1", document_id="d1", document_source_path=document_source_path, text="texte", position=0, token_count=1)
    return RetrievedChunk(chunk=chunk)


def test_compute_hit_true_when_expected_source_present() -> None:
    chunks = [_retrieved("contrat.pdf"), _retrieved("avenant.pdf")]

    assert compute_hit(chunks, "avenant.pdf") is True


def test_compute_hit_false_when_expected_source_absent() -> None:
    chunks = [_retrieved("contrat.pdf")]

    assert compute_hit(chunks, "avenant.pdf") is False


def test_aggregate_hit_rate() -> None:
    assert aggregate_hit_rate([True, True, False, True]) == 0.75
    assert aggregate_hit_rate([]) == 0.0
