"""Evaluate compiled Mir->En program with local Ollama qwen3.5:4b + semantic sim."""
import csv, json, random, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

import dspy
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent / "packages" / "translator" / "src"))

from mirad_translator.translate import DefaultTranslator
from mirad_translator.evaluate import _normalize


def main():
    # Configure local Ollama qwen3.5:4b
    lm = dspy.LM(model="ollama/qwen3.5:4b", num_retries=3, cache=True)
    dspy.settings.configure(lm=lm)

    # Load eval data (same 30-example split)
    csv_path = Path(__file__).parent / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en, mi = row["english"].strip(), row["mirad"].strip()
            if en and mi:
                examples.append(dspy.Example(mirad_text=mi, english_text=en).with_inputs("mirad_text"))
    rng = random.Random(42)
    rng.shuffle(examples)
    eval_examples = examples[50:80]
    print(f"Eval set: {len(eval_examples)} examples")
    print(f"Model: ollama/qwen3.5:4b (local)")

    # Metrics
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

    # Semantic model
    st_model = SentenceTransformer("all-MiniLM-L6-v2")

    def sem_sim(gold, pred):
        g, p = _normalize(gold), _normalize(pred)
        emb = st_model.encode([g, p], normalize_embeddings=True)
        return float(np.dot(emb[0], emb[1]))

    # Load compiled Mir->En program (LM overridden to qwen3.5:4b)
    print("Loading compiled Mir->En program...")
    translator = DefaultTranslator(direction="mir_to_en", use_compiled=True)
    print(f"  Type: {type(translator).__name__}")

    # Run evaluation
    print("Running evaluation...")
    t0 = time.time()
    results = []
    sems = []
    exact_scores = []
    norm_scores = []
    errors = 0
    for i, ex in enumerate(eval_examples):
        try:
            pred = translator(mirad_text=ex.mirad_text)
            pred_text = pred.english_text if pred.english_text else ""
        except Exception as exc:
            print(f"  [{i+1}] ERROR: {type(exc).__name__}: {str(exc)[:100]}")
            pred_text = ""
            errors += 1
        
        gold = ex.english_text
        e = exact_match(gold, pred_text) if pred_text else 0.0
        n = norm_match(gold, pred_text) if pred_text else 0.0
        s = sem_sim(gold, pred_text) if pred_text else 0.0
        results.append((ex.mirad_text, gold, pred_text))
        sems.append(s)
        exact_scores.append(e)
        norm_scores.append(n)
        if (i + 1) % 5 == 0:
            print(f"  {i+1}/{len(eval_examples)} done (e={e}, n={n}, s={s:.2f}) errors={errors}")
    eval_time = time.time() - t0

    # Aggregates
    exact_pct = sum(exact_scores) / len(exact_scores) * 100
    norm_pct = sum(norm_scores) / len(norm_scores) * 100
    sem_mean = sum(sems) / len(sems) * 100
    sem_median = sorted(sems)[len(sems) // 2] * 100

    # Load DeepSeek comparison data
    ds_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / "mir2en_compiled_vs_uncompiled.json"
    with open(ds_path) as f:
        ds_data = json.load(f)

    ds = ds_data["compiled"]

    hdr = "=" * 72
    print()
    print(hdr)
    print("  Compiled Mir->En: qwen3.5:4b (local) vs DeepSeek-V4-Flash (cloud)")
    print(hdr)
    print(f"  {'Metric':<25} {'qwen3.5:4b':>14} {'DeepSeek-V4':>14} {'Delta':>10}")
    print(f"  {'-' * 63}")
    print(f"  {'Exact match':<25} {exact_pct:>13.1f}% {ds['exact_pct']:>13.1f}% {exact_pct - ds['exact_pct']:>+9.1f}pp")
    print(f"  {'Normalized match':<25} {norm_pct:>13.1f}% {ds['norm_pct']:>13.1f}% {norm_pct - ds['norm_pct']:>+9.1f}pp")
    print(f"  {'Semantic sim (mean)':<25} {sem_mean:>13.1f}% {ds['sem_mean_pct']:>13.1f}% {sem_mean - ds['sem_mean_pct']:>+9.1f}pp")
    print(f"  {'Semantic sim (median)':<25} {sem_median:>13.1f}% {ds['sem_median_pct']:>13.1f}% {sem_median - ds['sem_median_pct']:>+9.1f}pp")
    print(f"  {'Eval time':<25} {eval_time:>13.1f}s {ds['eval_time_s']:>13.1f}s")
    print(f"  {'Errors (empty resp)':<25} {errors:>13}")
    print(hdr)

    # Per-example details
    print("\nPer-example results:")
    for i, (mi, gold, pred) in enumerate(results):
        e, n, s = exact_scores[i], norm_scores[i], sems[i]
        ds_s = ds_data["per_example"][i]["compiled_sem"]
        d = s - ds_s
        print(f"  sem={s:.2f} (ds={ds_s:.2f} d={d:+.2f}) ex={int(e)}  MI:{mi[:30]}  GOLD:{gold[:35]}  PRED:{pred[:35]}")

    # Save results
    out_data = {
        "direction": "mir_to_en",
        "model": "qwen3.5:4b (ollama local)",
        "optimizer": "BootstrapRS-fast-mir2en (compiled with DeepSeek-V4-Flash)",
        "eval_size": len(eval_examples),
        "compiled_with": "DeepSeek-V4-Flash",
        "evaluated_with": "qwen3.5:4b",
        "exact_pct": round(exact_pct, 1),
        "norm_pct": round(norm_pct, 1),
        "sem_mean_pct": round(sem_mean, 1),
        "sem_median_pct": round(sem_median, 1),
        "eval_time_s": round(eval_time, 2),
        "per_example": [
            {
                "mirad_text": mi,
                "gold_english": gold,
                "predicted_english": pred,
                "exact_match": int(exact_scores[i]),
                "normalized_match": int(norm_scores[i]),
                "semantic_similarity": round(sems[i], 4),
            }
            for i, (mi, gold, pred) in enumerate(results)
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    out_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / "mir2en_qwen35_compiled.json"
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()