from __future__ import annotations

from pathlib import Path


DOC = Path(__file__).parents[1] / "docs" / "m005_s07_uat.md"


REQUIRED_PHRASES = [
    "# M005 S07 local UAT walkthrough",
    "## Local startup",
    "PYTHONPATH=packages/webapp/src uvicorn mirad_webapp.api:create_app --factory --reload",
    "npm --prefix packages/webapp/frontend run dev",
    "MIRALINGO_DATABASE_PATH",
    "## Browser UAT walkthrough",
    "Welcome to MiraLingo",
    "Wikibooks grammar",
    "Continue Practice",
    "Revision",
    "Build Vocabulary",
    "Give Up",
    "Hear Mirad answer",
    "Analytics",
    "Settings",
    "Iconify status",
    "/practice/progress",
    "/settings",
    "/auth/current-user",
    "users",
    "user_settings",
    "shown_cards",
    "answer_events",
    "## Automation limits",
    "## Failure modes and where to look",
    "Backend port conflict",
    "Frontend port conflict",
    "Missing MBROLA",
    "Iconify timeout or offline behavior",
    "Malformed API response",
    "Stale browser session",
    "## Load profile",
    "## Negative tests checklist",
    "Wrong typed answer",
    "Blank typed answer",
    "Deletion confirmation mismatch",
]


def main() -> None:
    assert DOC.exists(), f"missing UAT doc: {DOC}"
    text = DOC.read_text(encoding="utf-8")
    assert text.strip(), "UAT doc is empty"

    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
    assert not missing, "missing required phrases:\n- " + "\n- ".join(missing)

    headings = [
        "## Local startup",
        "## Browser UAT walkthrough",
        "## Expected evidence to capture",
        "## Automation limits",
        "## Failure modes and where to look",
        "## Load profile",
        "## Negative tests checklist",
    ]
    for heading in headings:
        assert text.count(heading) == 1, f"expected heading exactly once: {heading}"


if __name__ == "__main__":
    main()
