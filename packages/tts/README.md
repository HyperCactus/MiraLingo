# Mirad TTS

Text-to-speech preparation for the Mirad constructed language.

## What This Package Does

Converts Mirad text into IPA transcriptions and synthesises audio via eSpeak NG, Piper, or MBROLA.

The pipeline:
- **Tokenization** — parse text into words and punctuation
- **Syllabification** — break words into syllables per Mirad phonotactics
- **Stress assignment** — mark the last non-final vowel
- **IPA transcription** — produce IPA notation
- **Synthesis** — generate audio via eSpeak NG, Piper, or MBROLA

## Installation

Requires Python 3.10+ and eSpeak NG installed.

```bash
pip install -e packages/tts/
```

This makes the `mirad-tts` command available system-wide.

For eSpeak NG installation, see [docs/TTS_INSTALLATION.md](../../docs/TTS_INSTALLATION.md).

### MBROLA (optional)

For MBROLA synthesis support, install MBROLA and the `de6` German voice:

```bash
sudo apt install mbrola mbrola-de6
```

The `de6` voice is chosen because it supports Mirad-critical phones including `h`, `S` /ʃ/, `Z` /ʒ/, `tS` /tʃ/, `j`, `w`, and `r` — phones that many other MBROLA voices (e.g. Italian) lack.

## Usage

```bash
# Output IPA transcription
mirad-tts "Be yuboj" --ipa

# Show syllables with stress
mirad-tts "Be yuboj" --syllables

# Output eSpeak phoneme input
mirad-tts "Be yuboj" --espeak

# Output MBROLA de6 phone symbols
mirad-tts "Be yuboj" --mbrola

# Generate WAV audio with eSpeak (default)
mirad-tts "Be yuboj" --wav output.wav

# Generate WAV audio with Piper
mirad-tts --backend piper "Be yuboj" --wav output.wav

# Generate WAV audio with MBROLA de6
mirad-tts --backend mbrola "Ha Mirad." --wav output.wav

# Generate .pho file (MBROLA only)
mirad-tts --backend mbrola --pho output.pho "Ha Mirad."

# MBROLA debug mode (per-word phone diagnostics)
mirad-tts --backend mbrola --mbrola-debug "Ha Mirad."

# Override MBROLA voice database path
mirad-tts --backend mbrola --mbrola-db /path/to/de6 "Ha Mirad." --wav output.wav

# Debug mode (all pipeline stages)
mirad-tts "Be yuboj" --debug
```

The same commands work via Python:

```bash
python -m mirad_tts.cli "Be yuboj" --ipa
python -m mirad_tts.cli --backend mbrola "Ha Mirad." --mbrola-debug
```

### Python API

```python
from mirad_tts import tokenize, text_to_ipa, text_to_espeak_phoneme_input
from mirad_tts import word_to_mbrola, text_to_mbrola_phones, generate_pho
from mirad_tts.mbrola_backend import synthesize_to_wav as mbrola_synthesize_to_wav

text = "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn."

tokens = tokenize(text)
ipa = text_to_ipa(text)
espeak = text_to_espeak_phoneme_input(text)

# MBROLA
phones = text_to_mbrola_phones(text)       # flat phone list
pho_lines = generate_pho(text)              # .pho file lines
mbrola_synthesize_to_wav(text, "out.wav")   # synthesize WAV
```

## MBROLA Backend Details

The MBROLA backend generates deterministic `.pho` files and invokes `mbrola de6` to produce WAV output. It uses the existing Mirad tokenizer, syllabifier, and stress assignment pipeline, then maps syllables to `de6` phone symbols.

### Phone Mapping

| Mirad | de6 | | Mirad | de6 | | Mirad | de6 |
|-------|-----|-|-------|-----|-|-------|-----|
| a | a | | b | b | | s | s |
| e | e: | | c | tS | | t | t |
| i | i: | | d | d | | v | v |
| o | o: | | f | f | | w | w |
| u | u: | | g | g | | x | S |
| | | | h | h | | y | j |
| | | | j | Z | | z | z |
| | | | k | k | | q | k |
| | | | l | l | | r | r |
| | | | m | m | | n | n |
| | | | p | p | | |

Complex vowels expand into de6 sequences: `ya` → `j a`, `ay` → `a j`, `aw` → `O`, `yay` → `j a j`, `way` → `w a j`, etc.

### Duration and Pitch

Deterministic durations: vowels 110ms (stressed 140ms), glides 55ms, liquids 65ms, nasals 75ms, stops 65ms, fricatives 85ms, affricate 95ms. Pauses: word 60ms, comma 140ms, sentence 220ms.

Pitch uses male F0 base of 115 Hz: stressed vowels get `0 115 50 135 100 110`, unstressed get `0 110 100 105`.

## Docker

Run without installing dependencies locally:

```bash
docker compose build tts
docker compose run --rm tts mirad-tts "Be yuboj" --ipa
```

## Status

In progress — see root [README.md](../../README.md) for roadmap.