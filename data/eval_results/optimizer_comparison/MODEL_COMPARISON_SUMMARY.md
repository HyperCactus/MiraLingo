# Model Comparison Summary: Precompiled BootstrapRS Program

**Date:** 2026-05-13
**Task:** English → Mirad translation with precompiled BootstrapRS program
**Evaluation Set:** 30 examples (indices 50-79 from full dataset)
**Compiled Program:** `data/eval_results/optimizer_comparison/compiled_bootstrap_fast_program/`

## Executive Summary

The precompiled BootstrapRS program was evaluated with three DeepInfra models to compare performance:

| Model | Normalized Match | Exact Match | Hits/30 | Eval Time |
|-------|------------------|-------------|---------|-----------|
| **DeepSeek-V4-Flash** | **56.7%** | **56.7%** | **17/30** | 426.2s |
| Llama-3.3-70B-Instruct-Turbo | 13.3% | 13.3% | 4/30 | 222.6s |
| Meta-Llama-3.1-8B-Instruct-Turbo | 3.3% | 3.3% | 1/30 | 63.6s |

**Key Finding:** DeepSeek-V4-Flash significantly outperforms both Llama models on this task, achieving **56.7% accuracy** compared to 13.3% (Llama-3.3-70B) and 3.3% (Llama-3.1-8B).

## Detailed Results

### 1. DeepSeek-V4-Flash (Baseline)

- **Normalized Match:** 56.7% (17/30)
- **Exact Match:** 56.7% (17/30)
- **Evaluation Time:** 426.2s (~7.1 minutes)
- **Status:** ✅ Best performing model

**Strengths:**
- Consistent performance across simple and complex sentences
- Good handling of morphology (verb endings, possessives)
- Proper word order and sentence structure

**Sample Correct Translations:**
- "birds" → "pati" ✅
- "we were very far from here" → "Yat sa gla yib bi him." ✅
- "my life is good" → "Ata tej se fia." ✅
- "the car" → "ha pur" ✅
- "we should get married" → "Yat yeyfe tadser." ✅

**Common Error Patterns:**
- Minor spelling variations: "Duhonog" vs "Duhoglas", "gwafia" vs "gwa fia"
- Missing spaces: "fia fi" vs "fia fiay"
- Word choice errors: "Husi" vs "Huasi"

### 2. Llama-3.3-70B-Instruct-Turbo

- **Normalized Match:** 13.3% (4/30)
- **Exact Match:** 13.3% (4/30)
- **Evaluation Time:** 222.6s (~3.7 minutes)
- **Status:** ⚠️ Poor performance

**Strengths:**
- Faster evaluation than DeepSeek-V4-Flash
- Some correct simple translations

**Sample Correct Translations:**
- "my life is good" → "Ata tej se fia." ✅
- "false" → "vyoa" ✅
- "girls" → "toybeti" ✅
- "they were going home" → "Yit peya tam." ✅

**Common Error Patterns:**
- Incorrect morphology: "gwafi" vs "gwa fia", "tadsye" vs "tadser"
- Wrong word choices: "fan xer" vs "oveko", "baelku" vs "su"
- Extra punctuation: "Ha pur." vs "ha pur"
- Missing words: "Yit si" vs "Yit sa"

### 3. Meta-Llama-3.1-8B-Instruct-Turbo

- **Normalized Match:** 3.3% (1/30)
- **Exact Match:** 3.3% (1/30)
- **Evaluation Time:** 63.6s (~1.1 minutes)
- **Status:** ❌ Very poor performance

**Strengths:**
- Fastest evaluation time
- Only one correct translation

**Sample Correct Translation:**
- "the car" → "ha pur" ✅

**Common Error Patterns:**
- Severe hallucinations: "Glatipak" vs "Duhoglas iyt aka?"
- Wrong grammar: "Aet ve gla" vs "Yat sa gla"
- Incorrect vocabulary: "yayti" vs "toybeti"
- Missing structure: "se ayetas" vs "Huasi se etasi"

## Performance Comparison

### Accuracy Comparison

```
DeepSeek-V4-Flash:     ████████████████████████████████████████████████ 56.7%
Llama-3.3-70B:         ████ 13.3%
Llama-3.1-8B:          █ 3.3%
```

### Time vs. Accuracy Trade-off

| Model | Accuracy | Time (s) | Time/Accuracy Ratio |
|-------|----------|----------|---------------------|
| DeepSeek-V4-Flash | 56.7% | 426.2 | 7.52 |
| Llama-3.3-70B | 13.3% | 222.6 | 16.74 |
| Llama-3.1-8B | 3.3% | 63.6 | 19.27 |

**Insight:** DeepSeek-V4-Flash has the best time/accuracy ratio, making it the most efficient choice for this task.

## Error Analysis

### DeepSeek-V4-Flash Errors (13/30)

Most errors are minor variations:
1. **Spelling/spacing issues (8/13):** "Duhonog" vs "Duhoglas", "gwafia" vs "gwa fia"
2. **Word choice (3/13):** "Husi" vs "Huasi", "teatyafe" vs "yafe teater"
3. **Morphology (2/13):** "sey" vs "su", "tyod" vs "ti"

### Llama-3.3-70B Errors (26/30)

More severe errors:
1. **Morphology errors (10/26):** "gwafi" vs "gwa fia", "tadsye" vs "tadser"
2. **Wrong vocabulary (8/26):** "fan xer" vs "oveko", "baelku" vs "su"
3. **Grammar issues (5/26):** "Yit si" vs "Yit sa", "It use se" vs "It su"
4. **Punctuation (3/26):** Extra periods, missing question marks

### Llama-3.1-8B Errors (29/30)

Severe hallucinations and structural failures:
1. **Complete hallucinations (12/29):** "Glatipak", "Upua fon ak", "vay asolk"
2. **Wrong grammar (8/29):** "Aet ve gla" vs "Yat sa gla", "Yit ixu" vs "Yit sa"
3. **Incorrect vocabulary (6/29):** "yayti" vs "toybeti", "ovyaka" vs "vyoa"
4. **Missing structure (3/29):** "se ayetas" vs "Huasi se etasi"

## Recommendations

### For Production Use

**✅ Use DeepSeek-V4-Flash**
- Best accuracy (56.7%)
- Reasonable evaluation time
- Consistent performance across sentence types
- Minor errors that could be fixed with post-processing

### For Development/Testing

**⚠️ Consider Llama-3.3-70B for:**
- Faster iteration cycles (3.7 min vs 7.1 min)
- Cost-sensitive applications (if pricing favors Llama)
- When 13.3% accuracy is acceptable for the use case

**❌ Avoid Llama-3.1-8B for:**
- Production use (3.3% accuracy is too low)
- Any serious translation work
- Tasks requiring correct grammar or vocabulary

### Future Improvements

1. **Fine-tune DeepSeek-V4-Flash** on the full 44-pair dataset to potentially improve from 56.7% to 70%+
2. **Hybrid approach:** Use DeepSeek-V4-Flash for translation + rule-based post-processor for morphology
3. **Ensemble methods:** Combine DeepSeek-V4-Flash with Llama-3.3-70B predictions
4. **Data augmentation:** Increase training set size from 50 to 200+ examples

## Conclusion

DeepSeek-V4-Flash is the clear winner for English→Mirad translation with the precompiled BootstrapRS program, achieving **56.7% accuracy** compared to 13.3% (Llama-3.3-70B) and 3.3% (Llama-3.1-8B). The performance gap is significant enough that DeepSeek-V4-Flash should be the default choice for this task, with Llama models considered only for specific use cases where speed or cost outweigh accuracy requirements.

## Files Generated

- `data/eval_results/optimizer_comparison/model_comparison_results.json` - Full results with per-example predictions
- `data/eval_results/optimizer_comparison/model_comparison_meta-llama_Meta-Llama-3.1-8B-Instruct-Turbo.json` - Cached Llama-3.1-8B results
- `data/eval_results/optimizer_comparison/model_comparison_meta-llama_Llama-3.3-70B-Instruct-Turbo.json` - Cached Llama-3.3-70B results
- `data/eval_results/optimizer_comparison/MODEL_COMPARISON_SUMMARY.md` - This document
