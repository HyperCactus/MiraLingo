You are implementing a solo-project prototype for rule-based Mirad speech synthesis.

Project goal:
Build a deterministic pipeline for the newer Mirad Grammar version:

    Mirad text
    → tokenization
    → Mirad syllabification
    → stress assignment
    → IPA output for verification/debugging
    → eSpeak NG phoneme/mnemonic output
    → WAV audio through eSpeak NG

Important correction:
Do not assume eSpeak NG can reliably consume arbitrary Unicode IPA directly. Use IPA as a human-readable verification layer, but generate eSpeak NG’s phoneme mnemonic notation separately for audio. eSpeak phoneme input should be placed inside [[...]], with word separation preserved and stressed syllables explicitly marked.

Current project structure:

    .
    ├── data
    │   └── mirad-docs
    │       ├── Mirad_grammer.md
    │       └── Mirad.md
    ├── LICENSE
    ├── README.md
    └── src
        └── convert_mirad_pdfs_to_markdown.py

The files data/mirad-docs/Mirad_grammer.md and data/mirad-docs/Mirad.md are local reference documents. Use Mirad_grammer.md as the authoritative source for the newer Mirad Grammar pronunciation. Treat Mirad.md as the older/legacy Unilingua-style reference only. Do not mix the older pronunciation rules into the new implementation unless explicitly adding a legacy mode later.

Core implementation target:
Create a Python package/module that can convert Mirad text to:
1. syllable breakdown
2. stressed IPA
3. eSpeak NG phoneme notation
4. WAV audio through the installed espeak-ng command

Recommended new structure:

    src/
      mirad_tts/
        __init__.py
        phonology.py
        tokenizer.py
        syllabify.py
        ipa.py
        espeak_backend.py
        cli.py
    tests/
      test_tokenizer.py
      test_syllabify.py
      test_ipa.py
      test_espeak_backend.py
    data/
      mirad-docs/
        Mirad_grammer.md
        Mirad.md
      pronunciation_tests.csv

Add project metadata if missing:
    pyproject.toml
    README.md updates

Suggested dependencies:
- Python 3.11+
- pytest
- ruff, optional
- mypy, optional
- no heavy TTS libraries yet
- call espeak-ng through subprocess for the first working version

Command-line goals:

    python -m mirad_tts.cli --ipa "At tixe Mirad."
    python -m mirad_tts.cli --syllables "At tixe Mirad."
    python -m mirad_tts.cli --espeak "At tixe Mirad."
    python -m mirad_tts.cli --wav out.wav "At tixe Mirad."
    python -m mirad_tts.cli --debug "At tixe Mirad."

Expected debug shape:

    INPUT:
    At tixe Mirad.

    TOKENS:
    WORD At
    WORD tixe
    WORD Mirad
    PUNCT .

    SYLLABLES:
    At      -> at
    tixe    -> ti-xe
    Mirad   -> mi-rad

    IPA:
    at ˈtiʃe ˈmiɽad .

    ESPEAK:
    [[ ... ]]

    WAV:
    out.wav

Important Mirad version choice:
Use the newer Mirad Grammar spelling and phonology:
- no native diacritics
- x = /ʃ/
- j = /ʒ/
- c = /t͡ʃ/
- s = /s/
- g = /g/ always hard
- r = flap/trill; use /ɽ/ or /ɾ/ internally, but document the choice
- q = /k/ for imported/scientific words
- y and w are used as glides in complex vowels
- native words are pronounced as written
- stress is regular

Do not use older Unilingua rules:
- do not treat c as /s/
- do not treat s as /ʃ/
- do not implement accented vowel letters á, à, â, etc. in the default mode
- do not stress Mirad as mi-RAD in the newer mode; in the newer grammar examples, Mirad syllabifies as Mi-rad, so stress falls on Mi.

Consonant mapping for newer Mirad:

    b -> IPA b
    c -> IPA t͡ʃ
    d -> IPA d
    f -> IPA f
    g -> IPA g
    h -> IPA h
    j -> IPA ʒ
    k -> IPA k
    l -> IPA l
    m -> IPA m
    n -> IPA n
    p -> IPA p
    q -> IPA k
    r -> IPA ɽ or ɾ
    s -> IPA s
    t -> IPA t
    v -> IPA v
    x -> IPA ʃ
    z -> IPA z

Use a single internal constant for this mapping, for example CONSONANT_IPA.

Simple vowel mapping:

    a -> /a/
    e -> /e/
    i -> /i/
    o -> /o/
    u -> /u/

Complex vowels:
The grammar treats complex glided vowels as single vowel nuclei for syllabification and stress. Implement these as vowel nuclei, not as arbitrary consonant + vowel sequences.

Pre-y-glided:
    ya -> /ja/
    ye -> /je/
    yi -> /ji/
    yo -> /jo/
    yu -> /ju/

Pre-w-glided:
    wa -> /wa/
    we -> /we/
    wi -> /wi/
    wo -> /wo/
    wu -> /wu/

Post-y-glided:
    ay -> /aɪ/
    ey -> /eɪ/
    iy -> /iɪ/
    oy -> /oɪ/
    uy -> /uɪ/

Post-w-glided:
    aw -> /ɔ/ or /aw/ depending on the chosen phonetic approximation; document the choice
    ew -> /eʊ/
    iw -> /iʊ/
    ow -> /oʊ/
    uw -> /uʊ/

Circum-y-glided:
    yay -> /jaɪ/
    yey -> /jeɪ/
    yiy -> /jiɪ/
    yoy -> /joɪ/
    yuy -> /juɪ/

Pre-w-post-y-glided:
    way -> /waɪ/
    wey -> /weɪ/
    wiy -> /wiɪ/
    woy -> /woɪ/
    wuy -> /wuɪ/

Important parsing rule:
Do not naïvely longest-match all y/w sequences, because adjacent vowels create separate syllables.

Examples from the grammar:
    ama     -> a-ma
    ayma    -> ay-ma
    aymsea  -> aym-se-a
    pixwa   -> pix-wa
    upayo   -> u-pa-yo
    vyaa    -> vya-a
    vyaay   -> vya-ay
    vay     -> vay
    tambwa  -> tam-bwa

These examples must be included in tests.

Syllabification rules to implement:
1. Every syllable contains exactly one vowel nucleus.
2. A simple vowel is a, e, i, o, u.
3. y or w immediately before a vowel may be a pre-glide belonging to that vowel nucleus.
4. y or w after a vowel may be a post-glide if final or followed by a consonant.
5. Two vowel letters in a row form two separate syllabic nuclei.
6. Liquids r and l, when final or followed by a consonant, belong to the syllable where the preceding vowel is the nucleus.
7. Final consonants after the last vowel normally attach to the preceding syllable.
8. Between two vowel nuclei, assign consonants according to Mirad phonotactic examples. For the first version, match the grammar examples exactly and keep the algorithm simple, documented, and test-driven.

Stress rule:
In words with more than one syllable, stress falls on the last non-final vowel nucleus, including complex/glided vowels.

This means:
    one syllable: no explicit primary stress required, or optionally no stress mark
    two syllables: stress syllable 1
    three syllables: stress syllable 2
    four syllables: stress syllable 3

Examples:
    tejna    -> tej-na     -> ˈ...
    igay     -> i-gay      -> stress i, not final ay
    alayn    -> a-layn     -> stress a
    Mirad    -> mi-rad     -> stress mi
    booka    -> bo-o-ka    -> stress o, the middle syllable
    bookan   -> bo-o-kan   -> stress o, the middle syllable
    akea     -> a-ke-a     -> stress ke
    oyse     -> oy-se      -> stress oy
    byoskyin -> byos-kyin  -> stress byos

Tokenization:
Implement tokenizer.py.

Token types:
- WORD: sequences of letters A-Z/a-z, optionally with internal apostrophe later
- NUMBER: sequences of digits, but do not implement full number reading yet
- PUNCT: punctuation
- SPACE: optional, but do not need to preserve as a token unless useful

For v1:
- Preserve punctuation in IPA/espeak output.
- Lowercase words internally for phonological processing.
- Preserve original token text for debug output.
- Handle hyphenated compounds by treating each hyphen-separated part as a separate stress domain unless tests reveal a better Mirad-specific rule.
- Reject or warn on older diacritics by default: á à â é è ê í ì î ó ò ô ú ù û.
- Implement a flag later for legacy conversion, but not now.

Data model:
Use dataclasses.

Suggested classes:

    class Token:
        type: Literal["word", "number", "punct", "space"]
        text: str

    class Syllable:
        spelling: str
        onset: str
        nucleus: str
        coda: str
        stressed: bool = False

    class WordPronunciation:
        original: str
        normalized: str
        syllables: list[Syllable]
        ipa: str
        espeak: str

Internal design:
Separate the pipeline into pure functions so they are easy to test.

Suggested functions:

    normalize_text(text: str) -> str
    tokenize(text: str) -> list[Token]
    syllabify_word(word: str) -> list[Syllable]
    assign_stress(syllables: list[Syllable]) -> list[Syllable]
    syllable_to_ipa(syllable: Syllable) -> str
    word_to_ipa(word: str) -> str
    text_to_ipa(text: str) -> str
    syllable_to_espeak(syllable: Syllable) -> str
    word_to_espeak(word: str) -> str
    text_to_espeak_phoneme_input(text: str) -> str
    synthesize_to_wav(text: str, output_path: Path, voice: str = "en") -> None

IPA formatting:
- Use ˈ before the stressed syllable.
- Do not put stress before one-syllable words unless explicitly enabled.
- Join syllables within words without dots by default, but offer a debug option that shows syllable boundaries using dots or hyphens.
- Preserve spaces between words.
- Keep punctuation readable.

Example:
    Mirad -> ˈmiɽad or ˈmiɾad
    tixe  -> ˈtiʃe
    igay  -> ˈigaɪ

eSpeak backend:
Implement espeak_backend.py.

Use subprocess.run with explicit arguments, not shell=True.

Example shape:
    espeak-ng -v en "[[ ...phoneme mnemonics... ]]" -w out.wav

Also support:
    espeak-ng -v en -x "test words"

But -x is for investigating eSpeak’s own phonemization of ordinary text. It should not be used as the Mirad phonemizer.

Create a mapping from internal Mirad phones to eSpeak phoneme mnemonics. This will need empirical testing. Start with a mapping based on eSpeak English phoneme mnemonics, then verify by listening and by using espeak-ng -x on known English words.

Investigate eSpeak symbols using commands like:
    espeak-ng -v en -x "shoe measure church see zoo go"
    espeak-ng -v en --ipa "shoe measure church see zoo go"

Then map:
    Mirad x /ʃ/   -> eSpeak symbol used for "sh"
    Mirad j /ʒ/   -> eSpeak symbol used for "measure"
    Mirad c /t͡ʃ/ -> eSpeak symbol used for "church"
    Mirad s /s/   -> eSpeak symbol used for "see"
    Mirad z /z/   -> eSpeak symbol used for "zoo"
    Mirad g /g/   -> eSpeak symbol used for "go"

Document the final eSpeak mapping in README.md and in code comments.

Important:
Do not make IPA and eSpeak mappings the same thing. IPA output is for human verification. eSpeak output is an implementation detail for synthesis.

Testing:
Create tests before or alongside implementation.

Create data/pronunciation_tests.csv with columns:
    word, expected_syllables, expected_stress_index, expected_ipa

Initial required test cases:

    ama,a-ma,0,ˈama
    ayma,ay-ma,0,ˈaɪma
    aymsea,aym-se-a,1,aɪmˈsea
    pixwa,pix-wa,0,ˈpiʃwa
    upayo,u-pa-yo,1,uˈpajo
    vyaa,vya-a,0,ˈvjaa
    vyaay,vya-ay,1,vjaˈaɪ
    vay,vay,,vaɪ
    tambwa,tam-bwa,0,ˈtambwa
    Mirad,Mi-rad,0,ˈmiɽad
    booka,bo-o-ka,1,boˈoka
    bookan,bo-o-kan,1,boˈokan
    akea,a-ke-a,1,aˈkea
    igay,i-gay,0,ˈigaɪ
    oyse,oy-se,0,ˈoɪse

Note:
If the implementation uses /ɾ/ rather than /ɽ/, adjust expected IPA consistently and document why. The grammar table uses a flap symbol. The important thing is consistency.

Add tests for consonant mapping:
    x -> ʃ
    j -> ʒ
    c -> t͡ʃ
    s -> s
    g -> g
    q -> k
    h -> h
    r -> chosen flap/trill symbol

Add tokenizer tests:
    "At tixe Mirad." -> ["At", "tixe", "Mirad", "."]
    "vyaa, vyaay!" -> ["vyaa", ",", "vyaay", "!"]

Add validation tests:
    Words containing old diacritics should raise UnsupportedLegacyOrthographyError or return a warning result.
    Empty input should produce empty output, not crash.
    Unknown symbols should be preserved or reported clearly.

Verification stages:
Stage 1: Syllable verification
- Run all syllabification tests.
- Confirm grammar examples match exactly.

Stage 2: Stress verification
- Confirm stress index equals last non-final syllable for all multisyllabic words.
- Confirm final glided vowels do not steal stress when they are in final syllables, e.g. igay -> i-gay with stress on i.

Stage 3: IPA verification
- Confirm each word’s IPA matches expected output.
- Confirm x/j/c/s are not accidentally interpreted with English spelling values.
- Confirm adjacent vowels remain separate syllables, e.g. booka -> bo-o-ka.

Stage 4: eSpeak verification
- Print generated eSpeak phoneme input with --espeak.
- Synthesize WAV.
- Listen to minimal pairs or contrast sets.
- Adjust eSpeak phoneme symbols only in espeak_backend.py, not in phonology.py.

Stage 5: End-to-end verification
Run:
    python -m mirad_tts.cli --debug "At tixe Mirad."
    python -m mirad_tts.cli --ipa "At tixe Mirad."
    python -m mirad_tts.cli --wav out.wav "At tixe Mirad."

README requirements:
Update README.md with:
1. Project purpose.
2. Explanation that this uses newer Mirad Grammar pronunciation.
3. Warning that older Mirad/Unilingua orthography is not supported in v1.
4. Installation instructions.
5. eSpeak NG installation instructions:
   - Ubuntu/Debian: sudo apt install espeak-ng
   - macOS: brew install espeak-ng
   - Windows: mention that espeak-ng must be installed and available on PATH
6. CLI examples.
7. IPA examples.
8. Known limitations:
   - robotic eSpeak voice
   - proper names and foreign words are approximate
   - numbers not fully spoken in v1
   - legacy accented orthography not implemented
   - eSpeak phoneme mapping may need tuning by voice
9. Reference docs:
   - data/mirad-docs/Mirad_grammer.md as authoritative for v1
   - data/mirad-docs/Mirad.md as legacy reference only

Implementation steps:

Step 1: Add pyproject.toml.
- Configure package under src.
- Add pytest.
- Add console script if convenient:
    mirad-tts = "mirad_tts.cli:main"

Step 2: Implement phonology.py.
- Define vowels, glides, consonant maps, supported alphabet, legacy diacritic set.
- Define IPA maps.
- Define custom exceptions:
    UnsupportedLegacyOrthographyError
    InvalidMiradWordWarning or similar

Step 3: Implement tokenizer.py.
- Regex tokenize text into word, number, punctuation.
- Do not lose punctuation.
- Preserve original text.

Step 4: Implement syllabify.py.
- Implement vowel nucleus detection.
- Use grammar examples as test anchors.
- Return structured Syllable objects.
- Add stress assignment.

Step 5: Implement ipa.py.
- Convert Syllable objects to IPA.
- Add primary stress mark before stressed syllable.
- Implement text_to_ipa.

Step 6: Implement espeak_backend.py.
- Define internal phone to eSpeak mnemonic mapping.
- Generate [[...]] phoneme input.
- Add synthesize_to_wav using subprocess.run.
- Check that espeak-ng exists using shutil.which.
- Raise a clear error if missing.

Step 7: Implement cli.py.
- argparse options:
    --ipa
    --syllables
    --espeak
    --debug
    --wav PATH
    --voice VOICE default en
- If no mode specified, print IPA by default.
- Make --wav synthesize audio.

Step 8: Add tests.
- Add pytest tests for tokenizer, syllabification, IPA, eSpeak string generation.
- Do not require espeak-ng installed for ordinary unit tests.
- Mark actual audio synthesis tests as integration tests and skip if espeak-ng is not on PATH.

Step 9: Run verification.
- pytest
- python -m mirad_tts.cli --debug "At tixe Mirad."
- python -m mirad_tts.cli --debug "ama ayma aymsea pixwa upayo vyaa vyaay vay tambwa"
- python -m mirad_tts.cli --wav out.wav "At tixe Mirad."

Step 10: Document unresolved decisions.
In README.md, explicitly document:
- whether r is represented as /ɽ/ or /ɾ/
- how aw is represented in IPA
- which eSpeak voice is used by default
- known mismatch between ideal Mirad phonology and eSpeak’s available voice/phoneme inventory

Quality bar:
The first successful version does not need to sound natural. It must be phonologically inspectable and deterministic. The target is:
- correct tokenization
- correct Mirad syllabification for grammar examples
- correct regular stress
- correct IPA output
- a working eSpeak WAV backend
- documented limitations

Do not:
- train a neural TTS model
- use machine learning
- scrape the web
- depend on online APIs
- silently apply English pronunciation rules
- silently mix old Mirad/Unilingua pronunciation with newer Mirad Grammar pronunciation

Deliverables:
1. New Python package under src/mirad_tts.
2. Working CLI.
3. Test suite.
4. pronunciation_tests.csv.
5. Updated README.md.
6. Clear comments explaining the Mirad phonology assumptions.
7. A short note in README explaining that IPA is the verification layer, while eSpeak NG uses its own phoneme mnemonic backend.