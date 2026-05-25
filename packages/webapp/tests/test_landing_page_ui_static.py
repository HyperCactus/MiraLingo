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

    assert "MiraLingo" in anonymous_chunk
    assert "Practice Mirad pronunciation and translation." in anonymous_chunk
    assert "Create account" in anonymous_chunk
    assert "Log in" in anonymous_chunk
    assert "Welcome to MiraLingo" not in anonymous_chunk


def test_logged_out_landing_includes_external_mirad_links() -> None:
    source = _source()

    assert WIKIBOOKS_GRAMMAR_URL in source
    assert "Mirad Grammar" in source
    assert "https://www.mirad.org/" in source
    assert 'target="_blank"' in source
    assert 'rel="noopener"' in source


def test_public_docs_links_do_not_expose_repo_relative_readmes() -> None:
    source = _source()

    for forbidden_link in FORBIDDEN_REPO_RELATIVE_LINKS:
        assert forbidden_link not in source


def test_public_links_are_plain_external_anchors_not_old_docs_collection() -> None:
    source = _source()

    assert "const docsLinks = [" not in source
    assert "{#each docsLinks as link}" not in source
    assert 'href="https://en.wikibooks.org/wiki/Mirad_Grammar"' in source
    assert 'href="https://www.mirad.org/"' in source
