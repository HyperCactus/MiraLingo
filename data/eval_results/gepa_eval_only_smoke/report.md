# GEPA Optimization Results

**Date:** 2026-05-31 23:59 UTC  
**Optimizer:** GEPA (auto=eval-only)  
**Train samples:** 5 (min 5 English words)  
**Num candidates:** 3 @ [0.1, 0.4, 0.8]  
**Context passages:** 3  
**Threads:** 24  
**Log dir:** data/eval_results/gepa_eval_only_smoke/gepa_logs  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 80.0% (4/5) |
| Exact Match | 80.0% (4/5) |
| Avg Judge Score | 100.0/100 |

## Timing

| | |
|-|--|
| Compile time | 0s (0.0 min) |
| Eval time | 382s (6.4 min) |
| Avg per sample | 15.29s |

## Results

| # | NM | Judge | Winner T | Sample |
|---|----|-------|----------|--------|
|   0 | ✓ | 100.0 | T=0.1 | we came → yat upa |
|   1 | ✗ | 100.0 | T=0.1 | people → tyod |
|   2 | ✓ | 100.0 | T=0.1 | they do not come → yit voy upe |
|   3 | ✓ | 100.0 | T=0.3 | your desk is clean → eta dresem se vyia |
|   4 | ✓ | 100.0 | T=0.1 | you do → et xe |

## Output Files

- `program.pkl` — Compiled GEPA program (cloudpickle)
- `examples.json` — Per-example predictions and scores
- `run_summary.json` — Machine-readable summary
- `log_dir/` — Raw GEPA optimization logs
