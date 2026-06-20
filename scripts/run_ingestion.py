#!/usr/bin/env python
"""CLI : lance l'ingestion PDF seule, sans passer par l'API.

Usage:
    python scripts/run_ingestion.py --source sample_corpus/docs/
    python scripts/run_ingestion.py --source data/contrat.pdf data/avenant.pdf
"""

import argparse
import sys
from pathlib import Path

from rip_agent.ingestion.pipeline import IngestPipeline
from rip_agent.telemetry import setup_telemetry


def _collect_pdf_paths(sources: list[str]) -> list[Path]:
    paths: list[Path] = []
    for source in sources:
        path = Path(source)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.pdf")))
        else:
            paths.append(path)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingère un ou plusieurs PDF dans pgvector.")
    parser.add_argument(
        "--source",
        nargs="+",
        required=True,
        help="Fichier(s) PDF ou dossier(s) contenant des PDF",
    )
    args = parser.parse_args()

    setup_telemetry(service_name="rip-agent-ingestion")

    paths = _collect_pdf_paths(args.source)
    if not paths:
        print("Aucun fichier PDF trouvé pour les sources fournies.", file=sys.stderr)
        return 1

    report = IngestPipeline().run(paths)

    print(f"Documents traités : {report.documents_processed}")
    print(f"Chunks insérés    : {report.chunks_inserted}")
    if report.failed_paths:
        print(f"Échecs ({len(report.failed_paths)}) :", file=sys.stderr)
        for failed in report.failed_paths:
            print(f"  - {failed}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
