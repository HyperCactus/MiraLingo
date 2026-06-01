from __future__ import annotations

from pathlib import Path
import re


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
DASHBOARD_PAGE = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "pages" / "Dashboard.svelte"


def _app_source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _dashboard_source() -> str:
    return DASHBOARD_PAGE.read_text(encoding="utf-8")


def _function_block(source: str, function_name: str) -> str:
    match = re.search(rf"async function {function_name}.*?(?=\n  async function |\n  function |\n  // ──)", source, re.DOTALL)
    assert match, f"expected {function_name} block"
    return match.group(0)


def test_progress_api_is_not_fetched_from_primary_practice_loop() -> None:
    app_source = _app_source()
    practice_blocks = [
        _function_block(app_source, "loadPracticeQueue"),
        _function_block(app_source, "recordAnswer"),
        _function_block(app_source, "advancePracticeCard"),
    ]

    assert all('/practice/progress' not in block for block in practice_blocks)
    assert all('/practice/analytics' not in block for block in practice_blocks)


def test_dashboard_owns_progress_helper_call() -> None:
    app_source = _app_source()
    dashboard_source = _dashboard_source()

    assert "<Dashboard" in app_source
    assert "getPracticeProgress" in dashboard_source
    assert "fetch('/practice/progress'" not in app_source
    assert "fetch(\"/practice/progress\"" not in app_source


def test_answer_result_feedback_remains_without_progress_or_analytics_fetches() -> None:
    source = _app_source()
    record_answer_block = _function_block(source, "recordAnswer")
    queue_block = _function_block(source, "loadPracticeQueue")

    assert "submitPracticeAnswer" in record_answer_block
    assert "scheduleDashboardRefresh" in record_answer_block
    assert "/practice/progress" not in record_answer_block
    assert "/practice/analytics" not in record_answer_block
    assert "/practice/progress" not in queue_block
    assert "/practice/analytics" not in queue_block
