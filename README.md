# Mirad Phonemes Engine

A text-to-speech preparation engine for **Mirad** — an artificial constructed language (conlang) designed for logical international communication.

## What is Mirad?

Mirad (formerly Unilingua) is a taxonomic/ontological constructed language developed by Noubar Agopoff in 1966. Its vocabulary is built on systematic, consistent rules where every letter has semantic or grammatical value, making words derivable and opposites predictable through vowel-switching.

**Learn more:**
- [Mirad Grammar (Wikibooks)](https://en.wikibooks.org/wiki/Mirad_Grammar/print_version)
- [Mirad Thesaurus](https://en.wikibooks.org/wiki/Mirad_Thesaurus)
- [Mirad Lexicon](https://en.wikibooks.org/wiki/Mirad_Lexicon)

## Monorepo Structure

This is a Python monorepo with three packages under `packages/`:

| Package | Description |
|---------|-------------|
| `packages/tts` | Mirad TTS preparation engine: tokenisation, syllabification, stress assignment, and IPA transcription. |
| `packages/translator` | Mirad translator (in progress) |
| `packages/webapp` | Mirad language learning web application (in progress) |

Shared reference data lives at the repo root under `data/`.

## What This Project Does

The `tts` package prepares Mirad text for speech synthesis by:

- **Tokenization** — parsing text into words, punctuation, and other tokens
- **Syllabification** — breaking words into syllables according to Mirad phonotactics
- **Stress assignment** — marking stress on the last non-final vowel
- **IPA transcription** — converting to International Phonetic Alphabet notation
- **TTS backend integration** — generating audio via eSpeak

## Work in Progress

Roadmap:
1. Mirad phoneme-based TTS engine
2. English/other languages to Mirad translator
3. Mirad language learning web-app

## Installation

Requires Python 3.10+.

```bash
# Install the TTS package from source
pip install -e packages/tts/
```

### Docker

Two services are defined in `docker-compose.yml`:

- **tts** — builds and runs the TTS engine in a container
- **ollama** — provides local LLM inference on port 11434 (used by the translator package)

```bash
# Build and run TTS via Docker
docker compose build tts
docker compose run --rm tts mirad-tts "test" --ipa

# Start all services (ollama + others)
docker compose up -d
```

On macOS or Windows, [Docker Desktop](https://docs.docker.com/desktop/) is required.

## Usage

### Command Line

```bash
# Output IPA transcription (default)
python -m mirad_tts.cli "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Output syllables with stress markers
python -m mirad_tts.cli --syllables "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Output eSpeak phoneme input
python -m mirad_tts.cli --espeak "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Generate WAV audio
python -m mirad_tts.cli --wav output.wav "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

# Debug mode (show all pipeline stages)
python -m mirad_tts.cli --debug "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."
```

After `pip install -e packages/tts/`, the `mirad-tts` command is also available:

```bash
mirad-tts "Be yuboj" --ipa
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
PYTHONPATH=src pytest
```

## Documentation

- [TTS Installation Guide](docs/TTS_INSTALLATION.md) — installing eSpeak NG locally and sample generation
- [data/README.md](data/README.md) — reference data overview
- [scripts/README.md](scripts/README.md) — utility scripts

## Scripts

Utility scripts in `scripts/`:

- `generate_samples.py` — generate audio samples from Mirad words
- `compare_backends.py` — compare eSpeak outputs side-by-side
- `download_wikibook_pdf.py` — download Wikibooks references as PDF
- `pdf_to_markdown.py` — convert PDF references to Markdown
- `verify-ollama.sh` — health-check script for the ollama service (use via Docker)

## License

MIT