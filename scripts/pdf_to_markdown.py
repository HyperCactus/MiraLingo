#!/usr/bin/env python3
"""Convert PDFs into high-quality Markdown.

This module provides a function to convert PDFs to Markdown using PyMuPDF4LLM's
layout-aware extraction, with conservative cleanup for common PDF artifacts.

It can be imported and used as a module, or run from the command line.

Example:
    Module usage:
    >>> from pdf_to_markdown import pdf_to_markdown
    >>> pdf_to_markdown("input.pdf", "output.md")
    Command-line usage:
    $ python pdf_to_markdown.py input.pdf -o output.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pymupdf4llm


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


def pdf_to_markdown(pdf_path: str | Path, output_path: str | Path) -> None:
    """Convert a PDF file to Markdown.

    Extracts the PDF using layout-aware conversion and applies conservative
    cleanup to improve readability.

    Args:
        pdf_path: Path to the input PDF file.
        output_path: Path where the output Markdown file will be written.

    Raises:
        FileNotFoundError: If the input PDF does not exist.
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
    cleaned_markdown = cleanup_markdown(markdown_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned_markdown, encoding="utf-8")


def main() -> int:
    """CLI entry point for converting PDFs to Markdown."""
    parser = argparse.ArgumentParser(
        description="Convert PDF files to Markdown.",
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the input PDF file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the output Markdown file. If not specified, uses the same name as the PDF with .md extension.",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path.resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    output_path = args.output or pdf_path.with_suffix(".md")
    output_path = output_path.resolve()

    pdf_to_markdown(pdf_path, output_path)
    print(f"Converted {pdf_path.name} -> {output_path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
