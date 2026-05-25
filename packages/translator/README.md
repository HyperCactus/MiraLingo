# Mirad Translator

Bidirectional English↔Mirad translation using DSPy, DeepInfra DeepSeek-V4-Flash, semantic lexicon lookup, structured grammar-rule retrieval, and deterministic post-processing.

## Current Default

The default runtime translator is the current structured-retrieval system:

- model: `deepseek-ai/DeepSeek-V4-Flash` via DeepInfra
- env loading: `.env` is loaded with `python-dotenv`
- vocabulary: SQLite lexicon plus semantic English-neighbor expansion (`top_k=5`)
- grammar: ChromaDB `grammar_rules` collection built from `data/mirad-docs/nirad_grammer_rules.json`
- grammar embeddings: each atomic rule is embedded by `retrieval_tags`
- prompt context: rule ID, description, pseudocode, examples, and word equivalents
- thesaurus chunks: excluded from translator prompt context
- compiled DSPy programs: not used by default because older compiled signatures are stale until regenerated

Required env vars:

| Env Var | Default | Description |
|---|---|---|
| `DEEPINFRA_API_KEY` | — | Required for live translation |
| `DEEPINFRA_BASE_URL` | `https://api.deepinfra.com/v1/openai` | DeepInfra OpenAI-compatible API base |
| `DEEPINFRA_TRANSLATION_MODEL` | `deepseek-ai/DeepSeek-V4-Flash` | Preferred runtime model override |
| `DEEPINFRA_TEACHER_MODEL` | `deepseek-ai/DeepSeek-V4-Flash` | Fallback model setting used by older eval helpers |
| `MIRAD_EVAL_CSV` | `data/phrases/english-mirad-sentence-pairs.csv` | Evaluation dataset |

## Quick Start

```bash
pip install -e packages/translator/
```

```python
import dspy
from dotenv import load_dotenv
from mirad_translator.evaluate import _make_deepinfra_lm
from mirad_translator.translate import DefaultTranslator

load_dotenv()
dspy.settings.configure(lm=_make_deepinfra_lm())

# English → Mirad
t = DefaultTranslator(direction="en_to_mir")
result = t.forward("you do not work at home")
print(result.mirad_text)

# Mirad → English
t_en = DefaultTranslator(direction="mir_to_en")
result = t_en.forward("Et voy yexe be tam.")
print(result.english_text)
```

CLI:

```bash
mirad-translate "you do not work at home" --retrieve
mirad-translate --reverse "Et voy yexe be tam." --retrieve
mirad-translate --vocab-only "congratulated toasted"
```

API:

```bash
uvicorn mirad_translator.api:app --reload
```

## Architecture

```text
Input text
    │
    ▼
Structural analysis
    │ identifies grammar concepts + vocabulary terms
    ▼
Semantic lexicon lookup
    │ exact DB lookup + semantic English-neighbor expansion
    ▼
Structured grammar-rule retrieval
    │ ChromaDB grammar_rules; one JSON rule per retrieval unit
    │ embeddings come from retrieval_tags
    ▼
DSPy translation module
    │ DeepInfra DeepSeek-V4-Flash
    ▼
Post-processor for En→Mir
    │ deterministic high-precision cleanup
    ▼
Output + diagnostics
```

### Grammar Retrieval Contract

`packages/translator/src/mirad_translator/retrieval.py` builds the `grammar_rules` collection from `data/mirad-docs/nirad_grammer_rules.json`.

Each rule is indexed as one retrieval unit. The embedding text is the rule's `retrieval_tags`; returned metadata/context includes:

- `rule_id`
- `description`
- `pseudocode`
- `examples`
- `retrieval_tags`

Rebuild indexes:

```bash
PYTHONPATH=packages/translator/src python - <<'PY'
from mirad_translator.retrieval import build_indexes, get_chunk_counts
print('before', get_chunk_counts())
print('build', build_indexes())
print('after', get_chunk_counts())
PY
```

Expected current counts:

```text
{'grammar_rules': 88, 'thesaurus_chunks': 329}
```

The thesaurus collection remains available for experiments, but default translator prompt context excludes thesaurus chunks.

## Current Baseline

The current forward baseline going into the next iteration is the sentence-only bidirectional run:

- devset: `data/eval/devset_sentence10_each_direction_seed20260526.json`
- live artifacts: `data/eval_results/sentence10_each_direction_seed20260526_fresh/`
- analysis: `data/eval_results/sentence10_each_direction_seed20260526_fresh/ANALYSIS.md`

Filter:

- English source has at least 5 words
- Mirad source has at least 5 tokens
- 10 sampled CSV rows evaluated in both directions

Results:

| Direction | Exact match | Normalized match | Estimated true-valid accuracy |
|---|---:|---:|---:|
| English → Mirad | 1/10 | 2/10 | ~2/10 |
| Mirad → English | 0/10 | 4/10 | ~8/10 strict, ~9/10 lenient |

Takeaway:

- English→Mirad remains weak on full sentences due vocabulary obedience, morphology fusion, and predicate/word-order errors.
- Mirad→English is much stronger than CSV normalized match indicates because many outputs are valid paraphrases.

## Running Evals

Sentence-only baseline used going forward:

```bash
bash -lc 'set -a; source .env; set +a; PYTHONPATH=packages/translator/src python packages/translator/scripts/run_s01_baseline.py \
  --devset data/eval/devset_sentence10_each_direction_seed20260526.json \
  --output-dir data/eval_results/sentence10_each_direction_seed20260526_next \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --max-examples 20 \
  --estimated-calls-per-example 1 \
  --estimated-cost-per-call-usd 0.0'
```

Full deterministic regression:

```bash
PYTHONPATH=packages/translator/src python -m pytest \
  packages/translator/tests/test_s01_devset.py \
  packages/translator/tests/test_s01_baseline.py \
  packages/translator/tests/test_evaluate.py \
  packages/translator/tests/test_translate.py \
  packages/translator/tests/test_lexicon_db.py \
  packages/translator/tests/test_cli.py \
  packages/translator/tests/test_retrieval.py -q
```

## Post-Processor Rules

| Rule | Pattern | Fix | Precision |
|---|---|---|---|
| Possessive `be→bi` | `noun be [determiner]` | Replace `be` → `bi` | High |
| Comparative `ge→vyel` | `ge ADJECTIVE ge NOUN` | Replace second `ge` → `vyel` | High |
| Meta-commentary strip | `Mirad: ...`, `Translation: ...` | Remove LM framing | High |
| Whitespace normalize | Extra spaces, punctuation wrappers | Collapse/fix punctuation | Always-safe |

## Next Improvement Targets

1. Add an En→Mir validator for exact vocabulary preservation and illegal fused forms.
2. Add a Mir→En paraphrase-validity judge so normalized string match does not undercount valid translations.
3. Regenerate compiled DSPy programs only after signatures stabilize.
4. Expand the sentence-focused dev set with representative grammar failure categories.

## Directory Layout

```text
packages/translator/
├── README.md
├── src/mirad_translator/
│   ├── __init__.py
│   ├── translate.py            # DSPy modules, DefaultTranslator factory
│   ├── evaluate.py             # DeepInfra-backed eval helpers and metrics
│   ├── postprocess.py          # Deterministic post-processor
│   ├── lexicon_db.py           # SQLite/FTS5 lexicon lookup
│   ├── semantic_lexicon.py     # Semantic lexicon expansion
│   ├── retrieval.py            # Structured grammar-rule retrieval
│   └── ollama_lm.py            # Optional legacy/local experiment adapter, not default
├── tests/
└── scripts/
```
