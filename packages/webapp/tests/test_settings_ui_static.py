from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_settings_placeholder_copy_is_removed() -> None:
    source = _source()

    assert "Placeholder settings" not in source
    assert "Settings arrives in S04" not in source
    assert "theme, TTS speed, voice display, and account deletion controls arriving in S04" not in source


def test_settings_fetches_and_updates_persisted_preferences() -> None:
    source = _source()

    assert 'fetch("/settings", {headers:{"Accept":"application/json"}})' in source
    assert 'fetch("/settings", {method:"PUT"' in source
    assert 'body:JSON.stringify(body)' in source
    assert 'theme: coerceTheme(settingsForm.theme)' in source
    assert 'tts_speed: coerceSpeed(settingsForm.tts_speed)' in source


def test_settings_section_contains_user_facing_controls_and_labels() -> None:
    source = _source()

    assert "Theme" in source
    assert "TTS speed:" in source
    assert "Save" in source
    assert "Delete account" in source
    assert "Admin account cannot be deleted." in source
    assert "Current Mirad voice" not in source


def test_settings_status_and_alert_diagnostics_are_present() -> None:
    source = _source()

    assert 'role="alert"' in source
    assert 'settingsStatus' in source
    assert 'settingsErr' in source
    assert 'deleteAccountStatus' in source
    assert 'deleteAccountErr' in source


def test_settings_logic_isolated_from_practice_queue_and_progress_fetches() -> None:
    source = _source()

    settings_chunk = source.split('async function loadSettings', maxsplit=1)[1].split('async function saveSettings()', maxsplit=1)[0]
    settings_markup = source.split('activeSection === "settings"', maxsplit=1)[1]

    assert "/practice/progress" not in settings_chunk
    assert "/practice/queue" not in settings_chunk
    assert "loadAnalytics" not in settings_markup
    assert "loadPracticeQueue" not in settings_markup
    assert "openSettings" not in source


def test_settings_theme_and_form_styles_exist() -> None:
    css = _css()

    assert '[data-theme="dark"]' in css
    assert ".settings-form" in css
    assert ".fset" in css
    assert ".toggle" in css
    assert ".danger-zone" in css
