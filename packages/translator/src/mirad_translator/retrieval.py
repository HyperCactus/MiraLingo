"""ChromaDB retrieval for grammar and thesaurus chunks."""
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHROMA_DIR = str(_PROJECT_ROOT / "data" / "chroma_db")

_CHROMA_AVAILABLE = False
_ST_AVAILABLE = False
_grammar_collection = None
_thesaurus_collection = None
_embedding_model = None

try:
    import chromadb
    _CHROMA_AVAILABLE = True
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    SentenceTransformer = None

from .chunker import get_grammar_chunks, get_thesaurus_chunks, count_tokens


def _get_embedder():
    global _embedding_model
    if _embedding_model is None:
        if not _ST_AVAILABLE:
            raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def _get_grammar_collection():
    global _grammar_collection
    if _grammar_collection is None:
        if not _CHROMA_AVAILABLE:
            raise RuntimeError("chromadb not installed. Run: pip install chromadb")
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _grammar_collection = client.get_or_create_collection(
            name="grammar", metadata={"doc_type": "grammar"}
        )
        if _grammar_collection.count() == 0:
            _index_grammar(_grammar_collection)
    return _grammar_collection


def _get_thesaurus_collection():
    global _thesaurus_collection
    if _thesaurus_collection is None:
        if not _CHROMA_AVAILABLE:
            raise RuntimeError("chromadb not installed. Run: pip install chromadb")
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _thesaurus_collection = client.get_or_create_collection(
            name="thesaurus", metadata={"doc_type": "thesaurus"}
        )
        if _thesaurus_collection.count() == 0:
            _index_thesaurus(_thesaurus_collection)
    return _thesaurus_collection


def _index_grammar(collection):
    chunks = get_grammar_chunks()
    embedder = _get_embedder()
    ids = [f"grammar_{i}" for i in range(len(chunks))]
    embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
    metadatas = [{"source_section": "grammar", "chunk_index": i, "doc_type": "grammar"} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def _index_thesaurus(collection):
    chunks = get_thesaurus_chunks()
    embedder = _get_embedder()
    ids = [f"thesaurus_{i}" for i in range(len(chunks))]
    embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
    metadatas = [{"source_section": "thesaurus", "chunk_index": i, "doc_type": "thesaurus"} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def retrieve_grammar(query, top_k=3):
    """Retrieve top_k grammar chunks for a query."""
    collection = _get_grammar_collection()
    embedder = _get_embedder()
    q_embedding = embedder.encode([query], show_progress_bar=False).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=top_k)
    return [
        {"text": doc, "distance": dist, "metadata": meta}
        for doc, dist, meta in zip(
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0]
        )
    ]


def retrieve_thesaurus(query, top_k=3):
    """Retrieve top_k thesaurus chunks for a query."""
    collection = _get_thesaurus_collection()
    embedder = _get_embedder()
    q_embedding = embedder.encode([query], show_progress_bar=False).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=top_k)
    return [
        {"text": doc, "distance": dist, "metadata": meta}
        for doc, dist, meta in zip(
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0]
        )
    ]


def retrieve_all(query, top_k=3):
    """Retrieve top_k chunks from both grammar and thesaurus."""
    return {
        "grammar": retrieve_grammar(query, top_k),
        "thesaurus": retrieve_thesaurus(query, top_k),
    }


def build_indexes():
    """Force-build both ChromaDB indexes."""
    if not _CHROMA_AVAILABLE:
        raise RuntimeError("chromadb not installed.")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    gc = client.get_or_create_collection("grammar", metadata={"doc_type": "grammar"})
    tc = client.get_or_create_collection("thesaurus", metadata={"doc_type": "thesaurus"})
    n_g = _index_grammar(gc)
    n_t = _index_thesaurus(tc)
    return {"grammar_chunks": n_g, "thesaurus_chunks": n_t}


def get_chunk_counts():
    """Return current chunk counts in ChromaDB."""
    if not _CHROMA_AVAILABLE:
        return {"grammar": 0, "thesaurus": 0}
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    gc = client.get_or_create_collection("grammar")
    tc = client.get_or_create_collection("thesaurus")
    return {"grammar": gc.count(), "thesaurus": tc.count()}