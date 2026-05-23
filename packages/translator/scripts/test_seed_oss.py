#!/usr/bin/env python3
"""Quick test: 1 sample with Seed-OSS 36B"""

import sys
import os
import json
import time
import random
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import dspy

RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
COMPILED_DIR = str(RESULTS_DIR / "compiled_bootstrap_fast_program")

def _normalize(text: str) -> str:
    text = text.strip()
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text)
    return text

def _strip_punct(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()

def normalized_match_en_to_mir(example, prediction, trace=None) -> float:
    gold = _normalize(getattr(example, "mirad_text", ""))
    pred = _normalize(getattr(prediction, "mirad_text", ""))
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0

def load_full_dataset():
    csv_path = str(PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv")
    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = __import__('csv').DictReader(f)
        for row in reader:
            en = row.get("English", row.get("english", "")).strip()
            mi = row.get("Mirad", row.get("mirad", "")).strip()
            if en and mi:
                examples.append(__import__('dspy').Example(english_text=en, mirad_text=mi).with_inputs("english_text"))
    random.Random(42).shuffle(examples)
    return examples

# Load compiled program
print("Loading compiled program...", flush=True)
compiled = dspy.load(COMPILED_DIR, allow_pickle=True)
print("✓ Compiled loaded", flush=True)

# Load dataset
all_examples = load_full_dataset()
test_ex = all_examples[0]
print(f"\nTest input: {test_ex.english_text}", flush=True)

# Configure LM
lm = dspy.LM(
    model="bytedance/seed-oss-36b-instruct",
    api_key=os.environ.get("NVIDIA_API_KEY", ""),
    api_base="https://integrate.api.nvidia.com/v1",
    num_retries=5,
    cache=True,
)
dspy.settings.configure(lm=lm)

# Make a single prediction
print("\nMaking prediction (this may take 30-60 seconds)...", flush=True)
start = time.time()

try:
    pred = compiled(english_text=test_ex.english_text)
    elapsed = time.time() - start

    gold = test_ex.mirad_text
    raw_mirad = pred.mirad_text
    norm_score = normalized_match_en_to_mir(test_ex, pred)

    print(f"\n{'='*60}")
    print(f"PREDICTION RESULTS")
    print(f"{'='*60}")
    print(f"Input:    {test_ex.english_text}")
    print(f"Gold:     {gold}")
    print(f"Predicted: {raw_mirad}")
    print(f"Score:    {norm_score:.2f}")
    print(f"Time:     {elapsed:.1f}s")
    print(f"{'='*60}")

    # Test API health
    print("\nTesting API connectivity directly...", flush=True)
    import requests as _r
    api_key = os.environ["NVIDIA_API_KEY"]
    resp = _r.get("https://integrate.api.nvidia.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
    print(f"API models endpoint: {_r.get('status_code', 'N/A')}", flush=True)
    if resp.status_code == 200:
        data = resp.json()
        model_info = [m for m in data.get('data', []) if m.get('id') == 'bytedance/seed-oss-36b-instruct']
        print(f"Seed-OSS 36B available: {bool(model_info)}", flush=True)
        if model_info:
            print(f"Status: {model_info[0].get('status', 'N/A')}", flush=True)
    else:
        print(f"Error: {resp.text[:200]}", flush=True)

except Exception as e:
    print(f"\nEXCEPTION: {e}", flush=True)
    import traceback
    traceback.print_exc()