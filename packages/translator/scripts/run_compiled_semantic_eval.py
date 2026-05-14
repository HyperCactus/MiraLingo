"""Evaluate COMPILED+SEMANTIC against existing COMPILED+EXACT results.

Only runs compiled+semantic (swapping MiradSemanticLexiconLookup into the
compiled BootstrapFewShot program). Compares against the compiled+exact
per-example data from the prior semantic_lexicon_comparison eval.
"""
import csv
import json
import os
import random
import re
import time
from pathlib import Path

import dspy
import cloudpickle

_PROJECT_ROOT = Path("/mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine")
EVAL_CSV_PATH = _PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
COMPILED_PROGRAM_PATH = _PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_bootstrap_fast_program" / "program.pkl"
PRIOR_EXACT_PATH = _PROJECT_ROOT / "data" / "eval_results" / "semantic_lexicon_comparison_compiled_per_example.json"
RESULTS_DIR = _PROJECT_ROOT / "data" / "eval_results"

def normalize(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text

def strip_punct(s):
    s = re.sub(r'[.,!?;:()"\'][\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()

def normalized_match(gold, pred):
    return strip_punct(normalize(gold)) == strip_punct(normalize(pred))

def main():
    from dotenv import load_dotenv
    load_dotenv(_PROJECT_ROOT / ".env")
    from mirad_translator.postprocess import postprocess_mirad
    from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup

    N_SAMPLES = 100
    SEED = 42
    TOP_K = 3
    MIN_SIM = 0.5
    MAX_PAIRS = 30
    MODEL = "deepseek-ai/DeepSeek-V4-Flash"

    # Load compiled program + demo texts
    print("[1/4] Loading compiled program...")
    with open(COMPILED_PROGRAM_PATH, "rb") as f:
        compiled = cloudpickle.load(f)

    demo_texts = set()
    for name, pred in compiled.named_predictors():
        for demo in pred.demos:
            if "english_text" in demo:
                demo_texts.add(demo["english_text"].strip())
    print(f"  Excluding {len(demo_texts)} demo texts")

    # Load eval set (same seed as prior run)
    print("[2/4] Loading evaluation dataset...")
    examples = []
    with open(EVAL_CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            english = row.get("English", row.get("english", "")).strip()
            mirad = row.get("Mirad", row.get("mirad", "")).strip()
            if english and mirad and english not in demo_texts:
                examples.append({"english": english, "mirad": mirad})

    rng = random.Random(SEED)
    examples = rng.sample(examples, min(N_SAMPLES, len(examples)))
    print(f"  {len(examples)} examples (same seed={SEED} as prior eval)")

    # Swap in semantic lexicon
    compiled.lexicon_lookup = MiradSemanticLexiconLookup(
        db_path=None, top_k_per_word=TOP_K, max_total_pairs=MAX_PAIRS, min_similarity=MIN_SIM,
    )

    # Configure LM
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    lm = dspy.LM(model=f"openai/{MODEL}", api_key=api_key, api_base=api_base)
    dspy.settings.configure(lm=lm)

    # Run compiled+semantic
    print(f"[3/4] COMPILED+SEMANTIC (k={TOP_K}, sim≥{MIN_SIM})...")
    results = []
    start = time.time()
    for i, ex in enumerate(examples):
        pred = compiled(english_text=ex["english"])
        mirad_text = postprocess_mirad(pred.mirad_text)
        nm = normalized_match(ex["mirad"], mirad_text)
        em = normalize(ex["mirad"]) == normalize(mirad_text)
        we = pred.word_equivalents if hasattr(pred, "word_equivalents") and pred.word_equivalents else {}
        results.append({
            "english": ex["english"], "gold_mirad": ex["mirad"],
            "predicted_mirad": mirad_text, "normalized_match": nm, "exact_match": em,
            "word_equivalents_count": len(we), "method": "COMPILED_SEMANTIC",
        })
        if (i + 1) % 10 == 0:
            pct = sum(r["normalized_match"] for r in results) / len(results) * 100
            print(f"  [{i+1}/{len(examples)}] norm={pct:.1f}%  elapsed={time.time()-start:.0f}s")
    elapsed = time.time() - start

    cs_norm = sum(1 for r in results if r["normalized_match"]) / len(results) * 100
    cs_exact = sum(1 for r in results if r["exact_match"]) / len(results) * 100
    cs_avg_we = sum(r["word_equivalents_count"] for r in results) / len(results)
    print(f"  COMPILED+SEMANTIC: norm={cs_norm:.1f}%  exact={cs_exact:.1f}%  avg_we={cs_avg_we:.1f}  time={elapsed:.0f}s")

    # Load prior compiled+exact results
    print("[4/4] Comparing against prior COMPILED+EXACT results...")
    prior = json.load(open(PRIOR_EXACT_PATH))
    # Verify same examples (same seed)
    prior_texts = [r["english"] for r in prior]
    current_texts = [r["english"] for r in results]
    assert prior_texts == current_texts, f"Example mismatch! {len(prior_texts)} vs {len(current_texts)}"

    ce_norm = sum(1 for r in prior if r["normalized_match"]) / len(prior) * 100

    # Pairwise comparison
    both_right = substantive_sem = substantive_ex = punct_sem = punct_ex = both_wrong = 0
    sem_wins = ex_wins = 0
    for ce, cs in zip(prior, results):
        ce_nm = ce["normalized_match"]
        cs_nm = cs["normalized_match"]
        if ce_nm and cs_nm:
            both_right += 1
        elif ce_nm and not cs_nm:
            ex_wins += 1
            if strip_punct(ce["predicted_mirad"]) == strip_punct(ce["gold_mirad"]):
                punct_ex += 1
            else:
                substantive_ex += 1
        elif cs_nm and not ce_nm:
            sem_wins += 1
            if strip_punct(cs["predicted_mirad"]) == strip_punct(cs["gold_mirad"]):
                punct_sem += 1
            else:
                substantive_sem += 1
        else:
            both_wrong += 1

    print("\n" + "=" * 70)
    print("COMPILED+SEMANTIC vs COMPILED+EXACT")
    print("=" * 70)
    print(f"  Eval samples:           {len(examples)}")
    print(f"  Semantic config:         k={TOP_K}, sim≥{MIN_SIM}, max_pairs={MAX_PAIRS}")
    print()
    print(f"  {'Config':<30} {'Norm%':>8} {'Avg WE':>8}")
    print(f"  {'-'*30} {'-'*8} {'-'*8}")
    print(f"  {'COMPILED+EXACT (prior)':<30} {ce_norm:>7.1f}% {sum(r['word_equivalents_count'] for r in prior)/len(prior):>7.1f}")
    print(f"  {'COMPILED+SEMANTIC':<30} {cs_norm:>7.1f}% {cs_avg_we:>7.1f}")
    print()
    print(f"  Pairwise (same 100 examples, same compiled program):")
    print(f"    Both correct:              {both_right}")
    print(f"    Compiled+Exact wins:       {ex_wins} (substantive: {substantive_ex}, punct-only: {punct_ex})")
    print(f"    Compiled+Semantic wins:    {sem_wins} (substantive: {substantive_sem}, punct-only: {punct_sem})")
    print(f"    Both wrong:                {both_wrong}")
    print(f"    Net substantive Δ:         {substantive_sem - substantive_ex:+d}")

    # Show examples
    if sem_wins > 0:
        print(f"\n=== COMPILED+SEMANTIC WINS ({sem_wins}) ===")
        for ce, cs in zip(prior, results):
            if cs["normalized_match"] and not ce["normalized_match"]:
                sub = strip_punct(cs["predicted_mirad"]) == strip_punct(cs["gold_mirad"])
                print(f"  EN: {ce['english'][:80]}")
                print(f"  GOLD:  {ce['gold_mirad'][:80]}")
                print(f"  CE({ce['word_equivalents_count']} WE): {ce['predicted_mirad'][:80]}")
                print(f"  CS({cs['word_equivalents_count']} WE): {cs['predicted_mirad'][:80]}")
                print(f"  Substantive: {not sub}")
                print()

    if ex_wins > 0:
        print(f"\n=== COMPILED+EXACT WINS ({ex_wins}) ===")
        for ce, cs in zip(prior, results):
            if ce["normalized_match"] and not cs["normalized_match"]:
                sub = strip_punct(ce["predicted_mirad"]) == strip_punct(ce["gold_mirad"])
                print(f"  EN: {ce['english'][:80]}")
                print(f"  GOLD:  {ce['gold_mirad'][:80]}")
                print(f"  CE({ce['word_equivalents_count']} WE): {ce['predicted_mirad'][:80]}")
                print(f"  CS({cs['word_equivalents_count']} WE): {cs['predicted_mirad'][:80]}")
                print(f"  Substantive: {not sub}")
                print()

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = {
        "method": "compiled_semantic_vs_compiled_exact",
        "n_samples": len(examples),
        "n_excluded_demos": len(demo_texts),
        "top_k_per_word": TOP_K, "min_similarity": MIN_SIM, "max_total_pairs": MAX_PAIRS,
        "seed": SEED, "model": MODEL,
        "compiled_exact_norm": round(ce_norm, 1),
        "compiled_semantic_norm": round(cs_norm, 1),
        "compiled_semantic_exact": round(cs_exact, 1),
        "compiled_semantic_avg_we": round(cs_avg_we, 1),
        "compiled_semantic_time_s": round(elapsed, 1),
        "pairwise": {
            "both_correct": both_right, "exact_wins": ex_wins, "semantic_wins": sem_wins,
            "both_wrong": both_wrong, "substantive_exact": substantive_ex,
            "substantive_semantic": substantive_sem, "net_substantive_delta": substantive_sem - substantive_ex,
        },
    }
    out_path = RESULTS_DIR / "compiled_semantic_vs_exact.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    per_path = RESULTS_DIR / "compiled_semantic_per_example.json"
    with open(per_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()