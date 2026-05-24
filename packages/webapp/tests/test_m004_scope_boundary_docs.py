from __future__ import annotations

import re
from pathlib import Path


DOC_PATH = Path(__file__).parents[1] / "docs" / "m004_scope_boundary_map.md"


REQUIRED_HEADINGS = [
    "# M004 Scope and Boundary Map",
    "## Canonical Boundary Map Artifact",
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
    "S10": ["requirement scope reconciliation", "R001/R009", "zero Active", "Completed evidence"],
    "S11": ["boundary map restoration", "S01-S11", "producer/consumer", "Completed"],
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

REQUIRED_CANONICAL_BOUNDARY_PHRASES = [
    "canonical validation-linked producer and consumer boundary map for M004",
    "auditable boundary-map source of truth",
    "validators and tests should link here instead of reading `.gsd/` planning files",
    "covers S01-S11",
    "traces each cross-slice webapp contract from producer slice",
]

REQUIRED_CONTRACT_SURFACES = {
    "Auth/session": ["S01", "S07", "S08"],
    "Registration": ["S07", "S08"],
    "Content importer": ["S02", "S08"],
    "Practice scheduler and answer events": ["S03", "S07", "S08"],
    "Audio service": ["S04"],
    "Progress diagnostics": ["S05", "S03", "S07", "S08"],
    "SQLite persistence": ["S08"],
    "Frontend UAT": ["S09", "S01-S08"],
    "Requirement-scope reconciliation": ["S10", "S11"],
}

REQUIRED_TRACE_COLUMNS = [
    "Producer slice(s)",
    "Consumer slice(s) or validation use",
    "Evidence source",
    "Diagnostic or inspection surface",
]

PLACEHOLDER_RE = re.compile(r"\b(TBD|TODO|FIXME|XXX)\b", re.IGNORECASE)


def _read_contract() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _table_row(text: str, first_cell: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"| {first_cell} "):
            return line
    raise AssertionError(f"Missing markdown table row for {first_cell}")


def _row_for_slice(text: str, slice_id: str) -> str:
    try:
        return _table_row(text, slice_id)
    except AssertionError as error:
        raise AssertionError(f"Missing coverage row for {slice_id}") from error


def test_m004_scope_boundary_contract_has_required_sections() -> None:
    text = _read_contract()

    for heading in REQUIRED_HEADINGS:
        assert heading in text, f"Missing required heading: {heading}"


def test_m004_scope_boundary_contract_maps_every_slice_id() -> None:
    text = _read_contract()

    for index in range(1, 12):
        slice_id = f"S{index:02d}"
        row = _row_for_slice(text, slice_id)
        assert row.count("|") >= 5, f"Coverage row for {slice_id} is malformed: {row}"
        assert len(row.replace("|", "").strip()) > len(slice_id), f"Coverage row for {slice_id} is blank"


def test_m004_scope_boundary_contract_names_key_boundaries() -> None:
    text = _read_contract()

    for term in REQUIRED_BOUNDARY_TERMS:
        assert term.lower() in text.lower(), f"Missing boundary term: {term}"


def test_m004_scope_boundary_contract_tracks_s07_through_s11_completion() -> None:
    text = _read_contract()

    for slice_id, phrases in REQUIRED_COMPLETED_PHRASES.items():
        row = _row_for_slice(text, slice_id)
        assert "pending remediation" not in row.lower(), (
            f"{slice_id} row regressed to pending remediation instead of completed evidence: {row}"
        )
        for phrase in phrases:
            assert phrase.lower() in row.lower(), f"Missing {phrase!r} in {slice_id} completed row: {row}"


def test_m004_scope_boundary_contract_identifies_canonical_boundary_map_artifact() -> None:
    text = _read_contract()

    for phrase in REQUIRED_CANONICAL_BOUNDARY_PHRASES:
        assert phrase in text, f"Missing canonical boundary-map phrase: {phrase!r}"


def test_m004_scope_boundary_contract_maps_required_producer_consumer_surfaces() -> None:
    text = _read_contract()

    for heading in REQUIRED_TRACE_COLUMNS:
        assert heading in text, f"Producer/consumer trace table is missing column: {heading}"

    for surface, producer_tokens in REQUIRED_CONTRACT_SURFACES.items():
        row = _table_row(text, surface)
        lower_row = row.lower()
        assert "producer" not in lower_row, f"{surface} row appears to be the header, not a trace row: {row}"
        assert "validation" in lower_row or "consumer" in lower_row, (
            f"{surface} row must name consumer or validation use: {row}"
        )
        assert "evidence" in lower_row, f"{surface} row must name tracked evidence: {row}"
        assert "diagnostic" in lower_row or "inspection" in lower_row or "status" in lower_row, (
            f"{surface} row must name diagnostic or inspection language: {row}"
        )
        for token in producer_tokens:
            assert token in row, f"{surface} row is missing producer/consumer slice token {token}: {row}"


def test_m004_scope_boundary_contract_has_no_stale_s07_s11_pending_wording() -> None:
    text = _read_contract().lower()

    assert "pending remediation" not in text, "Scope contract still contains stale pending-remediation wording"
    for slice_id in ("s07", "s08", "s09", "s10", "s11"):
        assert f"{slice_id} must" not in text, f"{slice_id.upper()} should be completed evidence, not future remediation"


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
