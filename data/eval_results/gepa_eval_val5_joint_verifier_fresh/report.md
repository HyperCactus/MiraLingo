# GEPA Optimization Results

**Date:** 2026-06-01 00:52 UTC  
**Optimizer:** GEPA (auto=eval-only)  
**Train samples:** 5 (min 5 English words)  
**Num candidates:** 3 @ [0.1, 0.4, 0.8]  
**Context passages:** 3  
**Threads:** 24  
**Log dir:** data/eval_results/gepa_eval_val5_joint_verifier_fresh/gepa_logs  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 20.0% (1/5) |
| Exact Match | 20.0% (1/5) |
| Avg Judge Score | 100.0/100 |

## Timing

| | |
|-|--|
| Compile time | 0s (0.0 min) |
| Eval time | 456s (7.6 min) |
| Avg per sample | 18.24s |

## Results

| # | NM | Judge | Winner T | Sample |
|---|----|-------|----------|--------|
|   0 | ✗ | 100.0 | T=0.8 | let us go → Yat pu. |
|   1 | ✗ | 100.0 | T=0.1 | our name is beautiful → Yata dyun se via. |
|   2 | ✗ | 100.0 | T=0.8 | he or she does not go → It ey iyt voy pe. |
|   3 | ✗ | 100.0 | T=0.8 | they were very far from here → Yit sa gla yiba bi him. |
|   4 | ✓ | 100.0 | T=0.1 | guilty → yova |

## Output Files

- `program.pkl` — Compiled GEPA program (cloudpickle)
- `examples.json` — Per-example predictions and scores
- `run_summary.json` — Machine-readable summary
- `log_dir/` — Raw GEPA optimization logs
