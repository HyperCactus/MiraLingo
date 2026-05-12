"""SQLite/FTS5 lexicon lookup for English→Mirad translation."""
import sqlite3, os, re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = os.environ.get("MIRAD_DATA_DIR", str(_PROJECT_ROOT / "data"))
DB_PATH = os.environ.get("MIRAD_DB_PATH", str(Path(DATA_DIR) / "mirad-db.sqlite"))
LEXICON_PATH = os.environ.get("MIRAD_LEXICON_PATH", str(Path(DATA_DIR) / "mirad-docs" / "mirad_lexicon.md"))


def _parse_entries_in_range(content, start, end):
    """Find all **english** = _mirad_ entries within content[start:end]."""
    entries = []
    for m in re.finditer(r"\*\*(.+?)\*\*", content[start:end]):
        after_start = start + m.end()
        after = content[after_start:after_start + 200]
        mm = re.match(r"\s*=\s*_(.+?)_", after)
        if mm:
            english = m.group(1).strip()
            mirad = mm.group(1).strip()
            if english and mirad and len(english) <= 100:
                entries.append((english.lower(), mirad))
    return entries


def build_lexicon_db(db_path=None, lexicon_path=None):
    """Build or rebuild the lexicon SQLite DB from mirad_lexicon.md.

    Idempotent: only rebuilds if lexicon.md mtime > db mtime.
    Returns dict with total count and per-letter counts.
    """
    db_path = db_path or DB_PATH
    lexicon_path = lexicon_path or LEXICON_PATH

    if os.path.exists(db_path):
        db_mtime = os.path.getmtime(db_path)
        lex_mtime = os.path.getmtime(lexicon_path)
        if lex_mtime <= db_mtime:
            conn = sqlite3.connect(db_path)
            total = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
            conn.close()
            return {"total": total, "by_letter": {}, "idempotent": True}

    with open(lexicon_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Find all section boundaries
    section_pat = re.compile(r"\*\*English-Mirad-([A-Z])\*\*")
    section_starts = [(m.group(1), m.start()) for m in section_pat.finditer(content)]
    section_starts.sort(key=lambda x: x[1])

    all_entries = []
    by_letter = {}
    for letter, start in section_starts:
        idx = section_starts.index((letter, start))
        end = section_starts[idx + 1][1] if idx + 1 < len(section_starts) else len(content)
        letter_entries = _parse_entries_in_range(content, start, end)
        all_entries.extend(letter_entries)
        by_letter[letter] = len(letter_entries)

    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE lexicon (id INTEGER PRIMARY KEY, english TEXT UNIQUE NOT NULL, mirad TEXT NOT NULL)"
    )
    cur.execute(
        "CREATE VIRTUAL TABLE lexicon_fts USING fts5(english, mirad, content='lexicon', content_rowid='id')"
    )
    cur.executemany("INSERT OR IGNORE INTO lexicon (english, mirad) VALUES (?, ?)", all_entries)
    cur.execute("INSERT INTO lexicon_fts(rowid, english, mirad) SELECT id, english, mirad FROM lexicon")
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    conn.close()
    return {"total": total, "by_letter": by_letter, "idempotent": False}


def lookup_word(db_path=None, english_word=None):
    """Look up an English word in the lexicon DB.

    Args:
        db_path: Path to the SQLite DB (default: MIRAD_DB_PATH env or DATA_DIR/mirad-db.sqlite)
        english_word: The English word to look up

    Returns:
        The Mirad translation str, or None if not found.
    """
    db_path = db_path or DB_PATH
    english_word = (english_word or "").lower().strip()
    if not english_word:
        return None
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT mirad FROM lexicon WHERE english = ?", (english_word,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def lookup_mirad_word(db_path=None, mirad_word=None):
    """Look up a Mirad word in the lexicon DB (reverse lookup).

    Args:
        db_path: Path to the SQLite DB.
        mirad_word: The Mirad word to look up.

    Returns:
        The English translation str, or None if not found.
    """
    db_path = db_path or DB_PATH
    mirad_word = (mirad_word or "").strip()
    if not mirad_word:
        return None
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT english FROM lexicon WHERE mirad = ?", (mirad_word,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_stats(db_path=None):
    """Return dict with total entry count and per-letter breakdown."""
    db_path = db_path or DB_PATH
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    rows = conn.execute(
        "SELECT SUBSTR(english,1,1), COUNT(*) FROM lexicon GROUP BY SUBSTR(english,1,1) ORDER BY SUBSTR(english,1,1)"
    ).fetchall()
    conn.close()
    by_letter = {r[0]: r[1] for r in rows}
    return {"total": total, "by_letter": by_letter}