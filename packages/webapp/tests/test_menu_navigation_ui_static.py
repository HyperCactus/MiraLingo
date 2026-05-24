from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_authenticated_shell_declares_main_menu_contract() -> None:
    source = _source()

    assert 'let activeSection = "menu";' in source or 'let currentSection = "menu";' in source
    assert "Continue Practice" in source
    assert "Revision" in source
    assert "Build Vocabulary" in source
    assert "Analytics" in source
    assert "Settings" in source
    assert "Log Out" in source


def test_navigation_handlers_cover_each_authenticated_destination() -> None:
    source = _source()

    assert 'activeSection === "menu"' in source or 'currentSection === "menu"' in source
    assert 'activeSection === "practice"' in source or 'currentSection === "practice"' in source
    assert 'activeSection === "revision"' in source or 'currentSection === "revision"' in source
    assert 'activeSection === "build_vocabulary"' in source or 'currentSection === "build_vocabulary"' in source
    assert 'activeSection === "analytics"' in source or 'currentSection === "analytics"' in source
    assert 'activeSection === "settings"' in source or 'currentSection === "settings"' in source


def test_queue_requests_cover_mixed_revision_and_build_vocabulary_modes() -> None:
    source = _source()

    assert '/practice/queue?mode=mixed' in source
    assert '/practice/queue?mode=revision' in source
    assert '/practice/queue?mode=build_vocabulary' in source


def test_menu_copy_keeps_practice_cards_uncluttered() -> None:
    source = _source()

    assert "Continue Practice" in source
    assert "Practice queue" in source
    assert "Analytics" in source
    assert 'fetch("/practice/progress"' not in source.split("async function loadPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]


def test_menu_and_navigation_have_dedicated_styles() -> None:
    css_source = _css()

    assert ".main-menu" in css_source
    assert ".menu-grid" in css_source or ".menu-actions" in css_source
    assert ".analytics-panel" in css_source
    assert ".practice-card" in css_source
