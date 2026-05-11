#!/usr/bin/env python3

"""
Download a Wikibooks book and save it as a single PDF.

Examples:

    python scripts/download_wikibook_pdf.py Mirad_Thesaurus
    python scripts/download_wikibook_pdf.py Mirad_Lexicon

For Mirad_Lexicon, this script discovers subpages from the table of contents
on the main page, e.g.:
    Mirad_Lexicon/Mirad-English-A
    Mirad_Lexicon/English-Mirad-A

Install:

    pip install requests beautifulsoup4 weasyprint

Output:

    data/pdfs/Mirad_Lexicon_full.pdf
"""

from __future__ import annotations

import argparse
import html
import random
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from weasyprint import HTML


API_URL = "https://en.wikibooks.org/w/api.php"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_OUTPUT_DIR = PROJECT_ROOT / "data" / "pdfs"

REQUEST_DELAY_SECONDS = 3.5
MAX_RETRIES = 8


def safe_filename(value: str) -> str:
    return (
        value.replace("/", "__")
        .replace(" ", "_")
        .replace(":", "_")
        .replace("?", "_")
        .replace("&", "_")
    )


def page_display_title(title: str, book_title: str) -> str:
    if title == book_title:
        return book_title.replace("_", " ")

    prefix = book_title + "/"
    if title.startswith(prefix):
        return title[len(prefix):].replace("_", " ")

    return title.replace("_", " ")


def sort_key_for_book_page(title: str) -> tuple:
    if "/" not in title:
        return (0, "", "")

    subpage = title.split("/", 1)[1]

    match = re.match(r"Mirad-English-([A-Z])$", subpage)
    if match:
        return (1, match.group(1), subpage)

    match = re.match(r"English-Mirad-([A-Z])$", subpage)
    if match:
        return (2, match.group(1), subpage)

    return (9, subpage.lower(), subpage)


def request_api(params: dict, max_retries: int = MAX_RETRIES) -> dict:
    headers = {
        "User-Agent": (
            "WikibooksOfflinePdfScript/1.0 "
            "(personal offline PDF generation; respectful retry/backoff)"
        )
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                API_URL,
                params=params,
                headers=headers,
                timeout=60,
            )
        except requests.RequestException as exc:
            wait_time = min(120, 10 * attempt) + random.uniform(0, 4)
            print(
                f"Request failed: {exc}. "
                f"Waiting {wait_time:.1f}s before retry {attempt}/{max_retries}..."
            )
            time.sleep(wait_time)
            continue

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            if retry_after and retry_after.isdigit():
                wait_time = int(retry_after)
            else:
                wait_time = min(240, 25 * attempt) + random.uniform(0, 8)

            print(
                f"Rate limited. Waiting {wait_time:.1f}s "
                f"before retry {attempt}/{max_retries}..."
            )
            time.sleep(wait_time)
            continue

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            wait_time = min(120, 10 * attempt) + random.uniform(0, 4)
            print(
                f"HTTP error: {exc}. "
                f"Waiting {wait_time:.1f}s before retry {attempt}/{max_retries}..."
            )
            time.sleep(wait_time)
            continue

        time.sleep(REQUEST_DELAY_SECONDS)
        return response.json()

    raise RuntimeError("API request failed after maximum retries.")


def fetch_page_html(title: str, cache_dir: Path) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_path = cache_dir / f"{safe_filename(title)}.html"

    if cache_path.exists():
        print(f"Using cached: {title}")
        return cache_path.read_text(encoding="utf-8")

    print(f"Downloading: {title}")

    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2",
    }

    data = request_api(params)

    if "error" in data:
        raise RuntimeError(f"Could not fetch {title}: {data['error']}")

    page_html = data["parse"]["text"]
    cache_path.write_text(page_html, encoding="utf-8")

    return page_html


def discover_pages_from_main_page(book_title: str, cache_dir: Path) -> list[str]:
    """
    Discover subpages from the main book page.

    For Mirad_Lexicon this finds pages like:
        Mirad_Lexicon/Mirad-English-A
        Mirad_Lexicon/English-Mirad-A

    It deliberately ignores edit links, special links, query strings, and
    non-lexicon links.
    """
    print(f"Discovering pages from main page: {book_title}")

    main_html = fetch_page_html(book_title, cache_dir)
    soup = BeautifulSoup(main_html, "html.parser")

    pages: list[str] = [book_title]

    valid_subpage_pattern = re.compile(
        r"^(Mirad-English|English-Mirad)-[A-Z]$"
    )

    for link in soup.find_all("a"):
        href = link.get("href", "")
        link_text = link.get_text(strip=True)

        candidates = [href, link_text]

        for candidate in candidates:
            if not candidate:
                continue

            candidate = candidate.strip()

            # Remove URL fragments.
            candidate = candidate.split("#", 1)[0]

            # Ignore edit/action/query links.
            if (
                "action=edit" in candidate
                or "index.php" in candidate
                or "?" in candidate
                or candidate.startswith("/w/")
                or candidate.startswith("w/")
                or candidate.startswith("/wiki/Special:")
                or candidate.startswith("Special:")
            ):
                continue

            full_title: str | None = None

            # Examples:
            #   ./Mirad-English-A
            #   ./English-Mirad-A
            if candidate.startswith("./"):
                subpage = candidate[2:]
                if valid_subpage_pattern.match(subpage):
                    full_title = f"{book_title}/{subpage}"

            # Example:
            #   /wiki/Mirad_Lexicon/Mirad-English-A
            elif candidate.startswith("/wiki/" + book_title + "/"):
                full_title = candidate.removeprefix("/wiki/")

            # Example:
            #   /Mirad-English-A
            elif candidate.startswith("/"):
                subpage = candidate[1:]
                if valid_subpage_pattern.match(subpage):
                    full_title = f"{book_title}/{subpage}"

            # Example from link text:
            #   Mirad-English-A
            elif valid_subpage_pattern.match(candidate):
                full_title = f"{book_title}/{candidate}"

            if not full_title:
                continue

            full_title = full_title.replace(" ", "_")

            # Final safety filter.
            if (
                full_title == book_title
                or not full_title.startswith(book_title + "/")
                or "?" in full_title
                or "index.php" in full_title
                or "action=edit" in full_title
            ):
                continue

            subpage = full_title.split("/", 1)[1]
            if not valid_subpage_pattern.match(subpage):
                continue

            pages.append(full_title)

    unique_pages = sorted(set(pages), key=sort_key_for_book_page)

    if book_title in unique_pages:
        unique_pages.remove(book_title)
    unique_pages.insert(0, book_title)

    print(f"Discovered {len(unique_pages)} pages from main page.")
    return unique_pages

def get_category_members(book_title: str) -> list[str]:
    """
    Try to get all pages in Category:Book:<book title>.

    This works for some Wikibooks books, but not reliably for Mirad_Lexicon.
    """
    category_title = "Category:Book:" + book_title.replace("_", " ")
    print(f"Discovering pages from {category_title}")

    pages: list[str] = []
    cmcontinue: str | None = None

    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmnamespace": "0",
            "cmlimit": "500",
            "format": "json",
            "formatversion": "2",
        }

        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        data = request_api(params)

        members = data.get("query", {}).get("categorymembers", [])
        for member in members:
            title = member.get("title")
            if title and (title == book_title or title.startswith(book_title + "/")):
                pages.append(title.replace(" ", "_"))

        cmcontinue = data.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            break

    unique_pages = sorted(set(pages), key=sort_key_for_book_page)

    if book_title in unique_pages:
        unique_pages.remove(book_title)
    unique_pages.insert(0, book_title)

    print(f"Discovered {len(unique_pages)} pages from category.")
    return unique_pages


def discover_pages(book_title: str, cache_dir: Path, method: str) -> list[str]:
    if method == "main":
        return discover_pages_from_main_page(book_title, cache_dir)

    if method == "category":
        return get_category_members(book_title)

    if method == "none":
        return [book_title]

    # auto mode: try category, but if it only finds the main page,
    # fall back to main-page link discovery.
    category_pages = get_category_members(book_title)

    if len(category_pages) > 1:
        return category_pages

    print("Category discovery only found the main page. Falling back to main-page links.")
    return discover_pages_from_main_page(book_title, cache_dir)


def clean_html_fragment(fragment: str) -> str:
    soup = BeautifulSoup(fragment, "html.parser")

    selectors_to_remove = [
        "script",
        "style",
        "noscript",
        "img",
        "figure",
        ".mw-editsection",
        ".noprint",
        ".metadata",
        ".navigation-not-searchable",
        ".printfooter",
        ".catlinks",
        ".mw-empty-elt",
        ".plainlinks",
        ".thumb",
        ".gallery",
    ]

    for tag in soup.select(", ".join(selectors_to_remove)):
        tag.decompose()

    for tag in soup.find_all(["annotation", "semantics"]):
        tag.decompose()

    for tag in soup.find_all(id=True):
        del tag["id"]

    for link in soup.find_all("a"):
        href = link.get("href", "")

        if (
            href.startswith("#")
            or "action=edit" in href
            or href.startswith("/w/")
            or href.startswith("/wiki/Special:")
        ):
            link.unwrap()
            continue

        if href.startswith("/wiki/"):
            link["href"] = "https://en.wikibooks.org" + href

    for tag in soup.find_all(["span", "div"]):
        text = tag.get_text(strip=True)
        if not text and not tag.find_all(["table", "ul", "ol", "p"]):
            tag.decompose()

    return str(soup)


def build_full_html(book_title: str, pages: list[str], cache_dir: Path) -> str:
    sections: list[str] = []
    total = len(pages)

    for index, title in enumerate(pages, start=1):
        print(f"[{index}/{total}] Processing: {title}")

        raw_html = fetch_page_html(title, cache_dir)
        cleaned_html = clean_html_fragment(raw_html)
        heading = html.escape(page_display_title(title, book_title))

        sections.append(
            f"""
            <section class="chapter">
                <h1>{heading}</h1>
                {cleaned_html}
            </section>
            """
        )

    sections_html = "\n".join(sections)
    display_book_title = html.escape(book_title.replace("_", " "))

    return f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>{display_book_title}</title>
    <style>
        @page {{
            size: A4;
            margin: 12mm 8mm 14mm 8mm;

            @bottom-center {{
                content: "Page " counter(page);
                font-size: 8pt;
                color: #666;
            }}
        }}

        body {{
            font-family: "DejaVu Serif", "Liberation Serif", serif;
            font-size: 8.8pt;
            line-height: 1.22;
            color: #111;
        }}

        .title-page {{
            page-break-after: always;
            text-align: center;
            margin-top: 35%;
        }}

        .title-page h1 {{
            font-size: 30pt;
            border: none;
        }}

        .title-page p {{
            font-size: 11pt;
            color: #555;
        }}

        .chapter {{
            page-break-before: always;
        }}

        .chapter:first-of-type {{
            page-break-before: auto;
        }}

        h1 {{
            font-size: 18pt;
            border-bottom: 1px solid #999;
            padding-bottom: 0.2em;
            margin-top: 0;
            margin-bottom: 0.5em;
        }}

        h2 {{
            font-size: 13pt;
            margin-top: 1em;
            margin-bottom: 0.35em;
        }}

        h3 {{
            font-size: 11pt;
            margin-top: 0.8em;
            margin-bottom: 0.3em;
        }}

        h4, h5, h6 {{
            font-size: 9.5pt;
            margin-top: 0.7em;
            margin-bottom: 0.2em;
        }}

        p {{
            margin: 0.25em 0;
        }}

        ul, ol {{
            margin-top: 0.2em;
            margin-bottom: 0.35em;
        }}

        li {{
            margin: 0.08em 0;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 0.5em 0;
            font-size: 7.5pt;
            page-break-inside: auto;
        }}

        tr {{
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid #bbb;
            padding: 2px 3px;
            vertical-align: top;
        }}

        th {{
            background: #eee;
            font-weight: bold;
        }}

        code, pre {{
            font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
            font-size: 7.5pt;
        }}

        pre {{
            white-space: pre-wrap;
        }}

        a {{
            color: #0645ad;
            text-decoration: none;
        }}

        .toc, #toc {{
            border: 1px solid #aaa;
            padding: 0.5em;
            margin: 1em 0;
            background: #f8f8f8;
        }}

        .mw-parser-output {{
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>{display_book_title}</h1>
        <p>Combined offline PDF generated from Wikibooks.</p>
    </div>

    {sections_html}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "book_title",
        nargs="?",
        default="Mirad_Lexicon",
        help="Wikibooks title, e.g. Mirad_Thesaurus or Mirad_Lexicon",
    )
    parser.add_argument(
        "--discover",
        choices=["auto", "main", "category", "none"],
        default="auto",
        help=(
            "Page discovery method. Use 'main' for Mirad_Lexicon if category "
            "only returns the table of contents."
        ),
    )

    args = parser.parse_args()
    book_title = args.book_title.strip().replace(" ", "_")

    output_dir = BASE_OUTPUT_DIR / safe_filename(book_title)
    cache_dir = output_dir / "cache"
    output_html = output_dir / f"{safe_filename(book_title)}_full.html"
    output_pdf = output_dir / f"{safe_filename(book_title)}_full.pdf"

    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    pages = discover_pages(book_title, cache_dir, args.discover)

    if not pages:
        print(f"No pages found for {book_title}", file=sys.stderr)
        sys.exit(1)

    print("\nPages to download:")
    for page in pages:
        print(f"  - {page}")

    print(f"\nTotal pages: {len(pages)}")

    full_html = build_full_html(book_title, pages, cache_dir)

    output_html.write_text(full_html, encoding="utf-8")
    print(f"\nWrote HTML backup: {output_html}")

    print(f"Creating PDF: {output_pdf}")
    HTML(string=full_html, base_url="https://en.wikibooks.org").write_pdf(output_pdf)

    print("\nDone.")
    print(f"PDF saved to: {output_pdf}")


if __name__ == "__main__":
    main()