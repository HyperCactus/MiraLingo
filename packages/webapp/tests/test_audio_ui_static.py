from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def test_audio_control_fetches_card_bound_encoded_endpoint() -> None:
    frontend_source = _source()

    assert "fetch(`/practice/audio/${encodeURIComponent(currentCard.id)}`" in frontend_source
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


def test_audio_json_unavailable_and_failure_messages_are_visible() -> None:
    frontend_source = _source()

    assert 'contentType.includes("application/json")' in frontend_source
    assert "const payload = await readJson(response);" in frontend_source
    assert 'audioState = response.status === 401 ? "error" : "unavailable";' in frontend_source
    assert "friendlyAudioError(payload, response.status)" in frontend_source
    assert "formatAudioDiagnostic(payload)" in frontend_source
    assert "Your session expired. Log in again to hear this card." in frontend_source
    assert "Could not play audio. Check the server, then try again." in frontend_source
    assert 'role={audioState === "error" || audioState === "unavailable" ? "alert" : "status"}' in frontend_source


def test_audio_state_resets_on_queue_refresh_card_change_and_logout() -> None:
    frontend_source = _source()

    load_queue_body = frontend_source.split("async function loadPracticeQueue()", maxsplit=1)[1].split("async function submitPracticeAnswer", maxsplit=1)[0]
    logout_body = frontend_source.split("async function logout()", maxsplit=1)[1].split("async function loadPracticeQueue", maxsplit=1)[0]

    assert "resetAudioState();" in load_queue_body
    assert "resetAudioState();" in logout_body
    assert "lastAudioCardId = null;" in logout_body
    assert '$: if ((currentCard?.id ?? null) !== lastAudioCardId)' in frontend_source
    assert "lastAudioCardId = currentCard?.id ?? null;" in frontend_source


def test_audio_styles_include_compact_mobile_row() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    assert ".audio-row" in css_source
    assert ".audio-button" in css_source
    assert ".audio-diagnostic" in css_source
    assert "@media (max-width: 820px)" in css_source
    assert ".audio-button," in css_source
