# Mirad TTS

Phoneme-based text-to-speech engine for the Mirad constructed language.

The TTS pipeline is entirely rule-driven — Mirad's regular phonology means no training data or neural models are needed for the phonological front-end. Text is tokenized, syllabified, stressed, and transcribed to IPA (or eSpeak/MBROLA phone symbols) through deterministic rules, then handed to a synthesis backend for audio output.

### Pipeline stages

| Stage | Input → Output | Method |
|-------|---------------|--------|
| **Tokenization** | raw text → token list | rule-based tokenizer |
| **Syllabification** | word → syllables | Mirad phonotactic rules |
| **Stress assignment** | syllables → stressed syllables | last non-final vowel receives primary stress |
| **IPA transcription** | stressed syllables → IPA string | phone mapping tables |
| **Synthesis** | IPA / phone string → audio WAV | eSpeak NG, Piper, or MBROLA backend |

Because each stage is deterministic and compositional, any stage can be used independently — e.g., you can stop at IPA transcription and pipe the result into another synthesizer.

---

## Installation

Requires Python 3.10+ and eSpeak NG.

```bash
pip install -e packages/tts/
```

This makes the `mirad-tts` CLI available system-wide.

For eSpeak NG installation, see [TTS_INSTALLATION.md](../../docs/TTS_INSTALLATION.md).

### MBROLA (optional)

For MBROLA synthesis, install MBROLA and the `de6` German voice:

```bash
sudo apt install mbrola mbrola-de6
```

The `de6` voice supports Mirad-critical phones (`h`, `ʃ`, `ʒ`, `tʃ`, `j`, `w`, `r`) that many other MBROLA voices lack.

---

## Usage

### Command Line

```bash
# IPA transcription (default)
mirad-tts "Be yuboj" --ipa

# Syllables with stress markers
mirad-tts "Be yuboj" --syllables

# eSpeak phoneme input
mirad-tts "Be yuboj" --espeak

# MBROLA de6 phone symbols
mirad-tts "Be yuboj" --mbrola

# Generate WAV audio (eSpeak default)
mirad-tts "Be yuboj" --wav output.wav

# Generate WAV audio (Piper backend)
mirad-tts --backend piper "Be yuboj" --wav output.wav

# Generate WAV audio (MBROLA backend)
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

All CLI options also work via `python -m mirad_tts.cli`.

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

---

## MBROLA Backend

The MBROLA backend generates deterministic `.pho` files and invokes `mbrola de6` for synthesis. It reuses the same tokenizer, syllabifier, and stress pipeline, then maps syllables to `de6` phone symbols.

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

Complex vowels expand: `ya` → `j a`, `ay` → `a j`, `aw` → `O`, `yay` → `j a j`, `way` → `w a j`, etc.

### Duration and Pitch

Deterministic durations: vowels 110 ms (stressed 140 ms), glides 55 ms, liquids 65 ms, nasals 75 ms, stops 65 ms, fricatives 85 ms, affricates 95 ms. Pauses: word 60 ms, comma 140 ms, sentence 220 ms. Pitch: male F0 base 115 Hz; stressed vowels `0 115 50 135 100 110`, unstressed `0 110 100 105`.

---

## Docker

```bash
docker compose build tts
docker compose run --rm tts mirad-tts "Be yuboj" --ipa
```

---

## Status

Functional. Back to [root README](../../README.md).