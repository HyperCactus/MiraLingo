# 3-Candidate Translation Eval

**Date:** 2026-05-27 15:42
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 20 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 32 workers
**Errors:** 0/20

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 25.0% (5/20) |
| Exact Match | 10.0% (2/20) |
| Avg Judge Score | 84.2/100 |

## Timing

| | |
|--|--|
| Total wall time | 162s |
| Avg per sample | 8.1s |
| Samples/sec | 0.1 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  43.0 | T=0.9 | whose book is this and whose are these books → Hota dyes hia ay hota hia dyesi? |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  88.0 | T=0.5 | do you all walk to school → Duven yet tyope bu tistam? |
|   3 | ✗ |  82.0 | T=0.5 | our teacher is good but their teacher is bad → Yata tuxut fia, ay yita tuxut fua. |
|   4 | ✗ |  83.0 | T=0.1 | this guy s house is on fire → hia twoba tam se be mag |
|   5 | ✓ | 100.0 | T=0.1 | we were → yat sa |
|   6 | ✗ |  52.0 | T=0.5 | unless they say otherwise we will be silent → Oven yit dye hyuay, yat so dola. |
|   7 | ✗ |  88.0 | T=0.1 | the teacher is good and the student is bad → ha tuxut fia ay ha tixut fua |
|   8 | ✓ |  86.0 | T=0.1 | do you know the answer → Duven et te ha dud? |
|   9 | ✗ | 100.0 | T=0.1 | justice → doyev |
|  10 | ✗ | 100.0 | T=0.1 | this teacher is very good → hia tuxut gla fia |
|  11 | ✗ |  55.0 | T=0.9 | play or get lost but do not laugh → Eku ey mepoku ab von dizeudu. |
|  12 | ✗ |  90.0 | T=0.5 | are the stars bright but the night cold → Se mari maa va moj oma? |
|  13 | ✗ |  35.0 | T=0.5 | he or she will come → it po |
|  14 | ✓ | 100.0 | T=0.5 | do → Xu! |
|  15 | ✗ | 100.0 | T=0.1 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✓ | 100.0 | T=0.5 | do they work at home → Duven yit yexe be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.1 | these persons → hia tobi |
|  19 | ✗ |  81.0 | T=0.1 | you are not my father but you know my father → Et voy se ata twed, oy et tier ata twed. |
