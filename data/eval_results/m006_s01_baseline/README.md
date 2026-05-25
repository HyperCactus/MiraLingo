# M006 S01 Baseline Artifacts

This directory stores the bounded baseline artifacts for milestone M006 slice S01.

## Purpose

The S01 baseline is the fixed comparison point for later model-improvement slices. Keep this directory inspectable by both humans and agents without exposing secrets or raw stack traces.

## Commands

### Dry-run verification

Use this command for deterministic local verification with no secrets:

```bash
PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s01_baseline.py \
  --dry-run \
  --output-dir data/eval_results/m006_s01_baseline
```

### Live baseline run

Use the same script surface for a real DeepInfra-backed run after `DEEPINFRA_API_KEY` is already present in the environment:

```bash
PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s01_baseline.py \
  --output-dir data/eval_results/m006_s01_baseline \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --estimated-calls-per-example 1 \
  --estimated-cost-per-call-usd 0.0
```

Do not paste or record secret values in commands, reports, commits, or summaries.

## Artifact files

- `run_summary.json` — run-level metadata, timestamps, API preflight status, call estimates, elapsed time, and failed example counts.
- `examples.json` — per-example diagnostics including direction, input, expected output, prediction, retrieval context, rule IDs, elapsed time, failure labels, and safe error summaries.
- `latest.md` — human-readable inspection report derived from the JSON artifacts with score summaries, taxonomy legend, and detailed example sections.

## Redaction and safety constraints

- Never store API keys, Authorization headers, cookies, or prompt-injection payloads in these artifacts.
- Error output must stay stacktrace-free and use short summaries such as `RuntimeError: translator backend timed out`.
- Retrieval context should include compact inspectable snippets or rule IDs only; avoid dumping full hidden prompts or unrelated corpus text.
- If preflight fails, keep the failure inspectable in `run_summary.json` and avoid writing partial Markdown.

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

1. Start with `latest.md` for quick score and failure review.
2. Open `examples.json` for exact field-level diffs or downstream scripting.
3. Check `run_summary.json` to confirm preflight state, timing, call estimates, and failure counts.
