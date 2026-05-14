"""Quick eval: Aya-8B uncompiled vs DeepSeek compiled/uncompiled (Mir->En)."""
import csv, json, random, re, sys, time
from pathlib import Path

import numpy as np
import dspy
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent / "packages" / "translator" / "src"))

from mirad_translator.ollama_lm import OllamaLM
from mirad_translator.translate import DefaultTranslator
from mirad_translator.evaluate import _normalize


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30
    model = sys.argv[2] if len(sys.argv) > 2 else "cas/aya-expanse-8b"

    lm = OllamaLM(model=model)
    dspy.settings.configure(lm=lm)

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
    start = 50
    eval_examples = examples[start:start + n_samples]
    print(f"Eval set: {len(eval_examples)} examples, model: {model}")

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

    # Uncompiled only (local models can't handle compiled program's prompt length)
    print(f"Loading uncompiled Mir->En ({model}, no RAG)...")
    translator = DefaultTranslator(direction="mir_to_en", use_compiled=False, num_context_passages=0)

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
            print(f"  [{i+1}] ERROR: {type(exc).__name__}: {str(exc)[:60]}")
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
        print(f"  [{i+1}] ex={int(e)} norm={int(n)} sem={s:.2f} MI:{ex.mirad_text[:25]} PRED:{pred_text[:35]}")
    eval_time = time.time() - t0

    exact_pct = sum(exact_scores) / len(exact_scores) * 100
    norm_pct = sum(norm_scores) / len(norm_scores) * 100
    sem_mean = sum(sems) / len(sems) * 100
    sem_median = sorted(sems)[len(sems) // 2] * 100

    # Load DeepSeek comparison data
    ds_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / "mir2en_compiled_vs_uncompiled.json"
    with open(ds_path) as f:
        ds_data = json.load(f)
    ds_ds = ds_data["compiled"]
    ds_uf = ds_data["uncompiled"]

    print()
    print("=" * 72)
    print(f"  {model} (uncompiled, no RAG) vs DeepSeek-V4-Flash (n={len(eval_examples)})")
    print("=" * 72)
    print(f"  {'Metric':<25} {'Aya uncomp':>12} {'DS uncomp':>12} {'DS comp':>12}")
    print(f"  {'-' * 61}")
    print(f"  {'Exact match':<25} {exact_pct:>11.1f}% {ds_uf['exact_pct']:>11.1f}% {ds_ds['exact_pct']:>11.1f}%")
    print(f"  {'Norm match':<25} {norm_pct:>11.1f}% {ds_uf['norm_pct']:>11.1f}% {ds_ds['norm_pct']:>11.1f}%")
    print(f"  {'Sem sim mean':<25} {sem_mean:>11.1f}% {ds_uf['sem_mean_pct']:>11.1f}% {ds_ds['sem_mean_pct']:>11.1f}%")
    print(f"  {'Sem sim median':<25} {sem_median:>11.1f}% {ds_uf['sem_median_pct']:>11.1f}% {ds_ds['sem_median_pct']:>11.1f}%")
    print(f"  {'Errors':<25} {errors:>12}")
    print(f"  {'Time':<25} {eval_time:>11.1f}s")
    print("=" * 72)

    out_data = {
        "direction": "mir_to_en",
        "model": model,
        "config": "uncompiled, no RAG",
        "eval_size": len(eval_examples),
        "exact_pct": round(exact_pct, 1),
        "norm_pct": round(norm_pct, 1),
        "sem_mean_pct": round(sem_mean, 1),
        "sem_median_pct": round(sem_median, 1),
        "errors": errors,
        "eval_time_s": round(eval_time, 2),
        "per_example": [
            {
                "mirad_text": mi,
                "gold_english": gold,
                "predicted_english": pred[:200],
                "exact_match": int(exact_scores[i]),
                "normalized_match": int(norm_scores[i]),
                "semantic_similarity": round(sems[i], 4),
            }
            for i, (mi, gold, pred) in enumerate(results)
        ],
    }
    model_slug = model.replace("/", "_").replace(":", "_")
    out_path = Path(__file__).parent / "data" / "eval_results" / f"mir2en_{model_slug}_eval.json"
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()