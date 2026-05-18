#!/usr/bin/env python3
"""
Evaluate the precompiled bootstrap_fast DSPy program with jina-embeddings-v5-text-small
for semantic lexicon lookup and RAG retrieval.

Compares against the prior all-MiniLM-L6-v2 baseline (50-sample DeepSeek-V4-Flash eval).

Usage:
    python run_jina_v5_eval.py
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

COMPILED_DIR = str(RESULTS_DIR / "compiled_bootstrap_fast_program")

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


def normalized_match_en_to_mir(example, prediction, trace=None) -> float:
    gold = _normalize(getattr(example, "mirad_text", ""))
    pred = _normalize(getattr(prediction, "mirad_text", ""))
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_eval_dataset(csv_path=None, seed=42, n_samples=50, train_size=50, exclude_demos=True):
    """Load eval examples, optionally excluding demo texts from a compiled program."""
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
        compiled_path = Path(COMPILED_DIR) / "program.pkl"
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
    print("JINA-V5 EMBEDDING EVAL: DeepSeek-V4-Flash + jina-embeddings-v5-text-small")
    print("Pre-compiled bootstrap_fast program with new embedding model")
    print("50-sample evaluation")
    print("=" * 70)

    N_SAMPLES = 50
    SEED = 42
    MODEL = "deepseek-ai/DeepSeek-V4-Flash"

    # Load compiled program
    print(f"\n[1/4] Loading compiled program from {COMPILED_DIR}/")
    import cloudpickle
    with open(Path(COMPILED_DIR) / "program.pkl", "rb") as f:
        compiled = cloudpickle.load(f)
    print("[1/4] Compiled program loaded")

    # Swap in semantic lexicon with new embeddings
    print("[2/4] Swapping in MiradSemanticLexiconLookup (will use jina-v5 embeddings)...")
    from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup
    compiled.lexicon_lookup = MiradSemanticLexiconLookup(
        db_path=None, top_k_per_word=3, max_total_pairs=30, min_similarity=0.5,
    )
    print("[2/4] Semantic lexicon attached")

    # Force ChromaDB rebuild with new embeddings
    print("[2/4] Forcing ChromaDB index rebuild with jina-embeddings-v5-text-small...")
    from mirad_translator.semantic_lexicon import _get_lexicon_collection
    collection = _get_lexicon_collection()
    print(f"[2/4] Lexicon collection has {collection.count()} entries")

    # Also rebuild grammar + thesaurus for RAG retrieval
    print("[2/4] Rebuilding grammar + thesaurus ChromaDB indexes...")
    from mirad_translator.retrieval import build_indexes, get_chunk_counts
    counts = build_indexes()
    print(f"[2/4] Indexed: {counts}")
    # Verify newly built counts
    new_counts = get_chunk_counts()
    print(f"[2/4] Verified: grammar={new_counts['grammar']} thesaurus={new_counts['thesaurus']}")

    # Load eval data (same seed as baseline, matching their exclusion logic)
    print(f"[3/4] Loading evaluation dataset (n={N_SAMPLES}, seed={SEED})...")
    eval_examples = load_eval_dataset(seed=SEED, n_samples=N_SAMPLES, exclude_demos=True)
    print(f"[3/4] {len(eval_examples)} examples loaded")

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
    print(f"[4/4] Running evaluation ({len(eval_examples)} samples with {MODEL})...")
    from mirad_translator.postprocess import postprocess_mirad

    per_example = []
    start_time = time.time()
    for i, ex in enumerate(eval_examples):
        pred = compiled(english_text=ex.english_text)
        mirad_text = postprocess_mirad(pred.mirad_text)
        gold = ex.mirad_text

        norm = normalized_match_en_to_mir(ex, pred)
        exact = 1.0 if _normalize(gold) == _normalize(mirad_text) else 0.0

        per_example.append({
            "english_text": ex.english_text,
            "gold_mirad": gold,
            "predicted_mirad": mirad_text,
            "normalized_match": norm,
            "exact_match": exact,
        })

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = sum(r["normalized_match"] for r in per_example) / len(per_example) * 100
            print(f"  [{i+1}/{len(eval_examples)}] {elapsed:.1f}s elapsed, norm={rate:.1f}%")

    eval_time = time.time() - start_time

    # Compute scores
    total = len(per_example)
    norm_score = sum(r["normalized_match"] for r in per_example) / total * 100
    exact_score = sum(r["exact_match"] for r in per_example) / total * 100

    print(f"\n  Results:")
    print(f"    Normalized match: {norm_score:.1f}% ({sum(r['normalized_match'] for r in per_example)}/{total})")
    print(f"    Exact match:       {exact_score:.1f}% ({sum(r['exact_match'] for r in per_example)}/{total})")
    print(f"    Eval time:         {eval_time:.1f}s ({eval_time/60:.1f} min)")

    # Save results
    output = {
        "model": MODEL,
        "label": "deepseek-ai/DeepSeek-V4-Flash + jina-v5-text-small",
        "embedding_model": "jinaai/jina-embeddings-v5-text-small",
        "embedding_dim": 1024,
        "per_example": per_example,
        "eval_time_s": round(eval_time, 2),
        "normalized_score": norm_score,
        "exact_score": exact_score,
        "normalized_hits": int(sum(r["normalized_match"] for r in per_example)),
        "exact_hits": int(sum(r["exact_match"] for r in per_example)),
        "total": total,
        "seed": SEED,
        "semantic_lexicon": True,
        "top_k_per_word": 3,
        "max_total_pairs": 30,
        "min_similarity": 0.5,
        "compiled_program": "compiled_bootstrap_fast_program",
        "postprocessor": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    out_path = RESULTS_DIR / "50s_eval_deepseek-v4-flash_jina-v5-text-small.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Results saved to {out_path}")

    # ── Comparison with baseline ──────────────────────────────────────────
    baseline_path = RESULTS_DIR / "50s_eval_deepseek-ai_DeepSeek-V4-Flash.json"
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline = json.load(f)

        print(f"\n{'=' * 75}")
        print("COMPARISON: jina-v5-text-small vs all-MiniLM-L6-v2")
        print(f"{'=' * 75}")
        print(f"  {'Config':<40} {'Norm%':>7} {'Exact%':>7} {'Hits':>7} {'Time':>8}")
        print(f"  {'-'*40} {'-'*7} {'-'*7} {'-'*7} {'-'*8}")
        print(f"  {'baseline (all-MiniLM-L6-v2)':<40} {baseline['normalized_score']:>6.1f}% "
              f"{baseline['exact_score']:>6.1f}% {baseline['normalized_hits']:>5}/{baseline['total']} "
              f"{baseline['eval_time_s']:>7.1f}s")
        print(f"  {'jina-v5-text-small':<40} {norm_score:>6.1f}% "
              f"{exact_score:>6.1f}% {int(sum(r['normalized_match'] for r in per_example)):>5}/{total} "
              f"{eval_time:>7.1f}s")
        print(f"  {'-'*40} {'-'*7} {'-'*7} {'-'*7} {'-'*8}")
        print(f"  {'Delta':<40} {norm_score - baseline['normalized_score']:>+6.1f}% "
              f"{exact_score - baseline['exact_score']:>+6.1f}%")

        # Pairwise comparison
        if len(baseline.get("per_example", [])) == len(per_example):
            both_right = ex_wins = jina_wins = both_wrong = 0
            sub_ex = sub_jina = 0
            for b, j in zip(baseline["per_example"], per_example):
                b_nm = b["normalized_match"]
                j_nm = j["normalized_match"]
                if b_nm and j_nm:
                    both_right += 1
                elif b_nm and not j_nm:
                    ex_wins += 1
                    if _strip_punct(b["predicted_mirad"]) != _strip_punct(b["gold_mirad"]):
                        sub_ex += 1  # baseline won on punctuation only
                elif j_nm and not b_nm:
                    jina_wins += 1
                    if _strip_punct(j["predicted_mirad"]) != _strip_punct(j["gold_mirad"]):
                        sub_jina += 1  # jina won on punctuation only
                else:
                    both_wrong += 1

            print(f"\n  Pairwise comparison (same {len(per_example)} examples):")
            print(f"    Both correct:              {both_right}")
            print(f"    Baseline (MiniLM) wins:   {ex_wins} (substantive: {ex_wins - sub_ex}, punct-only: {sub_ex})")
            print(f"    Jina-v5 wins:             {jina_wins} (substantive: {jina_wins - sub_jina}, punct-only: {sub_jina})")
            print(f"    Both wrong:               {both_wrong}")
            print(f"    Net substantive Δ:        {(jina_wins - sub_jina) - (ex_wins - sub_ex):+d}")

            # Show jina wins
            if jina_wins > 0:
                print(f"\n  === JINA-V5 WINS ({jina_wins}) ===")
                for b, j in zip(baseline["per_example"], per_example):
                    if j["normalized_match"] and not b["normalized_match"]:
                        print(f"    EN:   {b['english_text'][:80]}")
                        print(f"    GOLD: {b['gold_mirad'][:80]}")
                        print(f"    BL:   {b['predicted_mirad'][:80]}")
                        print(f"    JN:   {j['predicted_mirad'][:80]}")
                        print()

            # Show baseline wins
            if ex_wins > 0:
                print(f"\n  === BASELINE WINS ({ex_wins}) ===")
                for b, j in zip(baseline["per_example"], per_example):
                    if b["normalized_match"] and not j["normalized_match"]:
                        print(f"    EN:   {b['english_text'][:80]}")
                        print(f"    GOLD: {b['gold_mirad'][:80]}")
                        print(f"    BL:   {b['predicted_mirad'][:80]}")
                        print(f"    JN:   {j['predicted_mirad'][:80]}")
                        print()
    else:
        print(f"\n  Baseline file not found: {baseline_path}")
        print("  Skipping comparison.")

    return output


if __name__ == "__main__":
    main()