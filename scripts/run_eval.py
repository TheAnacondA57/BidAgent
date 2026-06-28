"""CLI : lance l'évaluation sur un jeu de cas JSONL.

Usage:
    python scripts/run_eval.py --eval-set eval/cases.jsonl
    python scripts/run_eval.py --eval-set eval/cases.jsonl --tree
"""

import argparse
import sys
from pathlib import Path

from rip_agent.config import Settings, get_settings
from rip_agent.evaluation.loader import load_eval_cases
from rip_agent.evaluation.runner import EvalRunner
from rip_agent.telemetry import setup_telemetry


def main() -> int:
    setup_telemetry("rip-agent-eval")

    parser = argparse.ArgumentParser(description="Lance l'évaluation RIP-Agent sur un jeu de cas JSONL")
    parser.add_argument("--eval-set", required=True, help="Chemin vers le fichier JSONL de cas d'éval")
    parser.add_argument(
        "--tree",
        action="store_true",
        help="Utilise TreeRetrievalPipeline (doc_nodes) au lieu du retrieval plat",
    )
    args = parser.parse_args()

    settings = Settings(use_tree_retrieval=True) if args.tree else get_settings()
    cases = load_eval_cases(Path(args.eval_set))
    report = EvalRunner(settings=settings).run(cases)

    print(f"Cas évalués       : {len(report.results)}")
    print(f"Hit rate          : {report.hit_rate:.2%}")
    print(f"Correctness moy.  : {report.correctness_avg:.2f}" if report.correctness_avg is not None else "Correctness moy.  : n/a")
    print(f"Faithfulness moy. : {report.faithfulness_avg:.2f}" if report.faithfulness_avg is not None else "Faithfulness moy. : n/a")

    return 0


if __name__ == "__main__":
    sys.exit(main())
