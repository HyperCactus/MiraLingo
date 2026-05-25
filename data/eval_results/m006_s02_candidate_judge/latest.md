# M006 S02 Candidate Judge Inspection Report

## Run Metadata

- started_at: 2026-05-25T07:03:57.737652+00:00
- completed_at: 2026-05-25T07:03:57.739267+00:00
- mode: dry-run
- model: deepseek-ai/DeepSeek-V4-Flash
- api_preflight: not-required
- devset_size: 12
- elapsed: 0 ms (0.00 s)
- failed_example_count: 0
- passed_example_count: 12

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
| s01-001-en-to-mir-progressive-going-home | English → Mirad | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-002-en-to-mir-comparison-vyel | English → Mirad | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-003-en-to-mir-dummy-it-negation | English → Mirad | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-004-en-to-mir-object-order | English → Mirad | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-005-en-to-mir-subordinate-whether | English → Mirad | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-006-en-to-mir-possession-book | English → Mirad | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-007-mir-to-en-locative-be-home | Mirad → English | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-008-mir-to-en-distance-bi-here | Mirad → English | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-009-mir-to-en-question-school | Mirad → English | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-010-mir-to-en-weather-dummy-it | Mirad → English | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-011-mir-to-en-subordinate-van | Mirad → English | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |
| s01-012-mir-to-en-pronoun-object-reference | Mirad → English | dry-run | dry_run | 2 | 0.91 | high | True | 0 ms |

## Detailed Examples

### s01-001-en-to-mir-progressive-going-home

- direction: English → Mirad
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-001-en-to-mir-progressive-going-home-cand-01
- selected_prediction: It peya tam.
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "fluency": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-001-en-to-mir-progressive-going-home-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-001-en-to-mir-progressive-going-home-cand-01",
  "candidate_ids": [
    "s01-001-en-to-mir-progressive-going-home-cand-01",
    "s01-001-en-to-mir-progressive-going-home-cand-03"
  ]
}
```

### s01-002-en-to-mir-comparison-vyel

- direction: English → Mirad
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-002-en-to-mir-comparison-vyel-cand-01
- selected_prediction: Ata tam se ga aga vyel etas.
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "fluency": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-002-en-to-mir-comparison-vyel-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-002-en-to-mir-comparison-vyel-cand-01",
  "candidate_ids": [
    "s01-002-en-to-mir-comparison-vyel-cand-01",
    "s01-002-en-to-mir-comparison-vyel-cand-03"
  ]
}
```

### s01-003-en-to-mir-dummy-it-negation

- direction: English → Mirad
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-003-en-to-mir-dummy-it-negation-cand-01
- selected_prediction: Voy se yeva jayevder hes.
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "fluency": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-003-en-to-mir-dummy-it-negation-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-003-en-to-mir-dummy-it-negation-cand-01",
  "candidate_ids": [
    "s01-003-en-to-mir-dummy-it-negation-cand-01",
    "s01-003-en-to-mir-dummy-it-negation-cand-03"
  ]
}
```

### s01-004-en-to-mir-object-order

- direction: English → Mirad
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-004-en-to-mir-object-order-cand-01
- selected_prediction: Buu at hua nyem.
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "fluency": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-004-en-to-mir-object-order-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-004-en-to-mir-object-order-cand-01",
  "candidate_ids": [
    "s01-004-en-to-mir-object-order-cand-01",
    "s01-004-en-to-mir-object-order-cand-03"
  ]
}
```

### s01-005-en-to-mir-subordinate-whether

- direction: English → Mirad
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-005-en-to-mir-subordinate-whether-cand-01
- selected_prediction: At voy ta ven it upo.
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "fluency": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-005-en-to-mir-subordinate-whether-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-005-en-to-mir-subordinate-whether-cand-01",
  "candidate_ids": [
    "s01-005-en-to-mir-subordinate-whether-cand-01",
    "s01-005-en-to-mir-subordinate-whether-cand-03"
  ]
}
```

### s01-006-en-to-mir-possession-book

- direction: English → Mirad
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-006-en-to-mir-possession-book-cand-01
- selected_prediction: At voy teata ita dyes.
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "fluency": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-006-en-to-mir-possession-book-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-006-en-to-mir-possession-book-cand-01",
  "candidate_ids": [
    "s01-006-en-to-mir-possession-book-cand-01",
    "s01-006-en-to-mir-possession-book-cand-03"
  ]
}
```

### s01-007-mir-to-en-locative-be-home

- direction: Mirad → English
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-007-mir-to-en-locative-be-home-cand-01
- selected_prediction: I work at home
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "literalness": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-007-mir-to-en-locative-be-home-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-007-mir-to-en-locative-be-home-cand-01",
  "candidate_ids": [
    "s01-007-mir-to-en-locative-be-home-cand-01",
    "s01-007-mir-to-en-locative-be-home-cand-03"
  ]
}
```

### s01-008-mir-to-en-distance-bi-here

- direction: Mirad → English
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-008-mir-to-en-distance-bi-here-cand-01
- selected_prediction: you were very far from here
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "literalness": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-008-mir-to-en-distance-bi-here-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-008-mir-to-en-distance-bi-here-cand-01",
  "candidate_ids": [
    "s01-008-mir-to-en-distance-bi-here-cand-01",
    "s01-008-mir-to-en-distance-bi-here-cand-03"
  ]
}
```

### s01-009-mir-to-en-question-school

- direction: Mirad → English
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-009-mir-to-en-question-school-cand-01
- selected_prediction: do you walk to school
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "literalness": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-009-mir-to-en-question-school-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-009-mir-to-en-question-school-cand-01",
  "candidate_ids": [
    "s01-009-mir-to-en-question-school-cand-01",
    "s01-009-mir-to-en-question-school-cand-03"
  ]
}
```

### s01-010-mir-to-en-weather-dummy-it

- direction: Mirad → English
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-010-mir-to-en-weather-dummy-it-cand-01
- selected_prediction: it will rain
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "literalness": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-010-mir-to-en-weather-dummy-it-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-010-mir-to-en-weather-dummy-it-cand-01",
  "candidate_ids": [
    "s01-010-mir-to-en-weather-dummy-it-cand-01",
    "s01-010-mir-to-en-weather-dummy-it-cand-03"
  ]
}
```

### s01-011-mir-to-en-subordinate-van

- direction: Mirad → English
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-011-mir-to-en-subordinate-van-cand-01
- selected_prediction: it is sad that she left
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "literalness": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-011-mir-to-en-subordinate-van-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-011-mir-to-en-subordinate-van-cand-01",
  "candidate_ids": [
    "s01-011-mir-to-en-subordinate-van-cand-01",
    "s01-011-mir-to-en-subordinate-van-cand-03"
  ]
}
```

### s01-012-mir-to-en-pronoun-object-reference

- direction: Mirad → English
- status: dry-run
- phase: dry_run
- candidate_count: 2
- confidence: 0.91
- confidence_bucket: high
- passes_threshold: True
- selected_candidate_id: s01-012-mir-to-en-pronoun-object-reference-cand-01
- selected_prediction: they did it well
- aggregate_score: 0.9566666666666667
- criteria_scores: {"semantic_fidelity": 0.98, "grammar": 0.95, "literalness": 0.94}
- judge_rationale: Dry run selected the first deterministic candidate for auditable offline inspection.
- error_summary: none

#### Rejected Candidates

- s01-012-mir-to-en-pronoun-object-reference-cand-03: Dry run retained only the first deterministic candidate.

#### Raw Judge Output

```json
{
  "mode": "dry-run",
  "selected_candidate_id": "s01-012-mir-to-en-pronoun-object-reference-cand-01",
  "candidate_ids": [
    "s01-012-mir-to-en-pronoun-object-reference-cand-01",
    "s01-012-mir-to-en-pronoun-object-reference-cand-03"
  ]
}
```
