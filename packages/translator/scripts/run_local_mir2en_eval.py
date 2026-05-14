"""Evaluate compiled & uncompiled Mir->En with local Ollama models + semantic sim."""
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
    model = sys.argv[1] if len(sys.argv) > 1 else "cas/aya-expanse-8b"
    model_label = model.replace("/", "_").replace(":", "_")
    
    # Configure local Ollama LM using OllamaLM (bypasses litellm, disables think mode)
    from mirad_translator.ollama_lm import OllamaLM
    lm = OllamaLM(model=model)
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
    # Support --quick flag for smaller eval set
    if "--quick" in sys.argv:
        eval_examples = eval_examples[:10]
    print(f"Eval set: {len(eval_examples)} examples")
    print(f"Model: {model}")

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

    # Evaluate both compiled and uncompiled
    configs = [
        ("compiled", True),
        ("uncompiled", False),
    ]
    
    all_results = {}
    
    for label, use_compiled in configs:
        print(f"\n--- {label} ---")
        try:
            translator = DefaultTranslator(direction="mir_to_en", use_compiled=use_compiled, num_context_passages=5 if not use_compiled else 0)
        except FileNotFoundError:
            print(f"  Compiled program not found, skipping compiled eval")
            continue
        
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
                # Truncate garbage output (some models hallucinate long output)
                if len(pred_text) > 500:
                    pred_text = pred_text[:500] + "..."
            except Exception as exc:
                err_msg = str(exc)[:80]
                print(f"  [{i+1}] ERROR: {type(exc).__name__}: {err_msg}")
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
            if (i + 1) % 10 == 0:
                print(f"  {i+1}/{len(eval_examples)} done (e={e}, n={n}, s={s:.2f}) errors={errors}")
        eval_time = time.time() - t0

        exact_pct = sum(exact_scores) / len(exact_scores) * 100
        norm_pct = sum(norm_scores) / len(norm_scores) * 100
        sem_mean = sum(sems) / len(sems) * 100
        sem_median = sorted(sems)[len(sems) // 2] * 100

        all_results[label] = {
            "exact_pct": exact_pct,
            "norm_pct": norm_pct,
            "sem_mean_pct": sem_mean,
            "sem_median_pct": sem_median,
            "eval_time_s": eval_time,
            "errors": errors,
            "per_example": list(zip(results, exact_scores, norm_scores, sems)),
        }

    # Load DeepSeek comparison data
    ds_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / "mir2en_compiled_vs_uncompiled.json"
    with open(ds_path) as f:
        ds_data = json.load(f)
    ds = ds_data["compiled"]

    # Print comparison table
    hdr = "=" * 80
    print(f"\n{hdr}")
    print(f"  Mir->En Translation Evaluation: {model_label} vs DeepSeek-V4-Flash")
    print(hdr)
    print(f"  {'Metric':<25} {'Comp(ollama)':>14} {'Uncomp(ollama)':>14} {'Comp(DS-V4)':>14}")
    print(f"  {'-' * 67}")
    
    if "compiled" in all_results:
        c = all_results["compiled"]
        u = all_results.get("uncompiled", {"exact_pct": 0, "norm_pct": 0, "sem_mean_pct": 0, "sem_median_pct": 0})
        print(f"  {'Exact match':<25} {c['exact_pct']:>13.1f}% {u['exact_pct']:>13.1f}% {ds['exact_pct']:>13.1f}%")
        print(f"  {'Normalized match':<25} {c['norm_pct']:>13.1f}% {u['norm_pct']:>13.1f}% {ds['norm_pct']:>13.1f}%")
        print(f"  {'Semantic sim (mean)':<25} {c['sem_mean_pct']:>13.1f}% {u['sem_mean_pct']:>13.1f}% {ds['sem_mean_pct']:>13.1f}%")
        print(f"  {'Semantic sim (median)':<25} {c['sem_median_pct']:>13.1f}% {u['sem_median_pct']:>13.1f}% {ds['sem_median_pct']:>13.1f}%")
        print(f"  {'Eval time':<25} {c['eval_time_s']:>12.1f}s {u['eval_time_s']:>12.1f}s {ds['eval_time_s']:>12.1f}s")
        print(f"  {'Errors':<25} {c['errors']:>14} {u['errors']:>14}")
    elif "uncompiled" in all_results:
        u = all_results["uncompiled"]
        print(f"  {'Exact match':<25} {'N/A':>14} {u['exact_pct']:>13.1f}% {ds['exact_pct']:>13.1f}%")
        print(f"  {'Normalized match':<25} {'N/A':>14} {u['norm_pct']:>13.1f}% {ds['norm_pct']:>13.1f}%")
        print(f"  {'Semantic sim (mean)':<25} {'N/A':>14} {u['sem_mean_pct']:>13.1f}% {ds['sem_mean_pct']:>13.1f}%")
        print(f"  {'Semantic sim (median)':<25} {'N/A':>14} {u['sem_median_pct']:>13.1f}% {ds['sem_median_pct']:>13.1f}%")
        print(f"  {'Eval time':<25} {'N/A':>14} {u['eval_time_s']:>12.1f}s {ds['eval_time_s']:>12.1f}s")
        print(f"  {'Errors':<25} {'N/A':>14} {u['errors']:>14}")
    print(hdr)

    # Save results
    out_data = {
        "direction": "mir_to_en",
        "model": model,
        "optimizer_compiled_with": "DeepSeek-V4-Flash",
        "eval_size": len(eval_examples),
        "results": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    for label, data in all_results.items():
        out_data["results"][label] = {
            "exact_pct": round(data["exact_pct"], 1),
            "norm_pct": round(data["norm_pct"], 1),
            "sem_mean_pct": round(data["sem_mean_pct"], 1),
            "sem_median_pct": round(data["sem_median_pct"], 1),
            "eval_time_s": round(data["eval_time_s"], 2),
            "errors": data["errors"],
            "per_example": [
                {
                    "mirad_text": r[0],
                    "gold_english": r[1],
                    "predicted_english": r[2],
                    "exact_match": int(e),
                    "normalized_match": int(n),
                    "semantic_similarity": round(s, 4),
                }
                for r, e, n, s in data["per_example"]
            ],
        }
    out_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / f"mir2en_{model_label.replace(':', '_').replace('/', '_')}_eval.json"
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()