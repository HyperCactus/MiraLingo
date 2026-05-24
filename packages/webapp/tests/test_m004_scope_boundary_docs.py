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

REQUIRED_RECONCILIATION_PHRASES = [
    "## Requirement Scope Reconciliation",
    "zero Active requirements",
    "validated non-webapp tokenizer requirements",
    "R001 is already validated tokenizer behavior",
    "R009 is already validated tokenizer rejection",
    "tokenizer foundation",
    "no M004 webapp slice owns or revalidates R001",
    "no M004 webapp slice owns or revalidates R009",
    "does not invent new requirement identifiers",
    "M004 validation maps the milestone acceptance criteria",
]

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
        assert "pending remediation" not in row.lower(), (
            f"{slice_id} row regressed to pending remediation instead of completed evidence: {row}"
        )
        for phrase in phrases:
            assert phrase.lower() in row.lower(), f"Missing {phrase!r} in {slice_id} completed row: {row}"


def test_m004_scope_boundary_contract_has_no_stale_s07_s09_pending_wording() -> None:
    text = _read_contract().lower()

    assert "pending remediation" not in text, "Scope contract still contains stale pending-remediation wording"
    assert "s07 must" not in text, "S07 should be completed evidence, not future remediation"
    assert "s08 must" not in text, "S08 should be completed evidence, not future remediation"
    assert "s09 must" not in text, "S09 should be completed evidence, not future remediation"


def test_m004_scope_boundary_contract_states_requirement_source_truth() -> None:
    text = _read_contract()

    for phrase in REQUIRED_RECONCILIATION_PHRASES:
        assert phrase in text, f"Missing requirement reconciliation source-truth phrase: {phrase!r}"

    assert text.count("R001") >= 3, "R001 must be named in status, reconciliation, and validation rules"
    assert text.count("R009") >= 3, "R009 must be named in status, reconciliation, and validation rules"
    assert "M004 validation should cover the milestone acceptance criteria" in text, (
        "M004 validation must map acceptance criteria instead of synthetic requirement IDs"
    )


def test_m004_scope_boundary_contract_has_no_placeholder_tokens() -> None:
    text = _read_contract()

    match = PLACEHOLDER_RE.search(text)
    assert match is None, f"Placeholder token found in scope contract: {match.group(0)}"
