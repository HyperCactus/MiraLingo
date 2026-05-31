# 3-Candidate Translation Eval

**Date:** 2026-05-27 16:53
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 20 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 8 workers
**Errors:** 0/20

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 40.0% (8/20) |
| Exact Match | 30.0% (6/20) |
| Avg Judge Score | 92.6/100 |

## Timing

| | |
|--|--|
| Total wall time | 287s |
| Avg per sample | 14.4s |
| Samples/sec | 0.1 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  91.0 | T=0.5 | whose book is this and whose are these books → Duhotas se hias ay duhotasi se hia dyesi |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ | 100.0 | T=0.9 | do you all walk to school → Duven yet tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.1 | our teacher is good but their teacher is bad → yata tuxut se fia oy yita tuxut se fua |
|   4 | ✗ | 100.0 | T=0.1 | this guy s house is on fire → Hia twoba tam se abmag. |
|   5 | ✓ | 100.0 | T=0.9 | we were → yat sa |
|   6 | ✗ |  69.0 | T=0.1 | unless they say otherwise we will be silent → Oven yit de hyuyen, yat so dola. |
|   7 | ✗ | 100.0 | T=0.1 | the teacher is good and the student is bad → tuxut se fia ay tixut se fua |
|   8 | ✓ | 100.0 | T=0.1 | do you know the answer → Duven et te ha dud? |
|   9 | ✓ | 100.0 | T=0.1 | justice → yevan |
|  10 | ✓ | 100.0 | T=0.1 | this teacher is very good → hia tuxut se gla fia |
|  11 | ✗ |  98.0 | T=0.9 | play or get lost but do not laugh → eku ey mepoku oy voy hihidu |
|  12 | ✗ |  94.0 | T=0.1 | are the stars bright but the night cold → Ha mari maa, oy ha moj oma. |
|  13 | ✓ |  25.0 | T=0.1 | he or she will come → it upo |
|  14 | ✓ | 100.0 | T=0.1 | do → Xu |
|  15 | ✗ | 100.0 | T=0.9 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✗ | 100.0 | T=0.9 | do they work at home → Du yit yexe be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka yukay |
|  18 | ✗ |  75.0 | T=0.1 | these persons → hia tobi |
|  19 | ✗ | 100.0 | T=0.5 | you are not my father but you know my father → Et voy se ata twed oy et te ata twed. |
