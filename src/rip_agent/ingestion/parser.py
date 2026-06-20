import uuid
from pathlib import Path
from typing import Protocol

from rip_agent.config import Settings, get_settings
from rip_agent.schemas.document import Document


class ParsedPage(Protocol):
    text: str


class PdfParserClient(Protocol):
    def load_data(self, file_path: str) -> list[ParsedPage]: ...


def _build_client(settings: Settings) -> PdfParserClient:
    from llama_parse import LlamaParse

    return LlamaParse(api_key=settings.llamaparse_api_key, result_type="markdown")


def parse_pdf(
    path: Path,
    settings: Settings | None = None,
    client: PdfParserClient | None = None,
) -> Document:
    """Parse a single PDF into a Document with its raw (markdown) text.

    `client` can be injected to bypass the real LlamaParse network call in tests.
    """
    settings = settings or get_settings()
    client = client or _build_client(settings)

    pages = client.load_data(str(path))
    raw_text = "\n\n".join(page.text for page in pages)

    return Document(
        id=str(uuid.uuid4()),
        source_path=str(path),
        title=path.stem,
        raw_text=raw_text,
        metadata={"num_pages": str(len(pages))},
    )
