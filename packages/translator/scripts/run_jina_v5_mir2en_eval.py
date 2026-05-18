#!/usr/bin/env python3
"""
Evaluate Mir→En translation with jina-embeddings-v5-text-small.

Uses the pre-compiled Mir→En bootstrap_fast program, 50 random samples,
DeepSeek-V4-Flash LM. Reports:
  - Normalized exact match (punctuation-tolerant)
  - Exact string match
  - Semantic similarity (jina-v5 cosine similarity on English text)

Usage:
    python run_jina_v5_mir2en_eval.py
"""

import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # packages/translator/scripts/x.py → project root
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import dspy

RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COMPILED_MIR2EN_DIR = str(RESULTS_DIR / "compiled_mir2en_program")

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text


def _strip_punct(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def _strip_punct_lower(s: str) -> str:
    """Strip punctuation and lowercase for case-insensitive comparison."""
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def normalized_match_mir_to_en(gold_en: str, pred_en: str) -> float:
    """Case-insensitive, punctuation-tolerant match for Mir→En direction."""
    gold = _normalize(gold_en)
    pred = _normalize(pred_en)
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct_lower(gold) == _strip_punct_lower(pred) else 0.0


def exact_match_mir_to_en(gold_en: str, pred_en: str) -> float:
    """Case-insensitive exact string match (normalized whitespace, lowercased)."""
    return 1.0 if _normalize(gold_en).lower() == _normalize(pred_en).lower() else 0.0


# ---------------------------------------------------------------------------
# Semantic similarity
# ---------------------------------------------------------------------------

_semantic_model = None


def _get_semantic_model():
    """Reuse the already-loaded jina-v5 model from retrieval, or load fresh."""
    global _semantic_model
    if _semantic_model is None:
        # Try to reuse the model already loaded by ChromaDB retrieval
        from mirad_translator.retrieval import _get_embedder
        try:
            _semantic_model = _get_embedder()
        except Exception:
            from sentence_transformers import SentenceTransformer
            _semantic_model = SentenceTransformer(
                "jinaai/jina-embeddings-v5-text-small",
                trust_remote_code=True,
                model_kwargs={"default_task": "retrieval"},
            )
    return _semantic_model


def semantic_similarity(gold_en: str, pred_en: str) -> float:
    """Cosine similarity between gold and predicted English text using jina-v5."""
    import numpy as np
    model = _get_semantic_model()
    embeddings = model.encode([_normalize(gold_en), _normalize(pred_en)], normalize_embeddings=True)
    a, b = embeddings[0], embeddings[1]
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_eval_dataset(csv_path=None, seed=42, n_samples=50):
    """Load Mir→En eval examples from the sentence pairs CSV."""
    if csv_path is None:
        csv_path = str(PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv")

    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("English", row.get("english", "")).strip()
            mi = row.get("Mirad", row.get("mirad", "")).strip()
            if en and mi:
                examples.append(dspy.Example(english_text=en, mirad_text=mi).with_inputs("mirad_text"))

    rng = random.Random(seed)
    rng.shuffle(examples)
    return examples[:n_samples]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("MIR→EN EVAL: DeepSeek-V4-Flash + jina-embeddings-v5-text-small")
    print("Pre-compiled mir2en bootstrap_fast program with new embedding model")
    print("50-sample evaluation (normalized match, exact match, semantic similarity)")
    print("=" * 70)

    N_SAMPLES = 50
    SEED = 42
    MODEL = "deepseek-ai/DeepSeek-V4-Flash"

    # Load compiled Mir→En program
    print(f"\n[1/5] Loading compiled Mir→En program from {COMPILED_MIR2EN_DIR}/")
    import cloudpickle
    compiled_path = Path(COMPILED_MIR2EN_DIR) / "program.pkl"
    with open(compiled_path, "rb") as f:
        compiled = cloudpickle.load(f)
    print("[1/5] Compiled Mir→En program loaded")

    # The Mir→En module uses MiradLexiconReverseLookup (SQLite FTS5, not semantic embeddings)
    # so we don't swap the lexicon. The jina-v5 benefit comes only from RAG retrieval (grammar/thesaurus)
    # and, separately, from semantic similarity scoring.
    print("[2/5] Mir→En uses MiradLexiconReverseLookup (SQLite FTS5) — no semantic lexicon swap needed")
    print("[2/5] jina-v5 benefit for Mir→En: RAG retrieval context + semantic similarity scoring")

    # Ensure ChromaDB indexes are built with jina-v5
    print("[3/5] Ensuring ChromaDB indexes use jina-v5...")
    from mirad_translator.semantic_lexicon import _get_lexicon_collection
    collection = _get_lexicon_collection()
    print(f"[3/5] Lexicon collection has {collection.count()} entries")

    from mirad_translator.retrieval import build_indexes, get_chunk_counts
    counts = get_chunk_counts()
    if counts["grammar"] == 0 or counts["thesaurus"] == 0:
        print("[3/5] Rebuilding grammar + thesaurus indexes...")
        counts = build_indexes()
        print(f"[3/5] Indexed: {counts}")
    else:
        print(f"[3/5] Grammar: {counts['grammar']}, Thesaurus: {counts['thesaurus']} (already built)")

    # Load eval data
    print(f"[4/5] Loading evaluation dataset (n={N_SAMPLES}, seed={SEED})...")
    eval_examples = load_eval_dataset(seed=SEED, n_samples=N_SAMPLES)
    print(f"[4/5] {len(eval_examples)} examples loaded")

    # Configure LM
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    lm = dspy.LM(
        model=f"openai/{MODEL}",
        api_key=api_key,
        api_base=api_base,
        num_retries=5,
        cache=True,
    )
    dspy.settings.configure(lm=lm)

    # Run evaluation
    print(f"[5/5] Running evaluation ({len(eval_examples)} samples with {MODEL})...")
    per_example = []
    start_time = time.time()
    for i, ex in enumerate(eval_examples):
        pred = compiled(mirad_text=ex.mirad_text)
        gold_en = ex.english_text
        pred_en = getattr(pred, "english_text", "")

        norm = normalized_match_mir_to_en(gold_en, pred_en)
        exact = exact_match_mir_to_en(gold_en, pred_en)
        sem_sim = semantic_similarity(gold_en, pred_en)

        per_example.append({
            "mirad_text": ex.mirad_text,
            "gold_english": gold_en,
            "predicted_english": pred_en,
            "normalized_match": norm,
            "exact_match": exact,
            "semantic_similarity": round(sem_sim, 6),
        })

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            norm_rate = sum(r["normalized_match"] for r in per_example) / len(per_example) * 100
            avg_sem = sum(r["semantic_similarity"] for r in per_example) / len(per_example)
            print(f"  [{i+1}/{len(eval_examples)}] {elapsed:.1f}s elapsed, norm={norm_rate:.1f}%, sem={avg_sem:.4f}")

    eval_time = time.time() - start_time

    # Compute scores
    total = len(per_example)
    norm_score = sum(r["normalized_match"] for r in per_example) / total * 100
    exact_score = sum(r["exact_match"] for r in per_example) / total * 100
    avg_sem = sum(r["semantic_similarity"] for r in per_example) / total

    print(f"\n  Results:")
    print(f"    Normalized match:    {norm_score:.1f}% ({int(sum(r['normalized_match'] for r in per_example))}/{total})")
    print(f"    Exact match:          {exact_score:.1f}% ({int(sum(r['exact_match'] for r in per_example))}/{total})")
    print(f"    Avg semantic sim:     {avg_sem:.4f}")
    print(f"    Eval time:            {eval_time:.1f}s ({eval_time/60:.1f} min)")

    # Save results
    output = {
        "model": MODEL,
        "direction": "mir_to_en",
        "label": "deepseek-ai/DeepSeek-V4-Flash + jina-v5-text-small (Mir→En)",
        "embedding_model": "jinaai/jina-embeddings-v5-text-small",
        "embedding_dim": 1024,
        "per_example": per_example,
        "eval_time_s": round(eval_time, 2),
        "normalized_score": norm_score,
        "exact_score": exact_score,
        "semantic_similarity_avg": avg_sem,
        "normalized_hits": int(sum(r["normalized_match"] for r in per_example)),
        "exact_hits": int(sum(r["exact_match"] for r in per_example)),
        "total": total,
        "seed": SEED,
        "semantic_lexicon": True,
        "top_k_per_word": 3,
        "max_total_pairs": 30,
        "min_similarity": 0.5,
        "compiled_program": "compiled_mir2en_program",
        "postprocessor": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    out_path = RESULTS_DIR / "mir2en_eval_deepseek-v4-flash_jina-v5-text-small.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Results saved to {out_path}")

    # ── Comparison with baseline (if available) ──────────────────────────
    baseline_path = RESULTS_DIR / "mir2en_compiled_vs_uncompiled.json"
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline = json.load(f)

        # Baseline has compiled_sem per example
        b_pe = baseline.get("per_example", [])
        if b_pe:
            b_norm = sum(1 for x in b_pe if x.get("compiled_norm")) / len(b_pe) * 100
            b_exact = sum(1 for x in b_pe if x.get("compiled_exact")) / len(b_pe) * 100
            b_sem = sum(x.get("compiled_sem", 0) for x in b_pe) / len(b_pe)

            print(f"\n{'=' * 75}")
            print("COMPARISON: jina-v5-text-small vs all-MiniLM-L6-v2 (Mir→En)")
            print(f"{'=' * 75}")
            print(f"  {'Config':<40} {'Norm%':>7} {'Exact%':>7} {'SemSim':>8} {'N':>4}")
            print(f"  {'-'*40} {'-'*7} {'-'*7} {'-'*8} {'-'*4}")
            print(f"  {'baseline (MiniLM, compiled)':<40} {b_norm:>6.1f}% {b_exact:>6.1f}% {b_sem:>7.4f} {len(b_pe):>4}")
            print(f"  {'jina-v5-text-small':<40} {norm_score:>6.1f}% {exact_score:>6.1f}% {avg_sem:>7.4f} {total:>4}")
            print(f"  {'-'*40} {'-'*7} {'-'*7} {'-'*8} {'-'*4}")
            print(f"  {'Delta':<40} {norm_score - b_norm:>+6.1f}% {exact_score - b_exact:>+6.1f}% {avg_sem - b_sem:>+7.4f}")
            print(f"\n  Note: baseline has {len(b_pe)} samples, jina-v5 has {total} samples")
            print(f"  (Direct comparison requires matched sample sets)")

    return output


if __name__ == "__main__":
    main()