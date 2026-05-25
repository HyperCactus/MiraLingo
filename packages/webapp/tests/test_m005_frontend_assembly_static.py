from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_logged_out_landing_keeps_public_mirad_learning_contracts() -> None:
    source = _source()
    anonymous_chunk = source.split("{:else}", maxsplit=1)[1]

    assert "MiraLingo" in anonymous_chunk
    assert "Practice Mirad pronunciation and translation." in anonymous_chunk
    assert "https://en.wikibooks.org/wiki/Mirad_Grammar" in source
    assert "Mirad Grammar" in source
    assert 'target="_blank"' in anonymous_chunk
    assert 'rel="noopener"' in anonymous_chunk
    assert "Welcome to MiraLingo" not in anonymous_chunk


def test_authenticated_menu_and_section_contracts_stay_visible() -> None:
    source = _source()

    assert 'let activeSection = $state("menu");' in source
    for section in ('"menu"', '"practice"', '"revision"', '"build_vocabulary"', '"analytics"', '"settings"'):
        assert f'activeSection === {section}' in source

    for label in ("Continue Practice", "Revision", "Vocabulary", "Analytics", "Settings", "Log Out"):
        assert label in source


def test_practice_mode_menu_items_and_queue_requests_cover_all_acceptance_modes() -> None:
    source = _source()

    assert 'mode:"mixed"' in source
    assert 'mode:"revision"' in source
    assert 'mode:"build_vocabulary"' in source
    assert '/practice/queue?mode=mixed&limit=${LIMIT}' in source
    assert '/practice/queue?mode=revision&limit=${LIMIT}' in source
    assert '/practice/queue?mode=build_vocabulary&limit=${LIMIT}' in source
    assert 'practiceQueueMode=mode' in source
    assert 'mode: "mixed"' not in source


def test_typed_answer_submission_and_skip_preserve_backend_truth_contract() -> None:
    source = _source()
    record_answer_chunk = source.split("async function recordAnswer(body)", maxsplit=1)[1].split(
        "async function submitAnswer()", maxsplit=1
    )[0]
    typed_submit_chunk = source.split("async function submitAnswer()", maxsplit=1)[1].split(
        "async function submitGiveUp()", maxsplit=1
    )[0]
    skip_chunk = source.split("async function submitGiveUp()", maxsplit=1)[1].split(
        "// ── audio", maxsplit=1
    )[0]

    assert 'fetch("/practice/answers", {' in record_answer_chunk
    assert 'body:JSON.stringify(body)' in record_answer_chunk
    assert 'const norm = typedAnswer.trim();' in typed_submit_chunk
    assert 'await recordAnswer({card_id:currentCard.id, answer:norm});' in typed_submit_chunk
    assert 'correct:true' not in typed_submit_chunk
    assert 'correct:true' not in record_answer_chunk
    assert 'await recordAnswer({card_id:currentCard.id, correct:false});' in skip_chunk
    assert 'answerResult.correct ? "✓ Correct" : "✗ Not quite"' in source
    assert 'expected_answer' in source
    assert 'submitted_answer' in source


def test_audio_settings_use_current_speed_and_error_surface() -> None:
    source = _source()
    audio_chunk = source.split("async function playCardAudio()", maxsplit=1)[1].split(
        "function canPlayAudio()", maxsplit=1
    )[0]

    assert 'const spd = effSpd();' in audio_chunk
    assert 'activeAudio.playbackRate=spd;' in audio_chunk
    assert 'audioState="error"' in audio_chunk
    assert 'audioMsg="Could not play audio."' in audio_chunk
    assert 'role="alert"' in source


def test_settings_load_save_and_account_deletion_contracts() -> None:
    source = _source()
    settings_save_chunk = source.split("async function saveSettings()", maxsplit=1)[1].split(
        "// ── practice queue", maxsplit=1
    )[0]
    delete_chunk = source.split("async function submitDeleteAccount()", maxsplit=1)[1].split(
        "// ── navigation helpers", maxsplit=1
    )[0]

    assert 'fetch("/settings", {headers:{"Accept":"application/json"}})' in source
    assert 'method:"PUT"' in settings_save_chunk
    assert 'body:JSON.stringify(body)' in settings_save_chunk
    assert 'theme: coerceTheme(settingsForm.theme)' in settings_save_chunk
    assert 'tts_speed: coerceSpeed(settingsForm.tts_speed)' in settings_save_chunk
    assert 'TTS speed:' in source
    assert 'Delete account' in source
    assert 'const deleteConfirmPhrase = () => `${user?.username ?? ""} DELETE`.trim();' in source
    assert 'fetch("/auth/account", {' in delete_chunk
    assert 'method:"DELETE"' in delete_chunk
    assert 'confirmation:deleteAccountConfirm' in delete_chunk
    assert 'username:deleteAccountUsername' in delete_chunk


def test_iconify_contract_uses_bounded_fetch_validation_cache_img_and_no_debug_panel() -> None:
    source = _source()
    icon_chunk = source.split("async function loadIc(card)", maxsplit=1)[1].split(
        "// ── state", maxsplit=1
    )[0]

    assert 'const IC_TMO = 2500;' in source
    assert 'const IC_LIM = 6;' in source
    assert 'const iconCache = new Map();' in source
    assert 'const ctrl = new AbortController();' in icon_chunk
    assert 'setTimeout(() => ctrl.abort(), IC_TMO);' in icon_chunk
    assert 'clearTimeout(to);' in icon_chunk
    assert 'fetch(`https://api.iconify.design/search?query=${q}&limit=${IC_LIM}`, {' in icon_chunk
    assert 'const match = icons.find(icOk);' in icon_chunk
    assert 'const IC_PAT = /^[a-z0-9-]+:[a-z0-9-]+$/;' in source
    assert '<img src={icImg} alt={icAlt} class="pcard-icon-img" />' in source
    assert 'Iconify status' not in source


def test_css_keeps_current_theme_focus_and_responsive_contracts() -> None:
    css = _css()

    assert '[data-theme="dark"]' in css
    assert '@media (max-width: 480px)' in css
    assert '.pcard-input:focus' in css
    assert '.menu-btns' in css
    assert '.stats-grid' in css
    assert '.settings-form' in css


def test_negative_static_guards_block_unsafe_or_drifted_frontend_patterns() -> None:
    source = _source()

    assert '{@html' not in source
    assert '@iconify/' not in source
    assert 'from "@iconify' not in source
    assert "from '@iconify" not in source
    assert '/node_modules/@iconify' not in source
    assert 'fetch("/practice/progress"' not in source.split("async function loadPracticeQueue", maxsplit=1)[1].split(
        "async function preloadPracticeQueue", maxsplit=1
    )[0]
    assert 'fetch("/practice/progress"' not in source.split("async function recordAnswer(body)", maxsplit=1)[1].split(
        "async function submitAnswer()", maxsplit=1
    )[0]
    assert 'correct:true' not in source
    assert 'async function recordPracticeAnswer' not in source


def test_error_paths_keep_alert_markers_for_settings_answers_and_iconify() -> None:
    source = _source()

    assert 'practiceErr=p?.detail??"Answer rejected."' in source
    assert 'settingsErr=p?.detail??"Could not save."' in source
    assert 'deleteAccountErr=p?.detail??"Could not delete."' in source
    assert 'icErr' in source
    assert 'role="alert"' in source
