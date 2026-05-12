"""Text chunking for Mirad grammar and thesaurus documents."""
import re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
GRAMMAR_PATH = str(_PROJECT_ROOT / "data" / "mirad-docs" / "mirad_grammer.md")
THESAURUS_PATH = str(_PROJECT_ROOT / "data" / "mirad-docs" / "mirad_thesaurus.md")


def count_tokens(text):
    """Rough token estimate (whitespace-split words)."""
    return len(text.split())


def chunk_by_paragraphs(text, max_tokens=500, overlap_tokens=50):
    """Split at blank-line paragraphs, then by max_tokens with overlap."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks, current, current_tokens = [], [], 0
    overlap_buffer, overlap_count = [], 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_tokens = count_tokens(para)

        if current_tokens + para_tokens <= max_tokens:
            current.append(para)
            current_tokens += para_tokens
        else:
            if current:
                chunks.append("\n\n".join(current))
            if overlap_tokens > 0 and current:
                all_words = " ".join(" ".join(c.split()[-overlap_tokens:]) for c in current[-2:])
                overlap_buffer = [all_words]
                overlap_count = count_tokens(all_words)
            else:
                overlap_buffer, overlap_count = [], 0
            current = overlap_buffer + [para]
            current_tokens = overlap_count + para_tokens

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def chunk_fixed(text, chunk_size=100, overlap=50):
    """Fallback fixed-size line chunking."""
    lines = text.splitlines()
    return ["\n".join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size - overlap) if lines[i:i+chunk_size]]


def chunk_grammar(text=None):
    """Chunk the Mirad grammar document.

    Strategy: split at ## ** headers. Sections >300 lines use
    paragraph chunking (max 400 tokens, 50-token overlap),
    then fixed 100-line fallback.
    """
    if text is None:
        with open(GRAMMAR_PATH, encoding="utf-8", errors="replace") as f:
            text = f.read()
    header_pattern = re.compile(r"^## \*\*", re.MULTILINE)
    parts = header_pattern.split(text)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.splitlines()
        if len(lines) > 300:
            para_chunks = chunk_by_paragraphs(part, max_tokens=400, overlap_tokens=50)
            chunks.extend(para_chunks if para_chunks else chunk_fixed(part, 100, 50))
        else:
            chunks.append(part)
    return chunks


def chunk_thesaurus(text=None):
    """Chunk the Mirad thesaurus document.

    Strategy: split at ## ** topic headers. Oversize topics (>300 lines)
    use paragraph chunking with fixed fallback.
    """
    if text is None:
        with open(THESAURUS_PATH, encoding="utf-8", errors="replace") as f:
            text = f.read()
    header_pattern = re.compile(r"^## \*\*", re.MULTILINE)
    parts = header_pattern.split(text)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.splitlines()
        if len(lines) > 300:
            para_chunks = chunk_by_paragraphs(part, max_tokens=400, overlap_tokens=50)
            chunks.extend(para_chunks if para_chunks else chunk_fixed(part, 100, 50))
        else:
            chunks.append(part)
    return chunks


def get_grammar_chunks():
    return chunk_grammar()


def get_thesaurus_chunks():
    return chunk_thesaurus()