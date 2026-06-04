from __future__ import annotations

from pathlib import Path


FRONTEND_SRC = Path(__file__).parents[1] / "frontend" / "src"
FRONTEND_APP = FRONTEND_SRC / "App.svelte"
FRONTEND_CSS = FRONTEND_SRC / "app.css"
DASHBOARD = FRONTEND_SRC / "lib" / "pages" / "Dashboard.svelte"
PRACTICE_API = FRONTEND_SRC / "lib" / "api" / "practice.ts"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8") + "\n" + DASHBOARD.read_text(encoding="utf-8") + "\n" + PRACTICE_API.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_authenticated_shell_declares_main_menu_contract() -> None:
    source = _source()

    assert "currentSection" in source
    assert "Continue Practice" in source
    assert "Revision" in source
    assert "Vocabulary" in source
    assert "Analytics" in source
    assert "Settings" in source
    assert "logout" in source.casefold()


def test_navigation_handlers_cover_each_authenticated_destination() -> None:
    source = _source()

    for section in ('"dashboard"', '"practice"', '"revision"', '"build_vocabulary"', '"analytics"', '"settings"'):
        assert section in source
    assert "async function navigateToSection(section)" in source
    assert 'target === "analytics"' in source
    assert 'target === "settings"' in source


def test_queue_requests_cover_mixed_revision_and_build_vocabulary_modes() -> None:
    source = _source()

    assert "getPracticeQueue" in source
    assert "new URLSearchParams({ mode, limit: String(limit) })" in source
    assert "`/practice/queue?${query.toString()}`" in source


def test_menu_copy_keeps_practice_cards_uncluttered() -> None:
    source = _source()

    assert "Continue Practice" in source
    assert "Today dashboard" in source or "Today" in source
    assert "Analytics" in source
    queue_block = source.split("async function loadPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert "/practice/progress" not in queue_block


def test_menu_and_navigation_have_current_dedicated_styles() -> None:
    css_source = _css()

    assert ".shell--menu" in css_source
    assert ".menu-wrap" in css_source
    assert ".menu-btns" in css_source
    assert ".menu-btn" in css_source
    assert ".main-menu" not in css_source
