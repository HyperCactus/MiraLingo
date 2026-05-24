from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_delete_account_form_requires_explicit_confirmation_phrase_before_enable() -> None:
    source = _source()

    assert 'const deleteAccountConfirmationPhrase = () => `${user?.username ?? ""} DELETE`.trim();' in source
    assert 'const deleteAccountConfirmHelpId = "delete-account-confirm-help";' in source
    assert 'const canSubmitAccountDeletion = () =>' in source
    assert 'deleteAccountConfirmation.trim() === deleteAccountConfirmationPhrase()' in source
    assert 'Type the exact confirmation phrase to enable deletion' in source
    assert 'placeholder={deleteAccountConfirmationPhrase()}' in source
    assert 'disabled={!canSubmitAccountDeletion() || deleteAccountState === "submitting"}' in source


def test_delete_account_uses_confirmed_delete_endpoint_and_clears_authenticated_state() -> None:
    source = _source()

    assert 'fetch("/auth/account", {' in source
    assert 'method: "DELETE"' in source
    assert 'confirmation: deleteAccountConfirmation,' in source
    assert 'clearAuthenticatedAppState(`Deleted account ${payload.deleted_username ?? user.username}. You can create a new learner account or log in again.`);' in source
    assert 'practiceQueue = null;' in source
    assert 'currentCard = null;' in source
    assert 'answerResult = null;' in source
    assert 'analyticsPayload = null;' in source
    assert 'persistedSettings = structuredClone(DEFAULT_SETTINGS);' in source
    assert 'audioDiagnostic = "";' in source
    assert 'authState = "anonymous";' in source


def test_delete_account_warning_copy_and_a11y_diagnostics_are_visible() -> None:
    source = _source()

    assert 'This permanently removes this learner account, saved settings, shown-card history, and recorded answers.' in source
    assert 'Current account deletion is irreversible.' in source
    assert 'aria-describedby={deleteAccountConfirmHelpId}' in source
    assert 'role="status"' in source
    assert 'role="alert"' in source
    assert 'Delete current account' in source
    assert 'let authStatusMessage = "";' in source
    assert 'authStatusMessage = statusMessage;' in source
    assert '{#if authStatusMessage}' in source


def test_delete_account_styles_cover_danger_zone_and_confirmation_field() -> None:
    css = _css()

    assert '.danger-zone' in css
    assert '.danger-note' in css
    assert '.delete-account-form' in css
