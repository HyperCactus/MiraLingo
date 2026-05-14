"""Quick multi-model eval: run several Ollama models on a 5-sample Mir->En subset.

Models are run SEQUENTIALLY with VRAM cleanup between each to avoid OOM.
"""
import csv, json, random, re, sys, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent / "packages" / "translator" / "src"))

import dspy
from mirad_translator.ollama_lm import OllamaLM
from mirad_translator.translate import DefaultTranslator
from mirad_translator.evaluate import _normalize


def free_vram():
    """Tell Ollama to unload models from VRAM by briefly loading then releasing."""
    try:
        # Ollama keeps models loaded for 5m by default. Forcing unload via API.
        subprocess.run(["ollama", "stop", "qwen3:4b"], capture_output=True, timeout=10)
        subprocess.run(["ollama", "stop", "mistral:7b"], capture_output=True, timeout=10)
        subprocess.run(["ollama", "stop", "llama3.2:3b"], capture_output=True, timeout=10)
        subprocess.run(["ollama", "stop", "gemma4:e2b"], capture_output=True, timeout=10)
        subprocess.run(["ollama", "stop", "cas/aya-expanse-8b"], capture_output=True, timeout=10)
        subprocess.run(["ollama", "stop", "qwen3.5:4b"], capture_output=True, timeout=10)
        subprocess.run(["ollama", "stop", "qwen3.5:latest"], capture_output=True, timeout=10)
    except Exception:
        pass
    time.sleep(3)  # Give VRAM time to be freed


def main():
    models = ["qwen3:4b", "mistral:7b", "llama3.2:3b", "gemma4:e2b"]
    n_samples = 5

    # Load eval data (same seed, first 5 after offset 50)
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
    eval_examples = examples[50:50 + n_samples]

    print(f"Eval set: {len(eval_examples)} examples")
    print(f"Models: {models}")
    print(f"Running SEQUENTIALLY with VRAM cleanup between models\n")

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

    st_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    def sem_sim(gold, pred):
        g, p = _normalize(gold), _normalize(pred)
        emb = st_model.encode([g, p], normalize_embeddings=True)
        return float(np.dot(emb[0], emb[1]))

    # Load DeepSeek reference
    ds_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / "mir2en_compiled_vs_uncompiled.json"
    with open(ds_path) as f:
        ds_data = json.load(f)

    # Load Aya reference
    aya_path = Path(__file__).parent / "data" / "eval_results" / "mir2en_cas_aya-expanse-8b_eval.json"
    with open(aya_path) as f:
        aya_data = json.load(f)

    all_results = {}

    # Free VRAM before starting
    free_vram()

    for model in models:
        print(f"\n{'=' * 72}")
        print(f"  Model: {model}")
        print(f"{'=' * 72}")
        try:
            lm = OllamaLM(model=model)
            dspy.settings.configure(lm=lm)
            translator = DefaultTranslator(direction="mir_to_en", use_compiled=False, num_context_passages=0)
        except Exception as e:
            print(f"  SKIP: {e}")
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
                pred_text = pred.english_text[:200] if pred.english_text else ""
            except Exception as exc:
                print(f"  [{i+1}] ERROR: {type(exc).__name__}: {str(exc)[:80]}")
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
            print(f"  [{i+1}] ex={int(e)} norm={int(n)} sem={s:.2f} MI:{ex.mirad_text[:30]} PRED:{pred_text[:40]}")
        elapsed = time.time() - t0

        all_results[model] = {
            "exact_pct": sum(exact_scores) / max(len(exact_scores), 1) * 100,
            "norm_pct": sum(norm_scores) / max(len(norm_scores), 1) * 100,
            "sem_mean_pct": sum(sems) / max(len(sems), 1) * 100,
            "sem_median_pct": sorted(sems)[len(sems) // 2] * 100 if sems else 0,
            "elapsed_s": round(elapsed, 1),
            "errors": errors,
            "per_example": list(zip(results, exact_scores, norm_scores, sems)),
        }

        # Free VRAM before next model
        free_vram()

    # Print comparison table
    print(f"\n{'=' * 80}")
    print(f"  Mir->En Translation: Local Ollama Models (n={n_samples}) vs DeepSeek-V4-Flash")
    print(f"{'=' * 80}")
    header = f"  {'Model':<20} {'Exact':>7} {'Norm':>7} {'Semμ':>7} {'Sem50':>7} {'Time':>7} {'Err':>4}"
    print(header)
    print(f"  {'-' * 60}")

    # DeepSeek references (first 5 samples for fair comparison)
    ds5_comp_exact = sum(ds_data["per_example"][i]["compiled_exact"] for i in range(5)) / 5 * 100
    ds5_comp_sem = sum(ds_data["per_example"][i]["compiled_sem"] for i in range(5)) / 5 * 100
    ds5_comp_norm = sum(ds_data["per_example"][i]["compiled_norm"] for i in range(5)) / 5 * 100

    ds5_uncomp_exact = sum(ds_data["per_example"][i]["uncompiled_exact"] for i in range(5)) / 5 * 100
    ds5_uncomp_sem = sum(ds_data["per_example"][i]["uncompiled_sem"] for i in range(5)) / 5 * 100
    ds5_uncomp_norm = sum(ds_data["per_example"][i]["uncompiled_norm"] for i in range(5)) / 5 * 100

    print(f"  {'DS-V4 compiled':<20} {ds5_comp_exact:>6.0f}% {ds5_comp_norm:>6.0f}% {ds5_comp_sem:>7.1f}% {'—':>7} {'8s':>6} {'0':>4}")
    print(f"  {'DS-V4 uncompiled':<20} {ds5_uncomp_exact:>6.0f}% {ds5_uncomp_norm:>6.0f}% {ds5_uncomp_sem:>7.1f}% {'—':>7} {'350s':>6} {'0':>4}")

    # Aya reference (first 5)
    aya5_exact = sum(e["exact_match"] for e in aya_data["per_example"][:5]) / 5 * 100
    aya5_norm = sum(e["normalized_match"] for e in aya_data["per_example"][:5]) / 5 * 100
    aya5_sem = sum(e["semantic_similarity"] for e in aya_data["per_example"][:5]) / 5 * 100

    print(f"  {'aya-8B uncompiled':<20} {aya5_exact:>6.0f}% {aya5_norm:>6.0f}% {aya5_sem:>7.1f}% {'—':>7} {'54s':>6} {'0':>4}")

    for model in models:
        if model not in all_results:
            print(f"  {model:<20} {'SKIP':>7}")
            continue
        r = all_results[model]
        print(f"  {model:<20} {r['exact_pct']:>6.0f}% {r['norm_pct']:>6.0f}% {r['sem_mean_pct']:>7.1f}% {r['sem_median_pct']:>7.1f}% {r['elapsed_s']:>6.1f}s {r['errors']:>4}")

    print(f"{'=' * 80}")

    # Save results
    out = {
        "direction": "mir_to_en",
        "n_samples": n_samples,
        "models": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    for model, data in all_results.items():
        out["models"][model] = {
            "exact_pct": round(data["exact_pct"], 1),
            "norm_pct": round(data["norm_pct"], 1),
            "sem_mean_pct": round(data["sem_mean_pct"], 1),
            "sem_median_pct": round(data["sem_median_pct"], 1),
            "elapsed_s": data["elapsed_s"],
            "errors": data["errors"],
            "per_example": [
                {
                    "mirad_text": r[0],
                    "gold_english": r[1],
                    "predicted_english": r[2][:200],
                    "exact_match": int(e),
                    "normalized_match": int(n),
                    "semantic_similarity": round(s, 4),
                }
                for r, e, n, s in data["per_example"]
            ],
        }
    out_path = Path(__file__).parent / "data" / "eval_results" / "mir2en_ollama_multimodel.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()