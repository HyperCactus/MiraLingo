#!/usr/bin/env python3
"""Quick eval timing test."""

import os, sys, json, random, time, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # packages/translator/scripts/ -> project root
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from mirad_translator.multi_candidate import MultiCandidateTranslator

print("[1] Building translator...")
t0 = time.time()
shared_mc = MultiCandidateTranslator(
    num_candidates=3,
    temperatures=[0.1, 0.3, 0.7],
    num_context_passages=3,
    top_k_per_word=0,
)
shared_mc._get_lm(0.0)
elapsed = time.time() - t0
print(f"[1] Translator built in {elapsed:.1f}s")

with open("data/eval/train.json") as f:
    raw = json.load(f)
all_data = raw.get("pairs", raw) if isinstance(raw, dict) else raw
samples = []
for d in all_data:
    en = d.get("english", "") or d.get("source", "")
    mir = d.get("mirad", "") or d.get("target", "")
    if en:
        samples.append({"english": en, "mirad": mir, "id": d.get("id", "")})
rng = random.Random(20260526)
rng.shuffle(samples)
samples = samples[:20]
print(f"[2] Loaded {len(samples)} samples")

def eval_one(sample):
    pred = shared_mc(english_text=sample["english"])
    return {
        "english": sample["english"],
        "gold": sample["mirad"],
        "pred": pred.mirad_text,
        "score": pred.total_score,
        "winner": pred.winner_index,
    }

def nmatch(a, b):
    a_n = re.sub(r"[^a-z0-9]", " ", a.lower())
    b_n = re.sub(r"[^a-z0-9]", " ", b.lower())
    return " ".join(a_n.split()) == " ".join(b_n.split())

# Test single eval
print("[3] Testing single eval...")
s0 = time.time()
r = eval_one(samples[0])
elapsed_s = time.time() - s0
p40 = r["pred"][:40]
print(f"[3] Single eval done in {elapsed_s:.1f}s -> pred: {p40}, score: {r['score']}")

# Test 4-parallel with 10 samples
print("[4] Testing 4-parallel with 10 samples...")
t1 = time.time()
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = [ex.submit(eval_one, s) for s in samples[:10]]
    results = [f.result() for f in futures]
elapsed_t = time.time() - t1
nm = sum(1 for r in results if nmatch(r["pred"], r["gold"]))
print(f"[4] 10 samples done in {elapsed_t:.1f}s ({elapsed_t/10:.1f}s/sample)")
print(f"    Normalized match: {nm}/{len(results)}")
avg_score = sum(r["score"] for r in results) / len(results)
print(f"    Avg judge score: {avg_score:.1f}")

# Extrapolate 100 samples at 4 parallel
per_sample = elapsed_t / 10
est_100 = per_sample * 100 / 4
print(f"[5] Extrapolated 100 samples at 4 parallel: {est_100:.0f}s ({est_100/60:.1f} min)")