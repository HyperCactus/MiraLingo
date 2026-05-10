# Mirad TTS - Text-to-Speech for Mirad Language

A Python text-to-speech pipeline for the Mirad constructed language, featuring phonology-aware tokenization, syllabification, IPA transcription, and neural synthesis.

## Features

- **Phonology-aware tokenization**: Handles Mirad's 20 consonants and 5 simple vowels
- **Complex vowel support**: Pre/post-y-glided, pre/post-w-glided, and circum-glided vowels
- **Accurate syllabification**: Implements Mirad Grammar rules for coda formation
- **Stress assignment**: Automatic stress on last non-final syllable
- **IPA transcription**: Full IPA output following Mirad Grammar specification
- **Multiple backends**: eSpeak NG (fast) and Piper TTS (natural)
- **CLI interface**: Easy-to-use command-line tool
- **Comprehensive tests**: 805 tests covering all phonology rules

## Installation

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
# Install the package
pip install -e .

# Install Piper TTS (for neural synthesis)
pip install piper-tts

# Download a Piper voice model
python3 -m piper.download_voices es_MX-claude-high --download_dir .gsd/piper-voices
```

### eSpeak NG (Optional)

eSpeak NG is installed locally for the traditional synthesis backend:

```bash
# Download and extract eSpeak NG packages
apt-get download espeak-ng espeak-ng-data
dpkg -x espeak-ng_*.deb /tmp/espeak-ng-extracted
dpkg -x espeak-ng-data_*.deb /tmp/espeak-ng-extracted

# Copy to project directory
mkdir -p .gsd/bin .gsd/share/espeak-ng-data
cp /tmp/espeak-ng-extracted/usr/bin/espeak-ng .gsd/bin/
cp -r /tmp/espeak-ng-extracted/usr/lib/x86_64-linux-gnu/espeak-ng-data/* .gsd/share/espeak-ng-data/
chmod +x .gsd/bin/espeak-ng
```

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Output IPA transcription (default)
python3 -m mirad_tts.cli "Mirad"

# Output syllables with stress
python3 -m mirad_tts.cli --syllables "Mirad"

# Output eSpeak phonemes
python3 -m mirad_tts.cli --espeak "Mirad"

# Debug mode (show all stages)
python3 -m mirad_tts.cli --debug "Mirad"
```

#### Generate Audio

```bash
# Using eSpeak backend (default)
PATH="$(pwd)/.gsd/bin:$PATH" \
ESPEAK_DATA_PATH="$(pwd)/.gsd/share/espeak-ng-data" \
PYTHONPATH=src \
python3 -m mirad_tts.cli --backend espeak --wav output.wav "Mirad"

# Using Piper backend (neural synthesis)
PYTHONPATH=src \
python3 -m mirad_tts.cli --backend piper --wav output.wav "Mirad"
```

#### Multiple Words

```bash
python3 -m mirad_tts.cli "Mirad igay tejna"
```

### Python API

```python
from mirad_tts.tokenizer import tokenize
from mirad_tts.syllabify import syllabify_word, assign_stress
from mirad_tts.ipa import text_to_ipa
from mirad_tts.espeak_backend import text_to_espeak_phoneme_input
from mirad_tts.piper_backend import synthesize_to_wav

# Tokenize
tokens = tokenize("Mirad")

# Syllabify
syllables = syllabify_word("mirad")
if len(syllables) > 1:
    syllables = assign_stress(syllables)

# Convert to IPA
ipa = text_to_ipa("Mirad")  # 'ˈmiɾad'

# Convert to eSpeak phonemes
espeak = text_to_espeak_phoneme_input("Mirad")  # '[[mI4\%ad]]'

# Synthesize with Piper
synthesize_to_wav("Mirad", "output.wav")
```

## Pronunciation Rules

### Consonant Mappings

| Mirad | IPA | eSpeak | Description |
|-------|-----|--------|-------------|
| b | b | b | Voiced bilabial plosive |
| c | t͡ʃ | tS | Voiceless postalveolar affricate |
| d | d | d | Voiced alveolar plosive |
| f | f | f | Voiceless labiodental fricative |
| g | g | g | Voiced velar plosive |
| h | h | h | Voiceless glottal fricative |
| j | ʒ | Z | Voiced palatal fricative |
| k | k | k | Voiceless velar plosive |
| l | l | l | Voiced alveolar lateral approximant |
| m | m | m | Voiced bilabial nasal |
| n | n | n | Voiced alveolar nasal |
| p | p | p | Voiceless bilabial plosive |
| q | k | k | Voiceless velar plosive (foreign) |
| r | ɾ | r | Alveolar flap (not trill) |
| s | s | s | Voiceless alveolar fricative |
| t | t | t | Voiceless alveolar plosive |
| v | v | v | Voiced labiodental fricative |
| w | w | w | Voiced labial-velar approximant |
| x | ʃ | S | Voiceless postalveolar fricative |
| y | j | j | Voiced palatal approximant |
| z | z | z | Voiced alveolar fricative |

### Vowel Mappings

#### Simple Vowels
- a → a
- e → e
- i → i
- o → o
- u → u

#### Post-y-glided Vowels
- ay → aɪ
- ey → eɪ
- iy → iɪ
- oy → oɪ
- uy → uɪ

#### Post-w-glided Vowels
- aw → ɔ
- ew → ɛʊ
- iw → iʊ
- ow → oʊ
- uw → uʊ

#### Pre-y-glided Vowels
- ya → ja
- ye → je
- yi → ji
- yo → jo
- yu → ju

#### Pre-w-glided Vowels
- wa → wa
- we → we
- wi → wi
- wo → wo
- wu → wu

#### Circum-y-glided Vowels
- yay → jaɪ
- yey → jeɪ
- yiy → jiɪ
- yoy → joɪ
- yuy → juɪ

#### Pre-w-post-y-glided Vowels
- way → waɪ
- wey → weɪ
- wiy → wiɪ
- woy → woɪ
- wuy → wuɪ

### Stress Assignment

- Stress falls on the **last non-final syllable**
- Final syllables are never stressed
- Complex vowels (glided) count as single syllable nuclei

Examples:
- "igay" → ˈigaɪ (stress on first syllable)
- "Mirad" → ˈmiɾad (stress on first syllable)
- "aymsea" → aɪmˈsea (stress on second syllable)

### Syllabification

- **r/l coda**: When followed by consonant or word-final
- **Adjacent vowels**: Form separate syllable nuclei
- **Complex vowels**: Treated as single units

Examples:
- "booka" → bo-o-ka (adjacent vowels)
- "ayma" → ay-ma (complex vowel as single unit)
- "alayn" → a-layn (l coda before consonant)

## Testing

```bash
# Run all tests
PYTHONPATH=src pytest tests/

# Run specific test file
PYTHONPATH=src pytest tests/test_phonology.py

# Run with verbose output
PYTHONPATH=src pytest tests/ -v

# Run specific test
PYTHONPATH=src pytest tests/test_phonology.py::test_simple_vowels
```

## Audio Samples

The project includes audio samples generated with both backends:

### Sample Structure

```
samples/
├── espeak/          # eSpeak NG samples
├── piper/           # Piper TTS samples
└── README.md        # Detailed sample documentation
```

### Generate Comparison Samples

```bash
# Compare backends for specific words
python3 compare_backends.py Mirad igay tejna

# Compare all grammar anchor words
python3 compare_backends.py Mirad igay tejna vay aymsea booka byoskyin auwa tixe jal ya wa yay way qatar ama oyse akea alayn
```

### Play Samples

```bash
# Using aplay
aplay samples/piper/mirad.wav

# Using ffplay
ffplay samples/piper/mirad.wav

# Using vlc
vlc samples/piper/mirad.wav
```

## Backend Comparison

| Feature | eSpeak NG | Piper TTS |
|---------|-----------|-----------|
| Type | Formant synthesis | Neural synthesis |
| Quality | Robotic | Natural |
| Speed | Very fast | Fast |
| Resource usage | Low | Moderate |
| Voice variety | Many | Custom models |
| File size | Larger | Smaller (~15% smaller) |
| Best for | Testing, low-end devices | Production, high-quality output |

## Development

### Project Structure

```
mirad-phonemes-engine/
├── src/mirad_tts/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── espeak_backend.py   # eSpeak NG synthesis
│   ├── ipa.py              # IPA transcription
│   ├── phonology.py        # Phonology constants
│   ├── piper_backend.py    # Piper TTS synthesis
│   ├── syllabify.py        # Syllabification logic
│   ├── tokenizer.py        # Tokenization
│   └── types.py            # Type definitions
├── tests/                  # Test suite
├── samples/                # Audio samples
├── .gsd/                   # Local dependencies
│   ├── bin/               # eSpeak binary
│   ├── share/             # eSpeak data
│   └── piper-voices/      # Piper voice models
└── pyproject.toml         # Project configuration
```

### Code Quality

```bash
# Run linting
PYTHONPATH=src pytest tests/ -v

# Check type hints (if mypy is installed)
mypy src/mirad_tts/
```

## License

MIT License - see LICENSE file for details.

## References

- [Mirad Grammar](https://www.mirad.org/grammar.html)
- [Piper TTS](https://github.com/rhasspy/piper)
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng)
