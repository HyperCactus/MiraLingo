"""Command-line surface for deterministic MiraLingo card content imports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from .card_content import (
    CardContentImportError,
    CardContentImportResult,
    CardContentSourceMissingError,
    import_card_content,
)
from .config import load_settings


def result_to_payload(result: CardContentImportResult) -> dict[str, Any]:
    """Return a JSON-serializable importer payload shared by CLI and API."""
    return {
        "ok": True,
        "mutating": False,
        "cards": result.cards,
        "counts": result.counts,
        "sources": result.sources,
    }


def error_to_payload(exc: BaseException) -> dict[str, Any]:
    """Return a structured, stacktrace-free importer error payload."""
    return {
        "ok": False,
        "error": getattr(exc, "code", "import_failed"),
        "phase": getattr(exc, "phase", "content_import"),
        "source_type": getattr(exc, "source_type", None),
        "source_path": getattr(exc, "source_path", None),
        "detail": str(exc),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview MiraLingo card content import counts.")
    parser.add_argument(
        "--phrase-csv",
        type=Path,
        default=None,
        help="Configured phrase CSV path. Defaults to MIRALINGO_PHRASE_CSV_PATH or project data.",
    )
    parser.add_argument(
        "--word-limit",
        type=int,
        default=500,
        help="Maximum number of default word candidates to inspect (0..5000).",
    )
    parser.add_argument(
        "--include-cards",
        action="store_true",
        help="Include card rows in JSON output; counts are always included.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the content import preview and print deterministic JSON diagnostics."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.word_limit < 0 or args.word_limit > 5000:
        payload = {
            "ok": False,
            "error": "invalid_word_limit",
            "phase": "argument_validation",
            "detail": "--word-limit must be between 0 and 5000.",
        }
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 2

    settings = load_settings()
    phrase_csv = args.phrase_csv or settings.phrase_csv_path
    try:
        result = import_card_content(phrase_csv_path=phrase_csv, word_limit=args.word_limit)
    except (CardContentSourceMissingError, CardContentImportError) as exc:
        print(json.dumps(error_to_payload(exc), sort_keys=True), file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive command boundary
        payload = {
            "ok": False,
            "error": "unexpected_import_error",
            "phase": "content_import",
            "detail": f"{type(exc).__name__}: {exc}",
        }
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 1

    payload = result_to_payload(result)
    if not args.include_cards:
        payload = {key: value for key, value in payload.items() if key != "cards"}
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
