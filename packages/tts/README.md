# Mirad TTS

Text-to-speech preparation for the Mirad constructed language.

## What This Package Does

Converts Mirad text into IPA transcriptions and synthesises audio via eSpeak NG.

The pipeline:
- **Tokenization** — parse text into words and punctuation
- **Syllabification** — break words into syllables per Mirad phonotactics
- **Stress assignment** — mark the last non-final vowel
- **IPA transcription** — produce IPA notation
- **Synthesis** — generate audio via eSpeak NG

## Installation

Requires Python 3.10+ and eSpeak NG installed.

```bash
pip install -e packages/tts/
```

This makes the `mirad-tts` command available system-wide.

For eSpeak NG installation, see [docs/TTS_INSTALLATION.md](../../docs/TTS_INSTALLATION.md).

## Usage

```bash
# Output IPA transcription
mirad-tts "Be yuboj" --ipa

# Show syllables with stress
mirad-tts "Be yuboj" --syllables

# Output eSpeak phoneme input
mirad-tts "Be yuboj" --espeak

# Generate WAV audio
mirad-tts "Be yuboj" --wav output.wav

# Debug mode (all pipeline stages)
mirad-tts "Be yuboj" --debug
```

The same commands work via Python:

```bash
python -m mirad_tts.cli "Be yuboj" --ipa
```

### Python API

```python
from mirad_tts import tokenize, text_to_ipa, text_to_espeak_phoneme_input

text = "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

tokens = tokenize(text)
ipa = text_to_ipa(text)
espeak = text_to_espeak_phoneme_input(text)
```

## Docker

Run without installing dependencies locally:

```bash
docker compose build tts
docker compose run --rm tts mirad-tts "Be yuboj" --ipa
```

## Status

In progress — see root [README.md](../../README.md) for roadmap.