from __future__ import annotations

from pathlib import Path


FRONTEND_ROOT = Path(__file__).parents[1] / "frontend" / "src"
APP = FRONTEND_ROOT / "App.svelte"
TOP_BAR = FRONTEND_ROOT / "lib" / "components" / "layout" / "TopBar.svelte"
APP_SHELL = FRONTEND_ROOT / "lib" / "components" / "layout" / "AppShell.svelte"
ADMIN_API = FRONTEND_ROOT / "lib" / "api" / "admin.ts"
ADMIN_PAGE = FRONTEND_ROOT / "lib" / "pages" / "AdminDashboard.svelte"


def _source() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (APP, TOP_BAR, APP_SHELL, ADMIN_API, ADMIN_PAGE))


def test_admin_dashboard_menu_route_and_server_api_client_are_wired() -> None:
    source = _source()

    assert 'const ADMIN_ACCOUNT_EMAIL = "sampollard888@gmail.com";' in source
    assert 'isAdminUser($currentUser)' in source
    assert '{ id: "admin", label: "Admin", href: "#admin", active: section === "admin" }' in source
    assert 'Admin dashboard' in source
    assert "dispatch('admin')" in source
    assert '$currentSection === "admin" && isAdminUser($currentUser)' in source
    assert "fetch('/admin/dashboard'" in source
    assert "fetch(`/admin/users/${encodeURIComponent(userId)}`" in source


def test_admin_dashboard_requires_exact_email_confirmation_before_delete() -> None:
    source = _source()

    assert 'confirmation_email: confirmationEmail' in source
    assert "Type <strong>{selectedUser.email}</strong> to delete this account." in source
    assert "confirmationEmail.trim().toLowerCase() !== selectedUser.email.toLowerCase()" in source
    assert "Only the configured admin account can load these user metrics or delete accounts." in source
    assert "Total users" in source
    assert "Active 7 days" in source
    assert "Active 30 days" in source
