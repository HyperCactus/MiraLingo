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


def test_progress_fetches_authenticated_diagnostics_endpoint() -> None:
    frontend_source = _source()

    assert "async function loadPracticeProgress()" in frontend_source
    assert 'fetch("/practice/progress", { headers: { Accept: "application/json" } })' in frontend_source
    assert 'payload.ok !== true' in frontend_source
    assert "practiceProgress = payload;" in frontend_source
    assert 'progressState = payload.event_count > 0 ? "ready" : "empty";' in frontend_source


def test_progress_refreshes_after_login_queue_refresh_and_answer_submission() -> None:
    frontend_source = _source()
    load_current_user_body = frontend_source.split("async function loadCurrentUser()", maxsplit=1)[1].split("async function submitLogin", maxsplit=1)[0]
    submit_login_body = frontend_source.split("async function submitLogin()", maxsplit=1)[1].split("async function logout", maxsplit=1)[0]
    load_queue_body = frontend_source.split("async function loadPracticeQueue()", maxsplit=1)[1].split("async function submitPracticeAnswer", maxsplit=1)[0]
    submit_answer_body = frontend_source.split("async function submitPracticeAnswer", maxsplit=1)[1].split("async function playCardAudio", maxsplit=1)[0]

    assert "await loadPracticeQueue();" in load_current_user_body
    assert "await loadPracticeQueue();" in submit_login_body
    assert "await loadPracticeProgress();" in load_queue_body
    assert "await loadPracticeQueue();" in submit_answer_body
    assert 'on:click={loadPracticeQueue}' in _authenticated_branch()
    assert 'on:click={loadPracticeProgress}' in _authenticated_branch()


def test_progress_panel_renders_visible_stats_and_scheduler_indicators() -> None:
    authenticated_branch = _authenticated_branch()

    assert 'class="progress-panel" aria-labelledby="progress-heading"' in authenticated_branch
    assert "Practice stats" in authenticated_branch
    assert "Attempts" in authenticated_branch
    assert "Correct" in authenticated_branch
    assert "Incorrect" in authenticated_branch
    assert "Accuracy" in authenticated_branch
    assert "Words" in authenticated_branch
    assert "Phrases" in authenticated_branch
    assert "Latest answer" in authenticated_branch
    assert "weak" in authenticated_branch
    assert "mastered" in authenticated_branch
    assert "new" in authenticated_branch
    assert "stale" in authenticated_branch
    assert "formatLatestAnswer(practiceProgress.latest_event)" in authenticated_branch
    assert "practiceProgress.per_type?.word?.attempts" in authenticated_branch
    assert "practiceProgress.per_type?.phrase?.attempts" in authenticated_branch


def test_progress_empty_error_and_malformed_payload_states_are_accessible_and_non_blocking() -> None:
    frontend_source = _source()
    authenticated_branch = _authenticated_branch()

    assert 'role="status">Loading practice progress…' in authenticated_branch
    assert 'role="status">No answers yet.' in authenticated_branch
    assert '<p class="error-message" role="alert">{progressError}</p>' in authenticated_branch
    assert "Progress is unavailable right now. Practice controls still work" in frontend_source
    assert "Your session expired. Log in again to view progress." in frontend_source
    assert 'payload.ok !== true' in frontend_source
    assert "friendlyProgressError(payload, response.status)" in frontend_source
    assert 'disabled={progressState === "loading"}' in authenticated_branch
    assert 'disabled={practiceState === "loading" || answerSubmitting}' in authenticated_branch


def test_progress_state_is_reset_on_logout_and_does_not_echo_credentials() -> None:
    frontend_source = _source()
    logout_body = frontend_source.split("async function logout()", maxsplit=1)[1].split("async function loadPracticeProgress", maxsplit=1)[0]
    progress_error_body = frontend_source.split("const friendlyProgressError", maxsplit=1)[1].split("const formatAccuracy", maxsplit=1)[0]

    assert 'progressState = "idle";' in logout_body
    assert 'progressError = "";' in logout_body
    assert "practiceProgress = null;" in logout_body
    assert 'password = "";' in logout_body
    assert "payload?.detail" not in progress_error_body
    assert "admin" not in progress_error_body.lower()
    assert "password" not in progress_error_body.lower()


def test_progress_panel_is_authenticated_only_and_logged_out_branch_stays_clean() -> None:
    authenticated_branch = _authenticated_branch()
    logged_out_branch = _logged_out_branch()

    assert "Practice stats" in authenticated_branch
    assert "Session progress" in authenticated_branch
    assert "progress-panel" in authenticated_branch
    assert "Practice stats" not in logged_out_branch
    assert "Session progress" not in logged_out_branch
    assert "progress-panel" not in logged_out_branch
    assert "/practice/progress" not in logged_out_branch


def test_progress_styles_include_responsive_panel_layout() -> None:
    css_source = FRONTEND_CSS.read_text(encoding="utf-8")

    assert ".progress-panel" in css_source
    assert ".progress-header" in css_source
    assert ".progress-summary" in css_source
    assert ".progress-breakdown" in css_source
    assert ".progress-badges" in css_source
    assert "grid-template-columns: repeat(4, minmax(0, 1fr));" in css_source
    assert "grid-template-columns: repeat(3, minmax(0, 1fr));" in css_source
    assert "@media (max-width: 820px)" in css_source
    assert ".progress-summary," in css_source
    assert ".progress-breakdown" in css_source
