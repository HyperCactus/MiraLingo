"""eSpeak NG phoneme conversion for Mirad text."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from .phonology import COMPLEX_VOWELS, SIMPLE_VOWELS
from .syllabify import Syllable, assign_stress, syllabify_word
from .tokenizer import tokenize
from .types import TokenType

_ESPEAK_CONSONANTS: dict[str, str] = {
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
    "w": "w",
    "x": "S",
    "y": "j",
    "z": "z",
}

_ESPEAK_SIMPLE_VOWELS: dict[str, str] = {
    "a": "a",
    "e": "e",
    "i": "i",
    "o": "o",
    "u": "u",
}

_ESPEAK_COMPLEX_VOWELS: dict[str, str] = {
    # Post-y-glided (ay, ey, iy, oy, uy)
    "ay": "ai",
    "ey": "ei",
    "iy": "ii",
    "oy": "oi",
    "uy": "ui",
    # Post-w-glided (aw, ew, iw, ow, uw)
    "aw": "au",
    "ew": "eu",
    "iw": "iu",
    "ow": "ou",
    "uw": "uu",
    # Pre-y-glided (ya, ye, yi, yo, yu)
    "ya": "ja",
    "ye": "je",
    "yi": "ji",
    "yo": "jo",
    "yu": "ju",
    # Pre-w-glided (wa, we, wi, wo, wu)
    "wa": "wa",
    "we": "we",
    "wi": "wi",
    "wo": "wo",
    "wu": "wu",
    # Circum-glided (yay, way, etc.)
    "yay": "jai",
    "yey": "jei",
    "yiy": "jii",
    "yoy": "joi",
    "yuy": "jui",
    "way": "wai",
    "wey": "wei",
    "wiy": "wii",
    "woy": "woi",
    "wuy": "wui",
}


class EspeakConversionError(ValueError):
    """Raised when Mirad -> eSpeak conversion fails."""


class EspeakSynthesisError(RuntimeError):
    """Raised when eSpeak NG synthesis to WAV fails."""


class EspeakBinaryNotFoundError(EspeakSynthesisError):
    """Raised when the ``espeak-ng`` binary is not available."""


class EspeakSynthesisTimeoutError(EspeakSynthesisError):
    """Raised when synthesis exceeds the configured timeout."""


@dataclass(frozen=True, slots=True)
class _Context:
    word: str


def _ensure_allowed(chars: str, context: _Context) -> None:
    for ch in chars:
        if not ch.isalpha() and ch != "'":
            raise EspeakConversionError(
                f"Cannot convert word {context.word!r}: invalid character {ch!r}."
            )


def _consonants_to_espeak(chars: str, context: _Context) -> str:
    output: list[str] = []
    for ch in chars.lower():
        if ch == "'":
            continue
        mapped = _ESPEAK_CONSONANTS.get(ch)
        if mapped is None:
            raise EspeakConversionError(
                f"Cannot convert word {context.word!r}: unsupported consonant {ch!r}."
            )
        output.append(mapped)
    return "".join(output)


def _nucleus_to_espeak(nucleus: str, context: _Context) -> str:
    lower_nucleus = nucleus.lower()
    if not lower_nucleus:
        return ""

    if lower_nucleus in _ESPEAK_COMPLEX_VOWELS:
        return _ESPEAK_COMPLEX_VOWELS[lower_nucleus]

    output: list[str] = []
    for ch in lower_nucleus:
        mapped = _ESPEAK_SIMPLE_VOWELS.get(ch)
        if mapped is None:
            raise EspeakConversionError(
                f"Cannot convert word {context.word!r}: unsupported nucleus part {ch!r}."
            )
        output.append(mapped)
    return "".join(output)


def syllable_to_espeak(syllable: Syllable, *, source_word: str = "") -> str:
    """Convert one syllable to eSpeak phoneme string.

    Stress is prefixed as `'` and comes only from ``syllable.stressed``.
    """

    context = _Context(word=source_word or syllable.text or "<unknown>")

    _ensure_allowed(syllable.onset, context)
    _ensure_allowed(syllable.nucleus, context)
    _ensure_allowed(syllable.coda, context)

    onset = _consonants_to_espeak(syllable.onset, context)
    nucleus = _nucleus_to_espeak(syllable.nucleus, context)
    coda = _consonants_to_espeak(syllable.coda, context)

    body = f"{onset}{nucleus}{coda}"
    if syllable.stressed and body:
        return f"'{body}"
    return body


def word_to_espeak(word: str, *, stress: bool = True) -> str:
    """Convert a Mirad word to eSpeak phoneme input."""

    normalized = word.strip()
    if not normalized:
        return ""

    normalized = normalized.lower()

    try:
        syllables = syllabify_word(normalized)
    except Exception as exc:  # pragma: no cover - defensive wrapper for dependency failures
        raise EspeakConversionError(
            f"Failed to syllabify word {word!r}: {exc}"
        ) from exc

    if stress and len(syllables) > 1:
        syllables = assign_stress(syllables)

    converted: list[str] = []
    for syllable in syllables:
        converted.append(syllable_to_espeak(syllable, source_word=normalized))
    return "".join(converted)


def text_to_espeak_phoneme_input(text: str) -> str:
    """Convert full text to eSpeak NG phoneme input wrapped in ``[[...]]``."""

    converted_tokens: list[str] = []
    for token in tokenize(text):
        if token.type_ == TokenType.WORD:
            try:
                converted_tokens.append(word_to_espeak(token.text))
            except EspeakConversionError as exc:
                raise EspeakConversionError(
                    f"Failed converting token {token.text!r}: {exc}"
                ) from exc
        else:
            converted_tokens.append(token.text)

    return f"[[{''.join(converted_tokens)}]]"


def _stderr_snippet(stderr: str | None, *, limit: int = 240) -> str:
    if not stderr:
        return "<empty>"
    collapsed = " ".join(stderr.strip().split())
    return collapsed[:limit] if collapsed else "<empty>"


def synthesize_to_wav(
    text: str,
    output_path: str | Path,
    *,
    voice: str | None = None,
    speed: int = 120,
    pitch: int = 40,
    word_gap: int = 4,
    amplitude: int = 90,
    no_final_pause: bool = True,
    timeout_seconds: float = 10.0,
) -> Path:
    """Convert Mirad text to eSpeak phoneme input and synthesize a WAV file.

    Defaults are tuned for natural-sounding Mirad output:
    ``speed=120`` (≈0.7× the default 175 wpm), ``pitch=40``
    (warmer, less robotic), ``word_gap=4`` (40 ms pauses between
    words), ``amplitude=90``, and ``no_final_pause=True`` (removes
    the trailing silence).  Pass ``speed=175``, ``pitch=50``,
    ``word_gap=0``, ``amplitude=100``, ``no_final_pause=False`` to
    get the raw espeak-ng defaults.
    """

    if not text.strip():
        raise ValueError("text must not be empty")

    output = Path(output_path)
    if output.exists() and output.is_dir():
        raise ValueError(f"output_path must be a file path, got directory: {output}")

    if not output.parent.exists():
        raise ValueError(
            f"output_path parent directory does not exist: {output.parent}"
        )

    phoneme_input = text_to_espeak_phoneme_input(text)
    command = [
        "espeak-ng",
        "-w", str(output),
        "-s", str(speed),
        "-p", str(pitch),
        "-g", str(word_gap),
        "-a", str(amplitude),
    ]
    if voice:
        command.extend(["-v", voice])
    if no_final_pause:
        command.append("-z")

    try:
        completed = subprocess.run(
            command,
            input=phoneme_input,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise EspeakBinaryNotFoundError(
            f"eSpeak binary not found for command {command!r}; output_path={output}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise EspeakSynthesisTimeoutError(
            "eSpeak synthesis timed out "
            f"for command {command!r}; timeout_seconds={timeout_seconds}; "
            f"output_path={output}; stderr={_stderr_snippet(exc.stderr)}"
        ) from exc

    if completed.returncode != 0:
        raise EspeakSynthesisError(
            "eSpeak synthesis failed "
            f"for command {command!r}; exit_code={completed.returncode}; "
            f"output_path={output}; stderr={_stderr_snippet(completed.stderr)}"
        )

    if not output.exists() or output.stat().st_size == 0:
        raise EspeakSynthesisError(
            "eSpeak synthesis completed without usable WAV output "
            f"for command {command!r}; exit_code={completed.returncode}; "
            f"output_path={output}; stderr={_stderr_snippet(completed.stderr)}"
        )

    return output


__all__ = [
    "EspeakConversionError",
    "EspeakSynthesisError",
    "EspeakBinaryNotFoundError",
    "EspeakSynthesisTimeoutError",
    "syllable_to_espeak",
    "word_to_espeak",
    "text_to_espeak_phoneme_input",
    "synthesize_to_wav",
    "SIMPLE_VOWELS",
    "COMPLEX_VOWELS",
]
