# Mirad Translator

Bidirectional translation between Mirad and English using local LLM inference via Ollama, with DSPy optimization and a deterministic post-processor for known systematic errors.

## Status

**Operational.** En→Mir accuracy: ~66.7% (BootstrapFewShot + post-processor, 39 eval pairs). The 90% accuracy target requires more training data or a fine-tuned model — see [Gap Analysis](#gap-analysis) below.

## Quick Start

```python
from mirad_translator.translate import DefaultTranslator

# English → Mirad (with post-processing by default)
t = DefaultTranslator(num_context_passages=0)
mirad_text = t.forward("Hello, how are you?")
print(mirad_text.mirad_text)

# Mirad → English
t_en = DefaultTranslator(direction="mir_to_en", num_context_passages=0)
english_text = t_en.forward("At fia se.")
print(english_text.english_text)
```

Or use the high-level entry point:

```python
from mirad_translator.translate import translate_with_lookup

mirad, word_eq, context = translate_with_lookup(
    "The house is beautiful.",
    top_k=0,
)
```

## Installation

```bash
pip install -e packages/translator/
```

## Model Comparison

Evaluated on 39 held-out sentence pairs (normalized match metric, DeepSeek-V4-Flash via DeepInfra API):

| Model | Normalized Match | Notes |
|-------|----------------|-------|
| **DeepSeek-V4-Flash** | **56.4%** | Best overall; used for optimization |
| DeepSeek-V4-Pro | 53.8% | Slightly worse than Flash |
| Gemini-2.5-Flash | 48.7% | Mid-range |
| Qwen3.6-35B-A3B | 48.7% | Competitive mid-range |
| GPT-OSS-120B | 33.3% | Open-weights but underperforms |
| GPT-OSS-20B | 28.2% | Too small for this task |
| Gemma-4-26B-A4B | 28.2% | Poor performance |

**Winner:** DeepSeek-V4-Flash at 56.4% normalized match. Ollama-local models (qwen3.5:4b) serve as fast fallback for development but have lower accuracy.

## BFS Parameter Sweep Results

BootstrapFewShot (BFS) optimization was sweep-tested across 6 configurations on the 44-pair dataset (train split: first 5 examples):

| Config | max_bootstrapped_demos | max_labeled_demos | max_rounds | Dev Normalized |
|--------|------------------------|-------------------|------------|----------------|
| d2_l4_r1 | 2 | 4 | 1 | 65.0% |
| **d8_l16_r2** | **8** | **16** | **2** | **70.0%** |
| d4_l8_r1 | 4 | 8 | 1 | 65.0% |
| d4_l8_r3 | 4 | 8 | 3 | 67.5% |
| d4_l16_r1 | 4 | 16 | 1 | 65.0% |
| d2_l8_t50 | 2 | 8 | 1 | 62.5% |

**Best configuration:** `d8_l16_r2` (max_bootstrapped_demos=8, max_labeled_demos=16, max_rounds=2)

BootstrapFewShotWithRandomSearch (BFSRS) was also attempted but timed out (>600s) due to DeepSeek-V4-Flash's 3-5s/call latency. The best BFS config (70.0% on dev) was confirmed as the practical ceiling for this dataset size.

## Post-Processor Rules

The `postprocess_mirad()` function applies deterministic corrections to raw LM output:

| Rule | Pattern | Fix | Precision |
|------|---------|-----|-----------|
| A1: Possessive be→bi | `noun be [determiner]` | Replace `be` → `bi` | High — only fires when `next_word` ends in -a |
| A2: Comparative ge→vyel | `ge ADJECTIVE ge NOUN` | Replace second `ge` → `vyel` | High — blacklists function words before `ge` |
| Meta-commentary strip | `Mirad: ...`, `Translation: ...`, `→ ...` | Remove prefix/trailing wrapper | High — removes LM framing, not content |
| Whitespace normalize | Extra spaces, `!./!`, `word.!"` | Collapse/fix punctuation | Always-safe |

**Not auto-corrected** (conservative flags only):
- Progressive `-eye` suffix truncation (B2: `mamilie` → possibly `mamili-eye`)
- Lexicon substitution errors (wrong word entirely)
- Structural/hallucination errors (completely different sentence)

## Gap Analysis

Best achievable accuracy with current approach:

| Configuration | Score |
|--------------|-------|
| LabeledFewShot k=5 baseline | 56.4% |
| **BFS d8_l16_r2 + post-processor (dev)** | **70.0%** |
| **BFS d8_l16_r2 + post-processor (full eval)** | **66.7%** |

**23.3pp short of the 90% target.** The gap cannot be closed with DSPy bootstrapping alone on 44 training pairs.

### Improvement Pathways

1. **Scale gold training data** (expected: +5-15pp)
   Increase from 44 to 200+ annotated Mir→En pairs via crowdsourcing or LLM-assisted annotation with human review. More demos = better BFS bootstrapping quality.

2. **LoRA fine-tuning** (expected: +10-20pp)
   Fine-tune a small LM (e.g., Qwen2.5-1.5B or Qwen2.5-4B) with LoRA on augmented 44-pair dataset. Data augmentation via back-translation and paraphrasing.

3. **Hybrid symbolic-neural** (expected: +5-10pp for morphology errors)
   Extend post-processor with grammar-constrained decoding. N-gram blocklist for common hallucinations, valid morphology enforcement.

4. **Switch to faster model for iterative optimization** (unblocks BFSRS)
   Use qwen3.5:4b (local, fast) for BFSRS sweeps to find optimal config in <5min, then deploy best config with DeepSeek-V4-Flash for inference.

### Deferred: HuggingFace Dataset Upload

Upload to HF is **blocked** until accuracy reaches ≥90%. The dataset requires clean, accurate translations; publishing the current model (66.7%) would introduce systematic errors into downstream consumers.

## Directory Layout

```
packages/translator/
├── README.md                   # This file
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
    ├── run_bfs_sweep.py        # BFS parameter sweep
    ├── deepseek_multihop_eval.py
    ├── deepseek_critique_eval.py
    └── deepinfra_model_eval.py
```

## Running Evals

### Baseline eval (Ollama, local)

```bash
cd /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine
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

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `DEEPINFRA_API_KEY` | — | Required for DeepInfra API access |
| `DEEPINFRA_BASE_URL` | `https://api.deepinfra.com/v1/openai` | DeepInfra API base |
| `MIRAD_EVAL_CSV` | `data/phrases/english-mirad-sentence-pairs.csv` | Evaluation dataset |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |

## Docker

The `ollama` service is defined in `docker-compose.yml`:

```bash
docker compose up -d ollama
```

See root [README.md](../../README.md) for full service configuration.