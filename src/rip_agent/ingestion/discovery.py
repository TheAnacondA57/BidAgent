import tempfile
import zipfile
from collections.abc import Sequence
from pathlib import Path


def discover_pdf_paths(sources: Sequence[Path], extract_root: Path | None = None) -> list[Path]:
    """Resolve files, folders, and zip archives into a flat, deduplicated list of PDF paths.

    Folders are scanned recursively. Zip archives are extracted (with zip-slip
    protection) under `extract_root` — or the system temp dir if unset — and
    the extracted content is scanned the same way, so a zip-of-zips works too.
    """
    if extract_root is not None:
        extract_root.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for source in sources:
        paths.extend(_discover_one(Path(source), extract_root))
    return sorted(set(paths))


def _discover_one(source: Path, extract_root: Path | None) -> list[Path]:
    if source.is_dir():
        found: list[Path] = []
        for entry in sorted(source.iterdir()):
            found.extend(_discover_one(entry, extract_root))
        return found
    if source.suffix.lower() == ".zip":
        extracted_dir = _extract_zip(source, extract_root)
        return _discover_one(extracted_dir, extract_root)
    if source.suffix.lower() == ".pdf":
        return [source]
    return []


def _extract_zip(zip_path: Path, extract_root: Path | None) -> Path:
    target_dir = Path(tempfile.mkdtemp(prefix=f"{zip_path.stem}_", dir=extract_root))
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            member_path = (target_dir / member).resolve()
            if not member_path.is_relative_to(target_dir.resolve()):
                raise ValueError(f"Entrée zip suspecte (path traversal) : {member}")
        archive.extractall(target_dir)
    return target_dir
