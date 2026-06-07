from __future__ import annotations

from pathlib import Path
import re


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
PRACTICE_API = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "api" / "practice.ts"
DASHBOARD_PAGE = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "pages" / "Dashboard.svelte"
ANALYTICS_PAGE = Path(__file__).parents[1] / "frontend" / "src" / "lib" / "pages" / "Analytics.svelte"


def _app_source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _api_source() -> str:
    return PRACTICE_API.read_text(encoding="utf-8")


def _dashboard_source() -> str:
    return DASHBOARD_PAGE.read_text(encoding="utf-8")


def test_analytics_route_is_hash_navigable_and_dashboard_stays_separate() -> None:
    source = _app_source()

    assert '$currentSection === "analytics"' in source
    assert 'if (target === "analytics")' in source
    assert "<Analytics" in source

    dashboard_source = _dashboard_source()
    assert "getPracticeSummary" in dashboard_source
    assert "summary?.mastered_count" in dashboard_source
    assert "masteredFromAnalytics" not in dashboard_source


def test_analytics_fetch_is_owned_by_api_helper_not_inline_fetch() -> None:
    app_source = _app_source()
    api_source = _api_source()

    analytics_source = _analytics_source()
    assert "getPracticeAnalytics" in analytics_source
    assert "Promise.all" in analytics_source

    assert "fetch('/practice/analytics'" in api_source or 'fetch("/practice/analytics"' in api_source
    assert "/practice/progress" in api_source
    assert "/practice/summary" in api_source


def test_analytics_replaces_session_card_with_streak() -> None:
    source = _analytics_source()

    assert ">Streak<" in source
    assert ">Sessions<" not in source


def test_analytics_ui_contains_error_and_sparse_history_markers() -> None:
    source = _analytics_source()

    assert 'role="alert"' in source
    assert "sparse_history" in source
    assert "No analytics yet" in source


def test_practice_answer_and_queue_blocks_do_not_fetch_detailed_analytics() -> None:
    source = _app_source()

    record_answer_block = source.split("async function recordAnswer", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    queue_block = source.split("async function loadPracticeQueue", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    advance_block = source.split("async function advancePracticeCard", maxsplit=1)[1].split("async function", maxsplit=1)[0]

    assert "/practice/analytics" not in record_answer_block
    assert "/practice/analytics" not in queue_block
    assert "/practice/analytics" not in advance_block


def test_analytics_mastery_uses_progress_mastery_flag_before_legacy_recent_flags() -> None:
    source = _analytics_source()

    assert "mastery: r.mastery ?? progressRow.mastery" in source
    assert "if (typeof mastery.mastered === 'boolean') return Boolean(mastery.mastered);" in source
    assert source.index("if (typeof mastery.mastered === 'boolean') return Boolean(mastery.mastered);") < source.index("const recent = obj(masteredRecentRaw?.[base]);")


def _analytics_source() -> str:
    return ANALYTICS_PAGE.read_text(encoding="utf-8")
