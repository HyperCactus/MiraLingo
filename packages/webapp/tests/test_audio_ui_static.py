from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def test_audio_control_fetches_mirad_audio_identifier_endpoint() -> None:
    frontend_source = _source()

    assert "const audioCardId = currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id;" in frontend_source
    assert "fetch(`/practice/audio/${encodeURIComponent(audioCardId)}`" in frontend_source
    assert 'headers: { Accept: "audio/wav, application/json" }' in frontend_source
    assert "if (!currentCard || audioState === \"loading\") return;" in frontend_source


def test_audio_control_has_accessible_speaker_affordance() -> None:
    frontend_source = _source()
    authenticated_branch = frontend_source.split('{#if authState === "authenticated"}', maxsplit=1)[1].split("{:else}", maxsplit=1)[0]

    assert 'class="audio-row" aria-label="Mirad answer audio"' in authenticated_branch
    assert 'aria-label="Play Mirad answer audio"' in authenticated_branch
    assert "Hear Mirad answer" in authenticated_branch
    assert "Preparing audio…" in authenticated_branch
    assert "Playing…" in authenticated_branch
    assert 'disabled={audioState === "loading"}' in authenticated_branch


def test_audio_success_path_uses_blob_url_and_revokes_stale_urls() -> None:
    frontend_source = _source()

    assert "const blob = await response.blob();" in frontend_source
    assert "URL.createObjectURL(blob)" in frontend_source
    assert "new Audio(nextBlobUrl)" in frontend_source
    assert "activeAudio.play()" in frontend_source
    assert "URL.revokeObjectURL(audioBlobUrl)" in frontend_source
    assert "activeAudio.pause()" in frontend_source
    assert "new Audio(" not in frontend_source.split("loadCurrentUser();", maxsplit=1)[1]


def test_audio_playback_rate_uses_persisted_speed_with_safe_default() -> None:
    frontend_source = _source()

    assert 'tts_speed: 0.8,' in frontend_source
    assert 'const effectiveTtsSpeed = () => coerceSpeed(persistedSettings?.tts_speed);' in frontend_source
    assert 'const ttsSpeed = effectiveTtsSpeed();' in frontend_source
    assert 'activeAudio.playbackRate = ttsSpeed;' in frontend_source
    assert 'Audio uses your saved {speedLabel(effectiveTtsSpeed())} learner speed preference.' in frontend_source
    assert 'Playing Mirad audio at ${speedLabel(ttsSpeed)}.' in frontend_source


def test_audio_json_unavailable_and_failure_messages_are_visible() -> None:
    frontend_source = _source()

    assert 'contentType.includes("application/json")' in frontend_source
    assert "const payload = await readJson(response);" in frontend_source
    assert 'audioState = response.status === 401 ? "error" : "unavailable";' in frontend_source
    assert "friendlyAudioError(payload, response.status)" in frontend_source
    assert "formatAudioDiagnostic(payload)" in frontend_source
    assert "Your session expired. Log in again to hear this card." in frontend_source
    assert 'payload?.error === "mbrola_voice_unavailable"' in frontend_source
    assert "The Mirad de6 voice is not installed on this server." in frontend_source
    assert 'audioDiagnostic = `playback_rate_unavailable requested=${speedLabel(ttsSpeed)}`;' in frontend_source
    assert 'audioDiagnostic = audioDiagnostic || "network_or_browser_playback";' in frontend_source
    assert "Could not play audio. Check the server, then try again." in frontend_source
    assert 'role={audioState === "error" || audioState === "unavailable" ? "alert" : "status"}' in frontend_source


def test_audio_state_resets_on_queue_refresh_card_change_and_logout() -> None:
    frontend_source = _source()

    load_queue_body = frontend_source.split("async function loadPracticeQueue(mode = activePracticeMode)", maxsplit=1)[1].split("async function openPracticeMode", maxsplit=1)[0]
    logout_body = frontend_source.split("async function logout()", maxsplit=1)[1].split("async function loadPracticeQueue(mode = activePracticeMode)", maxsplit=1)[0]

    assert "resetAudioState();" in load_queue_body
    assert "resetPracticeSurface();" in logout_body
    assert "resetSettingsSurface();" in logout_body
    assert '$: if ((currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id ?? null) !== lastAudioCardId)' in frontend_source
    assert "lastAudioCardId = currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id ?? null;" in frontend_source


def test_audio_styles_include_compact_mobile_row() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    assert ".audio-row" in css_source
    assert ".audio-button" in css_source
    assert ".audio-diagnostic" in css_source
    assert "@media (max-width: 820px)" in css_source
    assert ".audio-button," in css_source
