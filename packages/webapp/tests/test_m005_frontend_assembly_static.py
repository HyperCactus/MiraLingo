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

    assert "Welcome to MiraLingo" in anonymous_chunk
    assert "Practice Mirad" in anonymous_chunk
    assert "Mirad learning lab" in anonymous_chunk
    assert "Mirad and MiraLingo docs" in anonymous_chunk
    assert "https://en.wikibooks.org/wiki/Mirad_Grammar" in source
    assert "Wikibooks grammar" in source
    assert 'target={link.external ? "_blank" : undefined}' in anonymous_chunk
    assert 'rel={link.external ? "noreferrer" : undefined}' in anonymous_chunk


def test_authenticated_menu_and_section_contracts_stay_visible() -> None:
    source = _source()

    assert 'let activeSection = "menu";' in source
    assert 'activeSection === "menu"' in source
    assert 'activeSection === "practice"' in source
    assert 'activeSection === "revision"' in source
    assert 'activeSection === "build_vocabulary"' in source
    assert 'activeSection === "analytics"' in source
    assert 'activeSection === "settings"' in source

    for label in (
        "Continue Practice",
        "Revision",
        "Build Vocabulary",
        "Analytics",
        "Settings",
        "Log Out",
    ):
        assert label in source


def test_practice_mode_menu_items_and_queue_requests_cover_all_acceptance_modes() -> None:
    source = _source()

    assert 'mode: "mixed"' in source
    assert 'mode: "revision"' in source
    assert 'mode: "build_vocabulary"' in source
    assert 'let queueUrl = "/practice/queue?mode=mixed&limit=3";' in source
    assert 'if (mode === "revision") queueUrl = "/practice/queue?mode=revision&limit=3";' in source
    assert 'if (mode === "build_vocabulary") queueUrl = "/practice/queue?mode=build_vocabulary&limit=3";' in source
    assert 'activePracticeMode = mode;' in source


def test_typed_answer_submission_and_give_up_preserve_backend_truth_contract() -> None:
    source = _source()
    record_answer_chunk = source.split("async function recordPracticeAnswer(payloadBody)", maxsplit=1)[1].split(
        "async function submitTypedPracticeAnswer()", maxsplit=1
    )[0]
    typed_submit_chunk = source.split("async function submitTypedPracticeAnswer()", maxsplit=1)[1].split(
        "async function submitGiveUp()", maxsplit=1
    )[0]
    give_up_chunk = source.split("async function submitGiveUp()", maxsplit=1)[1].split(
        "async function advancePracticeCard()", maxsplit=1
    )[0]

    assert 'fetch("/practice/answers", {' in record_answer_chunk
    assert 'body: JSON.stringify(payloadBody)' in record_answer_chunk
    assert 'const normalizedAnswer = typedAnswer.trim();' in typed_submit_chunk
    assert 'await recordPracticeAnswer({ card_id: currentCard.id, answer: normalizedAnswer });' in typed_submit_chunk
    assert 'correct: true' not in typed_submit_chunk
    assert 'correct: true' not in record_answer_chunk
    assert 'await recordPracticeAnswer({ card_id: currentCard.id, correct: false });' in give_up_chunk
    assert 'answerResult.correct ? "Correct" : "Not quite"' in source
    assert 'The correct answer is revealed below.' in source
    assert 'expected_answer' in source
    assert 'submitted_answer' in source


def test_audio_settings_and_diagnostics_use_persisted_speed_fallback() -> None:
    source = _source()
    audio_chunk = source.split("async function playCardAudio()", maxsplit=1)[1].split(
        "function activateMenuItem(item)", maxsplit=1
    )[0]

    assert 'const ttsSpeed = effectiveTtsSpeed();' in audio_chunk
    assert 'activeAudio.playbackRate = ttsSpeed;' in audio_chunk
    assert 'audioDiagnostic = `playback_rate_unavailable requested=${speedLabel(ttsSpeed)}`;' in audio_chunk
    assert 'Audio uses your saved {speedLabel(effectiveTtsSpeed())} learner speed preference.' in source
    assert 'role={audioState === "error" || audioState === "unavailable" ? "alert" : "status"}' in source
    assert 'audioDiagnostic' in source


def test_settings_load_save_voice_metadata_and_account_deletion_contracts() -> None:
    source = _source()
    settings_load_chunk = source.split("async function loadSettings", maxsplit=1)[1].split(
        "async function loadCurrentUser()", maxsplit=1
    )[0]
    settings_save_chunk = source.split("async function saveSettings()", maxsplit=1)[1].split(
        "async function submitDeleteAccount()", maxsplit=1
    )[0]
    delete_chunk = source.split("async function submitDeleteAccount()", maxsplit=1)[1].split(
        "async function recordPracticeAnswer(payloadBody)", maxsplit=1
    )[0]

    assert 'const response = await fetch("/settings", {' in settings_load_chunk
    assert 'method: "PUT"' in settings_save_chunk
    assert 'body: JSON.stringify(payloadBody)' in settings_save_chunk
    assert 'theme: coerceTheme(settingsForm.theme)' in settings_save_chunk
    assert 'tts_speed: coerceSpeed(settingsForm.tts_speed)' in settings_save_chunk
    assert 'Current Mirad voice' in source
    assert 'aria-label="Current voice metadata"' in source
    assert 'Voice label' in source
    assert 'Voice id' in source
    assert 'Provider' in source
    assert 'Single available voice' in source
    assert 'Type the exact confirmation phrase to enable deletion' in source
    assert 'const deleteAccountConfirmHelpId = "delete-account-confirm-help";' in source
    assert 'const deleteAccountConfirmationPhrase = () => `${user?.username ?? ""} DELETE`.trim();' in source
    assert 'fetch("/auth/account", {' in delete_chunk
    assert 'method: "DELETE"' in delete_chunk
    assert 'confirmation: deleteAccountConfirmation,' in delete_chunk
    assert 'username: deleteAccountUsername,' in delete_chunk


def test_iconify_contract_uses_bounded_fetch_validation_cache_img_and_visible_status() -> None:
    source = _source()
    icon_chunk = source.split("async function loadCardIcon(card)", maxsplit=1)[1].split(
        "const formatPercent =", maxsplit=1
    )[0]

    assert 'const ICONIFY_TIMEOUT_MS = 2500;' in source
    assert 'const ICONIFY_SEARCH_LIMIT = 6;' in source
    assert 'const iconCache = new Map();' in source
    assert 'const controller = new AbortController();' in icon_chunk
    assert 'setTimeout(() => controller.abort(), ICONIFY_TIMEOUT_MS);' in icon_chunk
    assert 'clearTimeout(timeoutId);' in icon_chunk
    assert 'fetch(`https://api.iconify.design/search?query=${query}&limit=${ICONIFY_SEARCH_LIMIT}`, {' in icon_chunk
    assert 'const matchedIcon = icons.find((name) => isAllowedIconName(name));' in icon_chunk
    assert 'const ICONIFY_ICON_NAME_PATTERN = /^[a-z0-9-]+:[a-z0-9-]+$/;' in source
    assert 'return ICONIFY_ALLOWED_COLLECTIONS.has(collection) && Boolean(icon);' in source
    assert 'return `https://api.iconify.design/${encodeURIComponent(collection)}/${encodeURIComponent(icon)}.svg?color=%231d4ed8`;' in source
    assert '<img class="card-icon-image" src={iconImageUrl} alt={iconAlt} />' in source
    assert 'Iconify status: {iconStatus}' in source
    assert 'role="status"' in source
    assert 'iconError' in source
    assert 'iconDiagnostic' in source
    assert 'fallback' in source


def test_css_keeps_theme_focus_and_responsive_contracts() -> None:
    css = _css()

    assert ':root[data-theme="dark"]' in css
    assert 'body[data-theme="dark"]' in css
    assert '@media (max-width: 980px)' in css
    assert '@media (max-width: 820px)' in css
    assert ':focus-visible' in css
    assert 'outline: 3px solid var(--focus-ring);' in css
    assert '.toggle-card:has(input:focus-visible)' in css
    assert '.menu-grid' in css
    assert '.analytics-grid' in css
    assert '.theme-fieldset' in css


def test_negative_static_guards_block_unsafe_or_drifted_frontend_patterns() -> None:
    source = _source()

    assert '{@html' not in source
    assert '@iconify/' not in source
    assert 'from "@iconify' not in source
    assert "from '@iconify" not in source
    assert '/node_modules/@iconify' not in source
    assert 'fetch("/practice/progress"' not in source.split("async function loadPracticeQueue", maxsplit=1)[1].split(
        "async function openPracticeMode", maxsplit=1
    )[0]
    assert 'fetch("/practice/progress"' not in source.split("async function recordPracticeAnswer(payloadBody)", maxsplit=1)[1].split(
        "async function submitTypedPracticeAnswer()", maxsplit=1
    )[0]
    assert 'correct: true' not in source


def test_error_paths_keep_status_or_alert_markers_for_settings_answers_and_iconify() -> None:
    source = _source()

    assert 'practiceError = friendlyPracticeError(payload, "Answer rejected. Refresh the queue and try again.");' in source
    assert 'settingsError = friendlySettingsError(payload, "Could not save learner settings. Your unsaved selections are still visible.");' in source
    assert 'Settings error ({settingsPhase}): {settingsError}' in source
    assert 'Account deletion error: {deleteAccountError}' in source
    assert 'Iconify status: {iconStatus}' in source
    assert 'role="alert"' in source
    assert 'role="status"' in source
