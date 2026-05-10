"""Command-line interface for Mirad phoneme conversion and synthesis."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from typing import Iterable

from .espeak_backend import text_to_espeak_phoneme_input, synthesize_to_wav as espeak_synthesize_to_wav
from .ipa import text_to_ipa
from .piper_backend import synthesize_to_wav as piper_synthesize_to_wav
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

    parser.add_argument("--debug", action="store_true", help="Print deterministic stage view")
    parser.add_argument("--wav", type=str, help="Optional output WAV path")
    parser.add_argument("--backend", type=str, choices=["espeak", "piper"], default="espeak",
                       help="TTS backend for WAV synthesis (default: espeak)")
    parser.add_argument("--voice", type=str, help="Optional voice for --wav (backend-specific)")
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

    selected = ipa
    if args.syllables:
        selected = syllables
    elif args.espeak:
        selected = espeak

    if args.wav:
        try:
            if args.backend == "piper":
                piper_synthesize_to_wav(text, args.wav, model_path=None)
            else:  # espeak
                espeak_synthesize_to_wav(text, args.wav, voice=args.voice)
        except Exception as exc:
            raise CliPipelineError("synthesis", exc) from exc

    debug_lines = _debug_lines(tokens, syllables, ipa, espeak) if args.debug else []
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
