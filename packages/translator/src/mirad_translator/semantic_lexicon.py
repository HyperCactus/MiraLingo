"""Semantic lexicon lookup using ChromaDB + jina-embeddings-v5-text-small embeddings.

Extends exact-match lookup (MiradLexiconLookup) with top-k nearest-neighbor
search over English word embeddings. This allows finding translations for
inflected forms ("ran" → "run" → "xebwa"), morphological variants ("houses" →
"house" → "tami"), and semantically related words ("bigger" → "big" → "aga").

Architecture:
    - A new "lexicon" ChromaDB collection stores each English entry as a document
      with its Mirad translation in metadata.
    - The jina-embeddings-v5-text-small model (1024-dim) embeds English words
      for semantic similarity search. This model provides better retrieval
      quality than all-MiniLM-L6-v2, especially for short queries like
      individual English words.
    - SemanticSemantiLookup returns top-k (English, Mirad) pairs per query word,
      optionally merged with exact-match results.
"""

import sqlite3
from pathlib import Path
from typing import Optional

import dspy

from mirad_translator.lexicon_db import DB_PATH, LEXICON_PATH
from mirad_translator.retrieval import _get_embedder, _CHROMA_AVAILABLE

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHROMA_DIR = str(_PROJECT_ROOT / "data" / "chroma_db")

_COLLECTION = None
_INDEXED = False


def _get_lexicon_collection():
    """Lazy-load or build the lexicon ChromaDB collection."""
    global _COLLECTION, _INDEXED
    if not _CHROMA_AVAILABLE:
        raise RuntimeError("chromadb not installed. Run: pip install chromadb")
    if _COLLECTION is not None and _INDEXED:
        return _COLLECTION

    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    _COLLECTION = client.get_or_create_collection(
        name="lexicon",
        metadata={"doc_type": "lexicon"},
    )

    if _COLLECTION.count() == 0:
        _index_lexicon(_COLLECTION)

    _INDEXED = True
    return _COLLECTION


def _index_lexicon(collection):
    """Build the lexicon ChromaDB collection from the SQLite DB.

    Each row becomes a document (the English word) with metadata containing
    the Mirad translation. Embeddings are computed with jina-embeddings-v5-text-small.
    """
    import chromadb

    db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT english, mirad FROM lexicon").fetchall()
    conn.close()

    if not rows:
        raise RuntimeError("Lexicon DB is empty — build it first.")

    embedder = _get_embedder()

    # Batch embed — ChromaDB can accept pre-computed embeddings
    english_words = [r[0] for r in rows]
    mirad_translations = [r[1] for r in rows]

    print(f"[semantic_lexicon] Embedding {len(english_words)} lexicon entries...")
    embeddings = embedder.encode(english_words, show_progress_bar=True, batch_size=1024).tolist()

    ids = [f"lex_{i}" for i in range(len(rows))]
    metadatas = [{"english": en, "mirad": mi} for en, mi in zip(english_words, mirad_translations)]

    # ChromaDB add has a batch-size limit; chunk it for safety with 1024-dim vectors
    batch_size = 5000
    for start in range(0, len(ids), batch_size):
        end = min(start + batch_size, len(ids))
        collection.add(
            ids=ids[start:end],
            documents=english_words[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"[semantic_lexicon] Indexed {len(rows)} lexicon entries into ChromaDB.")
    return len(rows)


def semantic_lookup(
    english_word: str,
    top_k: int = 3,
    min_similarity: float = 0.5,
    include_exact: bool = True,
) -> list[dict]:
    """Look up an English word in the lexicon using semantic similarity.

    Returns up to ``top_k`` results sorted by relevance, each containing:
        - english: The matched English word from the lexicon
        - mirad: The Mirad translation
        - distance: ChromaDB L2 distance (lower = more similar)

    Results below ``min_similarity`` cosine threshold are filtered out.
    If ``include_exact`` is True, an exact match (if found) is always included
    and de-duplicated against the semantic results.

    Args:
        english_word: The word to look up.
        top_k: Maximum number of semantic neighbors to return.
        min_similarity: Minimum cosine similarity (0-1) to include a result.
            jina-embeddings-v5 L2 distances can be converted: cos ≈ 1 - L2²/2
            Default 0.35 filters out very distant hits.
        include_exact: Whether to merge in the exact-match result from SQLite.

    Returns:
        List of dicts with english, mirad, distance, and is_exact keys.
    """
    from mirad_translator.lexicon_db import lookup_word

    collection = _get_lexicon_collection()
    embedder = _get_embedder()

    q_embedding = embedder.encode([english_word.lower()], show_progress_bar=False).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=top_k + (1 if include_exact else 0))

    # Convert L2 distance to approximate cosine similarity for filtering
    # L2² ≈ 2(1 - cos) for normalized vectors => cos ≈ 1 - L2²/2
    semantic_hits = []
    for doc, dist, meta in zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0],
    ):
        cos_sim = max(0, 1.0 - (dist * dist) / 2.0)
        if cos_sim >= min_similarity:
            semantic_hits.append({
                "english": doc,
                "mirad": meta["mirad"],
                "distance": dist,
                "cosine_similarity": round(cos_sim, 4),
                "is_exact": False,
            })

    # Merge exact match if requested
    if include_exact:
        exact_mirad = lookup_word(english_word=english_word)
        if exact_mirad:
            exact_en = english_word.lower()
            # Check if exact match already appears in semantic results
            exact_in_semantic = any(
                h["english"] == exact_en for h in semantic_hits
            )
            if not exact_in_semantic:
                # Prepend exact match with best possible score
                semantic_hits.insert(0, {
                    "english": exact_en,
                    "mirad": exact_mirad,
                    "distance": 0.0,
                    "cosine_similarity": 1.0,
                    "is_exact": True,
                })
            else:
                # Mark the existing semantic hit as exact
                for h in semantic_hits:
                    if h["english"] == exact_en:
                        h["is_exact"] = True
                        break

    return semantic_hits[:top_k]


def semantic_lookup_multi(
    english_text: str,
    top_k_per_word: int = 3,
    max_total_pairs: int = 30,
    min_similarity: float = 0.5,
    include_exact: bool = True,
) -> dict[str, str]:
    """Semantic lookup for all words in an English text.

    For each word, finds the top-k semantically similar English words in the
    lexicon and their Mirad translations, then merges all results into a
    single dict of {english: mirad} pairs. Duplicates are removed; when the
    same English word appears from multiple input words, the first (highest-
    similarity) translation wins.

    Args:
        english_text: The English text to look up words from.
        top_k_per_word: Number of semantic neighbors per input word.
        max_total_pairs: Cap on total output pairs to control prompt size.
        min_similarity: Minimum cosine similarity threshold.
        include_exact: Whether to merge exact-match results.

    Returns:
        Dict mapping English words to their Mirad translations, ready for
        the ``word_equivalents`` field in EnglishToMiradSignature.
    """
    # Simple tokenization — split on whitespace, strip punctuation
    words = []
    for w in english_text.split():
        w_clean = w.strip().rstrip('.,!?;:"\'-()[]{}').lower()
        if w_clean and len(w_clean) > 1:  # Skip single-char tokens
            words.append(w_clean)
    # Deduplicate input words to avoid redundant lookups
    seen_words = set()
    unique_words = []
    for w in words:
        if w not in seen_words:
            seen_words.add(w)
            unique_words.append(w)

    # Collect all lookup results with similarity scores
    all_pairs = {}  # english → (mirad, cosine_similarity, is_exact)

    for word in unique_words:
        hits = semantic_lookup(
            word,
            top_k=top_k_per_word,
            min_similarity=min_similarity,
            include_exact=include_exact,
        )
        for hit in hits:
            en = hit["english"]
            mirad = hit["mirad"]
            sim = hit["cosine_similarity"]
            is_exact = hit["is_exact"]
            # Keep highest-similarity translation for each English word
            if en not in all_pairs or sim > all_pairs[en][1]:
                all_pairs[en] = (mirad, sim, is_exact)

    # Sort by relevance: exact matches first, then by similarity, then alphabetically
    sorted_pairs = sorted(
        all_pairs.items(),
        key=lambda x: (-x[1][2], -x[1][1], x[0]),  # exact first, then sim desc
    )

    # Cap total pairs and return as dict
    result = {}
    for en, (mirad, sim, is_exact) in sorted_pairs[:max_total_pairs]:
        result[en] = mirad

    return result


class MiradSemanticLexiconLookup(dspy.Module):
    """DSPy-traceable semantic lexicon lookup module.

    Uses ChromaDB + jina-embeddings-v5-text-small embeddings to find top-k semantically
    similar English words for each input word, along with their Mirad
    translations. Falls back gracefully if ChromaDB/embeddings are unavailable.
    """

    def __init__(self, db_path=None, top_k_per_word: int = 3, max_total_pairs: int = 30, min_similarity: float = 0.5):
        super().__init__()
        self._db_path = db_path
        self._top_k_per_word = top_k_per_word
        self._max_total_pairs = max_total_pairs
        self._min_similarity = min_similarity

    def forward(self, english_text: str) -> dspy.Prediction:
        try:
            word_equivalents = semantic_lookup_multi(
                english_text,
                top_k_per_word=self._top_k_per_word,
                max_total_pairs=self._max_total_pairs,
                min_similarity=self._min_similarity,
                include_exact=True,
            )
        except Exception:
            # Fallback to exact lookup if semantic search fails
            from mirad_translator.lexicon_db import lookup_word
            words = english_text.split()
            word_equivalents = {}
            for w in words:
                w_clean = w.strip().rstrip('.,!?;:"\'-()[]{}')
                if w_clean:
                    mirad = lookup_word(db_path=self._db_path, english_word=w_clean)
                    if mirad:
                        word_equivalents[w_clean.lower()] = mirad

        return dspy.Prediction(word_equivalents=word_equivalents)