from __future__ import annotations

from pathlib import Path


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"


WIKIBOOKS_GRAMMAR_URL = "https://en.wikibooks.org/wiki/Mirad_Grammar"
FORBIDDEN_REPO_RELATIVE_LINKS = (
    "../../README.md",
    "../README.md",
    "../../packages/translator/README.md",
)


def _source() -> str:
    return FRONTEND_APP.read_text(encoding="utf-8")


def test_logged_out_landing_copy_mentions_mirad_and_miralingo_practice() -> None:
    source = _source()

    anonymous_chunk = source.split('{:else}', maxsplit=1)[1]

    assert "Welcome to MiraLingo" in anonymous_chunk
    assert "Practice Mirad" in anonymous_chunk
    assert "MiraLingo" in anonymous_chunk
    assert "Mirad" in anonymous_chunk


def test_logged_out_landing_includes_external_wikibooks_grammar_link() -> None:
    source = _source()

    assert WIKIBOOKS_GRAMMAR_URL in source
    assert "Wikibooks" in source
    assert "Grammar" in source
    assert 'target={link.external ? "_blank" : undefined}' in source
    assert 'rel={link.external ? "noreferrer" : undefined}' in source


def test_public_docs_links_do_not_expose_repo_relative_readmes() -> None:
    source = _source()

    public_links_chunk = source.split("const docsLinks = [", maxsplit=1)[1].split("];", maxsplit=1)[0]

    for forbidden_link in FORBIDDEN_REPO_RELATIVE_LINKS:
        assert forbidden_link not in public_links_chunk


def test_public_link_data_is_rendered_from_docs_links_collection() -> None:
    source = _source()

    assert "const docsLinks = [" in source
    assert "{#each docsLinks as link}" in source
    assert "href={link.href}" in source
    assert 'aria-label={`${link.label}: ${link.description}`}' in source
    assert "Mirad and MiraLingo docs" in source
