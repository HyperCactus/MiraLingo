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

    assert 'let activeSection = $state("menu");' in source
    assert "Continue Practice" in source
    assert "Revision" in source
    assert "Vocabulary" in source
    assert "Analytics" in source
    assert "Settings" in source
    assert "Log Out" in source
    assert 'let activeSection = "menu";' not in source


def test_navigation_handlers_cover_each_authenticated_destination() -> None:
    source = _source()

    for section in ('"menu"', '"practice"', '"revision"', '"build_vocabulary"', '"analytics"', '"settings"'):
        assert f'activeSection === {section}' in source
    assert "function activateItem(item)" in source
    assert 'loadAnalytics(); return;' in source
    assert 'loadSettings(); return;' in source


def test_queue_requests_cover_mixed_revision_and_build_vocabulary_modes() -> None:
    source = _source()

    assert '/practice/queue?mode=mixed' in source
    assert '/practice/queue?mode=revision' in source
    assert '/practice/queue?mode=build_vocabulary' in source


def test_menu_copy_keeps_practice_cards_uncluttered() -> None:
    source = _source()

    assert "Continue Practice" in source
    assert "Mixed recall" in source
    assert "Analytics" in source
    assert 'fetch("/practice/progress"' not in source.split("async function loadPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]


def test_menu_and_navigation_have_current_dedicated_styles() -> None:
    css_source = _css()

    assert ".shell--menu" in css_source
    assert ".menu-wrap" in css_source
    assert ".menu-btns" in css_source
    assert ".menu-btn" in css_source
    assert ".main-menu" not in css_source
