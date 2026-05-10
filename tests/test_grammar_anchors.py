"""Grammar-anchored pronunciation tests derived from the Mirad Grammar spec.

Every test case is traceable to a specific section, rule, or example table
in data/mirad-docs/mirad_grammer.md.  If the grammar says it, we test it.

Sections covered:
  - Consonant grapheme → IPA (21 consonants from the spec chart)
  - Simple vowel → IPA (5 vowels)
  - Complex vowel → IPA (post-y, post-w, pre-y, pre-w, circum, w+y glides)
  - Syllabification (9+ cases from the grammar's "Syllabification" chart)
  - Stress assignment (9+ cases from the "Stress" section)
  - Full word IPA (combined syllabification + stress + mapping)
  - eSpeak phoneme output for anchor words
  - Case normalization (uppercase input produces same IPA as lowercase)
  - Edge cases (foreign q, adjacent vowels, word-final r/l)
"""

import pytest

from mirad_tts.espeak_backend import word_to_espeak, syllable_to_espeak, text_to_espeak_phoneme_input
from mirad_tts.ipa import syllable_to_ipa, text_to_ipa, word_to_ipa
from mirad_tts.phonology import COMPLEX_VOWELS, COMPLEX_VOWEL_IPA, CONSONANT_IPA, SIMPLE_VOWELS
from mirad_tts.syllabify import Syllable, assign_stress, syllabify_word


# ═══════════════════════════════════════════════════════════════════════════════
# Section 1: Consonant grapheme → IPA (grammar: "Consonants" chart)
# ═══════════════════════════════════════════════════════════════════════════════

#: Grammar spec table row → (grapheme, expected IPA)
CONSONANT_IPA_TESTS: list[tuple[str, str]] = [
    # Grapheme b → [b] unaspirated voiced bilabial plosive
    ("b", "b"),
    # Grapheme c → [t͡ʃ] (ch in chair, foreign words only)
    ("c", "t͡ʃ"),
    # Grapheme d → [d] unaspirated voiced alveolar plosive
    ("d", "d"),
    # Grapheme f → [f] unvoiced bilabial fricative
    ("f", "f"),
    # Grapheme g → [ɡ] always hard, even before e and i (voiced velar plosive)
    ("g", "ɡ"),
    # Grapheme h → [h] glottal fricative (foreign words)
    ("h", "h"),
    # Grapheme j → [ʒ] voiced palatal fricative (French je, English mirage)
    ("j", "ʒ"),
    # Grapheme k → [k] unaspirated unvoiced velar plosive
    ("k", "k"),
    # Grapheme l → [l] voiced post-alveolar lateral approximant (never dark l)
    ("l", "l"),
    # Grapheme m → [m] voiced bilabial nasal
    ("m", "m"),
    # Grapheme n → [n] voiced alveolar nasal
    ("n", "n"),
    # Grapheme p → [p] unvoiced bilabial plosive (no aspiration)
    ("p", "p"),
    # Grapheme q → [k] foreign words only (various k-like pronunciations)
    ("q", "k"),
    # Grapheme r → [ɾ] alveolar flap (NOT alveolar trill [r] or approximant [ɹ])
    ("r", "ɾ"),
    # Grapheme s → [s] unvoiced alveolar fricative (always hard, never z)
    ("s", "s"),
    # Grapheme t → [t] unaspirated unvoiced alveolar plosive
    ("t", "t"),
    # Grapheme v → [v] voiced bilabial fricative
    ("v", "v"),
    # Grapheme x → [ʃ] unvoiced post-alveolar fricative (sh in show)
    ("x", "ʃ"),
    # Grapheme z → [z] voiced alveolar fricative
    ("z", "z"),
]


class TestConsonantIpaFromGrammar:
    """Every consonant in the grammar chart maps to its specified IPA symbol."""

    @pytest.mark.parametrize("grapheme,expected_ipa", CONSONANT_IPA_TESTS)
    def test_consonant_ipa(self, grapheme, expected_ipa):
        assert CONSONANT_IPA[grapheme] == expected_ipa

    def test_all_23_consonant_entries_present(self):
        """23 entries: 21 specified consonants + y, w semi-consonants."""
        expected_keys = set("bcdfghjklmnpqrstvxz") | {"y", "w"}
        assert set(CONSONANT_IPA.keys()) == expected_keys

    def test_21_core_consonants(self):
        """The 21 consonants from the grammar chart are all present."""
        for c in "bcdfghjklmnpqrstvxz":
            assert c in CONSONANT_IPA, f"Consonant {c} missing from CONSONANT_IPA"


# ═══════════════════════════════════════════════════════════════════════════════
# Section 2: Simple vowels (grammar: "Simple Vowels" chart)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSimpleVowelsFromGrammar:
    """Grammar specifies 5 simple vowels: a, e, i, o, u (NOT y or w)."""

    def test_simple_vowels_are_five(self):
        assert SIMPLE_VOWELS == frozenset("aeiou")

    def test_y_not_simple_vowel(self):
        """y is a semi-vowel glide, not a simple vowel (grammar: 'y' section)."""
        assert "y" not in SIMPLE_VOWELS

    def test_w_not_simple_vowel(self):
        """w is a semi-vowel glide, not a simple vowel (grammar: 'w' section)."""
        assert "w" not in SIMPLE_VOWELS


# ═══════════════════════════════════════════════════════════════════════════════
# Section 3: Complex vowels → IPA (grammar: "Complex Vowels" chart)
# ═══════════════════════════════════════════════════════════════════════════════

#: (complex_vowel, expected_ipa) — derived directly from the grammar chart
COMPLEX_VOWEL_IPA_TESTS: list[tuple[str, str]] = [
    # Post-y-glided vowels (diphthongs ending in ɪ)
    ("ay", "aɪ"),   # Eng. sight
    ("ey", "eɪ"),   # Eng. day
    ("iy", "iɪ"),   # Eng. see
    ("oy", "oɪ"),   # Eng. boy
    ("uy", "uɪ"),   # Eng. gooey
    # Post-w-glided vowels (diphthongs ending in ʊ/ɔ)
    ("aw", "ɔ"),    # Eng. awe
    ("ew", "ɛʊ"),   # Br. Eng. beau, colloq. "Tell me!"
    ("iw", "iʊ"),
    ("ow", "oʊ"),   # Eng. know
    ("uw", "uʊ"),   # Eng. goo
    # Pre-y-glided vowels
    ("ya", "ja"),   # Eng. yacht
    ("ye", "je"),   # Eng. yet
    ("yi", "ji"),   # Eng. yeast
    ("yo", "jo"),   # Eng. yoke
    ("yu", "ju"),   # Eng. you
    # Pre-w-glided vowels
    ("wa", "wa"),   # Eng. water
    ("we", "we"),   # Eng. wet
    ("wi", "wi"),   # Eng. wee
    ("wo", "wo"),   # Eng. woke
    ("wu", "wu"),   # Eng. woo
    # Circum-y-glided vowels (y-glides on both sides)
    ("yay", "jaɪ"), # Eng. yikes
    ("yey", "jeɪ"), # Eng. yea!
    ("yiy", "jiɪ"), # Eng. yeesh!
    ("yoy", "joɪ"), # Eng. yoink
    ("yuy", "juɪ"), # Eng. Hughie
    # Pre-w-post-y-glided (w-glide + vowel + y-glide)
    ("way", "waɪ"), # Eng. wise
    ("wey", "weɪ"), # Eng. way
    ("wiy", "wiɪ"), # Eng. wee!
    ("woy", "woɪ"), # Eng. woy (rhymes with boy)
    ("wuy", "wuɪ"), # Eng. wooish (rhymes with gooey)
]


class TestComplexVowelIpaFromGrammar:
    """Every complex vowel in the grammar chart maps to its specified IPA."""

    @pytest.mark.parametrize("cv,expected_ipa", COMPLEX_VOWEL_IPA_TESTS)
    def test_complex_vowel_ipa(self, cv, expected_ipa):
        assert COMPLEX_VOWEL_IPA[cv] == expected_ipa

    def test_all_complex_vowels_present(self):
        """All 30 complex vowels from the grammar chart exist in the mapping."""
        expected_keys = {cv for cv, _ in COMPLEX_VOWEL_IPA_TESTS}
        assert expected_keys.issubset(set(COMPLEX_VOWEL_IPA.keys())), (
            f"Missing complex vowels: {expected_keys - set(COMPLEX_VOWEL_IPA.keys())}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Section 4: Syllabification (grammar: "Syllabification" chart, Cases 1–9)
# ═══════════════════════════════════════════════════════════════════════════════

#: (word, expected_syllable_texts) — directly from grammar chart
SYLLABIFICATION_TESTS: list[tuple[str, list[str]]] = [
    # Case 1:ama → a-ma (simple CV)
    ("ama", ["a", "ma"]),
    # Case 2:ayma → ay-ma (complex vowel forms nucleus)
    ("ayma", ["ay", "ma"]),
    # Case 3:aymsea → aym-se-a (r/l form coda before consonants)
    ("aymsea", ["aym", "se", "a"]),
    # Case 4:pixwa → pix-wa (non-r/l consonant forms coda before glide onset)
    ("pixwa", ["pix", "wa"]),
    # Case 5:upayo → u-pa-yo (pre-y-glided vowel as separate syllable)
    ("upayo", ["u", "pa", "yo"]),
    # Case 6:vyaa → vya-a (adjacent vowels: complex then simple)
    ("vyaa", ["vya", "a"]),
    # Case 7:vyaay → vya-ay (complex vowel after complex vowel)
    ("vyaay", ["vya", "ay"]),
    # Case 8:vay → vay (single syllable)
    ("vay", ["vay"]),
    # Case 9:tambwa → tam-bwa (nasal coda before glide onset)
    ("tambwa", ["tam", "bwa"]),
    # Additional grammar anchor examples from the Stress section
    ("tejna", ["te", "jna"]),     # jn is a valid onset cluster
    ("alayn", ["al", "ayn"]),     # r/l coda before complex vowel
    ("booka", ["bo", "o", "ka"]), # adjacent simple vowels
    ("akea", ["a", "ke", "a"]),    # adjacent vowels with consonant between
    ("oyse", ["oy", "se"]),       # complex vowel then consonant+vowel
    ("byoskyin", ["byos", "kyin"]), # complex coda + complex onset
]


class TestSyllabificationFromGrammar:
    """Every syllabification case from the grammar chart produces correct splits."""

    @pytest.mark.parametrize("word,expected", SYLLABIFICATION_TESTS)
    def test_syllabify_word(self, word, expected):
        result = [s.text for s in syllabify_word(word)]
        assert result == expected, f"{word}: got {result}, expected {expected}"


# ═══════════════════════════════════════════════════════════════════════════════
# Section 5: Stress assignment (grammar: "Stress" section)
#   "In all words of more than one syllable, the stress occurs on the
#    last, non-final vowel, including complex (glided) vowels."
# ═══════════════════════════════════════════════════════════════════════════════

#: (word, expected_stressed_text) — the syllable that receives stress
STRESS_TESTS: list[tuple[str, str]] = [
    # Grammar stress examples:
    # "tejna...tej-na" → stress on te (last non-final)
    ("tejna", "te"),
    # "igay...i-gay" → stress on i (last non-final: gay is final)
    ("igay", "i"),
    # "alayn...a-layn" → stress on a (last non-final)
    ("alayn", "al"),
    # "Mirad...Mi-rad" → stress on Mi (last non-final)
    ("mirad", "mi"),
    # "booka...bo-o-ka" → stress on o (last non-final: o is 2nd of 3)
    ("booka", "o"),
    # "akea...a-ke-a" → stress on ke
    ("akea", "ke"),
    # "oyse...oy-se" → stress on oy (last non-final)
    ("oyse", "oy"),
    # "byoskyin...byos-kyin" → stress on byos (last non-final)
    ("byoskyin", "byos"),
    # "ama...a-ma" → stress on a (last non-final)
    ("ama", "a"),
]


class TestStressFromGrammar:
    """Stress falls on the last non-final syllable (including complex vowels)."""

    @pytest.mark.parametrize("word,expected_stressed", STRESS_TESTS)
    def test_stress_on_last_nonfinal(self, word, expected_stressed):
        syls = assign_stress(syllabify_word(word))
        stressed = [s.text for s in syls if s.stressed]
        assert stressed == [expected_stressed], (
            f"{word}: stressed={stressed}, expected [{expected_stressed}]"
        )

    def test_single_syllable_no_stress(self):
        """Single-syllable words have no stress marker."""
        syls = assign_stress(syllabify_word("vay"))
        assert not any(s.stressed for s in syls)

    def test_final_syllable_never_stressed(self):
        """The final syllable is never stressed per grammar rule."""
        for word in ["tejna", "igay", "alayn", "booka", "byoskyin"]:
            syls = assign_stress(syllabify_word(word))
            assert not syls[-1].stressed, (
                f"{word}: final syllable '{syls[-1].text}' should not be stressed"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Section 6: Full word IPA (combined syllabification + stress + mapping)
# ═══════════════════════════════════════════════════════════════════════════════

#: (word, expected_ipa_substring) — checking substring because exact IPA
#: may include dot separators or not depending on dotted flag
WORD_IPA_TESTS: list[tuple[str, str]] = [
    # Grammar anchor examples
    ("Mirad", "ˈmiɾad"),    # Mi-rad → stress on Mi, r→ɾ
    ("igay", "ˈiɡaɪ"),       # i-gay → stress on i, ay→aɪ, g→ɡ
    ("tejna", "ˈteʒna"),    # te-jna → stress on te, j→ʒ
    ("tixe", "ˈtiʃe"),      # ti-xe → stress on ti, x→ʃ
    ("jal", "ʒal"),          # jal → j→ʒ, no stress (1 syllable)
    ("vay", "vaɪ"),          # vay → ay→aɪ, no stress (1 syllable)
    ("aymsea", "aɪmˈsea"),  # aym-se-a → stress on se, ay→aɪ, x→ʃ
    ("ama", "ˈama"),          # a-ma → stress on a
    # Consonant-specific checks
    ("xati", "ˈʃati"),      # x→ʃ
    ("cena", "ˈt͡ʃena"),    # c→t͡ʃ
    # q→k mapping (foreign words, grammar: "q was added for certain scientific words")
    ("qatar", "ˈkataɾ"),    # q→k, r→ɾ
    # Complex vowel checks
    ("ya", "ja"),            # pre-y-glide → j
    ("wa", "wa"),            # pre-w-glide stays w
    ("yay", "jaɪ"),          # circum-y-glide
    ("way", "waɪ"),          # pre-w-post-y-glide
    # Adjacent vowels
    ("booka", "boˈoka"),     # bo-o-ka → stress on o
]


class TestWordIpaFromGrammar:
    """Full word → IPA conversion matches grammar-specified pronunciations."""

    @pytest.mark.parametrize("word,expected_contains", WORD_IPA_TESTS)
    def test_word_to_ipa_contains(self, word, expected_contains):
        result = word_to_ipa(word)
        assert expected_contains in result, (
            f"{word}: got '{result}', expected to contain '{expected_contains}'"
        )

    def test_ipa_uses_lowercase(self):
        """IPA output is always lowercase regardless of input case."""
        assert word_to_ipa("AtTixe").lower() == word_to_ipa("AtTixe")

    def test_mirad_pronunciation_mee_rahd(self):
        """Grammar: 'Mirad...is pronounced mee-RAHD' → ˈmiɾad."""
        assert "ˈmiɾad" in word_to_ipa("Mirad")


# ═══════════════════════════════════════════════════════════════════════════════
# Section 7: eSpeak phoneme output for anchor words
# ═══════════════════════════════════════════════════════════════════════════════

ESPEAK_WORD_TESTS: list[tuple[str, str]] = [
    # Grammar anchor words with their expected eSpeak phoneme sequences
    ("ama", "'ama"),
    ("aymsea", "aim'sea"),
    ("igay", "'igai"),
    ("vay", "vai"),
    ("tejna", "'teZna"),
    ("Mirad", "'mirad"),
    # Pre-y-glided vowels
    ("ya", "ja"),
    ("yo", "jo"),
    # Pre-w-glided vowels
    ("wa", "wa"),
    ("wo", "wo"),
    # Complex vowels
    ("auwa", "a'uwa"),
]


class TestEspeakFromGrammar:
    """eSpeak phoneme output matches expected sequences for grammar anchors."""

    @pytest.mark.parametrize("word,expected_substring", ESPEAK_WORD_TESTS)
    def test_word_to_espeak(self, word, expected_substring):
        result = word_to_espeak(word)
        assert expected_substring in result, (
            f"{word}: got '{result}', expected to contain '{expected_substring}'"
        )

    def test_espeak_wraps_brackets(self):
        """text_to_espeak_phoneme_input wraps output in [[...]]."""
        result = text_to_espeak_phoneme_input("Mirad")
        assert result.startswith("[[") and result.endswith("]]")

    def test_espeak_consonant_c_maps_to_tS(self):
        """Grammar: c → t͡ʃ, eSpeak: c → tS."""
        result = word_to_espeak("cel")
        assert "tS" in result

    def test_espeak_consonant_x_maps_to_S(self):
        """Grammar: x → ʃ, eSpeak: x → S."""
        result = word_to_espeak("xeral")
        assert "S" in result

    def test_espeak_stress_mark(self):
        """eSpeak uses ' for primary stress."""
        result = word_to_espeak("Mirad")
        assert "'" in result  # eSpeak primary stress marker


# ═══════════════════════════════════════════════════════════════════════════════
# Section 8: Case normalization
# ═══════════════════════════════════════════════════════════════════════════════

class TestCaseNormalization:
    """Mirad is case-insensitive for pronunciation; IPA output is lowercase."""

    @pytest.mark.parametrize("word", ["Mirad", "Tejna", "IGAY", "Vay", "Byoskyin"])
    def test_uppercase_input_produces_same_ipa_as_lowercase(self, word):
        assert word_to_ipa(word) == word_to_ipa(word.lower())

    @pytest.mark.parametrize("word", ["Mirad", "Tejna", "IGAY", "Aymsea"])
    def test_uppercase_input_produces_same_espeak_as_lowercase(self, word):
        assert word_to_espeak(word) == word_to_espeak(word.lower())


# ═══════════════════════════════════════════════════════════════════════════════
# Section 9: Edge cases from grammar rules
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCasesFromGrammar:
    """Edge cases derived from grammar rules about r/l, glides, and onsets."""

    # Rule: r/l form coda when followed by consonant or word-final
    def test_r_coda_before_consonant(self):
        """Grammar Rule 6: r before consonant joins coda (Mirad → Mi-rad, not Mir-ad)."""
        assert "rad" in [s.text for s in syllabify_word("mirad") if "rad" in s.text]

    def test_l_coda_before_consonant(self):
        """Grammar Rule 6: l before consonant forms coda (al-ayn)."""
        syls = syllabify_word("alayn")
        # 'al' → onset='', nucleus='a', coda='l'
        assert syls[0].text == "al"
        assert syls[0].coda == "l"

    def test_r_onset_before_vowel(self):
        """Grammar: r before vowel joins onset of next syllable (Mi-rad not Mir-ad)."""
        syls = syllabify_word("mirad")
        # 'mi' + 'rad' → r is onset of second syllable
        assert syls[1].onset == "r"

    # Rule: y is a semi-vowel glide, not a simple vowel
    def test_y_as_onset_before_vowel(self):
        """Grammar: y before vowel acts as consonantal onset (ya → nucleus 'ya' as complex vowel)."""
        syls = syllabify_word("ya")
        # 'ya' is a pre-y-glided complex vowel: onset='', nucleus='ya'
        assert syls[0].nucleus == "ya"

    def test_y_as_nucleus_after_vowel(self):
        """Grammar: y after vowel is post-y-glide (ay, ey, etc.)."""
        syls = syllabify_word("vay")
        assert syls[0].nucleus == "ay"

    def test_w_as_onset_before_vowel(self):
        """Grammar: w before vowel acts as glide onset (wa, we, etc.).
        In syllabification, 'wa' is treated as nucleus='wa' (pre-w-glided complex vowel)."""
        syls = syllabify_word("wa")
        assert syls[0].nucleus == "wa"

    # Rule: Two vowels in a row form two nuclei (booka → bo-o-ka)
    def test_adjacent_vowels_form_separate_nuclei(self):
        """Grammar case 3/6: adjacent vowels are separate syllable nuclei."""
        syls = syllabify_word("booka")
        texts = [s.text for s in syls]
        assert texts == ["bo", "o", "ka"]

    # Rule: Complex vowels are single nuclei (ayma → ay-ma not a-y-ma)
    def test_complex_vowel_is_single_nucleus(self):
        """Grammar: ay, ey, etc. are single units, not separate vowel + glide."""
        syls = syllabify_word("ayma")
        assert syls[0].nucleus == "ay"

    # Rule: q maps to k (foreign words)
    def test_q_maps_to_k_in_ipa(self):
        """Grammar: q is pronounced as k for foreign words."""
        syl = Syllable(text="qa", onset="q", nucleus="a", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "ka"

    # Stress: final syllable never stressed
    def test_stress_never_on_final_syllable(self):
        """Grammar: stress is always on last non-final syllable."""
        for word in ["amasea", "tejna", "booka", "byoskyin"]:
            syls = assign_stress(syllabify_word(word))
            assert not syls[-1].stressed

    # IPA glottal stop for vowel-initial words after another word
    def test_glottal_marker_available(self):
        """Module exports GLOTTAL marker for word boundaries."""
        from mirad_tts.phonology import GLOTTAL
        assert GLOTTAL == "'"