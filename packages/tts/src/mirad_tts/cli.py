"""Command-line interface for Mirad phoneme conversion and synthesis."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable

from .espeak_backend import text_to_espeak_phoneme_input, synthesize_to_wav as espeak_synthesize_to_wav
from .ipa import text_to_ipa
from .syllabify import assign_stress, syllabify_word
from .tokenizer import Token, tokenize
from .types import TokenType


@dataclass(frozen=True, slots=True)
class CliPipelineError(RuntimeError):
    stage: str
    cause: Exception

    def __str__(self) -> str:
        return f"stage={self.stage} {self.cause.__class__.__name__}: {self.cause}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m mirad_tts.cli")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ipa", action="store_true", help="Output IPA transcription (default)")
    mode.add_argument(
        "--syllables",
        action="store_true",
        help="Output dotted syllables with stress marker",
    )
    mode.add_argument("--espeak", action="store_true", help="Output eSpeak phoneme input")
    mode.add_argument("--piper", action="store_true", help="Output Piper-safe phoneme symbols")
    mode.add_argument("--mbrola", action="store_true", help="Output MBROLA de6 phone symbols")

    parser.add_argument("--debug", action="store_true", help="Print deterministic stage view")
    parser.add_argument("--piper-debug", action="store_true",
                       help="Print per-word Piper phoneme diagnostics (symbols, IDs, missing)")
    parser.add_argument("--mbrola-debug", action="store_true",
                       help="Print per-word MBROLA phone diagnostics")
    parser.add_argument("--wav", type=str, help="Optional output WAV path")
    parser.add_argument("--pho", type=str, help="Output .pho file path (MBROLA backend only)")
    parser.add_argument("--backend", type=str, choices=["espeak", "piper", "mbrola"], default="espeak",
                       help="TTS backend for WAV synthesis (default: espeak)")
    parser.add_argument("--voice", type=str, help="Optional voice for --wav (backend-specific)")
    parser.add_argument("--mbrola-db", type=str, default=None,
                       help="Override path to MBROLA voice database (e.g. /usr/share/mbrola/de6/de6)")
    parser.add_argument("--speed", type=int, default=None,
                       help="eSpeak speed in WPM (default: 120 for natural Mirad)")
    parser.add_argument("--pitch", type=int, default=None,
                       help="eSpeak pitch 0-99 (default: 40 for warmer tone)")
    parser.add_argument("--word-gap", type=int, default=None,
                       help="eSpeak word gap in 10ms units (default: 4)")
    parser.add_argument("--amplitude", type=int, default=None,
                       help="eSpeak amplitude 0-200 (default: 90)")
    parser.add_argument("--no-final-pause", action="store_true", default=True,
                       help="Remove trailing sentence pause (default: True)")
    parser.add_argument("--final-pause", action="store_true",
                       help="Keep trailing sentence pause (override --no-final-pause)")
    parser.add_argument("--length-scale", type=float, default=None,
                       help="Piper length_scale (< 1 faster, > 1 slower; default: 1.25)")
    parser.add_argument("--noise-scale", type=float, default=None,
                       help="Piper noise_scale (default: 0.667)")
    parser.add_argument("--noise-w-scale", type=float, default=None,
                       help="Piper noise_w_scale (default: 0.4)")
    parser.add_argument("text", nargs="*", help="Mirad text to convert")

    return parser


def _tokens_debug(tokens: list[Token]) -> str:
    return "|".join(f"{token.type_}:{token.text!r}" for token in tokens)


def _word_to_syllables_stress(word: str) -> str:
    lowered = word.lower()
    syllables = syllabify_word(lowered)
    if not syllables:
        return lowered

    if len(syllables) > 1:
        syllables = assign_stress(syllables)

    parts: list[str] = []
    for syllable in syllables:
        if syllable.stressed:
            parts.append(f"ˈ{syllable.text}")
        else:
            parts.append(syllable.text)
    return ".".join(parts)


def _text_to_syllables_stress(text: str) -> str:
    output: list[str] = []
    for token in tokenize(text):
        if token.type_ == TokenType.WORD:
            output.append(_word_to_syllables_stress(token.text))
        else:
            output.append(token.text)
    return "".join(output)


def _debug_lines(tokens: list[Token], syllables: str, ipa: str, espeak: str) -> list[str]:
    return [
        f"debug stage=tokenizer tokens={_tokens_debug(tokens)}",
        f"debug stage=syllables_stress output={syllables}",
        f"debug stage=ipa output={ipa}",
        f"debug stage=espeak output={espeak}",
    ]


def _piper_debug_lines(text: str) -> list[str]:
    """Generate per-word Piper diagnostics showing symbols, IDs, and missing phonemes."""
    from .piper_backend import diagnose_text as piper_diagnose_text

    lines: list[str] = []
    try:
        diagnostics = piper_diagnose_text(text)
    except Exception as exc:
        return [f"piper_diagnose_error: {exc}"]

    for diag in diagnostics:
        sym_str = " ".join(diag.piper_symbols)
        lines.append(
            f"WORD: {diag.word}\n"
            f"  IPA:            {diag.ipa}\n"
            f"  PIPER SYMBOLS:  {sym_str}\n"
            f"  PIPER IDS:      {diag.piper_ids}\n"
            f"  MISSING:        {sorted(set(diag.missing_symbols)) if diag.missing_symbols else 'none'}"
        )

    return lines


def _mbrola_debug_lines(text: str) -> list[str]:
    """Generate per-word MBROLA diagnostics showing phones."""
    from .mbrola_backend import diagnose_mbrola

    lines: list[str] = []
    try:
        diagnostics = diagnose_mbrola(text)
    except Exception as exc:
        return [f"mbrola_diagnose_error: {exc}"]

    for diag in diagnostics:
        phones_str = " ".join(diag["phones"])
        syl_str = ".".join(diag["syllables"]) if diag["syllables"] else "<none>"
        err_str = diag["error"] or "none"
        lines.append(
            f"WORD: {diag['word']}\n"
            f"  SYLLABLES:  {syl_str}\n"
            f"  MBROLA PHONES: {phones_str}\n"
            f"  ERROR:      {err_str}"
        )

    return lines


def _resolve_text(parts: Iterable[str]) -> str:
    text = " ".join(parts)
    if not text.strip():
        raise ValueError("text must not be empty")
    return text


def run(argv: list[str] | None = None) -> tuple[str, list[str], str | None, str | None]:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        text = _resolve_text(args.text)
    except Exception as exc:
        raise CliPipelineError("input", exc) from exc

    try:
        tokens = tokenize(text)
    except Exception as exc:
        raise CliPipelineError("tokenizer", exc) from exc

    try:
        syllables = _text_to_syllables_stress(text)
    except Exception as exc:
        raise CliPipelineError("syllables_stress", exc) from exc

    try:
        ipa = text_to_ipa(text)
    except Exception as exc:
        raise CliPipelineError("ipa", exc) from exc

    try:
        espeak = text_to_espeak_phoneme_input(text)
    except Exception as exc:
        raise CliPipelineError("espeak", exc) from exc

    try:
        from .mbrola_backend import word_to_mbrola
        mbrola_phones = " ".join(
            word_to_mbrola(t.text) for t in tokens if t.type_ == TokenType.WORD
        )
    except Exception as exc:
        mbrola_phones = f"<error: {exc}>"

    try:
        from .piper_backend import text_to_piper_phonemes
        piper_phonemes = text_to_piper_phonemes(text)
        piper_str = " ".join(piper_phonemes)
    except Exception as exc:
        piper_str = f"<error: {exc}>"

    selected = ipa
    if args.syllables:
        selected = syllables
    elif args.espeak:
        selected = espeak
    elif args.piper:
        selected = piper_str
    elif args.mbrola:
        selected = mbrola_phones

    # .pho output (MBROLA only)
    if args.pho:
        try:
            from .mbrola_backend import write_pho
            write_pho(text, args.pho)
        except Exception as exc:
            raise CliPipelineError("mbrola_pho", exc) from exc

    if args.wav:
        try:
            if args.backend == "piper":
                from .piper_backend import PiperPhonemeError, synthesize_to_wav as piper_synthesize_to_wav
                piper_synthesize_to_wav(
                    text,
                    args.wav,
                    model_path=None,
                    length_scale=args.length_scale,
                    noise_scale=args.noise_scale,
                    noise_w_scale=args.noise_w_scale,
                )
            elif args.backend == "mbrola":
                from .mbrola_backend import MbrolaError, MbrolaNotFoundError, MbrolaSynthesisError, MbrolaVoiceNotFoundError, synthesize_to_wav as mbrola_synthesize_to_wav
                mbrola_db = Path(args.mbrola_db) if args.mbrola_db else None
                mbrola_synthesize_to_wav(
                    text,
                    args.wav,
                    voice=args.voice or "de6",
                    mbrola_db=mbrola_db,
                )
            else:  # espeak
                espeak_synthesize_to_wav(
                    text,
                    args.wav,
                    voice=args.voice,
                    speed=args.speed if args.speed is not None else 120,
                    pitch=args.pitch if args.pitch is not None else 40,
                    word_gap=args.word_gap if args.word_gap is not None else 4,
                    amplitude=args.amplitude if args.amplitude is not None else 90,
                    no_final_pause=not args.final_pause,
                )
        except Exception as exc:
            # Map backend-specific errors to pipeline errors
            from .piper_backend import PiperPhonemeError as _PiperPhonemeError
            from .mbrola_backend import MbrolaError as _MbrolaError, MbrolaNotFoundError as _MbrolaNotFoundError, MbrolaSynthesisError as _MbrolaSynthesisError, MbrolaVoiceNotFoundError as _MbrolaVoiceNotFoundError
            if isinstance(exc, _PiperPhonemeError):
                raise CliPipelineError("piper_phoneme", exc) from exc
            if isinstance(exc, (_MbrolaNotFoundError, _MbrolaVoiceNotFoundError)):
                raise CliPipelineError("mbrola_preflight", exc) from exc
            if isinstance(exc, (_MbrolaError, _MbrolaSynthesisError)):
                raise CliPipelineError("mbrola_synthesis", exc) from exc
            raise CliPipelineError("synthesis", exc) from exc

    debug_lines = _debug_lines(tokens, syllables, ipa, espeak) if args.debug else []

    if args.piper_debug:
        debug_lines.extend(_piper_debug_lines(text))

    if args.mbrola_debug:
        debug_lines.extend(_mbrola_debug_lines(text))

    return selected, debug_lines, args.wav, args.voice


def main(argv: list[str] | None = None) -> int:
    try:
        selected, debug_lines, _, _ = run(argv)
    except CliPipelineError as exc:
        print(f"error {exc}", file=sys.stderr)
        return 1

    if debug_lines:
        for line in debug_lines:
            print(line, file=sys.stderr)

    print(selected)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())