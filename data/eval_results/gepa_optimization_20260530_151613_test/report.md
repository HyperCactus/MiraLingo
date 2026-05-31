# GEPA Optimization Results

**Date:** 2026-05-30 15:19 UTC  
**Optimizer:** GEPA (auto=light)  
**Train samples:** 3 (min 5 English words)  
**Num candidates:** 3 @ [0.1, 0.4, 0.8]  
**Context passages:** 3  
**Threads:** 24  
**Log dir:** /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval_results/gepa_optimization_20260530_151613_test/gepa_logs  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 0.0% (0/3) |
| Exact Match | 0.0% (0/3) |
| Avg Judge Score | 77.3/100 |

## Timing

| | |
|-|--|
| Compile time | 0s (0.0 min) |
| Eval time | 220s (3.7 min) |
| Avg per sample | 24.44s |

## Results

| # | NM | Judge | Winner T | Sample |
|---|----|-------|----------|--------|
|   0 | ✗ | 100.0 | T=0.4 | do they walk to school every day → Yit tyope bu tistam hyajub? |
|   1 | ✗ |  91.0 | T=0.4 | while they are here they will work at home → Je van yit se him, yit yexo be tam. |
|   2 | ✗ |  41.0 | T=0.4 | he or she was going home → it pa be tam |

## Output Files

- `program.pkl` — Compiled GEPA program (cloudpickle)
- `examples.json` — Per-example predictions and scores
- `run_summary.json` — Machine-readable summary
- `log_dir/` — Raw GEPA optimization logs
