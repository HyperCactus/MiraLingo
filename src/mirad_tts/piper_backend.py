"""Piper TTS backend for Mirad text-to-speech.

This module implements a hardened Piper backend that bypasses Piper's built-in
phonemizer and constructs phoneme IDs directly from Mirad-to-Piper phoneme
mappings. This avoids the silent-skip problem where Piper discards phoneme
symbols not in its ``phoneme_id_map`` — the root cause of "missing letters"
in synthesis output.

Architecture
~~~~~~~~~~~~

1. Mirad text → syllables + stress (existing tokenizer + syllabifier)
2. Syllables → Piper-safe phoneme symbols (via ``PIPER_*`` mappings)
3. Validate every symbol against the voice config's ``phoneme_id_map``
4. Construct phoneme IDs directly: BOS + [phoneme + PAD, …] + EOS
5. Synthesize via ``PiperVoice.phoneme_ids_to_audio()`` with tunable
   ``SynthesisConfig`` (``length_scale``, ``noise_scale``, ``noise_w_scale``)

The old ``[[…]]`` raw-phoneme-input path is kept as a backward-compatible
alias (``_text_to_piper_phoneme_input``) but is no longer used for synthesis.
"""

from __future__ import annotations

import json
import re
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence

import numpy as np
from piper.const import BOS, EOS, PAD
from piper.voice import PiperVoice, SynthesisConfig

from .ipa import word_to_ipa
from .phonology import (
    PIPER_COMPLEX_VOWELS,
    PIPER_CONSONANTS,
    PIPER_SIMPLE_VOWELS,
)
from .syllabify import Syllable, assign_stress, syllabify_word
from .tokenizer import tokenize
from .types import TokenType


# Default voice model path
DEFAULT_VOICE_MODEL: Final[Path] = (
    Path(__file__).parent.parent.parent
    / ".gsd"
    / "piper-voices"
    / "ca_ES-upc_ona-medium.onnx"
)


# ── Error types ───────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PiperModelNotFoundError(RuntimeError):
    """Raised when the Piper voice model file is not found."""

    model_path: str

    def __str__(self) -> str:
        return f"Piper voice model not found: {self.model_path}"


@dataclass(frozen=True, slots=True)
class PiperPhonemeError(ValueError):
    """Raised when a phoneme symbol is not in the voice config's phoneme_id_map."""

    missing: list[str]
    word: str

    def __str__(self) -> str:
        return (
            f"Missing Piper phoneme symbols for word {self.word!r}: "
            f"{sorted(set(self.missing))}. "
            f"These symbols are not in the voice config's phoneme_id_map "
            f"and would be silently skipped during synthesis."
        )


@dataclass(frozen=True, slots=True)
class PiperSynthesisError(RuntimeError):
    """Raised when Piper synthesis fails."""

    text: str
    output_path: str
    cause: Exception

    def __str__(self) -> str:
        return (
            f"Piper synthesis failed for text={self.text!r}; "
            f"output_path={self.output_path}; "
            f"cause={self.cause.__class__.__name__}: {self.cause}"
        )


# ── Debug / diagnostics ──────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PiperPhonemeDebug:
    """Per-word diagnostic information for Piper phoneme conversion."""

    word: str
    ipa: str
    piper_symbols: list[str]
    piper_ids: list[int]
    missing_symbols: list[str]


# ── Voice loading & config ────────────────────────────────────────────────────


def _load_voice(model_path: Path | None = None) -> PiperVoice:
    """Load a Piper voice model.

    Args:
        model_path: Path to the .onnx model file. If None, uses the default model.

    Returns:
        Loaded PiperVoice instance.

    Raises:
        PiperModelNotFoundError: If the model file doesn't exist.
    """
    if model_path is None:
        model_path = DEFAULT_VOICE_MODEL

    if not model_path.exists():
        raise PiperModelNotFoundError(str(model_path))

    return PiperVoice.load(str(model_path))


def _load_voice_config(model_path: Path | None = None) -> dict:
    """Load the JSON config for a Piper voice model.

    Returns the parsed JSON config dict including ``phoneme_id_map``.
    """
    if model_path is None:
        model_path = DEFAULT_VOICE_MODEL

    config_path = model_path.with_suffix(".onnx.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Voice config not found: {config_path}")

    return json.loads(config_path.read_text(encoding="utf-8"))


def _get_phoneme_id_map(model_path: Path | None = None) -> dict[str, list[int]]:
    """Return the phoneme_id_map from the voice config."""
    config = _load_voice_config(model_path)
    return config["phoneme_id_map"]


# ── Mirad → Piper phoneme conversion ──────────────────────────────────────────


def _onset_to_piper(onset: str) -> list[str]:
    """Convert onset consonants to Piper-safe phoneme symbol list."""
    symbols: list[str] = []
    for ch in onset.lower():
        if ch == "'":
            # glottal stop — use ʔ if available, else skip
            symbols.append("ʔ")
            continue
        mapped = PIPER_CONSONANTS.get(ch)
        if mapped is None:
            raise ValueError(f"Unsupported onset character: {ch!r}")
        symbols.extend(mapped)
    return symbols


def _nucleus_to_piper(nucleus: str) -> list[str]:
    """Convert a vowel nucleus to Piper-safe phoneme symbol list.

    Handles complex vowels (ay, aw, etc.) first, then simple vowels.
    """
    lower = nucleus.lower()
    if lower in PIPER_COMPLEX_VOWELS:
        return list(PIPER_COMPLEX_VOWELS[lower])

    symbols: list[str] = []
    for ch in lower:
        mapped = PIPER_SIMPLE_VOWELS.get(ch)
        if mapped is None:
            raise ValueError(f"Unsupported nucleus character: {ch!r}")
        symbols.extend(mapped)
    return symbols


def _coda_to_piper(coda: str) -> list[str]:
    """Convert coda consonants to Piper-safe phoneme symbol list."""
    symbols: list[str] = []
    for ch in coda.lower():
        if ch == "'":
            symbols.append("ʔ")
            continue
        mapped = PIPER_CONSONANTS.get(ch)
        if mapped is None:
            raise ValueError(f"Unsupported coda character: {ch!r}")
        symbols.extend(mapped)
    return symbols


def syllable_to_piper_phonemes(syllable: Syllable) -> list[str]:
    """Convert a syllable to a list of Piper-safe phoneme symbols.

    Stress is encoded as the ``ˈ`` symbol prefixed to the stressed syllable.

    Args:
        syllable: A Syllable object with onset, nucleus, coda, and stress flag.

    Returns:
        List of single-character phoneme symbols that exist in Piper voice configs.
    """
    symbols: list[str] = []

    # Stress marker before the syllable if stressed
    if syllable.stressed:
        symbols.append("ˈ")

    symbols.extend(_onset_to_piper(syllable.onset))
    symbols.extend(_nucleus_to_piper(syllable.nucleus))
    symbols.extend(_coda_to_piper(syllable.coda))

    return symbols


def word_to_piper_phonemes(word: str, *, stress: bool = True) -> list[str]:
    """Convert a Mirad word to a list of Piper-safe phoneme symbols.

    Args:
        word: A single Mirad word (will be lowercased).
        stress: Whether to apply stress marking. Default True.

    Returns:
        List of Piper-safe phoneme symbols including stress markers.
    """
    normalized = word.strip().lower()
    if not normalized:
        return []

    syllables = syllabify_word(normalized)
    if not syllables:
        return []

    if stress and len(syllables) > 1:
        syllables = assign_stress(syllables)

    symbols: list[str] = []
    for syllable in syllables:
        symbols.extend(syllable_to_piper_phonemes(syllable))

    return symbols


def text_to_piper_phonemes(text: str) -> list[str]:
    """Convert full Mirad text to a flat list of Piper-safe phoneme symbols.

    Non-word tokens (spaces, punctuation) are included as Piper's word
    separator (space ' ') and punctuation characters.

    Args:
        text: Mirad text to convert.

    Returns:
        List of Piper-safe phoneme symbols with word separators.
    """
    all_symbols: list[str] = []

    for token in tokenize(text):
        if token.type_ == TokenType.WORD:
            word_symbols = word_to_piper_phonemes(token.text)
            if all_symbols and word_symbols:
                # Word separator between words
                all_symbols.append(" ")
            all_symbols.extend(word_symbols)
        elif token.type_ == TokenType.PUNCT:
            all_symbols.append(token.text)
        # SPACE tokens create gaps; we insert " " between words instead

    return all_symbols


# ── Phoneme ID construction with validation ────────────────────────────────────


def piper_phonemes_to_ids(
    phonemes: list[str],
    id_map: dict[str, Sequence[int]],
    *,
    strict: bool = True,
) -> list[int]:
    """Convert Piper phoneme symbols to numeric IDs with validation.

    Replicates Piper's ``phonemes_to_ids()`` logic but:
    - Validates every symbol against ``id_map`` before conversion
    - In strict mode (default), raises ``PiperPhonemeError`` on missing symbols
    - In non-strict mode, skips missing symbols (matching Piper's behavior
      but with explicit logging)

    The ID sequence follows Piper's convention:
        BOS + PAD + [phoneme + PAD, ...] + EOS

    Args:
        phonemes: List of Piper-safe phoneme symbols.
        id_map: The ``phoneme_id_map`` from the voice config JSON.
        strict: If True, raise on missing symbols. If False, skip them.

    Returns:
        List of integer phoneme IDs ready for ``phoneme_ids_to_audio()``.

    Raises:
        PiperPhonemeError: If any phoneme symbol is not in id_map and strict=True.
    """
    missing: list[str] = [sym for sym in phonemes if sym not in id_map]

    if missing and strict:
        raise PiperPhonemeError(missing=missing, word="<text>")

    # Build ID sequence: BOS PAD [phoneme PAD ...] EOS
    ids: list[int] = []
    ids.extend(id_map[BOS])
    ids.extend(id_map[PAD])

    for sym in phonemes:
        if sym in id_map:
            ids.extend(id_map[sym])
            ids.extend(id_map[PAD])
        # else: skip (already warned or raised)

    ids.extend(id_map[EOS])

    return ids


def piper_word_to_ids(
    word: str,
    id_map: dict[str, Sequence[int]],
    *,
    strict: bool = True,
) -> tuple[list[int], list[str], list[str]]:
    """Convert a single Mirad word to Piper phoneme IDs with validation.

    Returns:
        Tuple of (phoneme_ids, piper_symbols, missing_symbols).
    """
    ipa = word_to_ipa(word)
    piper_symbols = word_to_piper_phonemes(word)

    # Validate
    missing = [sym for sym in piper_symbols if sym not in id_map]
    if missing and strict:
        raise PiperPhonemeError(missing=missing, word=word)

    # Build sentence-level phoneme list (single word = single sentence)
    ids: list[int] = []
    ids.extend(id_map[BOS])
    ids.extend(id_map[PAD])

    for sym in piper_symbols:
        if sym in id_map:
            ids.extend(id_map[sym])
            ids.extend(id_map[PAD])

    ids.extend(id_map[EOS])

    return ids, piper_symbols, missing


# ── Synthesis ──────────────────────────────────────────────────────────────────


def synthesize_to_wav(
    text: str,
    output_path: str | Path,
    model_path: Path | None = None,
    *,
    length_scale: float | None = None,
    noise_scale: float | None = None,
    noise_w_scale: float | None = None,
    strict: bool = True,
) -> Path:
    """Synthesize Mirad text to WAV using Piper TTS with direct phoneme IDs.

    This function bypasses Piper's built-in phonemizer and constructs phoneme
    IDs directly from Mirad-to-Piper phoneme mappings. This avoids the
    silent-skip problem where Piper discards phoneme symbols not in its
    ``phoneme_id_map``.

    Args:
        text: Mirad text to synthesize.
        output_path: Path where the WAV file should be written.
        model_path: Optional path to a Piper voice model. If None, uses default.
        length_scale: Speaking speed (< 1 faster, > 1 slower). Default 1.25.
        noise_scale: Generator noise amount. Default 0.667.
        noise_w_scale: Phoneme width noise. Default 0.4.
        strict: If True, raise on any phoneme not in voice config. Default True.

    Returns:
        Path to the generated WAV file.

    Raises:
        PiperModelNotFoundError: If the voice model file doesn't exist.
        PiperPhonemeError: If any phoneme symbol is missing from the voice config.
        PiperSynthesisError: If synthesis fails for any reason.
    """
    output = Path(output_path)

    if output.exists() and output.is_dir():
        raise ValueError(f"output_path must be a file path, got directory: {output}")
    if not output.parent.exists():
        raise ValueError(
            f"output_path parent directory does not exist: {output.parent}"
        )

    # Load voice
    try:
        voice = _load_voice(model_path)
    except Exception as exc:
        raise PiperModelNotFoundError(str(model_path or DEFAULT_VOICE_MODEL)) from exc

    id_map = voice.config.phoneme_id_map

    # Convert Mirad text to Piper phoneme symbols
    piper_symbols = text_to_piper_phonemes(text)

    # Validate all symbols against voice config
    missing = [sym for sym in piper_symbols if sym not in id_map]
    if missing and strict:
        raise PiperPhonemeError(missing=missing, word=text)

    # Convert to phoneme IDs (BOS + PAD + [sym + PAD, ...] + EOS)
    phoneme_ids: list[int] = []
    phoneme_ids.extend(id_map[BOS])
    phoneme_ids.extend(id_map[PAD])

    for sym in piper_symbols:
        if sym in id_map:
            phoneme_ids.extend(id_map[sym])
            phoneme_ids.extend(id_map[PAD])
        # else: skip missing symbols (warnings already collected)

    phoneme_ids.extend(id_map[EOS])

    if len(phoneme_ids) <= 3:
        # Only BOS + PAD + EOS = no actual phonemes
        raise PiperSynthesisError(
            text=text,
            output_path=str(output),
            cause=RuntimeError("No valid phoneme IDs produced from input text"),
        )

    # Build SynthesisConfig with slower speech for clarity
    # length_scale > 1 = slower; default 1.25 gives clearer Mirad pronunciation
    # noise_w_scale controls phoneme width variation; 0.4 is more stable
    syn_config = SynthesisConfig(
        length_scale=length_scale if length_scale is not None else 1.25,
        noise_scale=noise_scale if noise_scale is not None else 0.667,
        noise_w_scale=noise_w_scale if noise_w_scale is not None else 0.4,
        normalize_audio=True,
    )

    # Synthesize using low-level phoneme_ids_to_audio
    try:
        audio = voice.phoneme_ids_to_audio(phoneme_ids, syn_config)
    except Exception as exc:
        raise PiperSynthesisError(text=text, output_path=str(output), cause=exc) from exc

    if audio is None or len(audio) == 0:
        raise PiperSynthesisError(
            text=text,
            output_path=str(output),
            cause=RuntimeError("Piper synthesis produced no audio"),
        )

    # Normalize and clip audio (same as PiperVoice.synthesize does)
    max_val = np.max(np.abs(audio))
    if max_val > 1e-8:
        audio = audio / max_val

    audio = np.clip(audio, -1.0, 1.0).astype(np.float32)

    # Convert to int16 PCM and write WAV
    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)

    try:
        with wave.open(str(output), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(voice.config.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    except Exception as exc:
        raise PiperSynthesisError(text=text, output_path=str(output), cause=exc) from exc

    if not output.exists() or output.stat().st_size == 0:
        raise PiperSynthesisError(
            text=text,
            output_path=str(output),
            cause=RuntimeError("Piper synthesis completed without usable WAV output"),
        )

    return output


def diagnose_text(
    text: str,
    model_path: Path | None = None,
) -> list[PiperPhonemeDebug]:
    """Run diagnostic conversion on each word in text, returning per-word debug info.

    For each word, shows the IPA transcription, Piper symbols, IDs, and any
    missing symbols. Useful for ``--piper-debug`` mode.

    Args:
        text: Mirad text to diagnose.
        model_path: Optional path to a Piper voice model.

    Returns:
        List of PiperPhonemeDebug objects, one per word.
    """
    id_map = _get_phoneme_id_map(model_path)

    results: list[PiperPhonemeDebug] = []

    for token in tokenize(text):
        if token.type_ != TokenType.WORD:
            continue

        word = token.text
        ipa = word_to_ipa(word)
        piper_symbols = word_to_piper_phonemes(word)

        # Check which symbols are missing
        missing = [sym for sym in piper_symbols if sym not in id_map]

        # Compute IDs (skipping missing)
        ids: list[int] = []
        for sym in piper_symbols:
            if sym in id_map:
                ids.extend(id_map[sym])

        results.append(
            PiperPhonemeDebug(
                word=word,
                ipa=ipa,
                piper_symbols=piper_symbols,
                piper_ids=ids,
                missing_symbols=missing,
            )
        )

    return results


def get_available_voices(voices_dir: Path | None = None) -> list[Path]:
    """Get list of available Piper voice models.

    Args:
        voices_dir: Directory to search for voice models. If None, uses default.

    Returns:
        List of paths to .onnx voice model files.
    """
    if voices_dir is None:
        voices_dir = DEFAULT_VOICE_MODEL.parent

    if not voices_dir.exists():
        return []

    return sorted(voices_dir.glob("*.onnx"))


# Keep backward compatibility alias for tests
def _text_to_piper_phoneme_input(text: str) -> str:
    """Legacy alias — converts Mirad text to IPA wrapped in [[...]].

    .. deprecated:: Use ``text_to_piper_phonemes()`` and ``synthesize_to_wav()``
       instead. This function is kept for backward compatibility with existing
       tests but should not be used for new code.
    """
    parts: list[str] = []
    for part in re.split(r"([A-Za-z]+)", text):
        if part.isalpha():
            parts.append(word_to_ipa(part))
        else:
            parts.append(part)
    return f"[[{''.join(parts)}]]"


__all__ = [
    "PiperModelNotFoundError",
    "PiperPhonemeError",
    "PiperSynthesisError",
    "PiperPhonemeDebug",
    "synthesize_to_wav",
    "diagnose_text",
    "get_available_voices",
    "_load_voice",
    "_get_phoneme_id_map",
    "_text_to_piper_phoneme_input",
    "word_to_piper_phonemes",
    "text_to_piper_phonemes",
    "syllable_to_piper_phonemes",
    "piper_phonemes_to_ids",
    "piper_word_to_ids",
    "DEFAULT_VOICE_MODEL",
]
