from __future__ import annotations

from pathlib import Path

FRONTEND_ROOT = Path(__file__).parents[1] / "frontend" / "src"
APP_SOURCE = FRONTEND_ROOT / "App.svelte"
EXERCISE_CARD = FRONTEND_ROOT / "lib" / "components" / "learning" / "ExerciseCard.svelte"
FEEDBACK_PANEL = FRONTEND_ROOT / "lib" / "components" / "learning" / "FeedbackPanel.svelte"
DASHBOARD_PAGE = FRONTEND_ROOT / "lib" / "pages" / "Dashboard.svelte"
WELCOME_PAGE = FRONTEND_ROOT / "lib" / "pages" / "Welcome.svelte"
APP_CSS = FRONTEND_ROOT / "app.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_app_uses_split_pages_and_components_contract() -> None:
    source = _read(APP_SOURCE)

    assert 'import Dashboard from "./lib/pages/Dashboard.svelte";' in source
    assert 'import Welcome from "./lib/pages/Welcome.svelte";' in source
    assert 'import ExerciseCard from "./lib/components/learning/ExerciseCard.svelte";' in source


def test_polish_labels_remove_give_up_text() -> None:
    app = _read(APP_SOURCE)
    exercise = _read(EXERCISE_CARD)
    feedback = _read(FEEDBACK_PANEL)

    assert "Give up" not in app
    assert "Give up" not in exercise
    assert "Give up" not in feedback
    assert "Show answer" in exercise or "Reveal answer" in exercise


def test_exercise_card_actions_keep_tappable_mobile_targets() -> None:
    source = _read(EXERCISE_CARD)

    assert 'className="min-h-12 w-full justify-center"' in source
    assert "Submit answer" in source
    assert "Show answer" in source
    assert "Continue" in source


def test_dashboard_and_welcome_page_surfaces_exist() -> None:
    assert DASHBOARD_PAGE.exists()
    assert WELCOME_PAGE.exists()


def test_css_keeps_responsive_and_settings_layout_contracts() -> None:
    css = _read(APP_CSS)

    assert '@media (max-width: 480px)' in css
    assert 'settings' in css.lower()
