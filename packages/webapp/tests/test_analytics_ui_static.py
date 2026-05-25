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
    assert source.count('/practice/progress') == 1
    analytics_window = re.search(r"async function loadAnalytics\(\).*?/practice/progress.*?\n  \}", source, re.DOTALL)
    assert analytics_window, "expected loadAnalytics to own /practice/progress"


def test_practice_answer_loop_does_not_fetch_progress() -> None:
    source = _source()

    record_answer_block = source.split("async function recordAnswer", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    queue_block = source.split("async function loadPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    advance_block = source.split("async function advancePracticeCard", maxsplit=1)[1].split("async function", maxsplit=1)[0]

    assert "/practice/progress" not in record_answer_block
    assert "/practice/progress" not in queue_block
    assert "/practice/progress" not in advance_block


def test_analytics_view_exposes_progress_metrics_and_error_surface() -> None:
    source = _source()

    assert 'analyticsState="loading"' in source
    assert 'analyticsErr' in source
    assert 'event_count' in source
    assert 'accuracy' in source
    assert 'weak_count' in source
    assert 'mastered_count' in source
    assert 'stale_count' in source
    assert 'new_count' in source
    assert 'scheduler_reason' not in source
    assert 'role="alert"' in source


def test_analytics_styles_match_current_stats_grid_not_old_panel_names() -> None:
    css_source = _css()

    assert ".stats-grid" in css_source
    assert ".stat-val" in css_source
    assert ".stat-lbl" in css_source
    assert ".analytics-panel" not in css_source
    assert ".analytics-grid" not in css_source
