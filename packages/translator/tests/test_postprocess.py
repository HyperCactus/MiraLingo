"""
Tests for mirad_translator.postprocess — deterministic Mirad post-processor.

Coverage:
  - A1: be → bi possessive construction (index 0)
  - A2: ge → vyel comparative (index 3)
  - B1/B2: progressive -eye flag (flagged only)
  - C1-C6: lexicon gaps (flagged only, not auto-fixed)
  - D1-D7: structural/hallucination (flagged only, not auto-fixed)
  - Structural cleanups: whitespace, meta-commentary
  - Conservative error flags
"""

import pytest
from mirad_translator.postprocess import (
    postprocess_mirad,
    flag_conservative_errors,
    _fix_comparative_ge,
    _fix_possessive_be,
    _strip_meta_commentary,
    _normalize_whitespace_and_punctuation,
)


# ---------------------------------------------------------------------------
# A1: be ↔ bi — possessive construction
# ---------------------------------------------------------------------------

def test_be_to_bi_possessive_construction():
    """
    A1 (index 0): 'be' → 'bi' in possessive construction
    Gold:  His se ha gwa aga tam bi yata yubem.
    Pred:  His se ha gwa aga tam be yata yubyem.
    Fix:   tam be yata → tam bi yata
    """
    predicted = "His se ha gwa aga tam be yata yubyem."
    result = postprocess_mirad(predicted)
    # be between 'tam' (noun) and 'yata' (possessive determiner) → bi
    assert "tam bi yata" in result
    assert "tam be yata" not in result


def test_be_not_changed_when_copula():
    """
    'be' should NOT be changed when used as copula (sentence internal).
    e.g. 'His se gwa aga' — se is the copula, not 'be'.
    This test ensures we don't over-correct.
    """
    text = "Hia drar se oga."
    result = postprocess_mirad(text)
    assert result == "Hia drar se oga."


def test_be_not_changed_without_determiner_after():
    """
    'be' between a noun and a non-determiner word should be preserved.
    This guards against false positives on other uses of 'be'.
    """
    text = "ha duhos se be"
    result = postprocess_mirad(text)
    assert result == "ha duhos se be"


def test_be_to_bi_direct():
    """Direct test of the possessive fix function."""
    text = "tam be yata yubyem"
    result = _fix_possessive_be(text)
    assert result == "tam bi yata yubyem"


# ---------------------------------------------------------------------------
# A2: ge → vyel — comparative particle
# ---------------------------------------------------------------------------

def test_ge_to_vyel_comparative():
    """
    A2 (index 3): 'ge' → 'vyel' in comparative construction.
    Pred:  Hia tam voy se ge aga ge atas.
    Fix:   ...aga ge atas → ...aga vyel atas (ge replaced with vyel)
    """
    predicted = "Hia tam voy se ge aga ge atas."
    result = postprocess_mirad(predicted)
    assert "vyel" in result
    # The comparative ge fix replaces the second 'ge' word (with any trailing
    # punctuation) with 'vyel' (without trailing period), so no trailing period.
    assert result == "Hia tam voy se ge aga vyel atas."


def test_ge_to_vyel_gwa_comparative():
    """
    Comparative with gwa degree marker + adjective + ge.
    Gold:  Hia tam voy se ge aga vyel atas.
    Pred:  Hia tam voy se ge aga ge atas.  (double ge is wrong)
    Expected fix: ge aga ge → ge aga vyel
    """
    predicted = "Hia tam voy se ge aga ge atas."
    result = _fix_comparative_ge(predicted)
    assert "vyel" in result
    assert "ge aga vyel" in result


def test_ge_not_changed_without_comparative():
    """
    'ge' should NOT be changed when not in a comparative construction.
    e.g. 'at texe' (I think) — ge is not comparative there.
    """
    text = "at texe av hus at amilk"
    result = postprocess_mirad(text)
    # 'ge' should not appear — but if it does, no transformation
    assert "vyel" not in result


def test_ge_to_vyel_direct():
    """Direct test of the comparative fix function."""
    text = "Hia tam voy se ge aga ge atas."
    result = _fix_comparative_ge(text)
    assert "ge aga vyel" in result


# ---------------------------------------------------------------------------
# B: Progressive morphology — flagged only, not auto-corrected
# ---------------------------------------------------------------------------

def test_progressive_eye_flag_ie_ending():
    """
    B2 (index 34): '-ie' verb ending that might be truncated -eye.
    Pred:  Mamilie.
    Flagged but not auto-corrected.
    """
    text = "Mamilie."
    flags = flag_conservative_errors(text)
    assert any("progressive_suffix_truncation" in f for f in flags)


def test_progressive_eye_no_flag():
    """
    Normal '-eye' ending should not be flagged.
    """
    text = "Ha tobud gaj tujeye."
    flags = flag_conservative_errors(text)
    assert not any("progressive" in f for f in flags)


# ---------------------------------------------------------------------------
# C: Lexicon gaps — flagged only, not auto-corrected
# ---------------------------------------------------------------------------

def test_lexicon_gap_ese_amilk_not_autofixed():
    """
    C3 (index 11): 'ese' → 'amilk' lexicon error.
    The post-processor should NOT silently replace amilk back to ese;
    it has no lexicon knowledge. This test confirms no change.
    """
    text = "At texe, av hus at amilk."
    result = postprocess_mirad(text)
    assert "amilk" in result  # Should remain unchanged


def test_lexicon_gap_has_insertion_not_autofixed():
    """
    C1 (index 2): 'has' insertion error.
    'has' is a valid pronoun — the error is contextual (wrong placement).
    The post-processor does NOT remove it since it would be a false-positive
    in many correct sentences.
    """
    text = "Et yefe xer has gwa ig."
    result = postprocess_mirad(text)
    # has is preserved — lexicon substitution cannot be auto-corrected
    assert "has" in result


def test_lexicon_gap_ted_twed_not_autofixed():
    """
    C4 (index 16): 'ted' → 'twed' — no auto-fix.
    """
    text = "At voy se eta twed."
    result = postprocess_mirad(text)
    assert "twed" in result  # left unchanged


# ---------------------------------------------------------------------------
# D: Structural/hallucination — flagged only, not auto-corrected
# ---------------------------------------------------------------------------

def test_verb_subject_inversion_flag():
    """
    D5 (index 23, 35): Subject-verb order inversion.
    Voy at sentence start suggests SVO inversion (should be At voy...).
    """
    text = "Voy tepoboxe at."
    flags = flag_conservative_errors(text)
    assert any("order_inversion" in f for f in flags)


def test_no_order_inversion_flag():
    """
    Normal sentence starting with 'Voy' in correct position should not flag.
    e.g. Hia tam voy se ge aga vyel atas — voy is before se (copula), fine.
    """
    text = "Hia tam voy se ge aga vyel atas."
    flags = flag_conservative_errors(text)
    assert not any("order_inversion" in f for f in flags)


def test_hallucination_not_modified():
    """
    D1-D7: Hallucinated sentences are left unchanged (no lexicon to fix).
    Example D2 (index 12): 'Afu ha niut biksu!' has no overlap with gold.
    The postprocessor does not touch it.
    """
    text = "Afu ha niut biksu!"
    result = postprocess_mirad(text)
    assert result == "Afu ha niut biksu!"


# ---------------------------------------------------------------------------
# Structural cleanups
# ---------------------------------------------------------------------------

def test_strip_leading_mirad_prefix():
    """Leading 'Mirad:' style meta-commentary should be stripped."""
    text = "Mirad: His se ha gwa aga tam bi yata yubem."
    result = postprocess_mirad(text)
    assert not result.startswith("Mirad")


def test_strip_leading_arrow_prefix():
    """Leading '→' style meta-commentary should be stripped."""
    text = "→ His se ha gwa aga tam bi yata yubem."
    result = postprocess_mirad(text)
    assert not result.startswith("→")


def test_strip_trailing_paren_commentary():
    """Trailing parenthetical commentary should be stripped."""
    text = "His se ha gwa aga tam bi yata yubem. (translation)"
    result = postprocess_mirad(text)
    assert "(translation)" not in result


def test_strip_trailing_bracket_commentary():
    """Trailing bracket commentary should be stripped."""
    text = "His se ha gwa aga tam bi yata yubem [done]"
    result = postprocess_mirad(text)
    assert "[done]" not in result


def test_normalize_multiple_spaces():
    """Multiple spaces should collapse to one."""
    text = "His  se   ha  gwa  aga  tam."
    result = postprocess_mirad(text)
    assert "  " not in result


def test_normalize_period_before_exclamation():
    """Trailing period before exclamation should be removed."""
    text = "Hoogla iva se at van et upa!."
    result = postprocess_mirad(text)
    assert "!." not in result


def test_normalize_newlines_to_space():
    """Internal newlines should be normalized to spaces."""
    text = "His se ha gwa aga tam\nbi yata yubem"
    result = postprocess_mirad(text)
    assert "\n" not in result


# ---------------------------------------------------------------------------
# Integration: full error examples from taxonomy
# ---------------------------------------------------------------------------

def test_integration_index0_possessive():
    """Full integration test for A1 (index 0)."""
    predicted = "His se ha gwa aga tam be yata yubyem."
    result = postprocess_mirad(predicted)
    assert "tam bi yata" in result
    assert "yubyem" in result  # variant form preserved


def test_integration_index3_comparative():
    """Full integration test for A2 (index 3)."""
    predicted = "Hia tam voy se ge aga ge atas."
    result = postprocess_mirad(predicted)
    assert "vyel" in result
    assert "ge aga ge" not in result


def test_integration_no_change_for_correct():
    """A correct sentence should be unchanged."""
    gold = "His se ha gwa aga tam bi yata yubem."
    result = postprocess_mirad(gold)
    # possessive be was already bi, no change needed
    assert result == gold


def test_integration_flag_on_problematic():
    """Combined test: postprocess + flags."""
    predicted = "Mamilie."
    result = postprocess_mirad(predicted)
    flags = flag_conservative_errors(predicted)
    # result stays the same (no auto-fix)
    assert result == "Mamilie."
    assert any("progressive" in f for f in flags)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_string():
    """Empty input should return empty."""
    assert postprocess_mirad("") == ""
    assert postprocess_mirad("   ") == ""


def test_whitespace_only():
    result = postprocess_mirad("   \n  \t  ")
    assert result == ""


def test_single_word():
    """Single word should pass through unchanged."""
    assert postprocess_mirad("tam") == "tam"


def test_flag_returns_list():
    """flag_conservative_errors should always return a list."""
    flags = flag_conservative_errors("any text")
    assert isinstance(flags, list)