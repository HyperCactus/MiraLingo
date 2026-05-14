"""Test Mistral 7B with COMPILED Mir->En program on 5 samples."""
import csv, json, random, re, sys, time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent / "packages" / "translator" / "src"))

import dspy
from mirad_translator.ollama_lm import OllamaLM
from mirad_translator.translate import DefaultTranslator
from mirad_translator.evaluate import _normalize


def main():
    n_samples = 5
    model = "mistral:7b"

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
    eval_examples = examples[50:50 + n_samples]

    print(f"Model: {model} | Compiled: True | Samples: {n_samples}")

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

    # Load COMPILED Mir->En program
    print("Loading compiled Mir->En program...")
    translator = DefaultTranslator(direction="mir_to_en", use_compiled=True)

    t0 = time.time()
    results = []
    errors = 0
    for i, ex in enumerate(eval_examples):
        try:
            pred = translator(mirad_text=ex.mirad_text)
            pred_text = pred.english_text[:200] if pred.english_text else ""
        except Exception as exc:
            print(f"  [{i+1}] ERROR: {type(exc).__name__}: {str(exc)[:100]}")
            pred_text = ""
            errors += 1
        gold = ex.english_text
        e = exact_match(gold, pred_text) if pred_text else 0.0
        n = norm_match(gold, pred_text) if pred_text else 0.0
        s = sem_sim(gold, pred_text) if pred_text else 0.0
        results.append({"mi": ex.mirad_text, "gold": gold, "pred": pred_text,
                        "exact": e, "norm": n, "sem": s})
        print(f"  [{i+1}] ex={int(e)} norm={int(n)} sem={s:.2f} | MI: {ex.mirad_text[:30]}")
        print(f"        GOLD: {gold[:60]}")
        print(f"        PRED: {pred_text[:60]}")
    elapsed = time.time() - t0

    exact_pct = sum(r["exact"] for r in results) / len(results) * 100
    norm_pct = sum(r["norm"] for r in results) / len(results) * 100
    sem_mean = sum(r["sem"] for r in results) / len(results) * 100
    sem_median = sorted(r["sem"] for r in results)[len(results) // 2] * 100

    # DeepSeek compiled reference (first 5)
    ds_path = Path(__file__).parent / "data" / "eval_results" / "optimizer_comparison" / "mir2en_compiled_vs_uncompiled.json"
    with open(ds_path) as f:
        ds_data = json.load(f)
    ds5 = ds_data["compiled"]
    ds5_sems = [ds_data["per_example"][i]["compiled_sem"] for i in range(5)]
    ds5_exact = sum(ds_data["per_example"][i]["compiled_exact"] for i in range(5)) / 5 * 100
    ds5_sem_mean = sum(ds5_sems) / len(ds5_sems) * 100

    print(f"\n{'=' * 72}")
    print(f"  Mistral 7B COMPILED vs DeepSeek-V4 COMPILED (n={n_samples})")
    print(f"{'=' * 72}")
    print(f"  {'Metric':<20} {'Mistral-comp':>14} {'DS-V4-comp':>14}")
    print(f"  {'-' * 48}")
    print(f"  {'Exact match':<20} {exact_pct:>13.0f}% {ds5_exact:>13.0f}%")
    print(f"  {'Norm match':<20} {norm_pct:>13.0f}% {'—':>14}")
    print(f"  {'Sem sim mean':<20} {sem_mean:>13.1f}% {ds5_sem_mean:>13.1f}%")
    print(f"  {'Sem sim median':<20} {sem_median:>13.1f}% {'—':>14}")
    print(f"  {'Total time':<20} {elapsed:>13.1f}s {'8s':>14}")
    print(f"  {'Errors':<20} {errors:>14}")
    print(f"{'=' * 72}")

    out = {
        "model": model, "compiled": True, "n_samples": n_samples,
        "exact_pct": round(exact_pct, 1), "norm_pct": round(norm_pct, 1),
        "sem_mean_pct": round(sem_mean, 1), "sem_median_pct": round(sem_median, 1),
        "elapsed_s": round(elapsed, 1), "errors": errors,
        "per_example": results,
    }
    out_path = Path(__file__).parent / "data" / "eval_results" / "mir2en_mistral7b_compiled.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()