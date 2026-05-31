from __future__ import annotations

from pathlib import Path


FRONTEND_ROOT = Path(__file__).parents[1] / "frontend" / "src"
LEARNING_ROOT = FRONTEND_ROOT / "lib" / "components" / "learning"
DASHBOARD_PAGE = FRONTEND_ROOT / "lib" / "pages" / "Dashboard.svelte"
EXERCISE_CARD = LEARNING_ROOT / "ExerciseCard.svelte"
FEEDBACK_PANEL = LEARNING_ROOT / "FeedbackPanel.svelte"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_learning_components_exist_for_studyshell_practice_flow() -> None:
    expected = {
        "ExerciseCard.svelte",
        "ExercisePrompt.svelte",
        "AnswerInput.svelte",
        "AudioButton.svelte",
        "FeedbackPanel.svelte",
    }

    assert expected == {path.name for path in LEARNING_ROOT.glob("*.svelte")}


def test_exercise_card_keeps_mobile_friendly_submit_reveal_and_continue_actions() -> None:
    source = _read(EXERCISE_CARD)

    assert "Submit answer" in source
    assert "Show answer" in source
    assert "Continue" in source
    assert "max-w-sm" in source
    assert "w-full" in source
    assert "submitPracticeAnswer" not in source


def test_feedback_panel_labels_revealed_answer_and_audio_gate_honestly() -> None:
    source = _read(FEEDBACK_PANEL)

    assert "Correct answer" in source
    assert "Listen to the Mirad answer after it has been revealed." in source
    assert "Show answer" in source


def test_dashboard_page_uses_progress_endpoint_and_offers_required_actions() -> None:
    source = _read(DASHBOARD_PAGE)

    assert "getPracticeProgress" in source
    assert "Continue Practice" in source
    assert "Revision" in source
    assert "Build Vocabulary" in source
    assert "Lexicon Search" in source
    assert "Honest placeholder" in source
