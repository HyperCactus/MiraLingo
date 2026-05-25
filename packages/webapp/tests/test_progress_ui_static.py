from __future__ import annotations

from pathlib import Path
import re


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _logged_out_branch() -> str:
    return _source().split("{:else}", maxsplit=1)[1]


def _primary_practice_section() -> str:
    source = _source()
    return source.split('authState === "authenticated" && (activeSection === "practice"', maxsplit=1)[1].split(
        '<!-- ══════════════════════════════════════════════════════════════\n     MENU', maxsplit=1
    )[0]


def _function_block(source: str, function_name: str) -> str:
    match = re.search(rf"async function {function_name}.*?(?=\n  async function |\n  function |\n  // ──)", source, re.DOTALL)
    assert match, f"expected {function_name} block"
    return match.group(0)


def test_progress_api_is_not_fetched_from_the_primary_practice_loop() -> None:
    frontend_source = _source()
    practice_blocks = [
        _function_block(frontend_source, "loadPracticeQueue"),
        _function_block(frontend_source, "recordAnswer"),
        _function_block(frontend_source, "advancePracticeCard"),
    ]

    assert "loadPracticeProgress" not in frontend_source
    assert all('/practice/progress' not in block for block in practice_blocks)
    assert 'Progress is unavailable right now. Practice controls still work' not in frontend_source


def test_authenticated_practice_loop_renders_flashcard_not_progress_dashboard() -> None:
    primary_practice_section = _primary_practice_section()

    assert 'class="pcard" aria-label="Practice card"' in primary_practice_section
    assert "{getPracticeTitle()}" in primary_practice_section
    assert "Submit" in primary_practice_section
    assert "Skip" in primary_practice_section
    assert "Practice stats" not in primary_practice_section
    assert "Session progress" not in primary_practice_section
    assert "scheduler_reason" not in primary_practice_section
    assert "progress-panel" not in primary_practice_section


def test_progress_markers_do_not_leak_into_logged_out_branch() -> None:
    logged_out_branch = _logged_out_branch()

    assert "Practice stats" not in logged_out_branch
    assert "Session progress" not in logged_out_branch
    assert "progress-panel" not in logged_out_branch
    assert "/practice/progress" not in logged_out_branch


def test_answer_result_keeps_runtime_feedback_without_progress_panel() -> None:
    practice_section = _primary_practice_section()

    assert 'class="pcard-resultbar"' in practice_section
    assert 'answerResult.correct ? "✓ Correct" : "✗ Not quite"' in practice_section
    assert "expected_answer" in _source()
    assert 'role="alert"' in practice_section
    assert "scheduler_reason" not in practice_section
    assert "latest_event" not in practice_section


def test_progress_styles_are_removed_from_primary_practice_css() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    assert ".progress-panel" not in css_source
    assert ".progress-header" not in css_source
    assert ".progress-summary" not in css_source
    assert ".progress-breakdown" not in css_source
    assert ".progress-badges" not in css_source
    assert ".pcard" in css_source
    assert ".pcard-resultbar" in css_source
