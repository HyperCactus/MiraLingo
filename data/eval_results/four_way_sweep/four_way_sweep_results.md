# Four-Way en→mir Eval Sweep

**Date:** 2026-05-26 18:45  
**Samples:** 100 (seed=20260526, min_words=0)  
**Direction:** en_to_mir  
**Model:** deepseek-ai/DeepSeek-V4-Flash

## Results

| Config | Grammar k | Word k | Normalized Match | Exact Match | Time |
|--------|-----------|--------|-----------------|-------------|------|
| g3_w0 | grammar_k=3 | word_k=0 | 49.0% | 0.0% | 432s (4320ms/sample) |
| g0_w0 | grammar_k=0 | word_k=0 | 31.0% | 0.0% | 216s (2162ms/sample) |
| g3_w2 | grammar_k=3 | word_k=2 | 31.0% | 0.0% | 130s (1297ms/sample) |
| g0_w2 | grammar_k=0 | word_k=2 | 31.0% | 0.0% | 109s (1089ms/sample) |

## Winner

**g3_w0** (grammar_k=3, word_k=0)  
Normalized match: 49.0%  
Exact match: 0.0%

## Analysis

See output below.
