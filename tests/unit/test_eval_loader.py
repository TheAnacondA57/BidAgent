import json
from pathlib import Path

from rip_agent.evaluation.loader import load_eval_cases


def test_load_eval_cases_parses_jsonl(tmp_path: Path) -> None:
    eval_set = tmp_path / "cases.jsonl"
    eval_set.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "q1",
                        "question": "Quelle est la durée du contrat ?",
                        "ground_truth": "25 ans",
                        "source_doc": "contrat.pdf",
                        "source_section": "Article 2",
                        "answer_type": "factual",
                        "difficulty": "easy",
                    }
                ),
                "",
                json.dumps(
                    {
                        "id": "q2",
                        "question": "Quel est le PIB de la France ?",
                        "ground_truth": "",
                        "source_doc": "contrat.pdf",
                        "answer_type": "negative",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    cases = load_eval_cases(eval_set)

    assert len(cases) == 2
    assert cases[0].id == "q1"
    assert cases[0].source_section == "Article 2"
    assert cases[1].answer_type == "negative"
    assert cases[1].difficulty == "medium"
