from __future__ import annotations

from pathlib import Path


FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"
APP_SVELTE = FRONTEND_SRC / "App.svelte"
EXERCISE_CARD = FRONTEND_SRC / "lib" / "components" / "learning" / "ExerciseCard.svelte"
ANSWER_INPUT = FRONTEND_SRC / "lib" / "components" / "learning" / "AnswerInput.svelte"
FEEDBACK_PANEL = FRONTEND_SRC / "lib" / "components" / "learning" / "FeedbackPanel.svelte"


def _source() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (APP_SVELTE, EXERCISE_CARD, ANSWER_INPUT, FEEDBACK_PANEL))


def test_typed_recall_uses_text_input_form_and_not_self_assessment_buttons() -> None:
    source = _source()

    assert 'typedAnswer = $state("")' in source
    assert "on:submit|preventDefault={submit}" in source
    assert "bind:value={answer}" in source
    assert "label={inputLabel(card)}" in source
    assert "I knew it" not in source
    assert "I missed it" not in source


def test_typed_recall_blocks_blank_answers_and_uses_backend_inference_payload() -> None:
    source = _source()

    assert "answer.trim()" in source
    assert "!answer" in source
    assert "Enter an answer before submitting." in source
    assert "await recordAnswer({ card_id: currentCard.id, answer });" in source
    assert "correct:true" not in source


def test_reveal_uses_explicit_incorrect_payload_without_self_assessment_buttons() -> None:
    source = _source()

    assert "await recordAnswer({ card_id: currentCard.id, correct: false }, { playSfx: false });" in source
    assert "I knew it" not in source
    assert "I missed it" not in source


def test_typed_recall_has_explicit_reveal_and_answer_status() -> None:
    source = _source()

    assert "Show answer" in source
    assert "async function submitGiveUp()" in source
    assert "answerResult" in source
    assert "expected_answer" in source
    assert "submitted_answer" in source
    assert "FeedbackPanel" in source


def test_typed_recall_surfaces_practice_achievements_from_answer_payload() -> None:
    source = _source()

    assert "payload?.achievements" in source
    assert "latestAchievement(payload)" in source
    assert "activeAchievement = achievement" in source
    assert "Achievement unlocked" in source
    assert 'data-testid="achievement-toast"' in source
    assert "/assets/sound_effects/atchevement.wav" in source


def test_typed_recall_refreshes_next_card_without_progress_panel_or_old_function_names() -> None:
    source = _source()

    assert 'await loadPracticeQueue(practiceQueueMode ?? "mixed");' in source
    assert "Practice stats" not in source
    assert "Session progress" not in source
    assert "loadPracticeProgress" not in source
    assert "playCardAudio" in source
    assert "submitAnswer" in source
    assert "submitTypedPracticeAnswer" not in source
    assert "recordPracticeAnswer" not in source
