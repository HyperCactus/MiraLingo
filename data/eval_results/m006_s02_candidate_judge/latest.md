# M006 S02 Candidate Judge Inspection Report

## Run Metadata

- started_at: 2026-05-25T08:24:49.857783+00:00
- completed_at: 2026-05-25T08:29:00.520671+00:00
- mode: live
- model: deepseek-ai/DeepSeek-V4-Flash
- api_preflight: ok
- devset_size: 12
- elapsed: 250663 ms (250.66 s)
- failed_example_count: 3
- passed_example_count: 8

## Preflight Call and Cost Estimate

- estimated_total_calls: 48
- estimated_cost_usd: $0.000000
- total_calls_recorded: 48
- candidates_per_example: 3
- english_to_mirad_examples: 6
- mirad_to_english_examples: 6

## Per-Example Summary

| ID | Direction | Status | Phase | Candidates | Confidence | Bucket | Passes | Elapsed |
|----|-----------|--------|-------|------------|------------|--------|--------|---------|
| s01-001-en-to-mir-progressive-going-home | English → Mirad | ok | judge_scoring | 1 | 1.00 | high | True | 17196 ms |
| s01-002-en-to-mir-comparison-vyel | English → Mirad | ok | judge_scoring | 1 | 0.98 | high | True | 29252 ms |
| s01-003-en-to-mir-dummy-it-negation | English → Mirad | ok | judge_scoring | 1 | 0.30 | low | False | 30437 ms |
| s01-004-en-to-mir-object-order | English → Mirad | ok | judge_scoring | 1 | 1.00 | high | True | 32091 ms |
| s01-005-en-to-mir-subordinate-whether | English → Mirad | error | judge_scoring | 1 | n/a | n/a | n/a | 33672 ms |
| s01-006-en-to-mir-possession-book | English → Mirad | ok | judge_scoring | 1 | 1.00 | high | True | 26923 ms |
| s01-007-mir-to-en-locative-be-home | Mirad → English | ok | judge_scoring | 1 | 0.98 | high | True | 11096 ms |
| s01-008-mir-to-en-distance-bi-here | Mirad → English | ok | judge_scoring | 1 | 1.00 | high | True | 13000 ms |
| s01-009-mir-to-en-question-school | Mirad → English | error | judge_scoring | 1 | n/a | n/a | n/a | 12649 ms |
| s01-010-mir-to-en-weather-dummy-it | Mirad → English | ok | judge_scoring | 1 | 0.98 | high | True | 11407 ms |
| s01-011-mir-to-en-subordinate-van | Mirad → English | ok | judge_scoring | 1 | 1.00 | high | True | 12109 ms |
| s01-012-mir-to-en-pronoun-object-reference | Mirad → English | error | judge_scoring | 1 | n/a | n/a | n/a | 20831 ms |

## Detailed Examples

### s01-001-en-to-mir-progressive-going-home

- direction: English → Mirad
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 1.00
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-001-en-to-mir-progressive-going-home-cand-01
- selected_prediction: It peya tam.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "fluency": 1.0}
- judge_rationale: The candidate exactly matches the expected translation and follows Mirad grammar rules correctly for a progressive past action with an animate subject.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-001-en-to-mir-progressive-going-home-cand-01",
  "confidence": "1.0",
  "rationale": "The candidate exactly matches the expected translation and follows Mirad grammar rules correctly for a progressive past action with an animate subject.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "fluency": 1.0
  },
  "rejected_candidates": []
}
```

### s01-002-en-to-mir-comparison-vyel

- direction: English → Mirad
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 0.98
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-002-en-to-mir-comparison-vyel-cand-01
- selected_prediction: ata tam se ga aga vyel etas.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "fluency": 1.0}
- judge_rationale: The candidate perfectly matches the expected translation (barring capitalization, which is not grammatically significant). It correctly conveys the comparative meaning using 'ga aga' and 'vyel', uses the correct possessive forms, and follows Mirad grammar rules. High confidence.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-002-en-to-mir-comparison-vyel-cand-01",
  "confidence": "0.98",
  "rationale": "The candidate perfectly matches the expected translation (barring capitalization, which is not grammatically significant). It correctly conveys the comparative meaning using 'ga aga' and 'vyel', uses the correct possessive forms, and follows Mirad grammar rules. High confidence.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "fluency": 1.0
  },
  "rejected_candidates": []
}
```

### s01-003-en-to-mir-dummy-it-negation

- direction: English → Mirad
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 0.30
- confidence_bucket: low
- passes_threshold: False
- selected_candidate_id: s01-003-en-to-mir-dummy-it-negation-cand-01
- selected_prediction: Jayevden heawa tob se loyeva.
- aggregate_score: 0.6333333333333333
- criteria_scores: {"semantic_fidelity": 0.4, "grammar": 0.8, "fluency": 0.7}
- judge_rationale: The candidate translates the meaning approximately but uses "heawa tob" (that person) instead of the indefinite "hes" (someone), and lacks the "Voy" negation structure, making it less semantically faithful to the source.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-003-en-to-mir-dummy-it-negation-cand-01",
  "confidence": "0.3",
  "rationale": "The candidate translates the meaning approximately but uses \"heawa tob\" (that person) instead of the indefinite \"hes\" (someone), and lacks the \"Voy\" negation structure, making it less semantically faithful to the source.",
  "criteria_scores": {
    "semantic_fidelity": 0.4,
    "grammar": 0.8,
    "fluency": 0.7
  },
  "rejected_candidates": []
}
```

### s01-004-en-to-mir-object-order

- direction: English → Mirad
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 1.00
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-004-en-to-mir-object-order-cand-01
- selected_prediction: Buu at hua nyem.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "fluency": 1.0}
- judge_rationale: The candidate exactly matches the reference translation. It correctly applies imperative form (buu), indirect-before-direct object order (at before hua nyem), and the distal demonstrative (hua).
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-004-en-to-mir-object-order-cand-01",
  "confidence": "1.0",
  "rationale": "The candidate exactly matches the reference translation. It correctly applies imperative form (buu), indirect-before-direct object order (at before hua nyem), and the distal demonstrative (hua).",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "fluency": 1.0
  },
  "rejected_candidates": []
}
```

### s01-005-en-to-mir-subordinate-whether

- direction: English → Mirad
- status: error
- phase: judge_scoring
- candidate_count: 1
- confidence: n/a
- confidence_bucket: n/a
- passes_threshold: n/a
- selected_candidate_id: none
- selected_prediction: none
- aggregate_score: n/a
- criteria_scores: {}
- judge_rationale: none
- error_summary: selected candidate cannot also be rejected

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-005-en-to-mir-subordinate-whether-cand-01",
  "confidence": "0.3",
  "rationale": "The only candidate uses incorrect negation ('o ta' instead of 'voy ta') and uses 'upu' (hypothetical) instead of 'upo' (future) as in the expected translation, resulting in poor grammar and fluency.",
  "criteria_scores": {
    "semantic_fidelity": 0.5,
    "grammar": 0.2,
    "fluency": 0.3
  },
  "rejected_candidates": [
    {
      "candidate_id": "s01-005-en-to-mir-subordinate-whether-cand-01",
      "reason": "Incorrect negation: uses 'o ta' instead of 'voy ta'. Wrong verb tense: 'upu' instead of 'upo'."
    }
  ]
}
```

### s01-006-en-to-mir-possession-book

- direction: English → Mirad
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 1.00
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-006-en-to-mir-possession-book-cand-01
- selected_prediction: At voy teata ita dyes.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "fluency": 1.0}
- judge_rationale: The single candidate translation exactly matches the expected reference translation, correctly rendering the English negation, past tense, gender-neutral possessive, and noun into fluent Mirad.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-006-en-to-mir-possession-book-cand-01",
  "confidence": "1.0",
  "rationale": "The single candidate translation exactly matches the expected reference translation, correctly rendering the English negation, past tense, gender-neutral possessive, and noun into fluent Mirad.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "fluency": 1.0
  },
  "rejected_candidates": []
}
```

### s01-007-mir-to-en-locative-be-home

- direction: Mirad → English
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 0.98
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-007-mir-to-en-locative-be-home-cand-01
- selected_prediction: I work at home.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "literalness": 1.0}
- judge_rationale: The single candidate perfectly matches the reference translation "I work at home." It is semantically faithful, grammatically correct, and literal.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-007-mir-to-en-locative-be-home-cand-01",
  "confidence": "0.98",
  "rationale": "The single candidate perfectly matches the reference translation \"I work at home.\" It is semantically faithful, grammatically correct, and literal.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "literalness": 1.0
  },
  "rejected_candidates": []
}
```

### s01-008-mir-to-en-distance-bi-here

- direction: Mirad → English
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 1.00
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-008-mir-to-en-distance-bi-here-cand-01
- selected_prediction: You were very far from here.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "literalness": 1.0}
- judge_rationale: The single candidate is identical to the expected translation, showing perfect semantic fidelity, grammar, and literalness.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-008-mir-to-en-distance-bi-here-cand-01",
  "confidence": "1.0",
  "rationale": "The single candidate is identical to the expected translation, showing perfect semantic fidelity, grammar, and literalness.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "literalness": 1.0
  },
  "rejected_candidates": []
}
```

### s01-009-mir-to-en-question-school

- direction: Mirad → English
- status: error
- phase: judge_scoring
- candidate_count: 1
- confidence: n/a
- confidence_bucket: n/a
- passes_threshold: n/a
- selected_candidate_id: none
- selected_prediction: none
- aggregate_score: n/a
- criteria_scores: {}
- judge_rationale: none
- error_summary: criteria_scores.semantic_fidelity must be between 0 and 1

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-009-mir-to-en-question-school-cand-01",
  "confidence": "0.98",
  "rationale": "The candidate translation is semantically faithful, grammatically correct English, and literal to the source.",
  "criteria_scores": {
    "semantic_fidelity": 3,
    "grammar": 3,
    "literalness": 3
  },
  "rejected_candidates": []
}
```

### s01-010-mir-to-en-weather-dummy-it

- direction: Mirad → English
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 0.98
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-010-mir-to-en-weather-dummy-it-cand-01
- selected_prediction: It will rain.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "literalness": 1.0}
- judge_rationale: The sole candidate "It will rain." is a perfect match for the source "Mamilo." and the expected translation, showing correct future tense interpretation and literal accuracy.
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-010-mir-to-en-weather-dummy-it-cand-01",
  "confidence": "0.98",
  "rationale": "The sole candidate \"It will rain.\" is a perfect match for the source \"Mamilo.\" and the expected translation, showing correct future tense interpretation and literal accuracy.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "literalness": 1.0
  },
  "rejected_candidates": []
}
```

### s01-011-mir-to-en-subordinate-van

- direction: Mirad → English
- status: ok
- phase: judge_scoring
- candidate_count: 1
- confidence: 1.00
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-011-mir-to-en-subordinate-van-cand-01
- selected_prediction: It is sad that she left.
- aggregate_score: 1.0
- criteria_scores: {"semantic_fidelity": 1.0, "grammar": 1.0, "literalness": 1.0}
- judge_rationale: The single candidate is an exact match to the reference translation, correctly applying all relevant Mirad grammar rules (subordinate van, verb past tense suffix, optional feminine pronoun).
- error_summary: none

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-011-mir-to-en-subordinate-van-cand-01",
  "confidence": "1.0",
  "rationale": "The single candidate is an exact match to the reference translation, correctly applying all relevant Mirad grammar rules (subordinate van, verb past tense suffix, optional feminine pronoun).",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "literalness": 1.0
  },
  "rejected_candidates": []
}
```

### s01-012-mir-to-en-pronoun-object-reference

- direction: Mirad → English
- status: error
- phase: judge_scoring
- candidate_count: 1
- confidence: n/a
- confidence_bucket: n/a
- passes_threshold: n/a
- selected_candidate_id: none
- selected_prediction: none
- aggregate_score: n/a
- criteria_scores: {}
- judge_rationale: none
- error_summary: selected candidate cannot also be rejected

#### Rejected Candidates

None.

#### Raw Judge Output

```json
{
  "selected_candidate_id": "s01-012-mir-to-en-pronoun-object-reference-cand-01",
  "confidence": "0.95",
  "rationale": "The candidate translation is accurate, grammatically correct, fluent, and literally mirrors the source structure, making it the best and only choice.",
  "criteria_scores": {
    "semantic_fidelity": 1.0,
    "grammar": 1.0,
    "literalness": 1.0
  },
  "rejected_candidates": [
    {
      "candidate_id": "s01-012-mir-to-en-pronoun-object-reference-cand-01",
      "reason": "Not rejected; this is the only candidate and it is correct."
    }
  ]
}
```
