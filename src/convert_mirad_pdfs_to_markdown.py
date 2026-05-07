#!/usr/bin/env python3
"""Convert the Mirad PDFs into high-quality Markdown.

This script prioritizes accuracy by using PyMuPDF4LLM's layout-aware extraction,
then applies conservative cleanup for common PDF line-break artifacts.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pymupdf4llm


DEFAULT_INPUTS = (
    "Mirad.pdf",
    "Mirad_grammer.pdf",
)


def cleanup_markdown(markdown_text: str) -> str:
    """Apply conservative cleanup that improves readability without changing meaning."""

    # Normalize line endings early.
    text = markdown_text.replace("\r\n", "\n").replace("\r", "\n")

    # Rejoin words split across line-wrapped hyphenation.
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)

    # Collapse repeated blank lines while preserving section spacing.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing spaces per line.
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    return text.strip() + "\n"


def convert_pdf_to_markdown(pdf_path: Path, output_path: Path) -> None:
    """Extract a PDF into Markdown using a layout-aware converter."""

    markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
    cleaned_markdown = cleanup_markdown(markdown_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned_markdown, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Mirad PDFs in mirad-docs to high-quality Markdown.",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("mirad-docs"),
        help="Directory containing source PDFs and output Markdown files.",
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=list(DEFAULT_INPUTS),
        help="Input PDF filenames relative to --docs-dir.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    docs_dir = args.docs_dir.resolve()
    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs directory does not exist: {docs_dir}")

    for input_name in args.inputs:
        pdf_path = docs_dir / input_name
        if not pdf_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {pdf_path}")

        output_name = Path(input_name).with_suffix(".md").name
        output_path = docs_dir / output_name

        convert_pdf_to_markdown(pdf_path, output_path)
        print(f"Converted {pdf_path.name} -> {output_path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
