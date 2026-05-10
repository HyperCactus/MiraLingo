# Mirad Phonemes Engine

A text-to-speech preparation engine for **Mirad** — an artificial constructed language (conlang) designed for logical international communication.

## What is Mirad?

Mirad (formerly Unilingua) is a taxonomic/ontological constructed language developed by Noubar Agopoff in 1966. Its vocabulary is built on systematic, consistent rules where every letter has semantic or grammatical value, making words derivable and opposites predictable through vowel-switching.

**Learn more:**
- [Mirad Grammar (Wikibooks)](https://en.wikibooks.org/wiki/Mirad_Grammar/print_version)
- [Mirad Thesaurus](https://en.wikibooks.org/wiki/Mirad_Thesaurus)
- [Mirad Lexicon](https://en.wikibooks.org/wiki/Mirad_Lexicon)

## What This Project Does

This engine prepares Mirad text for speech synthesis by:

- **Tokenization** — parsing text into words, punctuation, and other tokens
- **Syllabification** — breaking words into syllables according to Mirad phonotactics
- **Stress assignment** — marking stress on the last non-final vowel
- **IPA transcription** — converting to International Phonetic Alphabet notation
- **TTS backend integration** — generating audio via eSpeak or Piper

## Work in Progress 
The Piper-TTS implementation has know issues with correct pronunciation.

### Roadmap
1. Mirad phoneme based TTS engine
2. English/other languages to Mirad translator
3. Mirad language learning web-app 

## Installation

Requires Python 3.10+.

```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install espeak-ng  # for eSpeak backend
```

## Usage

### Command Line

```bash
# Output IPA transcription (default)
python -m mirad_tts.cli "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Output syllables with stress markers
python -m mirad_tts.cli --syllables "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Output eSpeak phoneme input
python -m mirad_tts.cli --espeak "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Generate WAV audio (eSpeak backend)
python -m mirad_tts.cli --wav output.wav "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Generate WAV audio (Piper backend)
python -m mirad_tts.cli --backend piper --wav output.wav "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Debug mode (show all pipeline stages)
python -m mirad_tts.cli --debug "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."
```

### Python API

```python
from mirad_tts import tokenize, text_to_ipa, text_to_espeak_phoneme_input

text = "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Tokenize
tokens = tokenize(text)

# Get IPA transcription
ipa = text_to_ipa(text)

# Get eSpeak phoneme input
espeak = text_to_espeak_phoneme_input(text)
```

## Development

Run tests:

```bash
pytest
```

## Documentation

- [Piper Integration Guide](docs/PIPER_INTEGRATION.md) — setup and usage of the Piper neural TTS backend
- [Piper README](docs/README_PIPER.md) — Piper-specific features, voices, and troubleshooting
- [TTS Installation Guide](docs/TTS_INSTALLATION.md) — installing eSpeak NG locally and sample generation

## Reference Data

The `data/` directory contains source materials used to derive pronunciation rules:

- `data/mirad-docs/` — Markdown conversions of the Mirad Grammar and Thesaurus
- `data/pdfs/` — Original PDF references
- `data/pronunciation_tests.csv` — test anchor data

## Scripts

Utility scripts in `scripts/`:

- `generate_samples.py` — generate audio samples from Mirad words
- `compare_backends.py` — compare eSpeak and Piper output side-by-side
- `download_wikibook_pdf.py` — download Wikibooks references as PDF
- `pdf_to_markdown.py` — convert PDF references to Markdown

## License

MIT
