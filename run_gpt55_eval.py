"""Evaluate GPT-5.5 on both En→Mir (40 samples) and Mir→En (20 samples) with compiled programs.

Uses compiled programs for both directions. Measures exact match, normalized match,
and semantic similarity (all-MiniLM-L6-v2). Saves results to data/eval_results/.
"""
import csv, json, os, random, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

import dspy
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent / "packages" / "translator" / "src"))

from mirad_translator.translate import DefaultTranslator
from mirad_translator.evaluate import _normalize
from mirad_translator.postprocess import postprocess_mirad

PROJECT_ROOT = Path(__file__).parent

# ── Metrics ──

def _strip_punct(s):
    s = re.sub(r'[.,!?;:()\"' + chr(39) + r'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()

def exact_match(gold, pred):
    return 1.0 if _normalize(gold) == _normalize(pred) else 0.0

def norm_match(gold, pred):
    g, p = _normalize(gold), _normalize(pred)
    if g == p:
        return 1.0
    return 1.0 if _strip_punct(g) == _strip_punct(p) else 0.0


def main():
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in .env")
        sys.exit(1)

    # Configure GPT-5.5 via DSPy (uses litellm openai/ prefix)
    lm = dspy.LM(
        model="openai/gpt-5.5",
        api_key=api_key,
        max_tokens=512,
    )
    dspy.settings.configure(lm=lm)

    # Load sentence transformer (CPU to avoid VRAM conflicts)
    st_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    def sem_sim(gold, pred):
        g, p = _normalize(gold), _normalize(pred)
        emb = st_model.encode([g, p], normalize_embeddings=True)
        return float(np.dot(emb[0], emb[1]))

    # Load evaluation data
    csv_path = PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en, mi = row["english"].strip(), row["mirad"].strip()
            if en and mi:
                examples.append({"english": en, "mirad": mi})
    rng = random.Random(42)
    rng.shuffle(examples)

    # ── En→Mir (40 samples) ──
    n_en_mir = 40
    en_mir_examples = examples[:n_en_mir]
    print(f"\n{'=' * 72}")
    print(f"  En→Mir: {n_en_mir} examples with GPT-5.5 (compiled)")
    print(f"{'=' * 72}")

    print("Loading En→Mir compiled translator...")
    en_mir_translator = DefaultTranslator(direction="en_to_mir", use_compiled=True)

    en_mir_results = []
    en_mir_exact = []
    en_mir_norm = []
    en_mir_sem = []
    en_mir_errors = 0
    t0 = time.time()
    for i, ex in enumerate(en_mir_examples):
        try:
            pred = en_mir_translator(english_text=ex["english"])
            pred_mirad = pred.mirad_text if pred.mirad_text else ""
            pred_mirad = postprocess_mirad(pred_mirad)
        except Exception as exc:
            print(f"  [{i+1}] ERROR: {type(exc).__name__}: {str(exc)[:80]}")
            pred_mirad = ""
            en_mir_errors += 1
        gold = ex["mirad"]
        e = exact_match(gold, pred_mirad)
        n = norm_match(gold, pred_mirad)
        s = sem_sim(gold, pred_mirad) if pred_mirad else 0.0
        en_mir_exact.append(e)
        en_mir_norm.append(n)
        en_mir_sem.append(s)
        en_mir_results.append({
            "english": ex["english"],
            "gold_mirad": gold,
            "predicted_mirad": pred_mirad[:300],
            "exact_match": int(e),
            "normalized_match": int(n),
            "semantic_similarity": round(s, 4),
        })
        print(f"  [{i+1:2d}/{n_en_mir}] ex={int(e)} norm={int(n)} sem={s:.2f} EN:{ex['english'][:35]} → MI:{pred_mirad[:35]}")
    en_mir_time = time.time() - t0

    # ── Mir→En (20 samples) ──
    n_mir_en = 20
    mir_en_examples = examples[50:50 + n_mir_en]
    print(f"\n{'=' * 72}")
    print(f"  Mir→En: {n_mir_en} examples with GPT-5.5 (compiled)")
    print(f"{'=' * 72}")

    print("Loading Mir→En compiled translator...")
    mir_en_translator = DefaultTranslator(direction="mir_to_en", use_compiled=True)

    mir_en_results = []
    mir_en_exact = []
    mir_en_norm = []
    mir_en_sem = []
    mir_en_errors = 0
    t0 = time.time()
    for i, ex in enumerate(mir_en_examples):
        try:
            pred = mir_en_translator(mirad_text=ex["mirad"])
            pred_english = pred.english_text if pred.english_text else ""
        except Exception as exc:
            print(f"  [{i+1}] ERROR: {type(exc).__name__}: {str(exc)[:80]}")
            pred_english = ""
            mir_en_errors += 1
        gold = ex["english"]
        e = exact_match(gold, pred_english)
        n = norm_match(gold, pred_english)
        s = sem_sim(gold, pred_english) if pred_english else 0.0
        mir_en_exact.append(e)
        mir_en_norm.append(n)
        mir_en_sem.append(s)
        mir_en_results.append({
            "mirad": ex["mirad"],
            "gold_english": gold,
            "predicted_english": pred_english[:300],
            "exact_match": int(e),
            "normalized_match": int(n),
            "semantic_similarity": round(s, 4),
        })
        print(f"  [{i+1:2d}/{n_mir_en}] ex={int(e)} norm={int(n)} sem={s:.2f} MI:{ex['mirad'][:35]} → EN:{pred_english[:35]}")
    mir_en_time = time.time() - t0

    # ── Load DeepSeek references ──
    ds_mir2en_path = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "mir2en_compiled_vs_uncompiled.json"
    ds_en2mir_data = None
    ds_sem_path = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_semantic_per_example.json"
    if ds_sem_path.exists():
        with open(ds_sem_path) as f:
            ds_en2mir_data = json.load(f)

    # ── Summary ──
    def pct(vals):
        return sum(vals) / max(len(vals), 1) * 100

    def median_pct(vals):
        s = sorted(vals)
        return s[len(s) // 2] * 100

    # Load DeepSeek En→Mir reference (100 compiled exact from run_semantic_eval)
    ds_en2mir_compiled_exact = None
    ds_en2mir_compiled_path = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_bootstrap_fast_program" / "metadata.json"
    # Try loading from the semantic eval results
    ds_en_sems = None
    if ds_en2mir_data and "per_example" in ds_en2mir_data:
        ds_en_sems = ds_en2mir_data["per_example"]

    # Load DeepSeek Mir→En reference
    ds_mir2en_ds = None
    if ds_mir2en_path.exists():
        with open(ds_mir2en_path) as f:
            ds_mir2en = json.load(f)
            ds_mir2en_ds = ds_mir2en.get("compiled", {})

    print(f"\n{'=' * 80}")
    print(f"  GPT-5.5 vs DeepSeek-V4-Flash: Translation Quality Comparison")
    print(f"{'=' * 80}")
    print(f"\n  En→Mir (GPT-5.5 n={n_en_mir}, DeepSeek n=100)")
    print(f"  {'Metric':<25} {'GPT-5.5':>12} {'DS-V4-Flash':>12}")
    print(f"  {'-' * 49}")
    print(f"  {'Exact match':<25} {pct(en_mir_exact):>11.1f}% {'61.0%':>12}")
    print(f"  {'Normalized match':<25} {pct(en_mir_norm):>11.1f}% {'NA':>12}")
    print(f"  {'Semantic sim (mean)':<25} {pct(en_mir_sem):>11.1f}%")
    print(f"  {'Semantic sim (median)':<25} {median_pct(en_mir_sem):>11.1f}%")
    print(f"  {'Errors':<25} {en_mir_errors:>12}")
    print(f"  {'Time':<25} {en_mir_time:>10.1f}s")

    print(f"\n  Mir→En (GPT-5.5 n={n_mir_en}, DeepSeek n=30)")
    print(f"  {'Metric':<25} {'GPT-5.5':>12} {'DS-V4-Flash':>12}")
    print(f"  {'-' * 49}")
    ds_mir2en_exact = ds_mir2en_ds.get("exact_pct", "—") if ds_mir2en_ds else "—"
    ds_mir2en_sem = ds_mir2en_ds.get("sem_mean_pct", "—") if ds_mir2en_ds else "—"
    ds_mir2en_med = ds_mir2en_ds.get("sem_median_pct", "—") if ds_mir2en_ds else "—"
    print(f"  {'Exact match':<25} {pct(mir_en_exact):>11.1f}% {str(ds_mir2en_exact):>12}%")
    print(f"  {'Normalized match':<25} {pct(mir_en_norm):>11.1f}% {'33.3':>12}%")
    print(f"  {'Semantic sim (mean)':<25} {pct(mir_en_sem):>11.1f}% {str(ds_mir2en_sem):>12}%")
    print(f"  {'Semantic sim (median)':<25} {median_pct(mir_en_sem):>11.1f}% {str(ds_mir2en_med):>12}%")
    print(f"  {'Errors':<25} {mir_en_errors:>12}")
    print(f"  {'Time':<25} {mir_en_time:>10.1f}s")
    print(f"{'=' * 80}")

    # ── Save results ──
    out = {
        "model": "gpt-5.5",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "en_to_mir": {
            "n_samples": n_en_mir,
            "compiled": True,
            "exact_pct": round(pct(en_mir_exact), 1),
            "norm_pct": round(pct(en_mir_norm), 1),
            "sem_mean_pct": round(pct(en_mir_sem), 1),
            "sem_median_pct": round(median_pct(en_mir_sem), 1),
            "errors": en_mir_errors,
            "elapsed_s": round(en_mir_time, 1),
            "per_example": en_mir_results,
        },
        "mir_to_en": {
            "n_samples": n_mir_en,
            "compiled": True,
            "exact_pct": round(pct(mir_en_exact), 1),
            "norm_pct": round(pct(mir_en_norm), 1),
            "sem_mean_pct": round(pct(mir_en_sem), 1),
            "sem_median_pct": round(median_pct(mir_en_sem), 1),
            "errors": mir_en_errors,
            "elapsed_s": round(mir_en_time, 1),
            "per_example": mir_en_results,
        },
    }
    out_path = PROJECT_ROOT / "data" / "eval_results" / "gpt55_compiled_eval.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()