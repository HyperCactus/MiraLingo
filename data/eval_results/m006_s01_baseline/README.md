# M006 S01 Baseline Artifacts

This directory stores the bounded baseline artifacts for milestone M006 slice S01.

## Purpose

The S01 baseline is the fixed comparison point for later model-improvement slices. Keep this directory inspectable by both humans and agents without exposing secrets or raw stack traces.

## Verified execution states

- Deterministic proof for this slice comes from pytest plus the runner's `--dry-run` mode.
- S01 is not complete unless this directory contains a real live `run_summary.json`, `examples.json`, and `latest.md` artifact set produced by the DeepInfra-backed runner surface.
- A real baseline run is credential-gated on `DEEPINFRA_API_KEY`.
- When that key is absent, the expected behavior is a preflight failure with exit code `2` and a stacktrace-free `run_summary.json` error payload before any model call begins.
- Do not treat dry-run output as the canonical live baseline; it is only a local verification aid.

## Commands

### Deterministic pytest verification

```bash
PYTHONPATH=packages/translator/src python -m pytest \
  packages/translator/tests/test_s01_devset.py \
  packages/translator/tests/test_s01_baseline.py \
  packages/translator/tests/test_evaluate.py -q
```

### Dry-run verification

Use this command for deterministic local verification with no secrets:

```bash
PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s01_baseline.py \
  --dry-run \
  --output-dir data/eval_results/m006_s01_baseline
```

### Live baseline run

Use the same script surface for a real DeepInfra-backed run after loading `.env` into the shell environment so `DEEPINFRA_API_KEY` is available to the Python process:

```bash
bash -lc 'set -a; source .env; set +a; PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s01_baseline.py \
  --output-dir data/eval_results/m006_s01_baseline \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --max-examples 15 \
  --estimated-calls-per-example 1 \
  --estimated-cost-per-call-usd 0.0'
```

Future auto-mode runs should use this exact env-loading command pattern instead of assuming exported shell state.

### Expected no-credential preflight check

This command should fail before model calls when `DEEPINFRA_API_KEY` is absent:

```bash
env -u DEEPINFRA_API_KEY \
  PYTHONPATH=packages/translator/src \
  python packages/translator/scripts/run_s01_baseline.py \
  --output-dir data/eval_results/m006_s01_baseline \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --max-examples 15
```

Do not paste or record secret values in commands, reports, commits, or summaries.

## Artifact files

Canonical live-run outputs are:

- `run_summary.json` — run-level metadata, timestamps, API preflight status, call estimates, elapsed time, and failed example counts.
- `examples.json` — per-example diagnostics including direction, input, expected output, prediction, retrieval context, rule IDs, elapsed time, failure labels, and safe error summaries.
- `latest.md` — human-readable inspection report derived from the JSON artifacts with score summaries, taxonomy legend, and detailed example sections.

When credentials are absent, only `run_summary.json` should be expected, containing the preflight failure instead of live example artifacts.

## Call, time, and cost budget

- Dev-set size is fixed at 12 bidirectional examples for S01, within the 10 to 15 example task bound.
- Default live estimate is `1` model call per example, so the expected total is `12` calls for the checked-in dev-set.
- `--max-examples 15` is the hard operator-facing ceiling for this slice; do not expand past it here.
- `--estimated-cost-per-call-usd` is intentionally operator-supplied. Leave it at `0.0` when you do not have an approved pricing input.
- Wall-clock time depends on network/model latency, but later agents should expect a short bounded run rather than an open-ended batch job.

## Redaction and safety constraints

- Never store API keys, Authorization headers, cookies, or prompt-injection payloads in these artifacts.
- Error output must stay stacktrace-free and use short summaries such as `RuntimeError: translator backend timed out`.
- Retrieval context should include compact inspectable snippets or rule IDs only; avoid dumping full hidden prompts or unrelated corpus text.
- If preflight fails, keep the failure inspectable in `run_summary.json` and avoid treating stale `examples.json` or `latest.md` as a live baseline.

## How later slices should compare against this baseline

Slices S02-S04 should treat S01 as the immutable baseline surface:

1. Re-run S01-compatible evaluation against the same bidirectional dev-set size and directions.
2. Preserve the same artifact schema so diffs are mechanical: `run_summary.json`, `examples.json`, and `latest.md`.
3. Compare at minimum:
   - normalized-match rate by direction
   - failed example count and IDs
   - retrieval rule usage and context quality
   - per-example failure labels
   - estimated total calls, elapsed time, and cost
4. Record improvements or regressions against this baseline rather than changing the baseline taxonomy retroactively.

## Expected inspection workflow

1. Start with `latest.md` for quick score and failure review when a live run completed.
2. Open `examples.json` for exact field-level diffs or downstream scripting when example artifacts exist.
3. Check `run_summary.json` to confirm preflight state, timing, call estimates, and failure counts.
4. If `run_summary.json` only contains a preflight error, obtain credentials and rerun the documented live command instead of inferring scores from dry-run output.
