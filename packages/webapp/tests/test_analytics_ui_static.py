from __future__ import annotations

from pathlib import Path
import re


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_progress_fetch_is_isolated_to_analytics_code() -> None:
    source = _source()

    assert 'fetch("/practice/progress"' in source
    occurrences = source.count('/practice/progress')
    assert occurrences >= 1
    assert occurrences <= 2

    analytics_window = re.search(r"async function .*Analytics.*?\{.*?/practice/progress.*?\n\}", source, re.DOTALL)
    assert analytics_window, "expected a dedicated analytics loader that owns /practice/progress"


def test_practice_answer_loop_does_not_fetch_progress() -> None:
    source = _source()

    record_answer_block = source.split("async function recordPracticeAnswer", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    queue_block = source.split("async function loadPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    advance_block = source.split("async function advancePracticeCard", maxsplit=1)[1].split("async function", maxsplit=1)[0]

    assert "/practice/progress" not in record_answer_block
    assert "/practice/progress" not in queue_block
    assert "/practice/progress" not in advance_block


def test_analytics_view_exposes_progress_status_and_error_surfaces() -> None:
    source = _source()

    assert "Progress status" in source or "Analytics status" in source
    assert "Progress error" in source or "Analytics error" in source
    assert 'role="status"' in source
    assert 'role="alert"' in source


def test_analytics_view_shows_scheduler_and_progress_diagnostics() -> None:
    source = _source()

    assert "scheduler_reason" in source
    assert "event_count" in source
    assert "progress percentage" in source or "completion percentage" in source or "accuracy" in source.lower()
    assert "weak cards" in source or "stale cards" in source or "new cards" in source or "mastered cards" in source


def test_analytics_styles_exist_separately_from_practice_card_styles() -> None:
    css_source = _css()

    assert ".analytics-panel" in css_source
    assert ".analytics-grid" in css_source or ".progress-grid" in css_source
    assert ".status-message" in css_source
    assert ".error-message" in css_source
    assert ".practice-card" in css_source
