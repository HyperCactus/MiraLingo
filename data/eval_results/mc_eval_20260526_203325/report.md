# Multi-Candidate Translation Eval

**Date:** 2026-05-26 20:49  
**Model:** deepseek-ai/DeepSeek-V4-Flash  
**Samples:** 8 (seed=20260526)  
**Candidates:** 5 @ [0.1, 0.3, 0.5, 0.7, 0.9]  
**Config:** num_context_passages=3, top_k_per_word=0  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 12.5% (1/8) |
| Exact Match | 12.5% (1/8) |
| Avg Judge Score | 81.8/100 |

## Timing

| | |
|-|---|
| Total wall time | 950s |
| Avg per sample | 118.7s |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ | 100.0 | T=0.9 | you are being bad → et sea fua |
|   0 | ✓ |  90.0 | T=0.1 | he or she will come → it upo |
|   0 | ✗ |  21.0 | T=0.5 | we would go → yat p-yu-er |
|   0 | ✗ | 100.0 | T=0.9 | you live in the neighborhood → Et teje bi ha doeym. |
|   0 | ✗ |  94.0 | T=0.1 | you all do not know → Eyt voy tere. |
|   0 | ✗ |  71.0 | T=0.5 | you all were going home but you all came here → yet sa per tambu oy yet upa him |
|   0 | ✗ |  78.0 | T=0.1 | i come from france → At upya bi Feram. |
|   0 | ✗ | 100.0 | T=0.1 | go to the store → per bu ha nam |
