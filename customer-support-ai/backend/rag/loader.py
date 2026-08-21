"""
Loads raw documents from the knowledge_base/ directory.

Supports .txt and .pdf. Each loaded document keeps its source
filename as metadata so RAG answers can cite sources.
"""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from backend.config import settings
from backend.utils.logger import logger


@dataclass
class RawDocument:
    source: str
    text: str


def _load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_knowledge_base(kb_path: str | None = None) -> list[RawDocument]:
    kb_dir = Path(kb_path or settings.knowledge_base_path)
    if not kb_dir.exists():
        logger.warning(f"Knowledge base path does not exist: {kb_dir}")
        return []

    documents: list[RawDocument] = []
    for file_path in sorted(kb_dir.glob("**/*")):
        if file_path.suffix.lower() == ".txt":
            text = _load_txt(file_path)
        elif file_path.suffix.lower() == ".pdf":
            text = _load_pdf(file_path)
        else:
            continue

        if text.strip():
            documents.append(RawDocument(source=file_path.name, text=text))

    logger.info(f"Loaded {len(documents)} document(s) from {kb_dir}")
    return documents
