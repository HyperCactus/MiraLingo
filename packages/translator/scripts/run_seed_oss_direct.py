#!/usr/bin/env python3
"""Direct Seed-OSS evaluation with minimal dependencies"""

import csv
import json
import os
import sys
import random
import re
import time
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root / "packages" / "translator" / "src"))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

import dspy

RESULTS_DIR = project_root / "data" / "eval_results" / "optimizer_comparison"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
COMPILED_DIR = str(RESULTS_DIR / "compiled_bootstrap_fast_program")


def _normalize(text):
    text = text.strip()
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text)
    return text

def _strip_punct(s):
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()

def normalized_match_en_to_mir(example, prediction):
    gold = _normalize(getattr(example, "mirad_text", ""))
    pred = _normalize(getattr(prediction, "mirad_text", ""))
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0

def load_full_dataset():
    csv_path = str(project_root / "data" / "phrases" / "english-mirad-sentence-pairs.csv")
    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("English", row.get("english", "")).strip()
            mi = row.get("Mirad", row.get("mirad", "")).strip()
            if en and mi:
                examples.append(dspy.Example(english_text=en, mirad_text=mi).with_inputs("english_text"))
    random.Random(42).shuffle(examples)
    return examples

print("Loading compiled program...")
compiled = dspy.load(COMPILED_DIR, allow_pickle=True)
print(f"✓ Loaded compiled program")

print("Loading dataset...")
all_examples = load_full_dataset()
eval_examples = all_examples[:50]
print(f"✓ Loaded {len(eval_examples)} examples")

print("Configuring LM...")
lm = dspy.LM(
    model="bytedance/seed-oss-36b-instruct",
    api_key=os.environ.get("NVIDIA_API_KEY"),
    api_base="https://integrate.api.nvidia.com/v1",
    num_retries=5,
    cache=True,
)
dspy.settings.configure(lm=lm)

print("\nStarting evaluation...")
print("=" * 60)

eval_start = time.time()
correct = 0

for i, ex in enumerate(eval_examples):
    try:
        pred = compiled(english_text=ex.english_text)
        score = normalized_match_en_to_mir(ex, pred)

        if score == 1.0:
            correct += 1

        elapsed = time.time() - eval_start
        rate = correct / (i + 1) * 100
        remaining = (elapsed / (i + 1)) * (len(eval_examples) - (i + 1))
        eta_min = remaining / 60

        print(f"[{i+1}/50] {rate:.1f}% | ETA: {eta_min:.1f} min", flush=True)

    except Exception as e:
        print(f"[{i+1}/50] ERROR: {e}", flush=True)

total_time = time.time() - eval_start
accuracy = correct / len(eval_examples) * 100

print("=" * 60)
print(f"\nResults:")
print(f"  Correct:  {correct}/50")
print(f"  Accuracy: {accuracy:.1f}%")
print(f"  Time:     {total_time:.1f}s ({total_time/60:.1f} min)")
print(f"\nSaved: data/eval_results/optimizer_comparison/seed_oss_eval_50s.json")
print("=" * 60)

result = {
    "model": "bytedance/seed-oss-36b-instruct",
    "correct": correct,
    "total": 50,
    "accuracy": accuracy,
    "time_s": round(total_time, 2),
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open(RESULTS_DIR / "seed_oss_eval_50s.json", "w") as f:
    json.dump(result, f, indent=2)

print("\n✓ Done!")