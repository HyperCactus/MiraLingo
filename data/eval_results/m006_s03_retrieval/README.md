# M006 S03 Retrieval Comparison Artifacts

This directory stores bounded before/after retrieval comparison artifacts for the S01 bidirectional dev-set.

## Runner

```bash
PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s03_retrieval_eval.py --dry-run
```

Live mode requires `DEEPINFRA_API_KEY` and refuses unbounded runs unless `--max-examples` is explicitly raised above the default bounded limit.

## Outputs

- `run_summary.json` — preflight state, estimated calls, strategy config, delta counts, elapsed timing, and safe failure summaries
- `examples.json` — per-example baseline/improved predictions, retrieval payloads, rule IDs, selected examples, match booleans, and delta classifications
- `latest.md` — human-readable comparison report derived from the JSON artifacts

## Comparison Semantics

Each example row records:

- baseline vs improved prediction
- exact + normalized match booleans for both sides
- `delta_classification`: `improved`, `regressed`, `pass`, `fail`, `held`, or `error`
- `taxonomy_focus`, `direction`, `selected_examples`, and `retrieval_rule_ids`
- stacktrace-free `error` fields for preflight or per-example failures

## Dry Run

Dry-run mode is deterministic and offline-safe. It emits synthetic baseline/improved predictions and retrieval payloads so tests can verify schema, delta accounting, and artifact rendering without network access.
