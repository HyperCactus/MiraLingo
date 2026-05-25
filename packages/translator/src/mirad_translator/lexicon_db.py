"""SQLite/FTS5 lexicon lookup for English↔Mirad translation."""
import sqlite3, os, re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = os.environ.get("MIRAD_DATA_DIR", str(_PROJECT_ROOT / "data"))
DB_PATH = os.environ.get("MIRAD_DB_PATH", str(Path(DATA_DIR) / "mirad-db.sqlite"))
LEXICON_PATH = os.environ.get("MIRAD_LEXICON_PATH", str(Path(DATA_DIR) / "mirad-docs" / "mirad_lexicon.md"))

_ENTRY_RE = re.compile(r"\*\*(.+?)\*\*\s*=\s*_(.+?)_")
_EN_SECTION_RE = re.compile(r"(?:#{1,3}\s*)?\*\*English-Mirad-([A-Z])\*\*")
_MI_SECTION_RE = re.compile(r"(?:#{1,3}\s*)?\*\*Mirad-English-([A-Z])\*\*")
_SECTION_RE = re.compile(r"(?:#{1,3}\s*)?\*\*(?:English-Mirad|Mirad-English)-[A-Z]\*\*")


def _split_equivalents(value: str) -> list[str]:
    """Split comma-delimited lexicon translations while preserving phrases."""
    result = []
    for part in (value or "").split(","):
        item = " ".join(part.strip().split())
        if item and item not in result:
            result.append(item)
    return result


def _parse_entries_in_range(content, start, end):
    """Find all **left** = _right_ entries within content[start:end]."""
    entries = []
    for m in _ENTRY_RE.finditer(content[start:end]):
        left = " ".join(m.group(1).strip().split())
        right = " ".join(m.group(2).strip().split())
        if left and right and len(left) <= 100:
            entries.append((left.lower(), right))
    return entries


def _section_ranges(content: str, section_re: re.Pattern) -> list[tuple[str, int, int]]:
    ranges = []
    matches = list(section_re.finditer(content))
    for match in matches:
        next_any = _SECTION_RE.search(content, match.end())
        end = next_any.start() if next_any else len(content)
        ranges.append((match.group(1), match.start(), end))
    return ranges


def _db_has_current_schema(db_path: str) -> bool:
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual')")}
        conn.close()
    except sqlite3.Error:
        return False
    return {"lexicon", "lexicon_fts", "reverse_lexicon", "reverse_lexicon_fts"}.issubset(tables)


def build_lexicon_db(db_path=None, lexicon_path=None):
    """Build or rebuild lexicon SQLite DB from mirad_lexicon.md.

    Stores English→Mirad entries from English-Mirad sections and Mirad→English
    entries from Mirad-English sections. Multi-valued entries stay intact in
    canonical tables; helper lookups expose split candidates when needed.
    """
    db_path = db_path or DB_PATH
    lexicon_path = lexicon_path or LEXICON_PATH

    if os.path.exists(db_path) and _db_has_current_schema(db_path):
        db_mtime = os.path.getmtime(db_path)
        lex_mtime = os.path.getmtime(lexicon_path)
        if lex_mtime <= db_mtime:
            conn = sqlite3.connect(db_path)
            total = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
            reverse_total = conn.execute("SELECT COUNT(*) FROM reverse_lexicon").fetchone()[0]
            conn.close()
            return {"total": total, "reverse_total": reverse_total, "by_letter": {}, "idempotent": True}

    with open(lexicon_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    all_entries = []
    reverse_entries = []
    by_letter = {}
    reverse_by_letter = {}

    for letter, start, end in _section_ranges(content, _EN_SECTION_RE):
        letter_entries = _parse_entries_in_range(content, start, end)
        all_entries.extend(letter_entries)
        by_letter[letter] = by_letter.get(letter, 0) + len(letter_entries)

    for letter, start, end in _section_ranges(content, _MI_SECTION_RE):
        letter_entries = _parse_entries_in_range(content, start, end)
        reverse_entries.extend(letter_entries)
        reverse_by_letter[letter] = reverse_by_letter.get(letter, 0) + len(letter_entries)

    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE lexicon (id INTEGER PRIMARY KEY, english TEXT UNIQUE NOT NULL, mirad TEXT NOT NULL)")
    cur.execute("CREATE VIRTUAL TABLE lexicon_fts USING fts5(english, mirad, content='lexicon', content_rowid='id')")
    cur.execute("CREATE TABLE reverse_lexicon (id INTEGER PRIMARY KEY, mirad TEXT UNIQUE NOT NULL, english TEXT NOT NULL)")
    cur.execute("CREATE VIRTUAL TABLE reverse_lexicon_fts USING fts5(mirad, english, content='reverse_lexicon', content_rowid='id')")
    cur.executemany("INSERT OR IGNORE INTO lexicon (english, mirad) VALUES (?, ?)", all_entries)
    cur.executemany("INSERT OR IGNORE INTO reverse_lexicon (mirad, english) VALUES (?, ?)", reverse_entries)
    cur.execute("INSERT INTO lexicon_fts(rowid, english, mirad) SELECT id, english, mirad FROM lexicon")
    cur.execute("INSERT INTO reverse_lexicon_fts(rowid, mirad, english) SELECT id, mirad, english FROM reverse_lexicon")
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    reverse_total = conn.execute("SELECT COUNT(*) FROM reverse_lexicon").fetchone()[0]
    conn.close()
    return {"total": total, "reverse_total": reverse_total, "by_letter": by_letter, "reverse_by_letter": reverse_by_letter, "idempotent": False}


def lookup_word(db_path=None, english_word=None):
    candidates = lookup_word_candidates(db_path=db_path, english_word=english_word)
    return ", ".join(candidates) if candidates else None


def lookup_word_candidates(db_path=None, english_word=None) -> list[str]:
    """Return Mirad candidates for an English word/phrase."""
    db_path = db_path or DB_PATH
    english_word = (english_word or "").lower().strip()
    if not english_word:
        return []
    build_lexicon_db(db_path=db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT mirad FROM lexicon WHERE english = ?", (english_word,))
    row = cur.fetchone()
    conn.close()
    return _split_equivalents(row[0]) if row else []


def lookup_mirad_word(db_path=None, mirad_word=None):
    candidates = lookup_mirad_word_candidates(db_path=db_path, mirad_word=mirad_word)
    return ", ".join(candidates) if candidates else None


def lookup_mirad_word_candidates(db_path=None, mirad_word=None) -> list[str]:
    """Return English candidates for a Mirad word/phrase."""
    db_path = db_path or DB_PATH
    mirad_word = (mirad_word or "").strip().lower()
    if not mirad_word:
        return []
    build_lexicon_db(db_path=db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT english FROM reverse_lexicon WHERE mirad = ?", (mirad_word,))
    row = cur.fetchone()
    conn.close()
    return _split_equivalents(row[0]) if row else []


def get_stats(db_path=None):
    """Return dict with total entry count and per-letter breakdown."""
    db_path = db_path or DB_PATH
    build_lexicon_db(db_path=db_path)
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    reverse_total = conn.execute("SELECT COUNT(*) FROM reverse_lexicon").fetchone()[0]
    rows = conn.execute(
        "SELECT SUBSTR(english,1,1), COUNT(*) FROM lexicon GROUP BY SUBSTR(english,1,1) ORDER BY SUBSTR(english,1,1)"
    ).fetchall()
    reverse_rows = conn.execute(
        "SELECT SUBSTR(mirad,1,1), COUNT(*) FROM reverse_lexicon GROUP BY SUBSTR(mirad,1,1) ORDER BY SUBSTR(mirad,1,1)"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "reverse_total": reverse_total,
        "by_letter": {r[0]: r[1] for r in rows},
        "reverse_by_letter": {r[0]: r[1] for r in reverse_rows},
    }
