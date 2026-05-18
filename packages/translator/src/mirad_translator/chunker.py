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


def _hard_split(text, max_words=200):
    """Split a chunk that's still too long by sentences, then by words."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current, current_len = [], [], 0
    for sent in sentences:
        sent_len = len(sent.split())
        if current_len + sent_len <= max_words:
            current.append(sent)
            current_len += sent_len
        else:
            if current:
                chunks.append(" ".join(current))
            # If a single sentence exceeds max_words, split by words
            if sent_len > max_words:
                words = sent.split()
                for j in range(0, len(words), max_words):
                    chunks.append(" ".join(words[j:j + max_words]))
                current, current_len = [], 0
            else:
                current, current_len = [sent], sent_len
    if current:
        chunks.append(" ".join(current))
    return chunks if chunks else [text]


def chunk_grammar(text=None):
    """Chunk the Mirad grammar document.

    Strategy: split at ## ** headers, then sub-chunk any section
    exceeding 200 words using paragraph chunking (max_tokens=200,
    30-token overlap), then hard-split any remaining oversize chunks.
    200 words ≈ 400 tokens which fits comfortably in 8 GiB VRAM
    with jina-embeddings-v5.
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
        word_count = count_tokens(part)
        if word_count > 200:
            para_chunks = chunk_by_paragraphs(part, max_tokens=200, overlap_tokens=30)
            if not para_chunks:
                para_chunks = chunk_fixed(part, chunk_size=50, overlap=25)
            # Hard-split any chunks that still exceed 200 words
            for pc in para_chunks:
                if count_tokens(pc) > 200:
                    chunks.extend(_hard_split(pc, max_words=200))
                else:
                    chunks.append(pc)
        else:
            chunks.append(part)
    return chunks


def chunk_thesaurus(text=None):
    """Chunk the Mirad thesaurus document.

    Strategy: split at ## ** topic headers, then sub-chunk any section
    exceeding 200 words using paragraph chunking (max_tokens=200,
    30-token overlap), then hard-split any remaining oversize chunks.
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
        word_count = count_tokens(part)
        if word_count > 200:
            para_chunks = chunk_by_paragraphs(part, max_tokens=200, overlap_tokens=30)
            if not para_chunks:
                para_chunks = chunk_fixed(part, chunk_size=50, overlap=25)
            for pc in para_chunks:
                if count_tokens(pc) > 200:
                    chunks.extend(_hard_split(pc, max_words=200))
                else:
                    chunks.append(pc)
        else:
            chunks.append(part)
    return chunks


def get_grammar_chunks():
    return chunk_grammar()


def get_thesaurus_chunks():
    return chunk_thesaurus()