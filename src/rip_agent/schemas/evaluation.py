from pydantic import BaseModel, Field

from rip_agent.schemas.generation import Answer


class EvalCase(BaseModel):
    id: str
    question: str
    ground_truth: str
    source_doc: str
    source_section: str | None = None
    answer_type: str = "factual"
    difficulty: str = "medium"


class EvalResult(BaseModel):
    case: EvalCase
    answer: Answer
    hit: bool
    correctness: float | None = None
    faithfulness: float | None = None


class EvalReport(BaseModel):
    results: list[EvalResult] = Field(default_factory=list)
    hit_rate: float = 0.0
    correctness_avg: float | None = None
    faithfulness_avg: float | None = None
