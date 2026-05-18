#!/usr/bin/env python3
"""
Round-trip evaluation: English → Mirad → English

Uses compiled DSPy programs for both directions (jina-v5 embeddings).
Measures at each step:
  Step 1 (En→Mir): Normalized match (case-insensitive, punct-tolerant) vs gold Mirad
  Step 2 (Mir→En): Normalized match (case-insensitive, punct-tolerant) of back-translation vs original English
  Step 2 (Mir→En): Semantic similarity (jina-v5) of back-translation vs original English

Core question: If the round-trip English has high semantic similarity to the original,
does that mean the intermediate Mirad was likely correct?

Usage:
    python run_roundtrip_eval.py
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

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import dspy
import numpy as np

RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COMPILED_EN2MIR_DIR = str(RESULTS_DIR / "compiled_bootstrap_fast_program")
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


def _strip_punct_lower(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def normalized_match_en_to_mir(gold_mir: str, pred_mir: str) -> bool:
    """Case-insensitive, punct-tolerant match for En→Mir step."""
    return _strip_punct_lower(gold_mir) == _strip_punct_lower(pred_mir)


def normalized_match_mir_to_en(gold_en: str, pred_en: str) -> bool:
    """Case-insensitive, punct-tolerant match for Mir→En back-translation."""
    return _strip_punct_lower(gold_en) == _strip_punct_lower(pred_en)


def exact_match(gold: str, pred: str) -> bool:
    """Case-insensitive exact match after normalize."""
    return _normalize(gold).lower() == _normalize(pred).lower()


# ---------------------------------------------------------------------------
# Semantic similarity
# ---------------------------------------------------------------------------

_semantic_model = None


def _get_semantic_model():
    global _semantic_model
    if _semantic_model is None:
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


def semantic_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity between two English texts using jina-v5."""
    model = _get_semantic_model()
    emb = model.encode([_normalize(text_a), _normalize(text_b)], normalize_embeddings=True)
    a, b = emb[0], emb[1]
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_eval_dataset(csv_path=None, seed=42, n_samples=50, train_size=50, exclude_demos=True):
    if csv_path is None:
        csv_path = str(PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv")

    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("English", row.get("english", "")).strip()
            mi = row.get("Mirad", row.get("mirad", "")).strip()
            if en and mi:
                examples.append(dspy.Example(english_text=en, mirad_text=mi).with_inputs("english_text"))

    rng = random.Random(seed)
    rng.shuffle(examples)

    if exclude_demos:
        import cloudpickle
        compiled_path = Path(COMPILED_EN2MIR_DIR) / "program.pkl"
        with open(compiled_path, "rb") as f:
            compiled = cloudpickle.load(f)
        demo_texts = set()
        for name, pred in compiled.named_predictors():
            for demo in pred.demos:
                if "english_text" in demo:
                    demo_texts.add(demo["english_text"].strip())
        examples = [ex for ex in examples if ex.english_text not in demo_texts]
        print(f"  Excluded {len(demo_texts)} demo texts, {len(examples)} remaining")

    return examples[:n_samples]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("ROUND-TRIP EVAL: En→Mir→En with jina-embeddings-v5-text-small")
    print("Combined compiled programs (En→Mir + Mir→En)")
    print("50 samples, DeepSeek-V4-Flash")
    print("=" * 70)

    N_SAMPLES = 50
    SEED = 42
    MODEL = "deepseek-ai/DeepSeek-V4-Flash"

    # ── Load En→Mir compiled program ─────────────────────────────────────
    print(f"\n[1/6] Loading En→Mir compiled program...")
    import cloudpickle
    with open(Path(COMPILED_EN2MIR_DIR) / "program.pkl", "rb") as f:
        en2mir = cloudpickle.load(f)

    # Swap in jina-v5 semantic lexicon for En→Mir
    from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup
    en2mir.lexicon_lookup = MiradSemanticLexiconLookup(
        db_path=None, top_k_per_word=3, max_total_pairs=30, min_similarity=0.5,
    )
    print("[1/6] En→Mir program ready (jina-v5 semantic lexicon)")

    # ── Load Mir→En compiled program ──────────────────────────────────────
    print("[2/6] Loading Mir→En compiled program...")
    with open(Path(COMPILED_MIR2EN_DIR) / "program.pkl", "rb") as f:
        mir2en = cloudpickle.load(f)
    # Mir→En uses MiradLexiconReverseLookup (SQLite FTS5, no swap needed)
    print("[2/6] Mir→En program ready")

    # ── Ensure ChromaDB indexes ──────────────────────────────────────────
    print("[3/6] Ensuring ChromaDB indexes (jina-v5)...")
    from mirad_translator.semantic_lexicon import _get_lexicon_collection
    coll = _get_lexicon_collection()
    print(f"[3/6] Lexicon: {coll.count()} entries")
    from mirad_translator.retrieval import get_chunk_counts
    counts = get_chunk_counts()
    if counts["grammar"] == 0 or counts["thesaurus"] == 0:
        from mirad_translator.retrieval import build_indexes
        build_indexes()
        counts = get_chunk_counts()
    print(f"[3/6] Grammar: {counts['grammar']}, Thesaurus: {counts['thesaurus']}")

    # ── Load eval data ───────────────────────────────────────────────────
    print(f"[4/6] Loading evaluation dataset (n={N_SAMPLES}, seed={SEED})...")
    eval_examples = load_eval_dataset(seed=SEED, n_samples=N_SAMPLES, exclude_demos=True)
    print(f"[4/6] {len(eval_examples)} examples loaded")

    # ── Configure LM ──────────────────────────────────────────────────────
    print(f"[5/6] Configuring LM ({MODEL})...")
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

    # ── Run round-trip evaluation ─────────────────────────────────────────
    print(f"[6/6] Running round-trip evaluation ({len(eval_examples)} samples)...")
    from mirad_translator.postprocess import postprocess_mirad

    per_example = []
    start_time = time.time()

    for i, ex in enumerate(eval_examples):
        original_en = ex.english_text
        gold_mir = ex.mirad_text

        # Step 1: En→Mir
        en2mir_pred = en2mir(english_text=original_en)
        pred_mir = postprocess_mirad(en2mir_pred.mirad_text)

        # Step 2: Mir→En (using predicted Mirad)
        mir2en_pred = mir2en(mirad_text=pred_mir)
        pred_en = getattr(mir2en_pred, "english_text", "")

        # Step 1 metrics: predicted Mirad vs gold Mirad
        step1_norm = normalized_match_en_to_mir(gold_mir, pred_mir)
        step1_exact = exact_match(gold_mir, pred_mir)

        # Step 2 metrics: round-trip English vs original English
        step2_norm = normalized_match_mir_to_en(original_en, pred_en)
        step2_exact = exact_match(original_en, pred_en)
        step2_sem = semantic_similarity(original_en, pred_en)

        per_example.append({
            "original_english": original_en,
            "gold_mirad": gold_mir,
            "predicted_mirad": pred_mir,
            "roundtrip_english": pred_en,
            "step1_normalized_match": step1_norm,
            "step1_exact_match": step1_exact,
            "step2_normalized_match": step2_norm,
            "step2_exact_match": step2_exact,
            "step2_semantic_similarity": round(step2_sem, 6),
        })

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            s1_norm = sum(r["step1_normalized_match"] for r in per_example) / len(per_example) * 100
            s2_norm = sum(r["step2_normalized_match"] for r in per_example) / len(per_example) * 100
            s2_sem = sum(r["step2_semantic_similarity"] for r in per_example) / len(per_example)
            print(f"  [{i+1}/{len(eval_examples)}] {elapsed:.1f}s  "
                  f"En→Mir norm={s1_norm:.1f}%  Mir→En norm={s2_norm:.1f}%  sem={s2_sem:.4f}")

    eval_time = time.time() - start_time

    # ── Compute aggregate scores ─────────────────────────────────────────
    total = len(per_example)
    s1_norm = sum(r["step1_normalized_match"] for r in per_example) / total * 100
    s1_exact = sum(r["step1_exact_match"] for r in per_example) / total * 100
    s2_norm = sum(r["step2_normalized_match"] for r in per_example) / total * 100
    s2_exact = sum(r["step2_exact_match"] for r in per_example) / total * 100
    s2_sem_avg = sum(r["step2_semantic_similarity"] for r in per_example) / total
    s2_sem_median = float(np.median([r["step2_semantic_similarity"] for r in per_example]))

    print(f"\n{'=' * 70}")
    print("ROUND-TRIP RESULTS: En→Mir→En")
    print(f"{'=' * 70}")
    print(f"  Step 1 (En→Mir vs gold Mirad):")
    print(f"    Normalized match:  {s1_norm:.1f}% ({int(sum(r['step1_normalized_match'] for r in per_example))}/{total})")
    print(f"    Exact match:       {s1_exact:.1f}% ({int(sum(r['step1_exact_match'] for r in per_example))}/{total})")
    print(f"  Step 2 (Mir→En vs original English):")
    print(f"    Normalized match:  {s2_norm:.1f}% ({int(sum(r['step2_normalized_match'] for r in per_example))}/{total})")
    print(f"    Exact match:       {s2_exact:.1f}% ({int(sum(r['step2_exact_match'] for r in per_example))}/{total})")
    print(f"    Avg semantic sim:  {s2_sem_avg:.4f}")
    print(f"    Median semantic:   {s2_sem_median:.4f}")
    print(f"  Eval time:           {eval_time:.1f}s ({eval_time/60:.1f} min)")

    # ── Correlation analysis ─────────────────────────────────────────────
    # Does high round-trip sem sim imply correct intermediate Mirad?
    s1_norm_arr = np.array([r["step1_normalized_match"] for r in per_example], dtype=float)
    s2_sem_arr = np.array([r["step2_semantic_similarity"] for r in per_example])
    s2_norm_arr = np.array([r["step2_normalized_match"] for r in per_example], dtype=float)

    # When step1 (En→Mir) is correct, what's the round-trip sem sim?
    correct_mirad_sem = s2_sem_arr[s1_norm_arr == 1]
    wrong_mirad_sem = s2_sem_arr[s1_norm_arr == 0]

    print(f"\n{'=' * 70}")
    print("CORRELATION: Does high round-trip sem sim imply correct Mirad?")
    print(f"{'=' * 70}")
    print(f"  When En→Mir is CORRECT ({len(correct_mirad_sem)} samples):")
    if len(correct_mirad_sem) > 0:
        print(f"    Avg round-trip sem sim:   {correct_mirad_sem.mean():.4f}")
        print(f"    Median round-trip sem sim: {float(np.median(correct_mirad_sem)):.4f}")
        print(f"    Min round-trip sem sim:    {correct_mirad_sem.min():.4f}")
    print(f"  When En→Mir is WRONG ({len(wrong_mirad_sem)} samples):")
    if len(wrong_mirad_sem) > 0:
        print(f"    Avg round-trip sem sim:   {wrong_mirad_sem.mean():.4f}")
        print(f"    Median round-trip sem sim: {float(np.median(wrong_mirad_sem)):.4f}")
        print(f"    Max round-trip sem sim:    {wrong_mirad_sem.max():.4f}")

    # Threshold analysis: if sem >= threshold, what fraction had correct Mirad?
    thresholds = [0.85, 0.90, 0.95, 0.97]
    print(f"\n  Threshold analysis (if round-trip sem >= threshold, P(correct Mirad)):")
    print(f"  {'Threshold':>10} {'P(correct|sem>=T)':>18} {'N(>=T)':>8} {'Coverage':>10}")
    for t in thresholds:
        above = s2_sem_arr >= t
        n_above = above.sum()
        if n_above > 0:
            p_correct = s1_norm_arr[above].mean() * 100
            coverage = n_above / total * 100
        else:
            p_correct = 0
            coverage = 0
        print(f"  {t:>10.2f} {p_correct:>17.1f}% {n_above:>8d} {coverage:>9.1f}%")

    # ── Common failures and successes ─────────────────────────────────────
    correct_mirad_wrong_en = [r for r in per_example if r["step1_normalized_match"] and not r["step2_normalized_match"]]
    wrong_mirad_right_en = [r for r in per_example if not r["step1_normalized_match"] and r["step2_normalized_match"]]
    both_correct = [r for r in per_example if r["step1_normalized_match"] and r["step2_normalized_match"]]
    both_wrong = [r for r in per_example if not r["step1_normalized_match"] and not r["step2_normalized_match"]]

    print(f"\n{'=' * 70}")
    print(f"CROSS-TABULATION")
    print(f"{'=' * 70}")
    print(f"  Both correct (good Mirad + good round-trip):     {len(both_correct)}/{total} ({len(both_correct)/total*100:.1f}%)")
    print(f"  Good Mirad, wrong round-trip:                     {len(correct_mirad_wrong_en)}/{total}")
    print(f"  Wrong Mirad, but good round-trip:                  {len(wrong_mirad_right_en)}/{total}")
    print(f"  Both wrong:                                       {len(both_wrong)}/{total}")

    # Show "wrong Mirad, high round-trip sem" — the misleading cases
    high_sem_wrong_mirad = [r for r in per_example if not r["step1_normalized_match"] and r["step2_semantic_similarity"] >= 0.9]
    print(f"\n  Wrong Mirad + high round-trip sem (>=0.9): {len(high_sem_wrong_mirad)}/{len(wrong_mirad_sem) if len(wrong_mirad_sem) > 0 else 0}")
    if high_sem_wrong_mirad:
        print(f"    === Misleading cases (wrong Mirad but sem >= 0.9) ===")
        for r in high_sem_wrong_mirad[:8]:
            print(f"      EN:  \"{r['original_english'][:60]}\"")
            print(f"      GOL: \"{r['gold_mirad'][:60]}\"")
            print(f"      PRED: \"{r['predicted_mirad'][:60]}\"")
            print(f"      RT:  \"{r['roundtrip_english'][:60]}\"")
            print(f"      sem: {r['step2_semantic_similarity']:.4f}")
            print()

    # Show "right Mirad, low round-trip sem" — another failure mode
    low_sem_right_mirad = [r for r in per_example if r["step1_normalized_match"] and r["step2_semantic_similarity"] < 0.85]
    print(f"  Right Mirad + low round-trip sem (<0.85): {len(low_sem_right_mirad)}/{len(correct_mirad_sem) if len(correct_mirad_sem) > 0 else 0}")

    # ── Save results ──────────────────────────────────────────────────────
    output = {
        "model": MODEL,
        "direction": "roundtrip_en_mir_en",
        "label": "DeepSeek-V4-Flash roundtrip (En→Mir→En) with jina-v5",
        "embedding_model": "jinaai/jina-embeddings-v5-text-small",
        "embedding_dim": 1024,
        "per_example": per_example,
        "eval_time_s": round(eval_time, 2),
        "step1_normalized_score": s1_norm,
        "step1_exact_score": s1_exact,
        "step2_normalized_score": s2_norm,
        "step2_exact_score": s2_exact,
        "step2_semantic_similarity_avg": s2_sem_avg,
        "step2_semantic_similarity_median": s2_sem_median,
        "step1_normalized_hits": int(sum(r["step1_normalized_match"] for r in per_example)),
        "step1_exact_hits": int(sum(r["step1_exact_match"] for r in per_example)),
        "step2_normalized_hits": int(sum(r["step2_normalized_match"] for r in per_example)),
        "step2_exact_hits": int(sum(r["step2_exact_match"] for r in per_example)),
        "total": total,
        "seed": SEED,
        "en2mir_compiled": "compiled_bootstrap_fast_program",
        "mir2en_compiled": "compiled_mir2en_program",
        "semantic_lexicon": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    out_path = RESULTS_DIR / "roundtrip_en_mir_en_jina-v5.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Results saved to {out_path}")

    return output


if __name__ == "__main__":
    main()