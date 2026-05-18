#!/usr/bin/env python3
"""
Commonness-weighted round-trip evaluation at scale.

Step 1: Add 'commonness' column to english_sentences.csv
  - Average wordfreq zipf_frequency per sentence, excluding stop words
  - Reorder descending by commonness

Step 2: Sample 1000 sentences using log-prob weighting (favor less common)
  - weight[i] = 1 / log(i + 2), sampled without replacement

Step 3: Translate sampled sentences En→Mir→En, measure round-trip sem sim
  - Save incrementally (row-by-row) so progress survives interruption
  - Resume by translating only rows with missing mirad/sem_sim

Usage:
    python commonness_roundtrip_eval.py [--skip-annotation] [--max-samples 1000]
"""

import csv
import json
import os
import re
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from wordfreq import zipf_frequency
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SENTENCES_CSV = PROJECT_ROOT / "data" / "phrases" / "english_sentences.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "phrases"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = RESULTS_DIR / "commonness_roundtrip_results.csv"

COMPILED_EN2MIR_DIR = str(
    PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_bootstrap_fast_program"
)
COMPILED_MIR2EN_DIR = str(
    PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_mir2en_program"
)

MODEL = "deepseek-ai/DeepSeek-V4-Flash"

# Wordfreq returns 0.0 for OOV words — treat as very rare
MIN_ZIPF = 0.5

STOP_WORDS = ENGLISH_STOP_WORDS


# ---------------------------------------------------------------------------
# Step 1: Annotate commonness
# ---------------------------------------------------------------------------


def sentence_commonness(sentence: str) -> float:
    """Average zipf_frequency of content words in a sentence (excluding stop words)."""
    words = re.findall(r"[a-zA-Z]+", sentence.lower())
    content_words = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    if not content_words:
        # Fall back to all words if no content words remain
        content_words = [w for w in words if len(w) > 1]
    if not content_words:
        return 0.0
    freqs = [max(zipf_frequency(w, "en"), MIN_ZIPF) for w in content_words]
    return sum(freqs) / len(freqs)


def annotate_and_sort_csv(csv_path: Path) -> Path:
    """Add commonness column and sort descending. Returns path to new file."""
    print(f"[ANNOTATE] Reading {csv_path}...")
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            idx, sentence = row[0].strip(), ",".join(row[1:]).strip()
            if not sentence:
                continue
            rows.append((idx, sentence))

    print(f"[ANNOTATE] Computing commonness for {len(rows):,} sentences...")
    annotated = []
    batch_size = 50_000
    for i, (idx, sentence) in enumerate(rows):
        commonness = sentence_commonness(sentence)
        annotated.append((idx, sentence, commonness))
        if (i + 1) % batch_size == 0:
            print(f"  [{i+1:,}/{len(rows):,}] computed")

    print(f"[ANNOTATE] Sorting by commonness (descending)...")
    annotated.sort(key=lambda x: x[2], reverse=True)

    # Write back with commonness column
    out_path = csv_path  # overwrite in-place
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "english", "commonness"])
        for idx, sentence, commonness in annotated:
            writer.writerow([idx, sentence, f"{commonness:.4f}"])

    # Stats
    commonnesses = [c for _, _, c in annotated]
    print(f"[ANNOTATE] Written {len(annotated):,} rows to {out_path}")
    print(f"  Commonness range: {min(commonnesses):.2f} – {max(commonnesses):.2f}")
    print(f"  Commonness mean:  {np.mean(commonnesses):.2f}")
    print(f"  Commonness median: {np.median(commonnesses):.2f}")
    return out_path


# ---------------------------------------------------------------------------
# Step 2: Log-prob sampling
# ---------------------------------------------------------------------------


def logprob_sample(rows: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Sample n rows using 1/log(i+2) weights (favoring less-common, i.e. later rows)."""
    rng = np.random.default_rng(seed)
    n_total = len(rows)
    n = min(n, n_total)

    # rows are sorted descending by commonness, so later rows are less common
    indices = np.arange(n_total)
    weights = 1.0 / np.log(indices + 2)
    probs = weights / weights.sum()

    chosen_indices = rng.choice(indices, size=n, replace=False, p=probs)
    # Sort by chosen index to preserve original order
    chosen_indices.sort()

    return [rows[i] for i in chosen_indices]


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


def _strip_punct_lower(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Commonness-weighted round-trip eval")
    parser.add_argument("--skip-annotation", action="store_true", help="Skip step 1 (annotation)")
    parser.add_argument("--max-samples", type=int, default=1000, help="Number of sentences to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = parser.parse_args()

    N_SAMPLES = args.max_samples
    SEED = args.seed

    print("=" * 70)
    print(f"COMMONNESS-WEIGHTED ROUND-TRIP EVAL (n={N_SAMPLES})")
    print("=" * 70)

    # ── Step 1: Annotate commonness ────────────────────────────────────────
    if not args.skip_annotation:
        print("\n[STEP 1] Annotating commonness...")
        annotated_path = annotate_and_sort_csv(SENTENCES_CSV)
    else:
        print("\n[STEP 1] Skipping annotation (using existing file)")
        annotated_path = SENTENCES_CSV

    # ── Step 2: Load annotated data and sample ──────────────────────────────
    print("\n[STEP 2] Loading annotated data...")
    rows = []
    with open(annotated_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"  Loaded {len(rows):,} rows, sampling {N_SAMPLES} with log-prob weighting...")
    sampled = logprob_sample(rows, N_SAMPLES, seed=SEED)
    print(f"  Sampled {len(sampled)} sentences")
    print(f"  Commonness range in sample: {min(float(r['commonness']) for r in sampled):.2f} – {max(float(r['commonness']) for r in sampled):.2f}")

    # ── Step 3: Initialize translations (resume-safe) ──────────────────────
    print(f"\n[STEP 3] Setting up incremental output: {OUTPUT_CSV}")

    # Load or create output file
    existing_results = {}
    if OUTPUT_CSV.exists():
        with open(OUTPUT_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['id']}|{row['english']}"
                existing_results[key] = row
        print(f"  Found {len(existing_results)} existing results to resume from")

    # ── Step 4: Load compiled programs ───────────────────────────────────────
    print("\n[STEP 4] Loading compiled DSPy programs...")
    import cloudpickle
    import dspy

    with open(Path(COMPILED_EN2MIR_DIR) / "program.pkl", "rb") as f:
        en2mir = cloudpickle.load(f)

    from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup

    en2mir.lexicon_lookup = MiradSemanticLexiconLookup(
        db_path=None, top_k_per_word=3, max_total_pairs=30, min_similarity=0.5,
    )
    print("  En→Mir program ready (jina-v5 semantic lexicon)")

    with open(Path(COMPILED_MIR2EN_DIR) / "program.pkl", "rb") as f:
        mir2en = cloudpickle.load(f)
    print("  Mir→En program ready")

    # ── Step 5: Ensure ChromaDB indexes ──────────────────────────────────────
    print("\n[STEP 5] Ensuring ChromaDB indexes (jina-v5)...")
    from mirad_translator.semantic_lexicon import _get_lexicon_collection

    coll = _get_lexicon_collection()
    print(f"  Lexicon: {coll.count()} entries")

    from mirad_translator.retrieval import get_chunk_counts

    counts = get_chunk_counts()
    if counts["grammar"] == 0 or counts["thesaurus"] == 0:
        from mirad_translator.retrieval import build_indexes

        build_indexes()
        counts = get_chunk_counts()
    print(f"  Grammar: {counts['grammar']}, Thesaurus: {counts['thesaurus']}")

    # ── Step 6: Configure LM ────────────────────────────────────────────────
    print(f"\n[STEP 6] Configuring LM ({MODEL})...")
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

    # ── Step 7: Semantic similarity model ────────────────────────────────────
    print("\n[STEP 7] Loading semantic similarity model (jina-v5)...")
    from mirad_translator.retrieval import _get_embedder
    import numpy as np

    sem_model = _get_embedder()

    def semantic_similarity(text_a: str, text_b: str) -> float:
        emb = sem_model.encode([_normalize(text_a), _normalize(text_b)], normalize_embeddings=True)
        a, b = emb[0], emb[1]
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    # ── Step 8: Run translations (incremental, resume-safe) ─────────────────
    print(f"\n[STEP 8] Running translations for {len(sampled)} sentences...")
    print(f"  Saving results incrementally to {OUTPUT_CSV}")

    # Prepare field names
    fieldnames = ["id", "english", "commonness", "mirad", "roundtrip_english", "semantic_similarity"]

    # Build results list from sampled + existing
    results = []
    needs_translation = []
    for s in sampled:
        key = f"{s['id']}|{s['english']}"
        if key in existing_results:
            row = existing_results[key]
            # Check if translation is complete
            if row.get("mirad", "").strip() and row.get("semantic_similarity", "").strip():
                results.append(row)
                continue
        # Needs translation
        needs_translation.append(s)
        results.append({
            "id": s["id"],
            "english": s["english"],
            "commonness": s.get("commonness", ""),
            "mirad": "",
            "roundtrip_english": "",
            "semantic_similarity": "",
        })

    print(f"  {len(results) - len(needs_translation)} already completed, {len(needs_translation)} need translation")

    from mirad_translator.postprocess import postprocess_mirad

    # Create index mapping for updating results
    id_to_idx = {}
    for i, r in enumerate(results):
        if not r.get("mirad", "").strip():
            id_to_idx[r["id"]] = i

    start_time = time.time()
    completed = len(results) - len(needs_translation)
    errors = 0

    for i, s in enumerate(needs_translation):
        original_en = s["english"]
        row_idx = id_to_idx[s["id"]]

        try:
            # Step 1: En→Mir
            en2mir_pred = en2mir(english_text=original_en)
            pred_mir = postprocess_mirad(en2mir_pred.mirad_text)

            # Step 2: Mir→En
            mir2en_pred = mir2en(mirad_text=pred_mir)
            pred_en = getattr(mir2en_pred, "english_text", "")

            # Semantic similarity
            if pred_en.strip() and original_en.strip():
                sem = semantic_similarity(original_en, pred_en)
            else:
                sem = 0.0

            results[row_idx] = {
                "id": s["id"],
                "english": original_en,
                "commonness": s.get("commonness", ""),
                "mirad": pred_mir,
                "roundtrip_english": pred_en,
                "semantic_similarity": f"{sem:.6f}",
            }

        except Exception as e:
            errors += 1
            print(f"  ERROR on row {s['id']}: {e}")
            results[row_idx] = {
                "id": s["id"],
                "english": original_en,
                "commonness": s.get("commonness", ""),
                "mirad": f"ERROR: {e}",
                "roundtrip_english": "",
                "semantic_similarity": "",
            }

        completed += 1

        # Save incrementally every 10 translations
        if completed % 10 == 0 or completed == len(results):
            elapsed = time.time() - start_time
            done_rows = [r for r in results if r.get("mirad", "").strip() and not r.get("mirad", "").startswith("ERROR")]
            if done_rows:
                avg_sem = sum(float(r["semantic_similarity"]) for r in done_rows if r.get("semantic_similarity")) / len(done_rows)
                avg_time = elapsed / max((completed - (len(results) - len(needs_translation))), 1)
            else:
                avg_sem = 0.0
                avg_time = 0

            print(f"  [{completed}/{len(results)}] {elapsed:.0f}s  "
                  f"avg_sem={avg_sem:.4f}  errors={errors}")

            # Write all results so far
            with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in results:
                    writer.writerow(r)

    # ── Final save ───────────────────────────────────────────────────────────
    print(f"\n[FINAL] Saving {len(results)} results to {OUTPUT_CSV}")
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # ── Summary statistics ───────────────────────────────────────────────────
    done_rows = [r for r in results if r.get("semantic_similarity", "").strip() and not r.get("mirad", "").startswith("ERROR")]
    if done_rows:
        sems = [float(r["semantic_similarity"]) for r in done_rows]
        commonnesses = [float(r["commonness"]) for r in done_rows]

        print(f"\n{'=' * 70}")
        print("RESULTS SUMMARY")
        print(f"{'=' * 70}")
        print(f"  Completed:  {len(done_rows)}/{len(results)}")
        print(f"  Errors:     {errors}")
        print(f"  Avg semantic similarity:  {np.mean(sems):.4f}")
        print(f"  Median semantic similarity: {np.median(sems):.4f}")
        print(f"  Min/Max:    {np.min(sems):.4f} / {np.max(sems):.4f}")
        print(f"  Commonness range: {min(commonnesses):.2f} – {max(commonnesses):.2f}")

        # Correlation: commonness vs semantic similarity
        corr = np.corrcoef(commonnesses, sems)[0, 1]
        print(f"  Correlation(commonness, sem_sim): {corr:.4f}")

        # Bin by commonness quartile
        quartiles = np.percentile(commonnesses, [25, 50, 75])
        print(f"\n  By commonness quartile:")
        labels = ["Q1 (rarest)", "Q2", "Q3", "Q4 (common)"]
        for qi, (lo, hi) in enumerate(
            [(0, quartiles[0]), (quartiles[0], quartiles[1]), (quartiles[1], quartiles[2]), (quartiles[2], 10)]
        ):
            mask = [(lo <= c <= hi) for c in commonnesses]
            quartile_sems = [s for s, m in zip(sems, mask) if m]
            if quartile_sems:
                print(f"    {labels[qi]:>15}: n={len(quartile_sems):4d}, avg_sem={np.mean(quartile_sems):.4f}")

    total_time = time.time() - start_time
    print(f"\n  Total translation time: {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"  Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()