"""Piper TTS backend for Mirad text-to-speech."""

from __future__ import annotations

import re
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from piper.voice import PiperVoice
from .ipa import word_to_ipa


# Default voice model path
DEFAULT_VOICE_MODEL: Final[Path] = Path(__file__).parent.parent.parent / ".gsd" / "piper-voices" / "es_MX-claude-high.onnx"


@dataclass(frozen=True, slots=True)
class PiperModelNotFoundError(RuntimeError):
    """Raised when the Piper voice model file is not found."""

    model_path: str

    def __str__(self) -> str:
        return f"Piper voice model not found: {self.model_path}"


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


def _text_to_piper_phoneme_input(text: str) -> str:
    """Convert Mirad text to Piper's raw phoneme input format.

    Convert Mirad words to IPA with ``word_to_ipa`` while preserving non-word
    characters (spaces, punctuation, numbers) from the original input. The
    resulting IPA stream is wrapped in ``[[...]]`` so Piper treats it as raw
    phoneme input.
    """
    parts = re.split(r'([A-Za-z]+)', text)
    out: list[str] = []
    for part in parts:
        if part.isalpha():
            out.append(word_to_ipa(part))
        else:
            out.append(part)

    return f"[[{''.join(out)}]]"


def synthesize_to_wav(
    text: str,
    output_path: str | Path,
    model_path: Path | None = None,
) -> Path:
    """Synthesize Mirad text to WAV using Piper TTS.

    This function converts Mirad text to IPA phoneme input, then passes the
    result to Piper using the ``[[...]]`` raw-phoneme input mode. Piper's own
    ``synthesize()`` method handles BOS/EOS/PAD markers and audio
    normalisation correctly, so we delegate to it rather than calling the
    low-level ``phoneme_ids_to_audio()`` API.

    Args:
        text: Mirad text to synthesize.
        output_path: Path where the WAV file should be written.
        model_path: Optional path to a Piper voice model. If None, uses the default.

    Returns:
        Path to the generated WAV file.

    Raises:
        PiperModelNotFoundError: If the voice model file doesn't exist.
        PiperSynthesisError: If synthesis fails for any reason.
    """
    output = Path(output_path)

    # Validate output path
    if output.exists() and output.is_dir():
        raise ValueError(f"output_path must be a file path, got directory: {output}")

    if not output.parent.exists():
        raise ValueError(
            f"output_path parent directory does not exist: {output.parent}"
        )

    # Load the voice model
    try:
        voice = _load_voice(model_path)
    except Exception as exc:
        raise PiperModelNotFoundError(str(model_path or DEFAULT_VOICE_MODEL)) from exc

    # Use raw IPA phoneme input and let the selected model handle its inventory.
    phoneme_input = _text_to_piper_phoneme_input(text)

    # Synthesize using Piper's high-level synthesize() method.
    # This correctly handles:
    #   - BOS (^) / EOS ($) / PAD (_) markers via phonemes_to_ids()
    #   - Audio normalisation (peak-normalise + clip to [-1, 1])
    #   - Proper float32 -> int16 PCM conversion via AudioChunk helpers
    first_chunk = True
    try:
        with wave.open(str(output), "wb") as wav_file:
            for chunk in voice.synthesize(phoneme_input):
                if first_chunk:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit PCM
                    wav_file.setframerate(chunk.sample_rate)
                    first_chunk = False
                wav_file.writeframes(chunk.audio_int16_bytes)

    except Exception as exc:
        raise PiperSynthesisError(
            text=text,
            output_path=str(output),
            cause=exc,
        ) from exc

    if first_chunk:
        raise PiperSynthesisError(
            text=text,
            output_path=str(output),
            cause=RuntimeError("Piper synthesis produced no audio"),
        )

    # Verify output was created
    if not output.exists() or output.stat().st_size == 0:
        raise PiperSynthesisError(
            text=text,
            output_path=str(output),
            cause=RuntimeError("Piper synthesis completed without usable WAV output"),
        )

    return output


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


__all__ = [
    "PiperModelNotFoundError",
    "PiperSynthesisError",
    "synthesize_to_wav",
    "get_available_voices",
    "_load_voice",
    "DEFAULT_VOICE_MODEL",
    "_text_to_piper_phoneme_input",
]
