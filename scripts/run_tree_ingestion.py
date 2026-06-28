#!/usr/bin/env python
"""CLI : ingestion hiérarchique PDF vers la table doc_nodes (arbre de sections).

Usage:
    python scripts/run_tree_ingestion.py --source sample_corpus/docs/
    python scripts/run_tree_ingestion.py --source data/contrat.pdf data/avenant.pdf
    python scripts/run_tree_ingestion.py --source data/archive.zip
"""

import argparse
import sys
from pathlib import Path

from rip_agent.ingestion.discovery import discover_pdf_paths
from rip_agent.ingestion.tree_pipeline import TreeIngestPipeline
from rip_agent.telemetry import setup_telemetry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingère un ou plusieurs PDF dans la table doc_nodes (retrieval hiérarchique)."
    )
    parser.add_argument(
        "--source",
        nargs="+",
        required=True,
        help="Fichier(s) PDF, dossier(s) ou archive(s) .zip contenant des PDF",
    )
    args = parser.parse_args()

    setup_telemetry("rip-agent-tree-ingestion")

    paths = discover_pdf_paths([Path(s) for s in args.source])
    if not paths:
        print("Aucun fichier PDF trouvé pour les sources fournies.", file=sys.stderr)
        return 1

    report = TreeIngestPipeline().run(paths)

    print(f"Documents traités : {report.documents_processed}")
    print(f"Feuilles insérées : {report.chunks_inserted}")
    if report.failed_paths:
        print(f"Échecs ({len(report.failed_paths)}) :", file=sys.stderr)
        for failed in report.failed_paths:
            print(f"  - {failed}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
