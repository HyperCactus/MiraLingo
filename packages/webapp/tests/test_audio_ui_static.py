from __future__ import annotations

from pathlib import Path


FRONTEND_SRC = Path(__file__).parents[1] / "frontend" / "src"
FRONTEND_APP = FRONTEND_SRC / "App.svelte"
FRONTEND_CSS = FRONTEND_SRC / "app.css"
AUDIO_API = FRONTEND_SRC / "lib" / "api" / "audio.ts"
EXERCISE_CARD = FRONTEND_SRC / "lib" / "components" / "learning" / "ExerciseCard.svelte"
EXERCISE_PROMPT = FRONTEND_SRC / "lib" / "components" / "learning" / "ExercisePrompt.svelte"
FEEDBACK_PANEL = FRONTEND_SRC / "lib" / "components" / "learning" / "FeedbackPanel.svelte"
AUDIO_BUTTON = FRONTEND_SRC / "lib" / "components" / "learning" / "AudioButton.svelte"


def _source() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (FRONTEND_APP, AUDIO_API, EXERCISE_CARD, EXERCISE_PROMPT, FEEDBACK_PANEL, AUDIO_BUTTON)
    )


def test_audio_control_fetches_mirad_audio_identifier_endpoint() -> None:
    source = _source()

    assert "currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id" in source
    assert "getPracticeAudioUrl(cardId" in source
    assert "`/practice/audio/${encodeURIComponent(cardId)}`" in source
    assert "Accept: \"audio/wav,application/json\"" in source
    assert "canPlayAudio" in source


def test_audio_button_is_accessible_and_reveal_aware() -> None:
    source = _source()

    assert "AudioButton" in source
    assert "aria-label={label}" in source
    assert "🔊" in source
    assert "showPromptAudio" in source
    assert "canPlayAudio={audioEnabled}" in source
    assert "audioLabel={'Play Mirad audio'}" in source


def test_audio_success_path_uses_blob_url_and_revokes_stale_urls() -> None:
    source = _source()

    assert "const blob = await response.blob();" in source
    assert "URL.createObjectURL(blob)" in source
    assert "new Audio(url)" in source
    assert "audio.playbackRate" in source
    assert "audio.play()" in source
    assert "URL.revokeObjectURL(audioBlobUrl)" in source
    assert "activeAudio.pause()" in source


def test_audio_playback_rate_uses_persisted_speed_with_safe_default() -> None:
    source = _source()

    assert "const coerceSpeed = (value) =>" in source
    assert "0.8" in source
    assert "tts_speed: coerceSpeed($ttsSpeed)" in source
    assert "audio.playbackRate" in source
    assert "$ttsSpeed" in source


def test_audio_json_unavailable_and_failure_messages_are_visible() -> None:
    source = _source()

    assert "contentType.includes(\"audio\")" in source
    assert "const payload = await readJson(response);" in source
    assert 'audioState = response.status === 404 ? "unavailable" : "error";' in source
    assert 'audioMsg = payload?.detail ?? "Audio unavailable.";' in source
    assert 'audioMsg = "Could not play audio.";' in source
    assert "audioMessage" in source


def test_audio_state_resets_on_queue_refresh_card_change_and_logout() -> None:
    source = _source()

    apply_queue_body = source.split("function applyPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert "resetAnswer();" in apply_queue_body
    assert "resetAudio();" in apply_queue_body
    assert "resetPracticeSurface" in source
    assert "lastAudioCardId" in source


def test_audio_styles_include_compact_mobile_row() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    assert ".btn-tts" in css_source
    assert ".pcard-icon-frame" in css_source
    assert ".audio-err" in css_source
