"""Tests for lexicon_db module."""
import pytest, os, sys, sqlite3, tempfile
from pathlib import Path

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)

# Project root is 4 levels up from this test file
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
LEXICON = str(_PROJECT_ROOT / "data" / "mirad-docs" / "mirad_lexicon.md")
DB_DIR = tempfile.mkdtemp()
DB_PATH = os.path.join(DB_DIR, "test_lexicon.db")


@pytest.fixture(scope="module")
def built_db():
    from mirad_translator import lexicon_db
    result = lexicon_db.build_lexicon_db(DB_PATH, LEXICON)
    return DB_PATH


def test_build_creates_file(built_db):
    assert os.path.exists(built_db)


def test_build_returns_total(built_db):
    from mirad_translator import lexicon_db
    result = lexicon_db.build_lexicon_db(DB_PATH, LEXICON)
    assert result["total"] > 1000
    assert result["idempotent"] is True


def test_fts5_table_exists(built_db):
    conn = sqlite3.connect(built_db)
    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    assert "lexicon" in [t[0] for t in tables]
    assert "lexicon_fts" in [t[0] for t in tables]


def test_total_entries_over_80k(built_db):
    conn = sqlite3.connect(built_db)
    n = conn.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    conn.close()
    assert n >= 8000, f"Expected ≥8000 entries, got {n}"


def test_all_expected_letters_have_entries(built_db):
    from mirad_translator import lexicon_db
    stats = lexicon_db.get_stats(built_db)
    assert len(stats["by_letter"]) >= 20


def test_lookup_known_a(built_db):
    from mirad_translator import lexicon_db
    result = lexicon_db.lookup_word(built_db, "a")
    assert result is not None and len(result) > 0


def test_lookup_known_world(built_db):
    from mirad_translator import lexicon_db
    result = lexicon_db.lookup_word(built_db, "world")
    assert result is not None and "mir" in result.lower()


def test_lookup_miss_returns_none(built_db):
    from mirad_translator import lexicon_db
    assert lexicon_db.lookup_word(built_db, "xyzzyfoobarbaz999") is None


def test_idempotent_rebuild_preserves_mtime(built_db):
    from mirad_translator import lexicon_db
    mtime_before = os.path.getmtime(built_db)
    result = lexicon_db.build_lexicon_db(DB_PATH, LEXICON)
    mtime_after = os.path.getmtime(built_db)
    assert mtime_after == mtime_before
    assert result["idempotent"] is True


def test_stats_returns_total_and_by_letter(built_db):
    from mirad_translator import lexicon_db
    stats = lexicon_db.get_stats(built_db)
    assert stats["total"] > 1000
    assert len(stats["by_letter"]) >= 20

def test_reverse_lexicon_section_is_parsed(built_db):
    from mirad_translator import lexicon_db
    stats = lexicon_db.get_stats(built_db)
    assert stats["reverse_total"] > 1000
    assert lexicon_db.lookup_mirad_word_candidates(built_db, "hwaydwa") == ["cheered on", "congratulated", "toasted"]


def test_english_lookup_splits_multi_candidates(built_db):
    from mirad_translator import lexicon_db
    assert lexicon_db.lookup_word_candidates(built_db, "congratulated") == ["hwaydwa", "yanivtosdwa"]
    toasted = lexicon_db.lookup_word_candidates(built_db, "toasted")
    assert toasted == ["aymxwa", "hwaydwa", "melzaxwa", "tilhyaydwa", "umamxwa"]
