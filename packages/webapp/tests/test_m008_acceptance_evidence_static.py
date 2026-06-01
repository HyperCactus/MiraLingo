from __future__ import annotations

from pathlib import Path


DOC_PATH = Path(__file__).parents[1] / "docs" / "m008-integrated-validation.md"

REQUIRED_COMMANDS = [
    "PYTHONPATH=packages/webapp/src python -m pytest packages/webapp/tests/test_m008_integrated_learner_flow.py -q",
    "PYTHONPATH=packages/webapp/src python -m pytest packages/webapp/tests/test_m008_analytics_api.py packages/webapp/tests/test_m008_weighted_queue_policy.py packages/webapp/tests/test_m008_practice_api_compatibility.py -q",
    "PYTHONPATH=packages/webapp/src python -m pytest packages/webapp/tests/test_analytics_ui_static.py packages/webapp/tests/test_progress_ui_static.py -q",
    "npm --prefix packages/webapp/frontend run build",
]

REQUIRED_EVIDENCE_PATHS = [
    "packages/webapp/tests/test_m008_integrated_learner_flow.py",
    "packages/webapp/tests/test_m008_analytics_api.py",
    "packages/webapp/tests/test_m008_weighted_queue_policy.py",
    "packages/webapp/tests/test_m008_practice_api_compatibility.py",
    "packages/webapp/tests/test_analytics_ui_static.py",
    "packages/webapp/tests/test_progress_ui_static.py",
    "packages/webapp/frontend/package.json",
]



def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")



def test_m008_validation_doc_exists_and_is_non_empty() -> None:
    assert DOC_PATH.exists(), f"missing validation doc: {DOC_PATH}"
    assert DOC_PATH.stat().st_size > 0



def test_m008_validation_doc_has_required_sections() -> None:
    source = _doc_text()

    assert "## Acceptance Matrix" in source
    assert "## Command Set (root-relative)" in source
    assert "## Manual Local UAT Checklist (documented manual evidence)" in source
    assert "## Failure Modes and Interpretation (Q5)" in source
    assert "## Negative-Test Evidence Rows (Q7)" in source



def test_m008_validation_doc_pins_required_commands_and_evidence_files() -> None:
    source = _doc_text()

    for command in REQUIRED_COMMANDS:
        assert command in source, f"missing command: {command}"

    for evidence_path in REQUIRED_EVIDENCE_PATHS:
        assert evidence_path in source, f"missing evidence path: {evidence_path}"



def test_m008_validation_doc_does_not_use_gitignored_or_gsd_artifacts_as_proof() -> None:
    source = _doc_text()
    lowered = source.lower()

    assert "/tmp/" not in source
    assert "__pycache__" not in source
    assert "gitignored" in lowered
    assert "not accepted as completion proof" in lowered
    assert ".gsd/" in source



def test_m008_validation_doc_marks_browser_uat_as_manual_not_automated() -> None:
    source = _doc_text()

    assert "manual follow-up checklist" in source
    assert "not automated proof" in source
    assert "no committed browser E2E runner" in source
