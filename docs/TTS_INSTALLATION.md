# TTS Installation and Samples

## Installation Summary

TTS dependencies are installed locally in `.gsd/` (no sudo required):

```
.gsd/
├── bin/
│   └── espeak-ng          # eSpeak NG binary (v1.51)
└── share/
    └── espeak-ng-data/    # eSpeak NG voice and phoneme data
```

### Installation Method

Downloaded Ubuntu `.deb` packages and extracted them locally:

```bash
apt-get download espeak-ng espeak-ng-data
dpkg -x espeak-ng_*.deb /tmp/espeak-ng-extracted
cp -r extracted files to .gsd/
```

## Audio Samples Generated

20 audio samples demonstrating Mirad pronunciation rules:

| File | Word | IPA | Rule Demonstrated |
|------|------|-----|------------------|
| mirad.wav | Mirad | ˈmiɾad | r→ɾ alveolar flap |
| igay.wav | igay | ˈigaɪ | Stress on last non-final |
| tejna.wav | tejna | ˈteʒna | j→ʒ, stress on te |
| vay.wav | vay | vaɪ | Post-y-glided (ay→aɪ) |
| aymsea.wav | aymsea | aɪmˈsea | Complex vowel + stress |
| booka.wav | booka | boˈoka | Adjacent vowels |
| byoskyin.wav | byoskyin | ˈbjoskjin | Complex coda + onset |
| auwa.wav | auwa | aˈuwa | Pre-w-glided vowel |
| tixe.wav | tixe | ˈtiʃe | x→ʃ (post-alveolar) |
| jal.wav | jal | ʒal | j→ʒ (palatal fricative) |
| ya.wav | ya | ja | Pre-y-glided (ya→ja) |
| wa.wav | wa | wa | Pre-w-glided vowel |
| yay.wav | yay | jaɪ | Circum-y-glided vowel |
| way.wav | way | waɪ | Pre-w-post-y-glided |
| qatar.wav | qatar | ˈkataɾ | q→k (foreign word) |
| ama.wav | ama | ˈama | Simple CV syllable |
| oyse.wav | oyse | ˈoɪse | Post-y-glided (oy→oɪ) |
| akea.wav | akea | aˈkea | Adjacent vowels + consonant |
| alayn.wav | alayn | ˈalaɪn | l coda before consonant |
| test.wav | test | ˈtɛst | Test word |

## Usage

### Generate New Samples

Using the helper script:

```bash
python3 generate_samples.py word1 word2 word3
```

Using the CLI directly:

```bash
PATH="$(pwd)/.gsd/bin:$PATH" \
ESPEAK_DATA_PATH="$(pwd)/.gsd/share/espeak-ng-data" \
PYTHONPATH=src \
python3 -m mirad_tts.cli --wav samples/word.wav "word"
```

### Play Samples

```bash
# Using aplay (ALSA)
aplay samples/mirad.wav

# Using ffplay
ffplay samples/mirad.wav

# Using vlc
vlc samples/mirad.wav
```

## Pronunciation Rules Covered

### Consonant Mappings
- **r → ɾ**: Alveolar flap (not trill)
- **j → ʒ**: Voiced palatal fricative
- **x → ʃ**: Post-alveolar fricative
- **q → k**: Foreign word mapping

### Vowel Mappings
- **Post-y-glided**: ay→aɪ, ey→eɪ, iy→iɪ, oy→oɪ, uy→uɪ
- **Post-w-glided**: aw→ɔ, ew→ɛʊ, iw→iʊ, ow→oʊ, uw→uʊ
- **Pre-y-glided**: ya→ja, ye→je, yi→ji, yo→jo, yu→ju
- **Pre-w-glided**: wa→wa, we→we, wi→wi, wo→wo, wu→wu
- **Circum-y-glided**: yay→jaɪ, yey→jeɪ, yiy→jiɪ, yoy→joɪ, yuy→juɪ
- **Pre-w-post-y-glided**: way→waɪ, wey→weɪ, wiy→wiɪ, woy→woɪ, wuy→wuɪ

### Stress Assignment
- Stress on **last non-final syllable**
- Final syllables never stressed
- Complex vowels count as single nuclei

### Syllabification
- **r/l coda**: When followed by consonant or word-final
- **Adjacent vowels**: Separate syllable nuclei
- **Complex vowels**: Single units (ayma → ay-ma)

## Technical Details

- **Audio format**: 16-bit mono WAV, 22050 Hz
- **Synthesis backend**: eSpeak NG v1.51
- **Pipeline**: Mirad text → IPA → eSpeak phonemes → audio
- **IPA standard**: Mirad Grammar specification
- **File sizes**: 25-39 KB per sample

## Notes

- All samples are generated from the grammar-anchored test cases
- IPA transcriptions match the Mirad Grammar document
- eSpeak NG is used as the synthesis backend
- The pipeline handles all Mirad-specific phonology rules
