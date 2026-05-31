#!/usr/bin/env python3
"""Minimal 2-sample test to measure per-sample eval latency."""
import os, sys, time
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # packages/translator/scripts -> project root
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

print("Loading modules...")
t0 = time.time()
from mirad_translator.multi_candidate import MultiCandidateTranslator
from mirad_translator.semantic_lexicon import semantic_lookup_structured

# Warm up embedding model in this process
semantic_lookup_structured("test", top_k_per_word=0, include_exact=True)
print(f"Modules loaded in {time.time()-t0:.1f}s")

mc = MultiCandidateTranslator(num_candidates=3, temperatures=[0.1, 0.3, 0.7],
                               num_context_passages=3, top_k_per_word=0)
mc._get_lm(0.0)

import json
with open("data/eval/train.json") as f:
    raw = json.load(f)
all_data = raw.get("pairs", raw) if isinstance(raw, dict) else raw
samples = []
for d in all_data:
    en = d.get("english","") or d.get("source","")
    mir = d.get("mirad","") or d.get("target","")
    if en:
        samples.append({"english": en, "mirad": mir})

# Test just 2 samples sequentially
for i, s in enumerate(samples[:2]):
    t1 = time.time()
    pred = mc(english_text=s["english"])
    elapsed = time.time() - t1
    nm = s["mirad"].lower().replace(" ","") == pred.mirad_text.lower().replace(" ","")
    print(f"Sample {i}: {elapsed:.1f}s -> '{pred.mirad_text[:50]}' (score={pred.total_score:.0f}, NM={nm})")

# Summary
print(f"\nAvg time per sample: ~{elapsed:.0f}s")
print(f"Estimated 100 samples at parallel=1: {elapsed*100:.0f}s")
print(f"Estimated 100 samples at parallel=6: {elapsed*100/6:.0f}s")