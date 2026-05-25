from __future__ import annotations

from pathlib import Path


APP_SVELTE = Path(__file__).resolve().parents[1] / "frontend" / "src" / "App.svelte"


def _source() -> str:
    return APP_SVELTE.read_text(encoding="utf-8")


def test_typed_recall_uses_text_input_form_and_not_self_assessment_buttons() -> None:
    source = _source()

    assert 'typedAnswer = $state("")' in source
    assert 'on:submit|preventDefault={submitAnswer}' in source
    assert 'bind:value={typedAnswer}' in source
    assert 'aria-label={inputLabel(currentCard)}' in source
    assert 'I knew it' not in source
    assert 'I missed it' not in source


def test_typed_recall_blocks_blank_answers_and_uses_backend_inference_payload() -> None:
    source = _source()

    assert 'const norm = typedAnswer.trim();' in source
    assert 'if (!norm)' in source
    assert 'role="alert"' in source
    assert 'await recordAnswer({card_id:currentCard.id, answer:norm});' in source
    assert 'correct:true' not in source


def test_skip_uses_explicit_incorrect_payload_without_self_assessment_buttons() -> None:
    source = _source()

    assert 'await recordAnswer({card_id:currentCard.id, correct:false});' in source
    assert 'I knew it' not in source
    assert 'I missed it' not in source


def test_typed_recall_has_explicit_skip_and_answer_reveal_status() -> None:
    source = _source()

    assert '>\n                Skip\n              </button>' in source or 'Skip' in source
    assert 'async function submitGiveUp()' in source
    assert 'answerResult' in source
    assert 'expected_answer' in source
    assert 'submitted_answer' in source
    assert 'pcard-resultbar' in source


def test_typed_recall_refreshes_next_card_without_progress_panel_or_old_function_names() -> None:
    source = _source()

    assert 'await loadPracticeQueue(practiceQueueMode ?? "mixed");' in source
    assert 'await loadPracticeProgress();' not in source
    assert 'Practice stats' not in source
    assert 'Session progress' not in source
    assert 'loadPracticeProgress' not in source
    assert 'playCardAudio' in source
    assert 'submitAnswer' in source
    assert 'submitTypedPracticeAnswer' not in source
    assert 'recordPracticeAnswer' not in source
