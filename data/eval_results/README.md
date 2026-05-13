# Evaluation Results

Results from DSPy optimization experiments on the 44-pair English→Mirad evaluation set.

## Files

### Model comparison (39 eval pairs, LabeledFewShot k=5, DeepSeek-V4-Flash baseline)

| File | Description |
|------|-------------|
| `labeled_fewshot_k5.json` | DeepSeek-V4-Flash LFS k=5 results (56.4%) |
| `labeled_fewshot_k5_per_example.json` | Per-example predictions |
| `labeled_fewshot_k10.json` | LFS k=10 results |
| `labeled_fewshot_k10_per_example.json` | Per-example predictions |
| `labeled_fewshot_k5_hops2.json` | LFS k=5 with 2-hop retrieval |
| `labeled_fewshot_k5_critique.json` | LFS k=5 + critique-and-fix |
| `mir_to_en_labeled_fewshot_k5.json` | Mir→En baseline (reverse direction) |

### Model comparison sweep (7 models, 39 eval pairs, LFS k=5)

| File | Model | Score |
|------|-------|-------|
| `model_deepseek_v4_flash.json` | DeepSeek-V4-Flash | baseline |
| `model_deepseek_v4_pro.json` | DeepSeek-V4-Pro | 53.8% |
| `model_gemini_25_flash.json` | Gemini-2.5-Flash | 48.7% |
| `model_qwen36_35b_a3b.json` | Qwen3.6-35B-A3B | 48.7% |
| `model_gpt_oss_120b.json` | GPT-OSS-120B | 33.3% |
| `model_gpt_oss_20b.json` | GPT-OSS-20B | 28.2% |
| `model_gemma4_26b_a4b.json` | Gemma-4-26B-A4B | 28.2% |

### BootstrapFewShot sweep

| File | Config | Dev Score | Full Score |
|------|--------|-----------|------------|
| `bootstrap_sweep/bfs_d8_l16_r2.json` | d=8, l=16, r=2 | 70.0% | — |
| `bootstrap_sweep/bfs_d8_l16_r2_full_eval.json` | d=8, l=16, r=2 | — | 66.7% |
| `bootstrap_sweep/bfs_d4_l8_r1.json` | d=4, l=8, r=1 | 65.0% | — |
| `bootstrap_sweep/bfs_d4_l8_r3.json` | d=4, l=8, r=3 | 67.5% | — |
| `bootstrap_sweep/bfs_d4_l16_r1.json` | d=4, l=16, r=1 | 65.0% | — |
| `bootstrap_sweep/bfs_d2_l4_r1.json` | d=2, l=4, r=1 | 65.0% | — |
| `bootstrap_sweep/bfs_d2_l8_t50.json` | d=2, l=8, r=1 (temp=0.5) | 62.5% | — |
| `bootstrap_sweep/sweep_summary.csv` | All configs, CSV format | — | — |
| `bootstrap_sweep/bfsrs_best.json` | BFSRS best result (timed out) | — | — |

### Final comparison (T05 task)

| File | Description |
|------|-------------|
| `final_comparison.json` | Side-by-side: LFS baseline, BFS best, BFS+post-processor, BFS+post-proc+threshold |
| `error_taxonomy.md` | 17 miss examples categorized: A=particle, B=morphology, C=lexicon, D=structural |

### Ollama baseline

| File | Description |
|------|-------------|
| `ollama_baseline.json` | qwen3.5:4b, normalized match metric |
| `ollama_baseline_exact.json` | qwen3.5:4b, exact match metric |
| `ollama_baseline_summary.json` | Summary dict |

### Trace inspection

| File | Description |
|------|-------------|
| `trace_inspection.json` | First 5 examples with word equivalents + retrieval context |

## Error Taxonomy Summary

From `error_taxonomy.md` (17 misses / 39 eval pairs):

| Category | Count | % | Fixable by Post-Processor? |
|----------|-------|---|---------------------------|
| A. Particle confusion (be↔bi, ge↔vyel) | 2 | 5.1% | ✅ Yes (both rules implemented) |
| B. Progressive morphology (-ye suffix) | 2 | 5.1% | ❌ Flagged only (ambiguity) |
| C. Lexicon gaps / wrong word | 6 | 15.4% | ❌ Model improvement needed |
| D. Structural / hallucination | 7 | 17.9% | ❌ Model improvement needed |
| **Hits** | **22** | **56.4%** | |

The post-processor fixes the 2 particle errors (A1, A2) but cannot address wrong word choices or hallucinated structures — those require model improvements (more training data, fine-tuning, or a different architecture).

## Key Results

- **Best score:** 66.7% normalized match (BFS d8_l16_r2 + post-processor, 39 eval pairs)
- **Best BFS config:** max_bootstrapped_demos=8, max_labeled_demos=16, max_rounds=2
- **BFSRS timed out** at 600s — DeepSeek-V4-Flash latency makes iterative optimization impractical
- **23.3pp gap** to 90% target; needs more training data or fine-tuning, not more optimization

## Reproducing Results

```bash
cd /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine

# Best result: BFS d8_l16_r2 + post-processor (66.7%)
PYTHONPATH=packages/translator/src python run_t05_combined_eval.py

# Model comparison sweep (requires DEEPINFRA_API_KEY)
PYTHONPATH=packages/translator/src python scripts/deepinfra_model_eval.py

# BFS parameter sweep
PYTHONPATH=packages/translator/src python scripts/run_bfs_sweep.py
```