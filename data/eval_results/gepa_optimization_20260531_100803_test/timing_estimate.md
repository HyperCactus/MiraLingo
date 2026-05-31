# GEPA Full-Run Timing Estimate

**Generated:** 2026-06-01 00:00 UTC  
**Based on test run:** 3 samples, 5525.8s compile, 3138.3s eval

---

## Timing Extrapolation

| Phase | Test (3 samples) | Full (100 samples) |
|-------|------------------|--------------------|
| Compile | 5526s (92.1 min) | ~5526s (92.1 min) |
| Eval | 3138s (52.3 min) | ~7300s (121.7 min) |
| **Total** | **8664s** | **~12826s (~213.8 min)** |

---

## Caveats

- Compile estimate now uses observed compile time from the successful resumed GEPA completion, not the later 0.0s checkpoint-resume path.
- Eval estimate still uses the script's simple per-sample heuristic and should be treated as approximate.
- Cost accounting remains approximate and LLM call counts in run_summary are known to under-report actual calls.
