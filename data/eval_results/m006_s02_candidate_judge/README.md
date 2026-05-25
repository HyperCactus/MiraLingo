# M006 S02 Candidate Judge Artifacts

This directory stores the bounded candidate-generation plus judge-confidence artifacts for milestone M006 slice S02.

## Purpose

S02 extends the S01 baseline from one translation attempt per example to a bounded set of candidates plus one judge decision. The goal is to keep every run inspectable by humans and agents without exposing secrets, raw stack traces, or hidden prompt material.

Use this directory to answer:

- which candidate was selected for each dev-set example
- which candidates were rejected and why
- what confidence bucket the judge assigned
- whether the example passed the S02 confidence threshold
- what raw judge output was preserved for audit
- whether a run failed during preflight, candidate generation, judge execution, or judge scoring

## Verified execution states

- Deterministic proof for this slice comes from pytest plus the runner's `--dry-run` mode.
- A real DeepInfra-backed run is credential-gated on `DEEPINFRA_API_KEY`.
- When that key is absent in live mode, the expected behavior is a preflight failure with exit code `2` and a stacktrace-free `run_summary.json` error payload before any model call begins.
- Dry-run output is for deterministic local inspection only. Do not treat it as evidence that live candidate quality improved over S01.

## Commands

### Deterministic pytest verification

```bash
PYTHONPATH=packages/translator/src python -m pytest \
  packages/translator/tests/test_s01_devset.py \
  packages/translator/tests/test_s01_baseline.py \
  packages/translator/tests/test_s02_candidate_judge.py \
  packages/translator/tests/test_s02_candidate_runner.py -q
```

### Deterministic dry-run artifact generation

Use this command to seed inspectable artifacts with no credentials and no live model calls:

```bash
PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s02_candidate_judge.py \
  --dry-run \
  --output-dir data/eval_results/m006_s02_candidate_judge
```

### Bounded live DeepInfra run

Use the same script surface for a real candidate-plus-judge run after `DEEPINFRA_API_KEY` is already present in the environment:

```bash
PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s02_candidate_judge.py \
  --output-dir data/eval_results/m006_s02_candidate_judge \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --max-examples 15 \
  --candidates-per-example 3 \
  --estimated-cost-per-call-usd 0.0
```

### Expected no-credential preflight check

This command should fail before any candidate generation or judge call when `DEEPINFRA_API_KEY` is absent:

```bash
env -u DEEPINFRA_API_KEY \
  PYTHONPATH=packages/translator/src \
  python packages/translator/scripts/run_s02_candidate_judge.py \
  --output-dir data/eval_results/m006_s02_candidate_judge \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --max-examples 15
```

Do not paste or record secret values in commands, reports, commits, or summaries.

## Preflight behavior and bounds

The runner is intentionally bounded for auditability and predictable load:

- dev-set input: `data/eval/devset_s01_bidirectional.json`
- default max examples: `15`
- checked-in dev-set size today: `12`
- default candidates per example: `3`
- safe candidate cap without explicit override: `3`
- directions required in the dev-set: both `en_to_mir` and `mir_to_en`

Preflight blocks execution when:

- `--max-examples` is below `1`
- `--candidates-per-example` is below `1`
- dev-set size exceeds the bounded `--max-examples` value without explicit override
- candidate count exceeds the safe bound without explicit override
- live mode starts without `DEEPINFRA_API_KEY`

When preflight fails from config or credentials, `run_summary.json` is still written with a short safe error summary and the script exits `2`.

## Artifact files

Canonical outputs are:

- `run_summary.json` — run-level metadata, timestamps, preflight state, direction counts, estimated calls/cost, elapsed time, and failed example counts
- `examples.json` — per-example selected and rejected candidates, judge summary, raw judge output, elapsed time, call estimates, and safe error summaries
- `latest.md` — human-readable inspection report derived from the JSON artifacts

If preflight fails before execution starts, only `run_summary.json` is guaranteed.

## Artifact schema guide

### `run_summary.json`

Expected keys for a successful run include:

- `started_at`, `completed_at`
- `dry_run`
- `model`
- `api_preflight`
- `devset_size`
- `direction_counts`
- `estimated_total_calls`
- `estimated_cost_usd`
- `total_calls`
- `elapsed_ms`
- `failed_example_count`, `failed_example_ids`
- `successful_example_count`
- `passed_example_count`, `passed_example_ids`
- `preflight`

On preflight failure, the file intentionally collapses to a short safe payload such as:

- `phase`
- `error`

### `examples.json`

Each row is expected to contain:

- `id`
- `status`
- `phase`
- `direction`
- `input`
- `expected`
- `candidate_count`
- `selected_candidate`
- `rejected_candidates`
- `judge_summary`
- `raw_judge_output`
- `elapsed_ms`
- `model`
- `estimated_calls`
- `estimated_cost_usd`
- `error`

`status` and `phase` communicate where the row ended:

- success in dry-run mode: `status="dry-run"`, `phase="dry_run"`
- success in live mode: `status="ok"`, `phase="judge_scoring"`
- candidate generator failure: `status="error"`, `phase="candidate_generation"`
- judge execution failure: `status="error"`, `phase="judge_execution"`
- malformed judge payload or scoring failure: `status="error"`, `phase="judge_scoring"`

### Selected and rejected candidate records

`selected_candidate` and each item in `rejected_candidates` preserve auditable candidate fields, including:

- `candidate_id`
- `candidate_rank`
- `candidate_count`
- `prediction`
- `source`
- `prompt_variant`
- `retrieval_rule_ids`
- `retrieval_context`
- `criteria_scores`
- `aggregate_score`
- `judge_rationale`
- `raw_candidate_output`
- `raw_judge_output`

Rejected candidates also carry `rejection_reason`.

### Judge summary fields

`judge_summary` includes:

- `selected_candidate_id`
- `confidence`
- `confidence_bucket`
- `passes_threshold`
- `rationale`
- `criteria_scores`
- `aggregate_score`
- `candidate_count`
- `rejected_candidates`
- `raw_judge_output`

## Confidence buckets and pass/fail rationale

Confidence is the judge's calibrated scalar from `0.0` to `1.0`. The implementation recomputes bucket and pass/fail from thresholds instead of trusting caller-provided values.

Current thresholds from `packages/translator/src/mirad_translator/candidate_judge.py` are:

- `high`: `confidence >= 0.85`
- `medium`: `0.60 <= confidence < 0.85`
- `low`: `confidence < 0.60`
- pass threshold: `confidence >= 0.60`

Why this matters:

- `high` means the judge is strongly confident in the selected candidate.
- `medium` still passes for S02 because the slice is proving a bounded audit surface, not yet enforcing a stricter launch bar.
- `low` fails closed and should not be treated as selection evidence for later strategy changes.
- If a live judge returns a mismatched `confidence_bucket` or `passes_threshold`, the scorer rejects that payload as malformed instead of silently trusting it.

What confidence does **not** prove:

- it does not prove the selected candidate beats the S01 baseline on user outcomes
- it does not prove retrieval quality is sufficient for production
- it does not prove the explanation is truthful beyond the preserved raw output
- it does not replace direct comparison against S01 and later S03 or S04 artifact diffs

## Expected call-count formula

Per example, the runner records:

- `estimated_calls = candidates_per_example + 1`

That is:

- one candidate-generation attempt per bounded candidate slot
- plus one judge call over the candidate set

For the default dry-run or live bounded setting of 12 examples and 3 candidates per example, the expected total is:

- `12 * (3 + 1) = 48` estimated calls

If later slices change candidate count, compare totals mechanically instead of inferring hidden work.

## Malformed judge output inspection

Malformed judge payloads are expected to fail safely and remain inspectable.

Examples include:

- missing `selected_candidate_id`
- non-numeric `criteria_scores`
- empty `rationale`
- out-of-range `confidence`
- selected candidate also listed as rejected
- candidate IDs in judge output that do not match the provided candidate set
- mismatched `confidence_bucket` or `passes_threshold`

Inspection workflow for that case:

1. Check `examples.json` for the row with `status="error"` and `phase="judge_scoring"`.
2. Read the row's `error` field for the short stacktrace-free contract failure.
3. Compare the row's preserved `raw_judge_output` against `judge_summary` expectations.
4. Use `latest.md` for a quick human-readable view, but treat `examples.json` as the exact field-level source.

## Redaction and safety constraints

- Never store API keys, Authorization headers, cookies, or raw secret values.
- Error output must stay stacktrace-free and use short summaries such as `JudgeExecutionError: judge backend unavailable`.
- Preserve compact retrieval snippets and rule IDs only; do not dump hidden prompts or unrelated corpora.
- Preserve raw judge output only insofar as it is already safe for repository storage.
- If preflight fails, do not treat stale `examples.json` or `latest.md` as proof of a live run.

## How S03 and S04 should compare against S01 and S02

S03 and S04 should treat S01 and S02 as immutable comparison surfaces over the same dev-set IDs and directions.

1. Confirm the run used the same bidirectional dev-set and bounded size.
2. Diff `run_summary.json` first for:
   - `failed_example_count` and `failed_example_ids`
   - `passed_example_count`
   - `estimated_total_calls`, `total_calls`, and `elapsed_ms`
   - direction counts and preflight configuration
3. Diff `examples.json` by example `id` for:
   - selected candidate prediction versus S01 single prediction or later S03 or S04 strategy output
   - rejected candidate reasons
   - confidence, bucket, and pass/fail state
   - aggregate score and per-criterion scores
   - retrieval rule usage and retrieval context quality
   - raw judge output shape when diagnosing malformed or surprising selections
4. Use `latest.md` for quick review, then fall back to the JSON artifacts for exact field-level comparison.
5. Treat dry-run artifacts as schema and workflow proof only; use live artifacts for any quality or strategy claims.

## Expected inspection workflow

1. Start with `latest.md` for quick run metadata and per-example scanning.
2. Open `examples.json` for exact field-level diffs, selected-versus-rejected candidate analysis, and downstream scripting.
3. Check `run_summary.json` to confirm preflight state, call estimates, elapsed time, and failure counts.
4. If `run_summary.json` only contains a preflight error, obtain credentials and rerun the documented live command instead of inferring quality from dry-run output.
