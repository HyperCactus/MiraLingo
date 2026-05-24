from __future__ import annotations

import re
from pathlib import Path


DOC_PATH = Path(__file__).parents[1] / "docs" / "m004_scope_boundary_map.md"


REQUIRED_HEADINGS = [
    "# M004 Scope and Boundary Map",
    "## Requirement Status",
    "## Requirement Scope Reconciliation",
    "## Requirement Coverage by Slice",
    "## Scope Boundaries",
    "## Producer and Consumer Contracts",
    "## Remediation Ownership",
    "## Validation Evidence",
    "## Validation Rules for Future Executors",
]

REQUIRED_BOUNDARY_TERMS = [
    "FastAPI",
    "Svelte",
    "SQLite",
    "wordfreq",
    "lexicon lookup",
    "MBROLA",
    "producer",
    "consumer",
    "boundary",
    "out of scope",
]

REQUIRED_COMPLETED_PHRASES = {
    "S07": ["registration", "bidirectional", "Completed evidence"],
    "S08": ["wordfreq", "SQLite", "Completed evidence"],
    "S09": ["browser UAT", "audio", "progress", "Completed evidence"],
}

PLACEHOLDER_RE = re.compile(r"\b(TBD|TODO|FIXME|XXX)\b", re.IGNORECASE)


def _read_contract() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _row_for_slice(text: str, slice_id: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"| {slice_id} "):
            return line
    raise AssertionError(f"Missing coverage row for {slice_id}")


def test_m004_scope_boundary_contract_has_required_sections() -> None:
    text = _read_contract()

    for heading in REQUIRED_HEADINGS:
        assert heading in text, f"Missing required heading: {heading}"


def test_m004_scope_boundary_contract_maps_every_slice_id() -> None:
    text = _read_contract()

    for index in range(1, 10):
        slice_id = f"S{index:02d}"
        row = _row_for_slice(text, slice_id)
        assert row.count("|") >= 5, f"Coverage row for {slice_id} is malformed: {row}"
        assert len(row.replace("|", "").strip()) > len(slice_id), f"Coverage row for {slice_id} is blank"


def test_m004_scope_boundary_contract_names_key_boundaries() -> None:
    text = _read_contract()

    for term in REQUIRED_BOUNDARY_TERMS:
        assert term.lower() in text.lower(), f"Missing boundary term: {term}"


def test_m004_scope_boundary_contract_tracks_s07_s08_s09_completion() -> None:
    text = _read_contract()

    for slice_id, phrases in REQUIRED_COMPLETED_PHRASES.items():
        row = _row_for_slice(text, slice_id)
        for phrase in phrases:
            assert phrase.lower() in row.lower(), f"Missing {phrase!r} in {slice_id} completed row: {row}"


def test_m004_scope_boundary_contract_has_no_stale_s07_s09_pending_wording() -> None:
    text = _read_contract().lower()

    assert "pending remediation" not in text
    assert "s07 must" not in text
    assert "s08 must" not in text
    assert "s09 must" not in text


def test_m004_scope_boundary_contract_states_requirement_source_truth() -> None:
    text = _read_contract()

    assert "no Active requirements" in text
    assert "R001" in text
    assert "R009" in text
    assert "non-webapp tokenizer requirements" in text
    assert "does not invent new requirement identifiers" in text
    assert "Requirement Scope Reconciliation" in text
    assert "foundation" in text
    assert "M004 webapp ownership" in text


def test_m004_scope_boundary_contract_has_no_placeholder_tokens() -> None:
    text = _read_contract()

    match = PLACEHOLDER_RE.search(text)
    assert match is None, f"Placeholder token found in scope contract: {match.group(0)}"
