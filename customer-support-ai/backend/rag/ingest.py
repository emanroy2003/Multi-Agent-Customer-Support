"""
Run this once (and any time knowledge_base/ changes) to (re)build the FAISS index.

Usage:
    python -m backend.rag.ingest
"""

from backend.rag.vector_store import VectorStore
from backend.utils.logger import logger


def main():
    store = VectorStore()
    count = store.build_from_knowledge_base()
    store.save()
    logger.info(f"Ingestion complete: {count} chunks indexed.")


if __name__ == "__main__":
    main()
