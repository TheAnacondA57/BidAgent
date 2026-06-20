from dataclasses import dataclass
from pathlib import Path

from rip_agent.config import Settings
from rip_agent.ingestion.parser import parse_pdf


@dataclass
class FakePage:
    text: str


class FakeClient:
    def __init__(self, pages: list[FakePage]) -> None:
        self._pages = pages

    def load_data(self, file_path: str) -> list[FakePage]:
        return self._pages


def test_parse_pdf_builds_document_from_pages() -> None:
    client = FakeClient([FakePage(text="# Article 1\ncontenu"), FakePage(text="# Article 2\nautre")])

    doc = parse_pdf(Path("contrat_dsp.pdf"), settings=Settings(), client=client)

    assert doc.title == "contrat_dsp"
    assert doc.source_path == "contrat_dsp.pdf"
    assert "Article 1" in doc.raw_text
    assert "Article 2" in doc.raw_text
    assert doc.metadata["num_pages"] == "2"
    assert doc.id
