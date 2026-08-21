from backend.rag.chunking import chunk_text
from backend.rag.vector_store import VectorStore


def test_chunking_produces_overlapping_chunks():
    text = " ".join(f"word{i}" for i in range(1200))
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 2
    # Every chunk should be non-empty and within expected word count
    for c in chunks:
        assert 0 < len(c.split()) <= 500


def test_chunking_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_vector_store_build_and_search(tmp_path):
    store = VectorStore(index_path=str(tmp_path / "index"))
    count = store.build_from_knowledge_base()
    assert count > 0

    results = store.search("refund policy", top_k=3)
    assert len(results) > 0
    assert all(r.source.endswith((".txt", ".pdf")) for r in results)


def test_vector_store_save_and_load_roundtrip(tmp_path):
    index_path = str(tmp_path / "index")
    store = VectorStore(index_path=index_path)
    store.build_from_knowledge_base()
    store.save()

    reloaded = VectorStore(index_path=index_path)
    assert reloaded.load() is True
    assert reloaded.index.ntotal == store.index.ntotal
