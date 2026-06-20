#!/usr/bin/env python
"""Génère le corpus factice versionné dans sample_corpus/docs/.

Ce script n'est pas un module métier : il sert uniquement à reproduire les
PDF d'exemple (contrats DSP fictifs, sans rapport avec un vrai document de
concession) afin que le repo reste clonable et testable sans données
confidentielles.

Usage: python scripts/generate_sample_corpus.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample_corpus" / "docs"

_CONTRAT_PRINCIPAL = [
    ("Heading1", "Contrat de concession fictif - Réseau Très Haut Débit"),
    ("Heading2", "Article 1 - Objet"),
    (
        "Normal",
        "Le présent contrat fictif a pour objet la conception, le déploiement et "
        "l'exploitation d'un réseau de communications électroniques à très haut "
        "débit sur le territoire de la collectivité fictive de Beauchamps-sur-Rip.",
    ),
    ("Heading2", "Article 2 - Durée"),
    (
        "Normal",
        "Le contrat est conclu pour une durée de vingt-cinq (25) ans à compter de "
        "sa date de notification, soit du 1er janvier 2020 au 31 décembre 2044.",
    ),
    ("Heading2", "Article 3 - Obligations de l'opérateur"),
    (
        "Normal",
        "L'opérateur s'engage à raccorder au moins quatre-vingt-quinze pour cent "
        "(95%) des locaux de la zone de déploiement avant le 31 décembre 2026. "
        "Il transmet un rapport d'avancement trimestriel à la collectivité.",
    ),
    ("Heading2", "Article 4 - Pénalités"),
    (
        "Normal",
        "En cas de retard constaté sur le calendrier de déploiement prévu à "
        "l'Article 3, une pénalité de 500 euros par local manquant et par mois "
        "de retard est appliquée, dans la limite de 2% du montant annuel du contrat.",
    ),
]

_AVENANT = [
    ("Heading1", "Avenant n°1 au contrat de concession fictif"),
    ("Heading2", "Article 1 - Modification du calendrier"),
    (
        "Normal",
        "Le calendrier de déploiement prévu à l'Article 3 du contrat principal "
        "est prolongé de douze (12) mois en raison de difficultés d'accès au "
        "génie civil existant.",
    ),
    ("Heading2", "Article 2 - Maintien des autres clauses"),
    (
        "Normal",
        "Toutes les autres clauses du contrat principal, notamment celles "
        "relatives aux pénalités prévues à l'Article 4, demeurent inchangées.",
    ),
]


def _write_pdf(filename: str, sections: list[tuple[str, str]]) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(OUTPUT_DIR / filename), pagesize=A4)
    flowables = []
    for style_name, text in sections:
        flowables.append(Paragraph(text, styles[style_name]))
        flowables.append(Spacer(1, 12))
    doc.build(flowables)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_pdf("contrat_dsp_fictif.pdf", _CONTRAT_PRINCIPAL)
    _write_pdf("avenant_1_fictif.pdf", _AVENANT)
    print(f"Corpus factice généré dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
