"""
Shared pytest fixtures.

Crucially, `mock_embeddings` replaces the real sentence-transformers
calls with a deterministic hash-based embedding function. This lets
the full RAG pipeline (chunking -> embed -> FAISS index -> search) be
tested without downloading model weights from huggingface.co, which
this sandbox's network policy blocks. On a real machine with normal
internet access, the actual MiniLM model is used instead (see
backend/rag/embeddings.py) -- this mock exists purely for offline CI.
"""

import hashlib
import os

os.environ.setdefault("DATABASE_TYPE", "sqlite")
os.environ.setdefault("SQLITE_URL", "sqlite:///./test.db")

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DIM = 384


def _fake_vector(text: str) -> np.ndarray:
    """Deterministic pseudo-embedding derived from a text hash (unit-normalized)."""
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.random(DIM).astype("float32")
    return vec / np.linalg.norm(vec)


@pytest.fixture(autouse=True)
def mock_embeddings(monkeypatch):
    import backend.rag.embeddings as emb

    def fake_embed_texts(texts):
        return np.stack([_fake_vector(t) for t in texts]).astype("float32")

    def fake_embed_query(text):
        return _fake_vector(text)

    monkeypatch.setattr(emb, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(emb, "embed_query", fake_embed_query)

    import backend.rag.vector_store as vs

    monkeypatch.setattr(vs, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(vs, "embed_query", fake_embed_query)
    yield


@pytest.fixture
def test_engine(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    from backend.database.session import Base
    from backend.models import conversation, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_engine, monkeypatch):
    from backend.database.session import get_db
    from backend.main import app
    from sqlalchemy.orm import sessionmaker

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
