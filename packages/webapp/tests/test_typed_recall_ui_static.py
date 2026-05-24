from __future__ import annotations

from pathlib import Path


APP_SVELTE = Path(__file__).resolve().parents[1] / "frontend" / "src" / "App.svelte"


def _source() -> str:
    return APP_SVELTE.read_text(encoding="utf-8")


def test_typed_recall_uses_text_input_form_and_not_self_assessment_buttons() -> None:
    source = _source()

    assert 'let typedAnswer = "";' in source
    assert 'on:submit|preventDefault={submitTypedPracticeAnswer}' in source
    assert 'bind:value={typedAnswer}' in source
    assert 'aria-label="Type your answer"' in source
    assert 'I knew it' not in source
    assert 'I missed it' not in source


def test_typed_recall_blocks_blank_answers_and_uses_backend_inference_payload() -> None:
    source = _source()

    assert 'const normalizedAnswer = typedAnswer.trim();' in source
    assert 'if (!normalizedAnswer)' in source
    assert 'role="alert"' in source
    assert 'await recordPracticeAnswer({ card_id: currentCard.id, answer: normalizedAnswer });' in source
    assert 'correct: true' not in source


def test_give_up_uses_explicit_incorrect_payload_without_self_assessment_buttons() -> None:
    source = _source()

    assert 'await recordPracticeAnswer({ card_id: currentCard.id, correct: false });' in source
    assert 'I knew it' not in source
    assert 'I missed it' not in source


def test_typed_recall_has_explicit_give_up_and_answer_reveal_status() -> None:
    source = _source()

    assert '>Give up<' in source or 'Give up' in source
    assert 'submitGiveUp()' in source
    assert 'answerResult' in source
    assert 'expected_answer' in source
    assert 'submitted_answer' in source
    assert 'role="status"' in source


def test_typed_recall_refreshes_next_card_without_progress_panel_or_audio_gate() -> None:
    source = _source()

    assert 'await loadPracticeQueue();' in source
    assert 'await loadPracticeProgress();' not in source
    assert 'Practice stats' not in source
    assert 'Session progress' not in source
    assert 'loadPracticeProgress' not in source
    assert 'playCardAudio' in source
    assert 'submitTypedPracticeAnswer' in source
