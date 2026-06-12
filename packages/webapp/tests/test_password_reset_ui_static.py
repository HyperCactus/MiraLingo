from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
RESET_PAGE = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "pages" / "ResetPassword.svelte"
WELCOME_PAGE = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "pages" / "Welcome.svelte"
AUTH_API = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "api" / "auth.ts"


def _source() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND_APP, RESET_PAGE, WELCOME_PAGE, AUTH_API))


def test_password_reset_link_renders_custom_form_and_posts_token_without_displaying_it() -> None:
    source = _source()

    assert 'new URLSearchParams(window.location.search).get("reset_token")' in source
    assert '{#if resetToken}' in source
    assert "<ResetPassword" in source
    assert "export async function resetPassword" in source
    assert "fetch('/auth/password/reset'" in source
    assert "body: JSON.stringify({ token, password })" in source
    assert "Choose a new password" in source
    assert "bind:confirmPassword" in source
    assert "Passwords do not match." in source


def test_password_length_bounds_are_visible_and_enforced_on_create_and_reset_forms() -> None:
    source = _source()

    assert "const PASSWORD_MIN_LENGTH = 8;" in source
    assert "const PASSWORD_MAX_LENGTH = 128;" in source
    assert "Password must be 8 to 128 characters." in source
    assert 'autocomplete="new-password" bind:value={registrationPassword} minlength="8" maxlength="128"' in source
    assert 'bind:value={newPassword} minlength="8" maxlength="128"' in source
    assert 'bind:value={confirmPassword} minlength="8" maxlength="128"' in source
