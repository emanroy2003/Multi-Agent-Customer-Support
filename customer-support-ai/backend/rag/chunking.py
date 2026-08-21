"""
Splits long documents into overlapping chunks suitable for embedding.

Uses a simple word-based sliding window. Word-based (rather than
character-based) keeps chunks readable and avoids splitting mid-word.
"""

from backend.config import settings


def chunk_text(
    text: str, chunk_size: int | None = None, chunk_overlap: int | None = None
) -> list[str]:
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    step = max(chunk_size - chunk_overlap, 1)

    while start < len(words):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
        start += step

    return chunks
