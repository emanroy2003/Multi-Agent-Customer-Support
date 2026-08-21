"""
FAISS-backed vector store for semantic search over the knowledge base.

Stores an IndexFlatIP (inner product = cosine similarity, since
embeddings are normalized) alongside a parallel metadata list
(source filename + chunk text) pickled to disk.
"""

import pickle
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from backend.config import settings
from backend.rag.chunking import chunk_text
from backend.rag.embeddings import embed_query, embed_texts
from backend.rag.loader import load_knowledge_base
from backend.utils.logger import logger


@dataclass
class SearchResult:
    source: str
    chunk: str
    score: float


class VectorStore:
    def __init__(self, index_path: str | None = None):
        self.index_path = Path(index_path or settings.faiss_index_path)
        self.index: faiss.Index | None = None
        self.metadata: list[dict] = []  # parallel to index vectors: {"source": ..., "chunk": ...}

    # ---------- Build ----------

    def build_from_knowledge_base(self) -> int:
        """Loads all docs from knowledge_base/, chunks, embeds, and builds the index."""
        documents = load_knowledge_base()
        all_chunks: list[str] = []
        metadata: list[dict] = []

        for doc in documents:
            for chunk in chunk_text(doc.text):
                all_chunks.append(chunk)
                metadata.append({"source": doc.source, "chunk": chunk})

        if not all_chunks:
            logger.warning("No chunks produced from knowledge base; index will be empty.")
            self.index = faiss.IndexFlatIP(384)  # MiniLM-L6-v2 dimension
            self.metadata = []
            return 0

        embeddings = embed_texts(all_chunks)
        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        self.index = index
        self.metadata = metadata

        logger.info(f"Built FAISS index with {index.ntotal} vectors (dim={dimension})")
        return index.ntotal

    # ---------- Persistence ----------

    def save(self):
        self.index_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Saved FAISS index to {self.index_path}")

    def load(self) -> bool:
        index_file = self.index_path / "index.faiss"
        meta_file = self.index_path / "metadata.pkl"
        if not index_file.exists() or not meta_file.exists():
            return False

        self.index = faiss.read_index(str(index_file))
        with open(meta_file, "rb") as f:
            self.metadata = pickle.load(f)

        logger.info(f"Loaded FAISS index from {self.index_path} ({self.index.ntotal} vectors)")
        return True

    # ---------- Search ----------

    def search(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        if self.index is None or self.index.ntotal == 0:
            return []

        top_k = top_k or settings.top_k_results
        query_vec = np.expand_dims(embed_query(query), axis=0)
        scores, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx]
            results.append(SearchResult(source=meta["source"], chunk=meta["chunk"], score=float(score)))

        return results


# Module-level singleton, loaded/built once on app startup (see main.py)
vector_store = VectorStore()
