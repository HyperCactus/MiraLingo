from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def test_audio_control_fetches_mirad_audio_identifier_endpoint() -> None:
    frontend_source = _source()

    # audio card id uses fallback chain: audio_card_id → base_card_id → id
    cid_line = "currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id"
    assert cid_line in frontend_source
    assert 'fetch(`/practice/audio/${encodeURIComponent(cid)}`,' in frontend_source  # backtick closes URL, then comma
    assert '{headers:{"Accept":"audio/wav,application/json"}}' in frontend_source
    assert 'if (!currentCard || audioState==="loading") return;' in frontend_source
    assert "canPlayAudio()" in frontend_source  # TTS gating: only play after answer revealed


def test_word_card_tts_uses_prompt_variant_not_full_card_content() -> None:
    """Word-card audio must call fetchMbrolaTextAudio with the single shown prompt variant,
    not the full card content (which contains all comma-separated alternatives)."""
    frontend_source = _source()

    # fetchMbrolaTextAudio must be imported so the frontend can call it with prompt text
    assert "fetchMbrolaTextAudio" in frontend_source

    # For word cards, TTS the shown prompt variant; for phrase cards, use card-ID endpoint
    assert 'currentCard.type === "word"' in frontend_source
    assert "fetchMbrolaTextAudio(currentCard.prompt ?? " in frontend_source
    # The phrase/other path must still fall back to the card-ID audio endpoint via template-literal fetch
    assert 'fetch(`/practice/audio/${encodeURIComponent(cid)}`,' in frontend_source


def test_audio_control_has_accessible_speaker_affordance() -> None:
    frontend_source = _source()

    # TTS is rendered inside the practice card section (inside {#if currentCard})
    assert 'class="btn-tts"' in frontend_source
    assert 'aria-label="Hear Mirad"' in frontend_source  # Mir→En direction (prompt visible)
    assert 'aria-label="Hear answer"' in frontend_source  # En→Mir direction (after reveal)
    assert 'disabled={audioState==="loading"}' in frontend_source
    assert "🔊" in frontend_source  # emoji-only TTS button


def test_audio_success_path_uses_blob_url_and_revokes_stale_urls() -> None:
    frontend_source = _source()

    assert "const blob = await r.blob();" in frontend_source
    assert "URL.createObjectURL(blob)" in frontend_source
    assert "activeAudio=new Audio(url)" in frontend_source  # creates Audio from blob URL
    assert "activeAudio.play()" in frontend_source
    assert "URL.revokeObjectURL(audioBlobUrl)" in frontend_source
    assert "activeAudio.pause()" in frontend_source
    # TTS gating: only allows playback after canPlayAudio() returns true
    assert "canPlayAudio()" in frontend_source


def test_audio_playback_rate_uses_persisted_speed_with_safe_default() -> None:
    frontend_source = _source()

    assert 'tts_speed: 0.8,' in frontend_source
    assert 'const coerceSpeed = (s) =>' in frontend_source  # validates 0.5-2.0, defaults 0.8
    assert 'const effSpd = () =>' in frontend_source  # reads from settingsForm
    assert "activeAudio.playbackRate=spd" in frontend_source
    assert 'parseFloat(settingsForm?.tts_speed)' in frontend_source  # uses form state, not persistedSettings


def test_audio_json_unavailable_and_failure_messages_are_visible() -> None:
    frontend_source = _source()

    assert "ct.includes(\"application/json\")" in frontend_source  # ct = content-type header
    assert "const p = await readJson(r);" in frontend_source
    assert 'audioState = r.status===401 ? "error" : "unavailable";' in frontend_source
    assert 'p?.error==="mbrola_unavailable"' in frontend_source
    assert '"Session expired."' in frontend_source  # 401 case
    assert '"Audio unavailable."' in frontend_source  # JSON error case
    assert 'audioState="error"; audioMsg="Could not play audio."' in frontend_source  # catch block
    # Error display uses role=alert for error/unavailable states
    assert 'audioState==="error" || audioState==="unavailable"' in frontend_source
    # TTS gating message when trying to play before answer is revealed
    assert "canPlayAudio()" in frontend_source
    assert '"Reveal answer first."' in frontend_source  # gating fallback message


def test_audio_state_resets_on_queue_refresh_card_change_and_logout() -> None:
    frontend_source = _source()

    # loadPracticeQueue resets audio before fetching
    load_queue_body = frontend_source.split("async function loadPracticeQueue(mode=", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert "resetAudio();" in load_queue_body
    assert "resetAnswer();" in load_queue_body

    # logout resets the full practice surface (includes audio)
    logout_body = frontend_source.split("async function logout()", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert "resetPracticeSurface();" in logout_body
    assert "resetSettingsSurface();" in logout_body

    # Card change resets audio via $effect watching audio_card_id
    assert "audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id" in frontend_source
    assert "lastAudioCardId=id" in frontend_source
    # advancePracticeCard also clears answerResult to prevent stale TTS on new card
    assert "resetAnswer();" in frontend_source.split("async function advancePracticeCard()", maxsplit=1)[1].split("async function", maxsplit=1)[0]


def test_audio_styles_include_compact_mobile_row() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    # New design uses .btn-tts (emoji-only, inline with Mirad text)
    assert ".btn-tts" in css_source
    assert ".pcard-icon-frame" in css_source  # icon frame in practice card
    assert ".audio-err" in css_source  # error message below card
