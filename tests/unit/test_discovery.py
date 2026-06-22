import zipfile
from pathlib import Path

import pytest

from rip_agent.ingestion.discovery import discover_pdf_paths


def _touch_pdf(path: Path) -> Path:
    path.write_bytes(b"%PDF-1.4 fake")
    return path


def test_discover_single_pdf_file(tmp_path: Path) -> None:
    pdf = _touch_pdf(tmp_path / "contrat.pdf")

    assert discover_pdf_paths([pdf]) == [pdf]


def test_discover_recurses_into_nested_folders(tmp_path: Path) -> None:
    (tmp_path / "sous_dossier").mkdir()
    top_pdf = _touch_pdf(tmp_path / "a.pdf")
    nested_pdf = _touch_pdf(tmp_path / "sous_dossier" / "b.pdf")
    _ = (tmp_path / "notes.txt").write_text("pas un pdf")

    assert discover_pdf_paths([tmp_path]) == sorted([top_pdf, nested_pdf])


def test_discover_extracts_pdfs_from_zip(tmp_path: Path) -> None:
    pdf_source = _touch_pdf(tmp_path / "contrat.pdf")
    zip_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(pdf_source, arcname="contrat.pdf")

    extract_root = tmp_path / "extracted"
    found = discover_pdf_paths([zip_path], extract_root=extract_root)

    assert len(found) == 1
    assert found[0].name == "contrat.pdf"
    assert found[0].is_relative_to(extract_root)


def test_discover_rejects_zip_slip(tmp_path: Path) -> None:
    zip_path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("../../etc/evil.pdf", b"%PDF-1.4 fake")

    with pytest.raises(ValueError, match="path traversal"):
        discover_pdf_paths([zip_path], extract_root=tmp_path / "extracted")


def test_discover_deduplicates_paths(tmp_path: Path) -> None:
    pdf = _touch_pdf(tmp_path / "contrat.pdf")

    assert discover_pdf_paths([pdf, pdf]) == [pdf]
