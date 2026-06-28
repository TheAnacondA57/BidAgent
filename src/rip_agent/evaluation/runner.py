from rip_agent.config import Settings, get_settings
from rip_agent.evaluation.judge import JudgeClient
from rip_agent.evaluation.metrics.correctness import compute_correctness
from rip_agent.evaluation.metrics.faithfulness import compute_faithfulness
from rip_agent.evaluation.metrics.hit_rate import aggregate_hit_rate, compute_hit
from rip_agent.generation.pipeline import GenerationPipeline
from rip_agent.retrieval._shared import RetrievalPipelineProtocol
from rip_agent.retrieval.pipeline import RetrievalPipeline
from rip_agent.schemas.evaluation import EvalCase, EvalReport, EvalResult
from rip_agent.schemas.retrieval import RetrievalQuery
from rip_agent.telemetry import get_tracer

_tracer = get_tracer(__name__)


class EvalRunner:
    """Runs an eval set end-to-end through the same retrieval/generation
    pipelines used in production, then scores each case.

    Negative cases (`answer_type == "negative"`) expect a refusal: their
    correctness is 1.0 if the pipeline refused and 0.0 otherwise, and
    faithfulness doesn't apply since there's no grounded answer to check.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        retrieval_pipeline: RetrievalPipelineProtocol | None = None,
        generation_pipeline: GenerationPipeline | None = None,
        judge: JudgeClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        if retrieval_pipeline is not None:
            self._retrieval_pipeline = retrieval_pipeline
        elif self._settings.use_tree_retrieval:
            from rip_agent.retrieval.tree_pipeline import TreeRetrievalPipeline
            self._retrieval_pipeline = TreeRetrievalPipeline(self._settings)
        else:
            self._retrieval_pipeline = RetrievalPipeline(self._settings)
        self._generation_pipeline = generation_pipeline or GenerationPipeline(self._settings)
        self._judge = judge or JudgeClient(self._settings)

    def run_case(self, case: EvalCase) -> EvalResult:
        with _tracer.start_as_current_span("evaluation.case") as span:
            span.set_attribute("evaluation.case_id", case.id)

            chunks = self._retrieval_pipeline.run(RetrievalQuery(question=case.question))
            answer = self._generation_pipeline.run(case.question, chunks)
            hit = compute_hit(chunks, case.source_doc)

            if case.answer_type == "negative":
                correctness = 1.0 if answer.refused else 0.0
                faithfulness = None
            else:
                correctness = compute_correctness(case.question, case.ground_truth, answer.text, self._judge)
                faithfulness = compute_faithfulness(answer.text, chunks, self._judge)

            span.set_attribute("evaluation.hit", hit)
            span.set_attribute("evaluation.correctness", correctness)

        return EvalResult(case=case, answer=answer, hit=hit, correctness=correctness, faithfulness=faithfulness)

    def run(self, cases: list[EvalCase]) -> EvalReport:
        with _tracer.start_as_current_span("evaluation") as span:
            span.set_attribute("evaluation.case_count", len(cases))
            results = [self.run_case(case) for case in cases]

        correctness_values = [r.correctness for r in results if r.correctness is not None]
        faithfulness_values = [r.faithfulness for r in results if r.faithfulness is not None]

        return EvalReport(
            results=results,
            hit_rate=aggregate_hit_rate([r.hit for r in results]),
            correctness_avg=sum(correctness_values) / len(correctness_values) if correctness_values else None,
            faithfulness_avg=sum(faithfulness_values) / len(faithfulness_values) if faithfulness_values else None,
        )
