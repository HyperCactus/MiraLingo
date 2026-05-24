from __future__ import annotations

from pathlib import Path


FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


BLUE_TOKEN_MARKERS = (
    "#dbeafe",
    "#bfdbfe",
    "#93c5fd",
    "#60a5fa",
    "#3b82f6",
    "#1d4ed8",
    "#0f172a",
)
RESPONSIVE_GRID_MARKERS = (
    ".menu-grid",
    ".practice-grid",
    ".analytics-grid",
    ".theme-fieldset",
)


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_default_theme_declares_blue_forward_tokens() -> None:
    css = _css()

    assert ":root {" in css
    for marker in BLUE_TOKEN_MARKERS[:5]:
        assert marker in css


def test_dark_theme_selector_and_deep_blue_tokens_exist() -> None:
    css = _css()

    dark_chunk = css.split(':root[data-theme="dark"]', maxsplit=1)[1].split("\n}\n\n*", maxsplit=1)[0]

    assert ':root[data-theme="dark"]' in css
    assert BLUE_TOKEN_MARKERS[5] in dark_chunk
    assert BLUE_TOKEN_MARKERS[6] in dark_chunk
    assert "--accent" in dark_chunk
    assert "--focus-ring" in dark_chunk


def test_focus_visible_contract_remains_present_for_interactive_elements() -> None:
    css = _css()

    assert ":focus-visible" in css
    assert "outline: 3px solid var(--focus-ring);" in css
    assert ".primary-action:focus-visible" in css
    assert ".toggle-card:has(input:focus-visible)" in css


def test_responsive_media_queries_keep_core_authenticated_grids() -> None:
    css = _css()

    assert "@media (max-width: 980px)" in css
    assert "@media (max-width: 820px)" in css
    for marker in RESPONSIVE_GRID_MARKERS:
        assert marker in css
