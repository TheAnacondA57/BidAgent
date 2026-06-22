from rip_agent.config import Settings
from rip_agent.evaluation.runner import EvalRunner
from rip_agent.schemas.document import Chunk
from rip_agent.schemas.evaluation import EvalCase
from rip_agent.schemas.generation import Answer
from rip_agent.schemas.retrieval import RetrievalQuery, RetrievedChunk


class FakeRetrievalPipeline:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    def run(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        return self._chunks


class FakeGenerationPipeline:
    def __init__(self, answer: Answer) -> None:
        self._answer = answer

    def run(self, question: str, chunks: list[RetrievedChunk]) -> Answer:
        return self._answer


class FakeJudge:
    def __init__(self, score: float) -> None:
        self._score = score

    def score(self, messages: list[dict[str, str]]) -> float:
        return self._score


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk=Chunk(id="c1", document_id="d1", document_source_path="contrat.pdf", text="texte", position=0, token_count=1)
    )


def test_run_case_scores_factual_case_via_judge() -> None:
    case = EvalCase(id="q1", question="Durée ?", ground_truth="25 ans", source_doc="contrat.pdf", answer_type="factual")
    runner = EvalRunner(
        settings=Settings(),
        retrieval_pipeline=FakeRetrievalPipeline([_chunk()]),
        generation_pipeline=FakeGenerationPipeline(Answer(text="25 ans [c1].", citations=[], refused=False)),
        judge=FakeJudge(score=0.9),
    )

    result = runner.run_case(case)

    assert result.hit is True
    assert result.correctness == 0.9
    assert result.faithfulness == 0.9


def test_run_case_negative_scores_refusal_as_correct() -> None:
    case = EvalCase(id="q2", question="PIB ?", ground_truth="", source_doc="contrat.pdf", answer_type="negative")
    runner = EvalRunner(
        settings=Settings(),
        retrieval_pipeline=FakeRetrievalPipeline([_chunk()]),
        generation_pipeline=FakeGenerationPipeline(Answer(text="REFUS: hors contexte.", citations=[], refused=True)),
        judge=FakeJudge(score=0.0),
    )

    result = runner.run_case(case)

    assert result.correctness == 1.0
    assert result.faithfulness is None


def test_run_case_negative_scores_non_refusal_as_incorrect() -> None:
    case = EvalCase(id="q3", question="PIB ?", ground_truth="", source_doc="contrat.pdf", answer_type="negative")
    runner = EvalRunner(
        settings=Settings(),
        retrieval_pipeline=FakeRetrievalPipeline([_chunk()]),
        generation_pipeline=FakeGenerationPipeline(Answer(text="Le PIB est de ...", citations=[], refused=False)),
        judge=FakeJudge(score=0.0),
    )

    result = runner.run_case(case)

    assert result.correctness == 0.0


def test_run_aggregates_hit_rate_and_metric_averages() -> None:
    cases = [
        EvalCase(id="q1", question="Durée ?", ground_truth="25 ans", source_doc="contrat.pdf", answer_type="factual"),
        EvalCase(id="q2", question="PIB ?", ground_truth="", source_doc="absent.pdf", answer_type="negative"),
    ]
    runner = EvalRunner(
        settings=Settings(),
        retrieval_pipeline=FakeRetrievalPipeline([_chunk()]),
        generation_pipeline=FakeGenerationPipeline(Answer(text="REFUS: hors contexte.", citations=[], refused=True)),
        judge=FakeJudge(score=0.8),
    )

    report = runner.run(cases)

    assert len(report.results) == 2
    assert report.hit_rate == 0.5
    assert report.correctness_avg == 0.9
    assert report.faithfulness_avg == 0.8
