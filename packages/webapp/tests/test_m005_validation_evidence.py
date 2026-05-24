from __future__ import annotations

from pathlib import Path


DOC = Path(__file__).parents[1] / "docs" / "m005_validation_evidence.md"

REQUIRED_HEADINGS = [
    "# M005 Validation Evidence Index",
    "## Scope and requirements posture",
    "## Acceptance coverage matrix",
    "## Evidence inventory by acceptance area",
    "## UAT evidence capture",
    "## Observability and diagnostics surfaces",
    "## Failure modes (Q5)",
    "## Load profile (Q6)",
    "## Negative-test coverage (Q7)",
    "## Automation limits",
    "## Final validator checklist",
    "## Verification commands referenced by this index",
]

REQUIRED_TERMS = {
    "auth/login": [
        "Logged-in user reaches a main menu",
        "login",
        "Continue Practice",
        "Revision",
        "Build Vocabulary",
        "Analytics",
        "Settings",
        "Log Out",
        "/auth/current-user",
    ],
    "practice-answer-flow": [
        "typed answer",
        "wrong answer",
        "Give Up",
        "reveal",
        "Correct",
        "Not quite",
        "/practice/answers",
    ],
    "audio-and-settings": [
        "audio",
        "TTS speed",
        "tts_speed",
        "voice",
        "theme",
        "persist",
        "/practice/audio/",
        "/settings",
        "mbrola_unavailable",
        "Audio uses your saved",
        "playback-rate fallback",
    ],
    "account-deletion": [
        "delete-account",
        "deletion",
        "users",
        "user_settings",
        "shown_cards",
        "answer_events",
        "session teardown",
    ],
    "landing-and-links": [
        "landing",
        "Welcome to MiraLingo",
        "Wikibooks grammar",
        "dark theme",
    ],
    "iconify-runtime": [
        "Iconify",
        "fallback",
        "offline",
        "timeout",
        "Iconify status",
    ],
    "analytics-observability": [
        "analytics",
        "progress",
        "/practice/progress",
        "Observability and diagnostics surfaces",
        "role=\"status\"",
        "role=\"alert\"",
    ],
    "failure-load-negative-limits": [
        "Failure mode",
        "Load profile",
        "Negative-test coverage",
        "Automation limits",
        "manual",
        "browser",
        "Validation remediation note",
        "round-1 validation evidence remediation",
    ],
    "verification-commands": [
        "PYTHONPATH=packages/webapp/src python3 -m pytest packages/webapp/tests/test_m005_final_learner_flow.py -q",
        "PYTHONPATH=packages/webapp/src python3 -m pytest packages/webapp/tests/test_m005_frontend_assembly_static.py -q",
        "PYTHONPATH=packages/webapp/src python3 packages/webapp/tests/verify_m005_s07_uat_doc.py",
        "npm --prefix packages/webapp/frontend run build",
    ],
    "scope-reconciliation": [
        "R001",
        "R009",
        "tokenizer",
        "legacy-orthography",
        "roadmap success criteria",
        "root-requirement status",
    ],
}


def _text() -> str:
    assert DOC.exists(), f"missing validation evidence doc: {DOC}"
    text = DOC.read_text(encoding="utf-8")
    assert text.strip(), f"validation evidence doc is empty: {DOC}"
    return text


def test_m005_validation_evidence_has_required_sections() -> None:
    text = _text()

    missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    assert not missing, "missing required headings:\n- " + "\n- ".join(missing)


def test_m005_validation_evidence_covers_required_acceptance_areas() -> None:
    text = _text()

    missing_groups: list[str] = []
    for group, terms in REQUIRED_TERMS.items():
        missing_terms = [term for term in terms if term not in text]
        if missing_terms:
            missing_groups.append(f"{group}: " + ", ".join(missing_terms))

    assert not missing_groups, "missing required evidence terms:\n- " + "\n- ".join(missing_groups)
