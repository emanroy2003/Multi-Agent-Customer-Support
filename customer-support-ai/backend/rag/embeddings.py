"""
Embedding model wrapper around sentence-transformers.

Loaded once (module-level singleton) since loading the model is
expensive and every RAG query needs it.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import settings
from backend.utils.logger import logger


@lru_cache
def get_embedder() -> SentenceTransformer:
    logger.info(f"Loading embedding model: {settings.embedding_model}")
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of strings, returning an (N, D) float32 normalized matrix."""
    model = get_embedder()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,  # so we can use inner-product = cosine similarity
    )
    return embeddings.astype("float32")


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])[0]
