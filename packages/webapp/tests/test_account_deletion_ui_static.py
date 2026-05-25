from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_delete_account_form_requires_current_confirmation_phrase_before_enable() -> None:
    source = _source()

    assert 'const deleteConfirmPhrase = () => `${user?.username ?? ""} DELETE`.trim();' in source
    assert 'deleteAccountConfirm.trim()===deleteConfirmPhrase()' in source
    assert 'placeholder={deleteConfirmPhrase()}' in source
    assert 'disabled={!canSubmitDelete() || deleteAccountState==="submitting"}' in source
    assert 'deleteAccountConfirmationPhrase' not in source


def test_delete_account_uses_confirmed_delete_endpoint_and_clears_authenticated_state() -> None:
    source = _source()

    assert 'fetch("/auth/account", {method:"DELETE"' in source
    assert 'body:JSON.stringify({username:deleteAccountUsername,confirmation:deleteAccountConfirm})' in source
    assert 'clearAuthAppState("Account deleted. Create a new account or log in again.");' in source
    assert 'resetPracticeSurface(); resetAnalyticsSurface(); resetSettingsSurface();' in source
    assert 'authState="anonymous"' in source


def test_delete_account_warning_copy_and_a11y_diagnostics_are_visible() -> None:
    source = _source()

    assert 'Delete account' in source
    assert 'Type <strong>{deleteConfirmPhrase()}</strong> to confirm' in source
    assert 'Admin account cannot be deleted.' in source
    assert 'role="alert"' in source
    assert 'deleteAccountStatus="Account deleted."' in source


def test_delete_account_styles_cover_current_danger_zone_and_confirmation_fields() -> None:
    css = _css()

    assert '.danger-zone' in css
    assert '.danger-title' in css
    assert '.del-form' in css
    assert '.field-input' in css
