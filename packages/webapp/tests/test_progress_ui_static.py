from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _authenticated_branch() -> str:
    return _source().split('{#if authState === "authenticated"}', maxsplit=1)[1].split("{:else}", maxsplit=1)[0]


def _logged_out_branch() -> str:
    return _source().split("{:else}", maxsplit=1)[1]


def test_progress_api_is_not_fetched_from_the_primary_practice_loop() -> None:
    frontend_source = _source()

    assert "loadPracticeProgress" not in frontend_source
    assert 'fetch("/practice/progress"' not in frontend_source
    assert 'Progress is unavailable right now. Practice controls still work' not in frontend_source


def test_authenticated_practice_loop_renders_flashcard_not_progress_dashboard() -> None:
    authenticated_branch = _authenticated_branch()

    assert 'class="practice-panel" aria-labelledby="practice-heading"' in authenticated_branch
    assert "Practice queue" in authenticated_branch
    assert "Refresh queue" in authenticated_branch
    assert "Practice stats" not in authenticated_branch
    assert "Session progress" not in authenticated_branch
    assert "Accuracy" not in authenticated_branch
    assert "Latest answer" not in authenticated_branch
    assert "weak" not in authenticated_branch
    assert "mastered" not in authenticated_branch
    assert "new" not in authenticated_branch
    assert "stale" not in authenticated_branch
    assert "Queue events" not in authenticated_branch
    assert "progress-panel" not in authenticated_branch


def test_progress_markers_do_not_leak_into_logged_out_branch() -> None:
    logged_out_branch = _logged_out_branch()

    assert "Practice stats" not in logged_out_branch
    assert "Session progress" not in logged_out_branch
    assert "progress-panel" not in logged_out_branch
    assert "/practice/progress" not in logged_out_branch


def test_answer_result_keeps_runtime_diagnostics_for_verification_without_progress_panel() -> None:
    authenticated_branch = _authenticated_branch()

    assert 'class="answer-result-panel"' in authenticated_branch
    assert 'class="diagnostic-grid" aria-label="Practice diagnostics"' in authenticated_branch
    assert "scheduler_reason" in authenticated_branch
    assert "latest_event" in authenticated_branch
    assert "event_count" in authenticated_branch
    assert 'role="status"' in authenticated_branch
    assert 'role="alert"' in authenticated_branch


def test_progress_styles_are_removed_from_primary_practice_css() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    assert ".progress-panel" not in css_source
    assert ".progress-header" not in css_source
    assert ".progress-summary" not in css_source
    assert ".progress-breakdown" not in css_source
    assert ".progress-badges" not in css_source
    assert ".practice-panel" in css_source
    assert ".practice-card" in css_source
    assert ".diagnostic-grid" in css_source
