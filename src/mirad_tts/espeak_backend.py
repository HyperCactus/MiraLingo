"""eSpeak NG phoneme conversion for Mirad text."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from .phonology import COMPLEX_VOWELS, SIMPLE_VOWELS
from .syllabify import Syllable, assign_stress, syllabify_word
from .tokenizer import tokenize

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
    "ay": "ai",
    "ey": "ei",
    "iy": "ii",
    "oy": "oi",
    "uy": "ui",
    "aw": "au",
    "ew": "eu",
    "iw": "iu",
    "ow": "ou",
    "uw": "uu",
    "yo": "jo",
    "yi": "ji",
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
        if token.type_ == "WORD":
            try:
                converted_tokens.append(word_to_espeak(token.value))
            except EspeakConversionError as exc:
                raise EspeakConversionError(
                    f"Failed converting token {token.value!r}: {exc}"
                ) from exc
        else:
            converted_tokens.append(token.value)

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
    timeout_seconds: float = 10.0,
) -> Path:
    """Convert Mirad text to eSpeak phoneme input and synthesize a WAV file."""

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
    command = ["espeak-ng", "-w", str(output)]
    if voice:
        command.extend(["-v", voice])

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
