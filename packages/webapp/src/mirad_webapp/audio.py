"""Authenticated card audio synthesis helpers for MiraLingo."""

from __future__ import annotations

import importlib
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .practice import stable_card_id

AUDIO_PHASE = "audio_synthesis"
AUDIO_BACKEND = "mbrola"
AUDIO_CONTENT_TYPE = "audio/wav"
_CARD_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*:[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class AudioSuccess:
    """Synthesized WAV bytes plus API diagnostics."""

    wav_bytes: bytes
    content_type: str
    diagnostics: dict[str, Any]


@dataclass(frozen=True)
class AudioFailure:
    """Stacktrace-free audio failure payload plus HTTP status."""

    status_code: int
    payload: dict[str, Any]


AudioResult = AudioSuccess | AudioFailure


def synthesize_card_audio(card_id: str, cards: list[dict[str, Any]]) -> AudioResult:
    """Synthesize one configured card answer to WAV bytes."""
    normalized_card_id = str(card_id or "").strip()
    if not _valid_card_id(normalized_card_id):
        return _failure(
            422,
            normalized_card_id,
            "invalid_card_id",
            "Card id must be a non-path stable practice id such as 'phrase:hello-world'.",
        )

    selected = _find_card(normalized_card_id, cards)
    if selected is None:
        return _failure(
            404,
            normalized_card_id,
            "unknown_card",
            "Practice card was not found in the configured content source.",
        )

    answer = str(selected.get("mirad") or "").strip()
    if not answer:
        return _failure(
            422,
            normalized_card_id,
            "invalid_card_payload",
            "Practice card has no Mirad answer to synthesize.",
        )

    return synthesize_text_audio(answer, diagnostic_id=normalized_card_id)


def synthesize_text_audio(text: str, *, diagnostic_id: str = "text:preview") -> AudioResult:
    """Synthesize arbitrary Mirad text to MBROLA WAV bytes.

    Used by Lexicon previews where the user clicks a semantic lookup result that
    may not correspond to an imported practice card. Text is never used as a
    filesystem path; synthesis happens through a deleted temporary WAV file.
    """
    normalized_text = " ".join(str(text or "").split())
    safe_id = str(diagnostic_id or "text:preview").strip()[:120] or "text:preview"
    if not normalized_text:
        return _failure(422, safe_id, "invalid_tts_text", "Text must not be empty.")
    if len(normalized_text) > 500:
        return _failure(422, safe_id, "invalid_tts_text", "Text must be 500 characters or fewer.")

    try:
        MbrolaError, MbrolaNotFoundError, MbrolaSynthesisError, MbrolaVoiceNotFoundError, synthesize_to_wav = _load_mbrola_backend()
    except ImportError as exc:
        return _failure(
            503,
            safe_id,
            "audio_backend_unavailable",
            f"MBROLA backend import failed: {exc.name or 'mirad_tts'}",
        )

    wav_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            wav_path = Path(handle.name)
        synthesize_to_wav(normalized_text, wav_path)
        wav_bytes = wav_path.read_bytes()
        if not wav_bytes:
            raise MbrolaSynthesisError("MBROLA produced empty WAV output.")
        return AudioSuccess(
            wav_bytes=wav_bytes,
            content_type=AUDIO_CONTENT_TYPE,
            diagnostics={
                "ok": True,
                "phase": AUDIO_PHASE,
                "backend": AUDIO_BACKEND,
                "card_id": safe_id,
                "content_type": AUDIO_CONTENT_TYPE,
                "byte_count": len(wav_bytes),
            },
        )
    except MbrolaNotFoundError as exc:
        return _failure(503, safe_id, "mbrola_unavailable", _safe_detail(exc))
    except MbrolaVoiceNotFoundError as exc:
        return _failure(503, safe_id, "mbrola_voice_unavailable", _safe_detail(exc))
    except (MbrolaSynthesisError, MbrolaError, ValueError, OSError) as exc:
        return _failure(502, safe_id, "audio_synthesis_failed", _safe_detail(exc))
    finally:
        if wav_path is not None:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass


def _load_mbrola_backend():
    """Import MBROLA backend with local-src fallback for dev runs."""
    try:
        module = importlib.import_module("mirad_tts.mbrola_backend")
    except ImportError:
        repo_root = Path(__file__).resolve().parents[4]
        src_path = str(repo_root / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        module = importlib.import_module("mirad_tts.mbrola_backend")

    return (
        module.MbrolaError,
        module.MbrolaNotFoundError,
        module.MbrolaSynthesisError,
        module.MbrolaVoiceNotFoundError,
        module.synthesize_to_wav,
    )


def _find_card(card_id: str, cards: list[dict[str, Any]]) -> dict[str, Any] | None:
    for card in cards:
        if str(card.get("id") or stable_card_id(card)) == card_id:
            return card
    return None


def _valid_card_id(card_id: str) -> bool:
    return bool(card_id) and "/" not in card_id and "\\" not in card_id and ".." not in card_id and bool(_CARD_ID_RE.fullmatch(card_id))


def _failure(status_code: int, card_id: str, error: str, detail: str) -> AudioFailure:
    return AudioFailure(
        status_code=status_code,
        payload={
            "ok": False,
            "error": error,
            "phase": AUDIO_PHASE,
            "backend": AUDIO_BACKEND,
            "card_id": card_id,
            "detail": detail,
        },
    )


def _safe_detail(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


__all__ = [
    "AUDIO_BACKEND",
    "AUDIO_CONTENT_TYPE",
    "AUDIO_PHASE",
    "AudioFailure",
    "AudioResult",
    "AudioSuccess",
    "synthesize_card_audio",
    "synthesize_text_audio",
]
