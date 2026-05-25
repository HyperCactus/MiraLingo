# Mirad Language Engine

An open-source **Mirad language learning** platform — early development.

This project builds tools for the [Mirad](https://en.wikibooks.org/wiki/Mirad_Grammar/print_version) constructed language: a phoneme-based text-to-speech system, a bidirectional English↔Mirad translator, and (eventually) an interactive web app for learning.

> **Status:** Early development. TTS is functional, translator produces results but needs improvement, web app not yet started.

---

## What is Mirad?

Mirad (formerly Unilingua) is an artificial constructed language designed by Noubar Agopoff in 1966 for logical international communication. Its vocabulary is built from systematic rules — every letter carries semantic or grammatical value, words are derivable from roots, and opposites are predictable through vowel-switching. This makes Mirad uniquely suited for computational processing: regular morphology, deterministic phonology, and an ontology-encoded lexicon.

**Learn more about Mirad:**

- [Mirad Grammar — Wikibooks](https://en.wikibooks.org/wiki/Mirad_Grammar/print_version) — full grammar reference
- [Mirad Lexicon — Wikibooks](https://en.wikibooks.org/wiki/Mirad_Lexicon) — word roots and derivations
- [Mirad Thesaurus — Wikibooks](https://en.wikibooks.org/wiki/Mirad_Thesaurus) — semantic groupings

---

## Packages

| Package | Description | Status |
|---------|-------------|--------|
| [**packages/tts**](packages/tts/) | Phoneme-based TTS engine — tokenization, syllabification, stress, IPA, audio synthesis via eSpeak NG / Piper / MBROLA | Functional |
| [**packages/translator**](packages/translator/) | Bidirectional English↔Mirad translation using DeepInfra DeepSeek-V4-Flash, DSPy, semantic lexicon lookup, structured grammar-rule retrieval, and deterministic post-processing | Active baseline: sentence-only eval, En→Mir ~20% true-valid, Mir→En ~80–90% true-valid |
| [**packages/webapp**](packages/webapp/) | Interactive language-learning web application | Not yet started |

Shared reference data (lexicon, grammar documents, evaluation results) lives in [`data/`](data/).

---

## Quick Start

Requires Python 3.10+.

```bash
# Install TTS
pip install -e packages/tts/

# Install translator
pip install -e packages/translator/

# TTS: transcribe to IPA
mirad-tts "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn." --ipa

# Translator: English → Mirad (uses DeepInfra env from .env)
python -c "
import dspy
from mirad_translator.evaluate import _make_deepinfra_lm
from mirad_translator.translate import DefaultTranslator

dspy.settings.configure(lm=_make_deepinfra_lm())
t = DefaultTranslator()
result = t.forward('you do not work at home')
print(result.mirad_text)
"
```

### Docker

```bash
# TTS via Docker
docker compose build tts
docker compose run --rm tts mirad-tts "Be yuboj" --ipa

# Optional local model services for experiments only
# Default translator runtime uses DeepInfra, not Ollama.
docker compose up -d ollama
```

See individual package READMEs for full usage, API details, and configuration.

---

## Project Roadmap

1. ✅ Mirad phoneme-based TTS engine
2. 🔧 Bidirectional English↔Mirad translator (improving accuracy toward 90%)
3. ⬜ Mirad language learning web application

---

## Documentation

- [TTS Installation Guide](docs/TTS_INSTALLATION.md) — setting up eSpeak NG, Piper, MBROLA
- [Piper Integration](docs/PIPER_INTEGRATION.md) — Piper TTS backend details
- [TTS README](docs/README_PIPER.md) — Piper-specific notes
- [Data Overview](data/README.md) — reference data and evaluation results

## License

MIT