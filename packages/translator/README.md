# Mirad Translator

Bidirectional English↔Mirad translation using local LLMs with DSPy optimization, RAG retrieval from Mirad reference documents, and a deterministic post-processor for systematic errors.

## The Data Problem

Mirad is a low-resource constructed language — there is no large parallel corpus of English–Mirad translation pairs. The available reference material consists of grammar guides, a lexicon, and a thesaurus (all sourced from Wikibooks), totalling a few hundred annotated sentence pairs at best.

This scarcity is the central challenge for the translator. Raw LLM output on Mirad is poor because models have seen very little Mirad text during pre-training. The project addresses this through:

1. **RAG retrieval** — ChromaDB stores chunked excerpts from the Mirad grammar, lexicon, and thesaurus. At inference time, relevant passages are retrieved and injected into the prompt as context, giving the LLM the reference material it needs to translate accurately.
2. **Few-shot bootstrapping (DSPy)** — BootstrapFewShot optimization selects the most effective demonstration pairs and compiles them into the prompt, improving accuracy from ~56% (zero-shot) to ~70% on the dev set.
3. **Deterministic post-processing** — known systematic LLM errors (possessive `be`/`bi` confusion, comparative `ge`/`vyel` mixing, meta-commentary wrappers) are corrected by rule before output reaches the user.
4. **LLM-assisted data generation** — future work: use the RAG pipeline itself to generate additional training pairs from reference documents, expanding the evaluation and fine-tuning datasets beyond manual annotation.

The goal is to bootstrap from sparse reference documents into a high-quality translator without requiring a large hand-annotated corpus.

---

## Quick Start

```python
from mirad_translator.translate import DefaultTranslator

# English → Mirad
t = DefaultTranslator(num_context_passages=0)
result = t.forward("Hello, how are you?")
print(result.mirad_text)

# Mirad → English
t_en = DefaultTranslator(direction="mir_to_en", num_context_passages=0)
result = t_en.forward("At fia se.")
print(result.english_text)
```

Or the high-level entry point:

```python
from mirad_translator.translate import translate_with_lookup

mirad, word_eq, context = translate_with_lookup("The house is beautiful.", top_k=0)
```

## Installation

```bash
pip install -e packages/translator/
```

---

## Current Accuracy

| Configuration | Normalized Match | Notes |
|--------------|-----------------|-------|
| Zero-shot (DeepSeek-V4-Flash) | 56.4% | Baseline |
| LabeledFewShot k=5 | 56.4% | Marginal improvement |
| **BFS d8_l16_r2 + post-processor (dev)** | **70.0%** | Best dev score |
| **BFS d8_l16_r2 + post-processor (full eval)** | **66.7%** | Best eval score |

**Target: 90% accuracy.** The remaining 23 pp gap requires more training data, fine-tuning, or extended RAG coverage — see [Gap Analysis](#gap-analysis).

---

## How It Works

### Architecture

```
Input text
    │
    ▼
┌──────────────────┐
│  Lexicon DB      │  SQLite + FTS5 for exact word lookups
│  (word-level)    │  ↓ top-k matches
└──────────────────┘
    │
    ▼
┌──────────────────┐
│  ChromaDB RAG    │  Grammar + thesaurus passages
│  (passage-level) │  ↓ num_context_passages retrieved
└──────────────────┘
    │
    ▼
┌──────────────────┐
│  LLM (DSPy)      │  Few-shot prompt with retrieved context
│  generate        │  ↓ raw Mirad/English text
└──────────────────┘
    │
    ▼
┌──────────────────┐
│  Post-processor  │  Deterministic corrections (possessives,
│  (rule-based)    │  comparatives, punctuation normalization)
└──────────────────┘
    │
    ▼
  Output
```

### Post-Processor Rules

| Rule | Pattern | Fix | Precision |
|------|---------|-----|-----------|
| A1: Possessive be→bi | `noun be [determiner]` | Replace `be` → `bi` | High |
| A2: Comparative ge→vyel | `ge ADJECTIVE ge NOUN` | Replace second `ge` → `vyel` | High |
| Meta-commentary strip | `Mirad: ...`, `Translation: ...` | Remove LM framing | High |
| Whitespace normalize | Extra spaces, `!./!`, `word.!"` | Collapse/fix punctuation | Always-safe |

Conservative flags only — structural/hallucination errors are not auto-corrected.

---

## Model Comparison

Evaluated on 39 held-out sentence pairs (normalized match, DeepSeek-V4-Flash via DeepInfra):

| Model | Normalized Match | Notes |
|-------|-----------------|-------|
| **DeepSeek-V4-Flash** | **56.4%** | Best overall; used for optimization |
| DeepSeek-V4-Pro | 53.8% | Slightly worse |
| Gemini-2.5-Flash | 48.7% | Mid-range |
| Qwen3.6-35B-A3B | 48.7% | Competitive mid-range |
| GPT-OSS-120B | 33.3% | Underperforms |
| GPT-OSS-20B | 28.2% | Too small |
| Gemma-4-26B-A4B | 28.2% | Poor |

---

## Gap Analysis

**23.3 pp short of 90% target.** Cannot be closed with DSPy bootstrapping alone on 44 training pairs.

| Pathway | Expected Gain | Approach |
|---------|--------------|----------|
| Scale gold training data | +5–15 pp | 200+ annotated pairs via LLM-assisted generation + human review |
| LoRA fine-tuning | +10–20 pp | Fine-tune Qwen2.5-1.5B/4B on augmented data |
| Hybrid symbolic-neural | +5–10 pp | Grammar-constrained decoding, n-gram blocklist for hallucinations |
| Faster optimization model | Unlocks BFSRS | Use local qwen3.5:4b for sweeps, deploy best config on DeepSeek |

### Deferred: HuggingFace Dataset Upload

Blocked until accuracy reaches ≥90%. Current output would introduce systematic errors into downstream consumers.

---

## Running Evals

### Baseline eval (Ollama, local)

```bash
PYTHONPATH=packages/translator/src python -c "
from mirad_translator.evaluate import run_baseline_eval
run_baseline_eval(model='qwen3.5:4b', metric_name='normalized_match', num_threads=4)
"
```

### LabeledFewShot with DeepSeek-V4-Flash (DeepInfra)

```bash
PYTHONPATH=packages/translator/src python -c "
from mirad_translator.evaluate import run_labeled_fewshot_eval
run_labeled_fewshot_eval(
    model='deepseek-ai/DeepSeek-V4-Flash',
    num_fewshot=5,
    num_threads=1,
    lm_type='deepinfra',
)
"
```

### BFS parameter sweep

```bash
PYTHONPATH=packages/translator/src python scripts/run_bfs_sweep.py
```

Results saved to `data/eval_results/bootstrap_sweep/sweep_summary.csv`.

### Mir→En baseline

```bash
PYTHONPATH=packages/translator/src python -c "
from mirad_translator.evaluate import run_mir_to_en_baseline_eval
run_mir_to_en_baseline_eval(
    model='deepseek-ai/DeepSeek-V4-Flash',
    num_fewshot=5,
    num_context_passages=5,
    lm_type='deepinfra',
)
"
```

---

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `DEEPINFRA_API_KEY` | — | Required for DeepInfra API access |
| `DEEPINFRA_BASE_URL` | `https://api.deepinfra.com/v1/openai` | DeepInfra API base |
| `MIRAD_EVAL_CSV` | `data/phrases/english-mirad-sentence-pairs.csv` | Evaluation dataset |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |

---

## Directory Layout

```
packages/translator/
├── README.md
├── src/mirad_translator/
│   ├── __init__.py             # Public API exports
│   ├── translate.py            # DSPy modules, DefaultTranslator factory
│   ├── evaluate.py             # DSPy Evaluate, metrics, optimizers
│   ├── postprocess.py          # Deterministic post-processor
│   ├── lexicon_db.py           # SQLite/FTS5 lexicon lookup
│   ├── retrieval.py            # ChromaDB grammar + thesaurus retrieval
│   └── ollama_lm.py            # OllamaLM adapter for DSPy
├── tests/
│   ├── test_translate.py
│   ├── test_evaluate.py
│   └── test_postprocess.py
└── scripts/
    ├── run_bfs_sweep.py
    ├── deepseek_multihop_eval.py
    ├── deepseek_critique_eval.py
    └── deepinfra_model_eval.py
```

---

## Docker

```bash
docker compose up -d ollama
```

See [root README](../../README.md) for full Docker setup.