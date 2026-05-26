# Translation Evaluation Report

**Date:** 2026-05-26T15:33:53.468180 | **Model:** unknown
**Direction:** en_to_mir | **Samples:** 8
**Data:** data/eval/test.json
**Parallelism:** 8 workers

## Metrics Summary

| Metric | Score | Count |
|---|---|---|
| Normalized Match | 25.0% | 2/8 |
| Word Overlap F1 | 57.9% | 3/8 (≥0.7) |
| Avg Time/Sample | 45706ms | — |

## All Results

| # | Source | Gold | Predicted | Score | Time |
|---|---|---|---|---|---|
| 0 | i am going home | at peye tam | At pye tampeye | ✗ | 44499ms |
| 1 | while we are here we will work at home | je van yat so him yat yex | Je van yat se him, yat ya | ✗ | 43744ms |
| 2 | this building was a store | hia tom sa nam | Hia tom sa nam. | ✓ | 35977ms |
| 3 | our books | yata dyesi | ayeta dravesi | ✗ | 49700ms |
| 4 | do we work at a grocery store near here  | duven yat yexe be tolnam  | Duven yat yex be telnam y | ✗ | 62711ms |
| 5 | i will be | at so | At so | ✓ | 37302ms |
| 6 | do not be late | von et jwosu | Von jwo. | ✗ | 40586ms |
| 7 | he or she knows | it te | it ter | ✗ | 51132ms |