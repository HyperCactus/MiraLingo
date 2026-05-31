# BootstrapFewShot Optimization — MultiCandidateTranslator

**Date:** 2026-05-29 15:11
**Model:** openai/deepseek-ai/DeepSeek-V4-Flash
**Trainset:** 100 examples (data/eval/train.json, bootstrap + eval split)
**Valset:** 100 examples (data/eval/val.json)

## Config
| Parameter | Value |
|-----------|-------|
| n_candidates | 3 |
| temperatures | [0.1, 0.3, 0.7] |
| num_context_passages (k_grammar) | 3 |
| top_k_per_word (k_vocab) | 0 |
| max_bootstrapped_demos | 18 |
| max_labeled_demos | 0 |
| max_errors (bootstrap) | 5 |
| num_retries (LM) | 3 |
| max_tokens | 4096 |
| parallel threads | 16 |
| max_in_flight | 16 |
| max_trace_size | 10000 |
| bootstrap_n | 100 |
| train_eval_n | 100 |

## Timing
| Phase | Duration |
|-------|----------|
| BootstrapFewShot.compile() | 184s |
| Eval train (normalized) | 774s |
| Eval val (normalized) | 729s |
| Exact match train | 769s |
| Exact match val | 915s |
| **Total wall time** | **3372s** |

## Results

### Train set
| Metric | Value |
|--------|-------|
| Normalized Match | 50.0% (50/100) |
| Exact Match | 46.0% (46/100) |

### Val set
| Metric | Value |
|--------|-------|
| Normalized Match | 62.0% (62/100) |
| Exact Match | 55.0% (55/100) |

## Output
- Compiled program: `/mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval_results/bsfs_optimization_20260529_141519/compiled_program`
- Summary JSON: `/mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval_results/bsfs_optimization_20260529_141519/run_summary.json`
- Run timestamp: 20260529_141519
