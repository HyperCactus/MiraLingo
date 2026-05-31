# GEPA Optimization Results

**Date:** 2026-05-30 16:29 UTC  
**Optimizer:** GEPA (auto=light)  
**Train samples:** 3 (min 5 English words)  
**Num candidates:** 3 @ [0.1, 0.4, 0.8]  
**Context passages:** 3  
**Threads:** 24  
**Log dir:** /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval_results/gepa_optimization_20260530_162356_test/gepa_logs  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 0.0% (0/3) |
| Exact Match | 0.0% (0/3) |
| Avg Judge Score | 79.3/100 |

## Timing

| | |
|-|--|
| Compile time | 0s (0.0 min) |
| Eval time | 309s (5.1 min) |
| Avg per sample | 34.31s |

## Results

| # | NM | Judge | Winner T | Sample |
|---|----|-------|----------|--------|
|   0 | ✗ |  95.0 | T=0.1 | do they walk to school every day → Yit tyope bu tistam hya jub? |
|   1 | ✗ |  93.0 | T=0.3 | while they are here they will work at home → je van yit se him, yit yexo be tam |
|   2 | ✗ |  50.0 | T=0.1 | he or she was going home → it sa pea be tam |

## Output Files

- `program.pkl` — Compiled GEPA program (cloudpickle)
- `examples.json` — Per-example predictions and scores
- `run_summary.json` — Machine-readable summary
- `log_dir/` — Raw GEPA optimization logs
