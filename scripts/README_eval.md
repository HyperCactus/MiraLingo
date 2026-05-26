# Unified Evaluation Framework

## Data Splits

Created by `split_eval_data.py`:
- **693 train pairs** → `data/eval/train.json`
- **148 val pairs**   → `data/eval/val.json`
- **149 test pairs**  → `data/eval/test.json`

Format: `{"metadata": {...}, "pairs": [{"id": "pair-0001", "source": "english", "target": "mirad"}, ...]}`

---

## Running Evaluation

### Quick start (CLI flags)

```bash
python scripts/run_evaluation.py \
  --data data/eval/test.json \
  --direction en_to_mir \
  --n 30 \
  --parallel 8 \
  --metrics normalized_match word_overlap
```

### With a config file

```bash
# Copy and edit the config
cp scripts/eval_config.yaml my_eval.yaml
# Edit my_eval.yaml with your settings
python scripts/run_evaluation.py --config my_eval.yaml
```

Config file (`scripts/eval_config.yaml`) covers:
- **Model** — provider, name, API key env var, base URL, timeout
- **Data** — file path, direction, min-english-words filter, sample count, seed
- **Translator** — type, DB path, num_context_passages, semantic lexicon params
- **Evaluation** — parallelism, metrics list
- **Output** — out_dir, overwrite flag

CLI flags override config file values.

---

## Key Features

- **Parallel execution** — configurable 1–16 concurrent workers
- **Per-example context** — each sample saves: word_equivalents, context_passages, used_rule_ids, elapsed_ms, per-metric scores
- **Separation of concerns** — `translator_adapter.py` wraps all translator logic; the eval script is translator-agnostic
- **Multiple metrics** — normalized_match, word_overlap (precision/recall/F1), semantic_similarity
- **Timing breakdown** — total eval duration, per-sample timing, model call time

---

## Output Files

Each run writes three files to `data/eval_results/<run_id>/`:

| File | Description |
|------|-------------|
| `examples.json` | Array of per-example results. Each has source, gold, pred, scores, timing, context_passages, word_equivalents |
| `run_summary.json` | Aggregated metrics, timing stats, counts |
| `report.md` | Human-readable summary table + all results |

---

## Adding a New Translator Type

1. Subclass `TranslatorAdapter` in `translator_adapter.py`
2. Register it in `_ADAPTERS` dict
3. Set `translator.type: "your_class_name"` in config (or use `--translator-type` CLI flag)

Or provide a Python import path:
```yaml
translator:
  type: "mypackage.translator.MyCustomAdapter"
```