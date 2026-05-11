"""MBROLA TTS backend for Mirad text-to-speech.

Synthesises Mirad text via MBROLA using the German ``de6`` voice, which
supports the Mirad-critical phones ``h``, ``S`` /ʃ/, ``Z`` /ʒ/, ``tS``
/tʃ/, ``j``, ``w``, and ``r``.

Architecture
~~~~~~~~~~~~

1. Mirad text → existing tokenizer / syllabifier / stress assignment
2. Syllables → de6 phone symbols (``MBROLA_CONSONANTS``,
   ``MBROLA_SIMPLE_VOWELS``, ``MBROLA_COMPLEX_VOWELS``)
3. Phone symbols → ``.pho`` file lines with deterministic durations and
   pitch targets
4. ``mbrola de6 input.pho output.wav`` via ``subprocess.run`` (no
   ``shell=True``)

Install::

    sudo apt install mbrola mbrola-de6
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

from .phonology import COMPLEX_VOWELS, SIMPLE_VOWELS
from .syllabify import Syllable, assign_stress, syllabify_word
from .tokenizer import tokenize
from .types import TokenType

# ── Phone mappings ────────────────────────────────────────────────────────────

MBROLA_CONSONANTS: dict[str, str] = {
    "b": "b",
    "c": "tS",
    "d": "d",
    "f": "f",
    "g": "g",
    "h": "h",
    "j": "Z",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": "p",
    "q": "k",
    "r": "r",
    "s": "s",
    "t": "t",
    "v": "v",
    "x": "S",
    "z": "z",
}

MBROLA_GLYES: dict[str, str] = {
    "y": "j",
    "w": "w",
}

MBROLA_SIMPLE_VOWELS: dict[str, str] = {
    "a": "a",
    "e": "e:",
    "i": "i:",
    "o": "o:",
    "u": "u:",
}

MBROLA_COMPLEX_VOWELS: dict[str, str] = {
    # Post-y-glided (ay, ey, iy, oy, uy)
    "ay": "a j",
    "ey": "e: j",
    "iy": "i: j",
    "oy": "o: j",
    "uy": "u: j",
    # Post-w-glided (aw, ew, iw, ow, uw)
    "aw": "O",
    "ew": "e: w",
    "iw": "i: w",
    "ow": "o: w",
    "uw": "u: w",
    # Pre-y-glided (ya, ye, yi, yo, yu)
    "ya": "j a",
    "ye": "j e:",
    "yi": "j i:",
    "yo": "j o:",
    "yu": "j u:",
    # Pre-w-glided (wa, we, wi, wo, wu)
    "wa": "w a",
    "we": "w e:",
    "wi": "w i:",
    "wo": "w o:",
    "wu": "w u:",
    # Circum-y-glided (yay, yey, yiy, yoy, yuy)
    "yay": "j a j",
    "yey": "j e: j",
    "yiy": "j i: j",
    "yoy": "j o: j",
    "yuy": "j u: j",
    # Pre-w-post-y-glided (way, wey, wiy, woy, wuy)
    "way": "w a j",
    "wey": "w e: j",
    "wiy": "w i: j",
    "woy": "w o: j",
    "wuy": "w u: j",
}

# ── Deterministic durations (ms) ──────────────────────────────────────────────

DURATIONS: dict[str, int] = {
    "vowel": 110,
    "stressed_vowel": 140,
    "glide": 55,       # j, w
    "liquid": 65,      # r, l
    "nasal": 75,       # m, n
    "stop": 65,        # p, t, k, b, d, g
    "fricative": 85,   # f, v, s, z, S, Z, h
    "affricate": 95,   # tS
    "word_pause": 60,
    "comma_pause": 140,
    "sentence_pause": 220,
}

# Base F0 for de6 (male voice)
_BASE_F0 = 115

# Pitch targets: position%  Hz
_STRESSED_PITCH = [0, _BASE_F0 - 0, 50, _BASE_F0 + 20, 100, _BASE_F0 - 5]
_UNSTRESSED_PITCH = [0, _BASE_F0 - 5, 100, _BASE_F0 - 10]

# ── Phone classification for duration lookup ────────────────────────────────────

_VOWEL_SET = frozenset({"a", "e:", "i:", "o:", "u:", "O"})
_GLIDE_SET = frozenset({"j", "w"})
_LIQUID_SET = frozenset({"r", "l"})
_NASAL_SET = frozenset({"m", "n"})
_STOP_SET = frozenset({"p", "t", "k", "b", "d", "g"})
_FRICATIVE_SET = frozenset({"f", "v", "s", "z", "S", "Z", "h"})
_AFFRICATE_SET = frozenset({"tS"})


def _phone_duration(phone: str, *, stressed: bool = False) -> int:
    """Return deterministic duration in ms for a single de6 phone symbol."""
    if phone in _VOWEL_SET:
        return DURATIONS["stressed_vowel"] if stressed else DURATIONS["vowel"]
    if phone in _GLIDE_SET:
        return DURATIONS["glide"]
    if phone in _LIQUID_SET:
        return DURATIONS["liquid"]
    if phone in _NASAL_SET:
        return DURATIONS["nasal"]
    if phone in _STOP_SET:
        return DURATIONS["stop"]
    if phone in _FRICATIVE_SET:
        return DURATIONS["fricative"]
    if phone in _AFFRICATE_SET:
        return DURATIONS["affricate"]
    # Fallback for unknown phones
    return 80


def _phone_pitch(phone: str, *, stressed: bool = False) -> list[int]:
    """Return pitch target list for a phone (position% Hz pairs).

    Only vowels and glides carry pitch targets; consonants get none.
    """
    if phone in _VOWEL_SET:
        if stressed:
            return list(_STRESSED_PITCH)
        return list(_UNSTRESSED_PITCH)
    # Consonants and glides: no explicit pitch
    return []


# ── Error types ─────────────────────────────────────────────────────────────────


class MbrolaError(ValueError):
    """Raised when MBROLA conversion fails."""


class MbrolaNotFoundError(RuntimeError):
    """Raised when the ``mbrola`` binary is not found on PATH."""


class MbrolaVoiceNotFoundError(RuntimeError):
    """Raised when the MBROLA voice database file is not found."""


class MbrolaSynthesisError(RuntimeError):
    """Raised when MBROLA synthesis fails."""


# ── Per-phone validation ──────────────────────────────────────────────────────

_ALL_VALID_PHONES: frozenset[str] = (
    _VOWEL_SET | _GLIDE_SET | _LIQUID_SET | _NASAL_SET
    | _STOP_SET | _FRICATIVE_SET | _AFFRICATE_SET
)


def _validate_phones(phones: list[str]) -> None:
    """Raise ``MbrolaError`` if any phone symbol is not valid for de6."""
    invalid = [p for p in phones if p != "_" and p not in _ALL_VALID_PHONES]
    if invalid:
        raise MbrolaError(
            f"Unsupported de6 phone symbols: {sorted(set(invalid))}. "
            f"Valid phones: {sorted(_ALL_VALID_PHONES)}."
        )


# ── Syllable → de6 phones ─────────────────────────────────────────────────────


def _consonants_to_mbrola(chars: str, context: str) -> str:
    """Convert onset/coda consonants to de6 phone symbols.

    ``y`` in onset/coda position maps to glide ``j``; ``w`` maps to ``w``.
    """
    output: list[str] = []
    for ch in chars.lower():
        if ch == "'":
            continue  # glottal stop — skip in MBROLA for now
        mapped = MBROLA_CONSONANTS.get(ch) or MBROLA_GLYES.get(ch)
        if mapped is None:
            raise MbrolaError(
                f"Cannot convert word {context!r}: unsupported consonant {ch!r}."
            )
        output.append(mapped)
    return " ".join(output)


def _nucleus_to_mbrola(nucleus: str, context: str) -> str:
    """Convert a vowel nucleus to de6 phone symbols.

    Complex vowels (ay, ya, aw, etc.) are mapped first; simple vowels
    use the long-vowel convention (e: i: o: u:).
    """
    lower = nucleus.lower()
    if not lower:
        return ""

    if lower in MBROLA_COMPLEX_VOWELS:
        return MBROLA_COMPLEX_VOWELS[lower]

    # Simple vowels
    output: list[str] = []
    for ch in lower:
        mapped = MBROLA_SIMPLE_VOWELS.get(ch)
        if mapped is None:
            raise MbrolaError(
                f"Cannot convert word {context!r}: unsupported nucleus part {ch!r}."
            )
        output.append(mapped)
    return " ".join(output)


def syllable_to_mbrola(syllable: Syllable, *, source_word: str = "") -> str:
    """Convert one syllable to a space-separated de6 phone string.

    Stress is indicated by returning the phone string; the caller or
    ``.pho`` generator tracks which vowels get stressed pitch/duration.
    """
    context = source_word or syllable.text or "<unknown>"

    onset = _consonants_to_mbrola(syllable.onset, context)
    nucleus = _nucleus_to_mbrola(syllable.nucleus, context)
    coda = _consonants_to_mbrola(syllable.coda, context)

    parts = [p for p in (onset, nucleus, coda) if p]
    return " ".join(parts)


def word_to_mbrola(word: str, *, stress: bool = True) -> str:
    """Convert a Mirad word to a space-separated de6 phone string."""
    normalized = word.strip().lower()
    if not normalized:
        return ""

    try:
        syllables = syllabify_word(normalized)
    except Exception as exc:
        raise MbrolaError(f"Failed to syllabify word {word!r}: {exc}") from exc

    if stress and len(syllables) > 1:
        syllables = assign_stress(syllables)

    converted: list[str] = []
    for syllable in syllables:
        converted.append(syllable_to_mbrola(syllable, source_word=normalized))
    return " ".join(converted)


def word_to_mbrola_phones(word: str, *, stress: bool = True) -> list[str]:
    """Convert a Mirad word to a flat list of de6 phone symbols."""
    phone_str = word_to_mbrola(word, stress=stress)
    if not phone_str:
        return []
    return phone_str.split()


def text_to_mbrola_phones(text: str) -> list[str]:
    """Convert full Mirad text to a flat list of de6 phone symbols.

    Punctuation tokens are converted to pause phones:
    - ``. ? !`` → sentence-final pause (handled by ``generate_pho``)
    - ``, ; :`` → comma pause (handled by ``generate_pho``)
    - Word boundaries → word pause (handled by ``generate_pho``)
    """
    all_phones: list[str] = []
    for token in tokenize(text):
        if token.type_ == TokenType.WORD:
            phones = word_to_mbrola_phones(token.text)
            if all_phones and phones:
                all_phones.append("_")  # word boundary
            all_phones.extend(phones)
        # PUNCT and SPACE tokens are handled by generate_pho pauses
    return all_phones


# ── .pho file generation ───────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PhoLine:
    """A single line in a ``.pho`` file."""

    phone: str
    duration_ms: int
    pitch: list[int]  # position% Hz pairs, may be empty

    def to_line(self) -> str:
        parts = [self.phone, str(self.duration_ms)]
        parts.extend(str(v) for v in self.pitch)
        return " ".join(parts)


def generate_pho(text: str) -> list[PhoLine]:
    """Generate a list of ``.pho`` lines for Mirad text using de6 phones.

    Produces:
    - Initial silence (``_ 80``)
    - For each word: phone lines with duration and optional pitch, then a
      word pause (``_ 60``)
    - Punctuation pauses: comma-level (``_ 140``) or sentence-final (``_ 220``)
    - Final silence (``_ 120``)
    """
    lines: list[PhoLine] = []

    # Initial silence
    lines.append(PhoLine(phone="_", duration_ms=80, pitch=[]))

    sentence_final_punct = {".", "!", "?"}
    comma_punct = {",", ";", ":"}

    tokens = tokenize(text)
    word_idx = 0

    for token in tokens:
        if token.type_ == TokenType.WORD:
            # Add word pause before second and subsequent words
            if word_idx > 0:
                lines.append(PhoLine(phone="_", duration_ms=DURATIONS["word_pause"], pitch=[]))

            syllables = syllabify_word(token.text.lower())
            if len(syllables) > 1:
                syllables = assign_stress(syllables)

            for syllable in syllables:
                phone_str = syllable_to_mbrola(syllable, source_word=token.text.lower())
                if not phone_str:
                    continue
                phones = phone_str.split()
                # Validate phones
                _validate_phones(phones)

                # Determine which phones are vowels (for stress pitch/duration)
                nucleus_phones = _nucleus_to_mbrola(syllable.nucleus, token.text.lower()).split()
                nucleus_set = set(nucleus_phones) if nucleus_phones else set()

                for phone in phones:
                    dur = _phone_duration(phone, stressed=(syllable.stressed and phone in nucleus_set))
                    pitch = _phone_pitch(phone, stressed=(syllable.stressed and phone in nucleus_set))
                    lines.append(PhoLine(phone=phone, duration_ms=dur, pitch=pitch))

            word_idx += 1

        elif token.type_ == TokenType.PUNCT:
            if token.text in sentence_final_punct:
                lines.append(PhoLine(phone="_", duration_ms=DURATIONS["sentence_pause"], pitch=[]))
            elif token.text in comma_punct:
                lines.append(PhoLine(phone="_", duration_ms=DURATIONS["comma_pause"], pitch=[]))
            # Other punctuation: skip (no pause)

    # Final silence
    lines.append(PhoLine(phone="_", duration_ms=120, pitch=[]))

    return lines


def pho_to_string(lines: list[PhoLine]) -> str:
    """Render ``.pho`` lines to a string suitable for writing to a file."""
    return "\n".join(line.to_line() for line in lines) + "\n"


def write_pho(text: str, path: str | Path) -> Path:
    """Generate and write a ``.pho`` file for Mirad text.

    Args:
        text: Mirad text to convert.
        path: Output ``.pho`` file path.

    Returns:
        Path to the written file.
    """
    out = Path(path)
    lines = generate_pho(text)
    out.write_text(pho_to_string(lines), encoding="utf-8")
    return out


# ── Preflight checks ────────────────────────────────────────────────────────────

_DEFAULT_DE6_PATH = Path("/usr/share/mbrola/de6/de6")


def _check_mbrola_binary() -> str:
    """Return the path to ``mbrola`` on PATH, or raise."""
    mbrola = shutil.which("mbrola")
    if mbrola is None:
        raise MbrolaNotFoundError(
            "mbrola binary not found on PATH. "
            "Install with: sudo apt install mbrola"
        )
    return mbrola


def _check_voice_db(db_path: Path | None = None) -> Path:
    """Return the path to the de6 database, or raise."""
    voice_db = db_path or _DEFAULT_DE6_PATH
    if not voice_db.exists():
        raise MbrolaVoiceNotFoundError(
            f"MBROLA de6 voice database not found at {voice_db}. "
            "Install with: sudo apt install mbrola-de6"
        )
    return voice_db


# ── Synthesis ──────────────────────────────────────────────────────────────────


def synthesize_to_wav(
    text: str,
    output_path: str | Path,
    *,
    voice: str = "de6",
    mbrola_db: Path | None = None,
    timeout_seconds: float = 30.0,
) -> Path:
    """Synthesize Mirad text to WAV using MBROLA.

    Args:
        text: Mirad text to synthesize.
        output_path: Path where the WAV file should be written.
        voice: MBROLA voice name (default ``de6``).
        mbrola_db: Override path to the MBROLA voice database file.
            If None, uses ``/usr/share/mbrola/de6/de6``.
        timeout_seconds: Maximum seconds to wait for MBROLA.

    Returns:
        Path to the generated WAV file.

    Raises:
        MbrolaNotFoundError: If ``mbrola`` is not on PATH.
        MbrolaVoiceNotFoundError: If the de6 database is missing.
        MbrolaError: If phone conversion encounters unsupported symbols.
        MbrolaSynthesisError: If MBROLA fails to synthesize.
    """
    if not text.strip():
        raise ValueError("text must not be empty")

    output = Path(output_path)
    if output.exists() and output.is_dir():
        raise ValueError(f"output_path must be a file path, got directory: {output}")
    if not output.parent.exists():
        raise ValueError(f"output_path parent directory does not exist: {output.parent}")

    # Preflight
    mbrola_bin = _check_mbrola_binary()
    voice_db = _check_voice_db(mbrola_db)

    # Generate .pho content to a temp file
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".pho", delete=False, encoding="utf-8"
    ) as tmp:
        pho_path = Path(tmp.name)
        lines = generate_pho(text)
        tmp.write(pho_to_string(lines))

    try:
        command = [mbrola_bin, str(voice_db), str(pho_path), str(output)]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise MbrolaSynthesisError(
                f"MBROLA synthesis timed out after {timeout_seconds}s "
                f"for text {text!r}; output_path={output}"
            ) from exc

        if completed.returncode != 0:
            stderr = (completed.stderr or "")[:500]
            raise MbrolaSynthesisError(
                f"MBROLA synthesis failed with exit code {completed.returncode}: "
                f"{stderr}; output_path={output}"
            )

        if not output.exists() or output.stat().st_size == 0:
            raise MbrolaSynthesisError(
                f"MBROLA produced no output for text {text!r}; output_path={output}"
            )

        return output
    finally:
        # Clean up temp .pho file
        try:
            pho_path.unlink(missing_ok=True)
        except OSError:
            pass


def diagnose_mbrola(text: str) -> list[dict]:
    """Run diagnostic conversion on each word in text for MBROLA.

    Returns per-word info: word, syllables, phones, and any errors.
    """
    results: list[dict] = []

    for token in tokenize(text):
        if token.type_ != TokenType.WORD:
            continue
        word = token.text
        try:
            syllables = syllabify_word(word.lower())
            if len(syllables) > 1:
                syllables = assign_stress(syllables)
            phone_str = word_to_mbrola(word)
            phones = phone_str.split() if phone_str else []
            results.append({
                "word": word,
                "syllables": [s.text for s in syllables],
                "phones": phones,
                "error": None,
            })
        except Exception as exc:
            results.append({
                "word": word,
                "syllables": [],
                "phones": [],
                "error": str(exc),
            })

    return results


__all__ = [
    "MbrolaError",
    "MbrolaNotFoundError",
    "MbrolaVoiceNotFoundError",
    "MbrolaSynthesisError",
    "DURATIONS",
    "MBROLA_CONSONANTS",
    "MBROLA_GLYES",
    "MBROLA_SIMPLE_VOWELS",
    "MBROLA_COMPLEX_VOWELS",
    "syllable_to_mbrola",
    "word_to_mbrola",
    "word_to_mbrola_phones",
    "text_to_mbrola_phones",
    "generate_pho",
    "PhoLine",
    "pho_to_string",
    "write_pho",
    "synthesize_to_wav",
    "diagnose_mbrola",
]