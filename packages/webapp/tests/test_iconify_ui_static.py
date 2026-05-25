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

    assert "const stopwords = new Set" in source
    assert "function icKw(card)" in source
    assert ".split(/[^a-z0-9]+/)" in source
    assert "filter(Boolean)" in source
    assert "!stopwords.has(t)" in source
    assert "slice(0, 3)" in source
    assert "if (!kws.length)" in source
    assert 'status:"fallback"' in source


def test_iconify_lookup_uses_in_memory_cache_abort_timeout_and_search_url() -> None:
    source = _source()

    assert "const iconCache = new Map();" in source
    assert "new AbortController()" in source
    assert "setTimeout(() => ctrl.abort(), IC_TMO)" in source
    assert "clearTimeout(to)" in source
    assert "api.iconify.design/search" in source
    assert "encodeURIComponent(" in source
    assert "AbortError" in source
    assert "controller.abort" not in source


def test_iconify_result_validation_restricts_icon_name_and_renders_encoded_svg_in_img() -> None:
    source = _source()

    assert "function icOk(name)" in source
    assert "/^[a-z0-9-]+:[a-z0-9-]+$/" in source
    assert "api.iconify.design/" in source
    assert ".svg?color=%231d4ed8" in source
    assert "<img src={icImg} alt={icAlt} class=\"pcard-icon-img\" />" in source
    assert "{@html" not in source


def test_iconify_ui_exposes_matched_icon_and_fallback_state_without_debug_panel() -> None:
    source = _source()
    css = _css()

    assert "icStatus" in source
    assert "icErr" in source
    assert "fallback" in source
    assert "matched" in source
    assert ".pcard-icon-row" in css
    assert ".pcard-icon-frame" in css
    assert ".pcard-icon-img" in css
    assert "Iconify status" not in source


def test_iconify_lookup_does_not_block_submit_skip_or_change_practice_contracts() -> None:
    source = _source()

    submit_chunk = source.split("async function submitAnswer()", maxsplit=1)[1].split(
        "async function submitGiveUp()", maxsplit=1
    )[0]
    give_up_chunk = source.split("async function submitGiveUp()", maxsplit=1)[1].split(
        "// ── audio", maxsplit=1
    )[0]

    assert "await recordAnswer({card_id:currentCard.id, answer:norm});" in submit_chunk
    assert "loadIc" not in submit_chunk
    assert "await recordAnswer({card_id:currentCard.id, correct:false});" in give_up_chunk
    assert "loadIc" not in give_up_chunk


def test_iconify_contract_stays_frontend_only_without_package_or_backend_coupling() -> None:
    source = _source()

    assert "@iconify/" not in source
    assert "from '@iconify" not in source
    assert 'from "@iconify' not in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "/api/icon" not in source
    assert "fetch(\"/icon" not in source
    assert "fetch('/icon" not in source
