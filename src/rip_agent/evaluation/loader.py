import json
from pathlib import Path

from rip_agent.schemas.evaluation import EvalCase


def load_eval_cases(path: Path) -> list[EvalCase]:
    """Reads a JSONL eval set, one EvalCase per non-empty line."""
    cases: list[EvalCase] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(EvalCase(**json.loads(line)))
    return cases
