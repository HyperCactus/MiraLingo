"""ChromaDB retrieval for structured grammar rules and thesaurus chunks.

Grammar rules are indexed one-per-document from nirad_grammer_rules.json.
Retrieval uses combined scoring: r = c² + i² where c = cosine similarity
(derived from ChromaDB L2 distance) and i = the rule's importance score (0-1).
"""
from pathlib import Path
import json
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHROMA_DIR = str(_PROJECT_ROOT / "data" / "chroma_db")

_EMBEDDING_MODEL_NAME = "jinaai/jina-embeddings-v5-text-small"
_EMBEDDING_MODEL_KWARGS = {"trust_remote_code": True, "model_kwargs": {"default_task": "retrieval"}}

_CHROMA_AVAILABLE = False
_ST_AVAILABLE = False
_grammar_collection = None
_thesaurus_collection = None
_grammar_rules_collection = None
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
        _embedding_model = SentenceTransformer(_EMBEDDING_MODEL_NAME, **_EMBEDDING_MODEL_KWARGS)
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


def _get_grammar_rules_path() -> Path:
    return _PROJECT_ROOT / "data" / "mirad-docs" / "nirad_grammer_rules.json"


def _load_grammar_rules() -> list[dict[str, Any]]:
    path = _get_grammar_rules_path()
    if not path.exists():
        raise FileNotFoundError(f"Grammar rules JSON not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    rule_sets = data.get("rule_sets", {}) if isinstance(data, dict) else {}
    rules: list[dict[str, Any]] = []

    for section, section_rules in rule_sets.items():
        if not isinstance(section_rules, list):
            continue
        for idx, rule in enumerate(section_rules):
            if not isinstance(rule, dict):
                continue
            rid = rule.get("id") or f"{section}.{idx}"
            tags = rule.get("retrieval_tags") or []
            if not isinstance(tags, list):
                tags = [str(tags)]
            examples = rule.get("examples") or []

            rule_payload = rule.get("rule") or {}
            if isinstance(rule_payload, dict):
                description = rule_payload.get("description") or ""
                pseudocode_payload = rule_payload.get("pseudocode") or []
            else:
                description = str(rule_payload)
                pseudocode_payload = rule.get("pseudocode") or []

            if isinstance(pseudocode_payload, list):
                pseudocode = "\n".join(str(line) for line in pseudocode_payload)
            else:
                pseudocode = str(pseudocode_payload or "")

            importance = rule.get("importance")
            if importance is not None:
                try:
                    importance = float(importance)
                except (ValueError, TypeError):
                    importance = 0.5
            else:
                importance = 0.5  # default importance if not specified

            rules.append(
                {
                    "id": str(rid),
                    "section": section,
                    "title": str(rule.get("title") or ""),
                    "description": str(description),
                    "pseudocode": pseudocode,
                    "examples": examples if isinstance(examples, list) else [examples],
                    "retrieval_tags": [str(t) for t in tags],
                    "direction": rule.get("direction") if isinstance(rule.get("direction"), list) else [],
                    "category": str(rule.get("category") or ""),
                    "subcategory": str(rule.get("subcategory") or ""),
                    "priority": int(rule.get("priority") or 0),
                    "importance": importance,
                }
            )

    return rules


def _format_rule_document(rule: dict[str, Any]) -> str:
    examples = rule.get("examples") or []
    ex_lines = []
    for ex in examples[:3]:
        if isinstance(ex, dict):
            mi = ex.get("mirad", "")
            en = ex.get("english", "")
            if mi or en:
                ex_lines.append(f"- {mi} => {en}".strip())
        else:
            ex_lines.append(f"- {str(ex)}")
    ex_text = "\n".join(ex_lines)

    return (
        f"ID: {rule.get('id', '')}\n"
        f"SECTION: {rule.get('section', '')}\n"
        f"TITLE: {rule.get('title', '')}\n"
        f"DESCRIPTION: {rule.get('description', '')}\n"
        f"PSEUDOCODE: {rule.get('pseudocode', '')}\n"
        f"EXAMPLES:\n{ex_text}".strip()
    )


def _get_grammar_rules_collection():
    global _grammar_rules_collection
    if _grammar_rules_collection is None:
        if not _CHROMA_AVAILABLE:
            raise RuntimeError("chromadb not installed. Run: pip install chromadb")
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _grammar_rules_collection = client.get_or_create_collection(
            name="grammar_rules", metadata={"doc_type": "grammar_rules"}
        )
        if _grammar_rules_collection.count() == 0:
            _index_grammar_rules(_grammar_rules_collection)
    return _grammar_rules_collection


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


def _batch_encode(embedder, texts, batch_size=1):
    """Encode texts item-by-item with OOM recovery for long documents.

    jina-embeddings-v5 uses a Qwen3-0.6B backbone whose attention scales
    quadratically with sequence length. Grammar chunks average 236 words
    (max 1944 → ~4000 tokens), which OOMs on 8GB GPUs.

    On OOM, we move the model to CPU and continue there. CPU is slower
    (~5x) but handles arbitrary document lengths without OOM.
    """
    import torch
    all_embeddings = []
    on_cpu = False

    for i, text in enumerate(texts):
        try:
            emb = embedder.encode([text], show_progress_bar=False, batch_size=1)
            if hasattr(emb, "cpu"):
                emb = emb.cpu().numpy()
            all_embeddings.append(emb[0].tolist())
        except RuntimeError as e:
            if "out of memory" in str(e).lower() and torch.cuda.is_available() and not on_cpu:
                n_words = len(text.split())
                print(f"[retrieval] GPU OOM on item {i}/{len(texts)} ({n_words} words). "
                      f"Moving embedder to CPU...")
                torch.cuda.empty_cache()
                embedder = embedder.to("cpu")
                on_cpu = True
                # Retry on CPU
                emb = embedder.encode([text], show_progress_bar=False, batch_size=1)
                if hasattr(emb, "numpy"):
                    emb = emb.numpy()
                all_embeddings.append(emb[0].tolist())
            else:
                raise
        if torch.cuda.is_available() and not on_cpu and (i + 1) % 50 == 0:
            torch.cuda.empty_cache()

    # If embedder was moved to CPU, update the global singleton so subsequent
    # calls (e.g. retrieval queries) also use CPU. Queries are short texts,
    # so the ~5x latency increase is acceptable.
    if on_cpu:
        global _embedding_model
        _embedding_model = embedder

    return all_embeddings


def _index_grammar(collection):
    chunks = get_grammar_chunks()
    embedder = _get_embedder()
    ids = [f"grammar_{i}" for i in range(len(chunks))]
    embeddings = _batch_encode(embedder, chunks)
    metadatas = [{"source_section": "grammar", "chunk_index": i, "doc_type": "grammar"} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def _index_grammar_rules(collection):
    rules = _load_grammar_rules()
    if not rules:
        return 0

    embedder = _get_embedder()
    # Embed retrieval tags only (as requested), but persist full structured rule payload in metadata.
    tag_texts = ["; ".join(r.get("retrieval_tags", [])) for r in rules]
    embeddings = _batch_encode(embedder, tag_texts)
    ids = [f"grammar_rule_{i}" for i in range(len(rules))]
    docs = [_format_rule_document(r) for r in rules]
    metadatas = []
    for i, rule in enumerate(rules):
        examples = rule.get("examples") or []
        examples_text = json.dumps(examples[:5], ensure_ascii=False)
        metadatas.append(
            {
                "doc_type": "grammar_rule",
                "source_section": rule.get("section", "grammar_rules"),
                "rule_id": rule.get("id", f"rule_{i}"),
                "title": rule.get("title", ""),
                "description": rule.get("description", ""),
                "pseudocode": rule.get("pseudocode", ""),
                "examples": examples_text,
                "retrieval_tags": "; ".join(rule.get("retrieval_tags", [])),
                "direction": "; ".join(rule.get("direction", [])),
                "category": rule.get("category", ""),
                "subcategory": rule.get("subcategory", ""),
                "priority": rule.get("priority", 0),
                "importance": rule.get("importance", 0.5),
            }
        )

    collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
    return len(rules)


def _index_thesaurus(collection):
    chunks = get_thesaurus_chunks()
    embedder = _get_embedder()
    ids = [f"thesaurus_{i}" for i in range(len(chunks))]
    embeddings = _batch_encode(embedder, chunks)
    metadatas = [{"source_section": "thesaurus", "chunk_index": i, "doc_type": "thesaurus"} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def retrieve_grammar(query, top_k=3, importance_weight=1.0):
    """Retrieve top_k grammar rules for a query using combined scoring.

    Uses r = c² + i² where c = cosine similarity (from ChromaDB L2 distance)
    and i = the rule's importance score (0-1). Both c and i are in [0,1],
    so r is in [0,2]. Rules that are both semantically close and important
    are ranked highest.

    Args:
        query: Search query text.
        top_k: Number of rules to return.
        importance_weight: Weight for the importance component. Default 1.0
            means r = c² + i². Set to 0 to ignore importance.
    """
    collection = _get_grammar_rules_collection()
    embedder = _get_embedder()
    q_embedding = embedder.encode([query], show_progress_bar=False).tolist()

    # Retrieve more candidates than needed so we can re-rank by combined score
    n_candidates = min(top_k * 4, collection.count()) if collection.count() > 0 else top_k
    n_candidates = max(n_candidates, top_k)
    results = collection.query(query_embeddings=q_embedding, n_results=n_candidates)

    # Re-rank by combined score: c² + i²
    scored = []
    for doc, dist, meta in zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0],
    ):
        # L2 distance → cosine similarity: cos ≈ 1 - L2²/2
        cos_sim = max(0.0, 1.0 - (dist * dist) / 2.0)
        importance = float(meta.get("importance", 0.5))

        # Combined score: c² + (importance_weight * i²)
        combined = (cos_sim ** 2) + (importance_weight * importance ** 2)
        scored.append((combined, cos_sim, doc, dist, meta))

    # Sort by combined score descending and take top_k
    scored.sort(key=lambda x: x[0], reverse=True)

    output = []
    for combined, cos_sim, doc, dist, meta in scored[:top_k]:
        examples = []
        try:
            examples = json.loads(meta.get("examples", "[]") or "[]")
        except Exception:
            examples = []

        output.append(
            {
                "text": doc,
                "distance": dist,
                "cosine_similarity": round(cos_sim, 4),
                "importance": float(meta.get("importance", 0.5)),
                "combined_score": round(combined, 4),
                "metadata": meta,
                "rule": {
                    "id": meta.get("rule_id", ""),
                    "description": meta.get("description", ""),
                    "pseudocode": meta.get("pseudocode", ""),
                    "examples": examples,
                    "retrieval_tags": [t.strip() for t in (meta.get("retrieval_tags", "") or "").split(";") if t.strip()],
                },
            }
        )
    return output


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
    """Force-build grammar-rules and thesaurus ChromaDB indexes."""
    if not _CHROMA_AVAILABLE:
        raise RuntimeError("chromadb not installed.")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    grc = client.get_or_create_collection("grammar_rules", metadata={"doc_type": "grammar_rules"})
    tc = client.get_or_create_collection("thesaurus", metadata={"doc_type": "thesaurus"})

    # Clear existing data for clean rebuild
    if grc.count() > 0:
        grc_ids = grc.get()["ids"]
        if grc_ids:
            grc.delete(ids=grc_ids)
    if tc.count() > 0:
        tc_ids = tc.get()["ids"]
        if tc_ids:
            tc.delete(ids=tc_ids)

    n_gr = _index_grammar_rules(grc)
    n_t = _index_thesaurus(tc)

    # Reset cached collections so next access picks up fresh data
    global _grammar_rules_collection, _thesaurus_collection
    _grammar_rules_collection = grc
    _thesaurus_collection = tc
    return {"grammar_rules": n_gr, "thesaurus_chunks": n_t}


def get_chunk_counts():
    """Return current index counts in ChromaDB."""
    if not _CHROMA_AVAILABLE:
        return {"grammar": 0, "grammar_rules": 0, "thesaurus": 0}
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    grc = client.get_or_create_collection("grammar_rules")
    tc = client.get_or_create_collection("thesaurus")
    count = grc.count()
    return {"grammar": count, "grammar_rules": count, "thesaurus": tc.count()}
