# Multi-Candidate Translation Eval

**Date:** 2026-05-26 23:19  
**Model:** deepseek-ai/DeepSeek-V4-Flash  
**Samples:** 3 (seed=20260526)  
**Candidates:** 2 @ [0.1, 0.7]  
**Config:** num_context_passages=3, top_k_per_word=0  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 66.7% (2/3) |
| Exact Match | 66.7% (2/3) |
| Avg Judge Score | 86.7/100 |

## Timing

| | |
|-|---|
| Total wall time | 97s |
| Avg per sample | 32.5s |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ | 100.0 | T=0.1 | you are being bad → Et se fua. |
|   0 | ✓ | 100.0 | T=0.1 | he or she will come → it upo |
|   0 | ✓ |  60.0 | T=0.1 | we would go → yat pu |
