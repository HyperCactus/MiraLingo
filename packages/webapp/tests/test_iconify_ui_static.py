from __future__ import annotations

from pathlib import Path


FRONTEND_SRC = Path(__file__).parents[1] / "frontend" / "src"
APP = FRONTEND_SRC / "App.svelte"
CLICKABLE_TEXT = FRONTEND_SRC / "lib" / "components" / "learning" / "ClickableTranslationText.svelte"
LEXICON_BUBBLE = FRONTEND_SRC / "lib" / "components" / "learning" / "LexiconBubble.svelte"
LOOKUP_API = FRONTEND_SRC / "lib" / "api" / "lookup.ts"


def _source() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (APP, CLICKABLE_TEXT, LEXICON_BUBBLE, LOOKUP_API))


def test_clickable_translation_text_tokenizes_and_normalizes_words() -> None:
    source = _source()

    assert "function tokenize" in source
    assert "function normalizeWord" in source
    assert "value.split" in source
    assert "data-word-click-target" in source
    assert "normalizeWord(token)" in source


def test_word_lookup_uses_api_helpers_and_bounded_semantic_fallback() -> None:
    source = _source()

    assert "lookupExact" in source
    assert "lookupWord" in source
    assert "await lookupExact(word, direction)" in source
    assert "await lookupWord(word, direction, 3)" in source
    assert "fetch(`/lookup/exact" in source
    assert "fetch(`/lookup?" in source
    assert "new URLSearchParams" in source


def test_lookup_bubble_validates_display_without_html_injection() -> None:
    source = _source()

    assert "translations = results.map" in source
    assert "No translation found" in source
    assert "Looking up" in source
    assert "{word}" in source
    assert "{@html" not in source


def test_lookup_ui_exposes_loading_error_and_result_state() -> None:
    source = _source()

    assert "bubbleLoading" in source
    assert "bubbleError" in source
    assert "bubbleResults" in source
    assert "LexiconBubble" in source
    assert "results.length === 0" in source
    assert "error" in source


def test_lookup_does_not_block_submit_reveal_or_change_practice_contracts() -> None:
    source = _source()

    submit_chunk = source.split("async function submitAnswer", maxsplit=1)[1].split("async function submitGiveUp", maxsplit=1)[0]
    reveal_chunk = source.split("async function submitGiveUp", maxsplit=1)[1].split("async function playCardAudio", maxsplit=1)[0]

    assert "await recordAnswer({ card_id: currentCard.id, answer });" in submit_chunk
    assert "lookup" not in submit_chunk.casefold()
    assert "await recordAnswer({ card_id: currentCard.id, correct: false }, { playSfx: false });" in reveal_chunk
    assert "lookup" not in reveal_chunk.casefold()


def test_lookup_contract_stays_frontend_only_without_iconify_or_storage_coupling() -> None:
    source = _source()

    assert "@iconify/" not in source
    assert "from '@iconify" not in source
    assert 'from "@iconify' not in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "/api/icon" not in source
