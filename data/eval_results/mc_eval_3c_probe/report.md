# 3-Candidate Translation Eval

**Date:** 2026-05-27 09:49
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 5 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 16 workers
**Errors:** 0/5

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 40.0% (2/5) |
| Exact Match | 20.0% (1/5) |
| Avg Judge Score | 91.0/100 |

## Timing

| | |
|--|--|
| Total wall time | 195s |
| Avg per sample | 39.1s |
| Samples/sec | 0.0 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  61.0 | T=0.9 | whose book is this and whose are these books → Duhota dyes hias ay duhota dyesi hiasi? |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  98.0 | T=0.5 | do you all walk to school → Duven yet tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.9 | our teacher is good but their teacher is bad → Yata tuxut se fia oy yita tuxut se fua. |
|   4 | ✗ |  96.0 | T=0.9 | this guy s house is on fire → Hia twoba tam se magsea. |
