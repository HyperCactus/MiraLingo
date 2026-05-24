from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"
FRONTEND_CSS = Path(__file__).parents[1] / "frontend" / "src" / "app.css"


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def _css() -> str:
    return FRONTEND_CSS.read_text(encoding="utf-8")


def test_iconify_keyword_extraction_is_bounded_and_stopword_aware() -> None:
    source = _source()

    assert "const ICONIFY_STOPWORDS" in source
    assert "extractIconKeywords" in source
    assert ".split(/[^a-z0-9]+/" in source or ".split(/[^\\w]+/" in source
    assert "filter(Boolean)" in source
    assert "ICONIFY_STOPWORDS.has" in source
    assert "slice(0, 3)" in source or "slice(0,3)" in source
    assert "if (!keywords.length)" in source
    assert "iconStatus = \"fallback\"" in source or "iconState = \"fallback\"" in source
    assert "No icon keywords" in source or "No eligible icon keyword" in source


def test_iconify_lookup_uses_in_memory_cache_abort_timeout_and_search_url() -> None:
    source = _source()

    assert "iconCache = new Map()" in source or "const iconCache = new Map()" in source
    assert "new AbortController()" in source
    assert "setTimeout(() => controller.abort()" in source or "setTimeout(() => abortController.abort()" in source
    assert "clearTimeout(" in source
    assert "api.iconify.design/search" in source
    assert "encodeURIComponent(" in source
    assert "AbortError" in source or "controller.signal.aborted" in source


def test_iconify_result_validation_restricts_icon_name_and_renders_encoded_svg_in_img() -> None:
    source = _source()

    assert "isAllowedIconName" in source
    assert "^[a-z0-9-]+:[a-z0-9-]+$" in source or "/^[a-z0-9-]+:[a-z0-9-]+$/" in source
    assert "api.iconify.design/" in source
    assert ".svg?" in source or ".svg\"" in source or ".svg`" in source
    assert "data:image/svg+xml" in source or "encodeURIComponent(svg" in source
    assert "<img" in source
    assert "iconSvgUrl" in source or "iconImageUrl" in source
    assert "{@html" not in source


def test_iconify_ui_exposes_status_fallback_and_accessible_diagnostics() -> None:
    source = _source()
    css = _css()

    assert "Iconify status" in source
    assert "role=\"status\"" in source
    assert "iconStatus" in source or "iconState" in source
    assert "iconError" in source or "iconDiagnostic" in source
    assert "fallback" in source
    assert "icon" in source.lower()
    assert ".practice-icon" in css or ".card-icon" in css
    assert ".icon-status" in css or ".icon-diagnostic" in css


def test_iconify_lookup_does_not_block_submit_give_up_or_change_practice_contracts() -> None:
    source = _source()

    submit_chunk = source.split("async function submitTypedPracticeAnswer()", maxsplit=1)[1].split(
        "async function submitGiveUp()", maxsplit=1
    )[0]
    give_up_chunk = source.split("async function submitGiveUp()", maxsplit=1)[1].split(
        "async function advancePracticeCard()", maxsplit=1
    )[0]

    assert "await recordPracticeAnswer({ card_id: currentCard.id, answer: normalizedAnswer });" in submit_chunk
    assert "fetchIcon" not in submit_chunk
    assert "loadIcon" not in submit_chunk
    assert "await lookupIcon" not in submit_chunk

    assert "await recordPracticeAnswer({ card_id: currentCard.id, correct: false });" in give_up_chunk
    assert "fetchIcon" not in give_up_chunk
    assert "loadIcon" not in give_up_chunk
    assert "await lookupIcon" not in give_up_chunk


def test_iconify_contract_stays_frontend_only_without_package_or_backend_coupling() -> None:
    source = _source()

    assert "@iconify/" not in source
    assert "from '@iconify" not in source
    assert 'from "@iconify' not in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "/api/icon" not in source
    assert "/icons" not in source
    assert "fetch(\"/icon" not in source
    assert "fetch('/icon" not in source
