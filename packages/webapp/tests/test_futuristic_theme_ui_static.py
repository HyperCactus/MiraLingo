from __future__ import annotations

from pathlib import Path


FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


CURRENT_TOKEN_MARKERS = (
    "--bg:",
    "--surface:",
    "--border:",
    "--text:",
    "--accent:",
    "--err:",
    "--ok:",
)
RESPONSIVE_MARKERS = (
    ".pcard",
    ".pcard-main",
    ".stats-grid",
)


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_default_theme_declares_current_design_tokens() -> None:
    css = _css()

    assert ":root {" in css
    for marker in CURRENT_TOKEN_MARKERS:
        assert marker in css


def test_dark_theme_selector_and_current_tokens_exist() -> None:
    css = _css()

    dark_chunk = css.split('[data-theme="dark"]', maxsplit=1)[1].split("\n}\n\n*", maxsplit=1)[0]

    assert '[data-theme="dark"]' in css
    assert "--accent" in dark_chunk
    assert "--surface" in dark_chunk
    assert "--text" in dark_chunk
    assert "--err" in dark_chunk


def test_interactive_elements_keep_focus_and_hover_feedback() -> None:
    css = _css()

    assert ".pcard-input:focus" in css
    assert ".field-input:focus" in css
    assert ".btn--primary:hover:not(:disabled)" in css
    assert ".menu-btn:hover" in css


def test_responsive_media_query_keeps_core_mobile_contracts() -> None:
    css = _css()

    assert "@media (max-width: 480px)" in css
    for marker in RESPONSIVE_MARKERS:
        assert marker in css
