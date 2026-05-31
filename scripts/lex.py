#!/usr/bin/env python3
"""Mirad lexicon lookup CLI.

Provides two lookup modes:
  1. lookup  - exact match in the SQLite lexicon
  2. search  - top-k semantically similar entries via ChromaDB

Usage:
    # Exact match: English → Mirad
    python scripts/lex.py lookup house

    # Exact match: Mirad → English
    python scripts/lex.py lookup tam -r

    # Semantic search: English → Mirad (top 3)
    python scripts/lex.py search big -k 3

    # Semantic search: Mirad → English (top 3)
    python scripts/lex.py search tam -r -k 3

    # Lexicon stats
    python scripts/lex.py stats
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSLATOR_SRC = PROJECT_ROOT / "packages" / "translator" / "src"
if str(TRANSLATOR_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSLATOR_SRC))


def cmd_lookup(word: str, reverse: bool) -> None:
    from mirad_translator.lexicon_db import lookup_word_candidates, lookup_mirad_word_candidates

    direction = "Mirad → English" if reverse else "English → Mirad"
    words = word.strip().split()

    if len(words) == 1:
        candidates = (
            lookup_mirad_word_candidates(mirad_word=words[0])
            if reverse
            else lookup_word_candidates(english_word=words[0].lower())
        )
        print(f"[{direction}] '{words[0]}'")
        if candidates:
            for i, c in enumerate(candidates, 1):
                print(f"  {i}. {c}")
        else:
            print("  (no exact match found)")
    else:
        # Multi-word: word-by-word, return first candidate for each in order
        if reverse:
            def first_candidate(w):
                c = lookup_mirad_word_candidates(mirad_word=w)
                return (c[0], c) if c else (f"[{w}?]", c)
            results = [first_candidate(w) for w in words]
            print(f"[{direction}] '{' '.join(words)}'")
            mirad_parts = [r[0] for r in results]
            print(f"  → {' '.join(mirad_parts)}")
            for w, (first, all_cands) in zip(words, results):
                tag = "" if all_cands else " [no match]"
                if all_cands and len(all_cands) > 1:
                    print(f"    {w} → {first} (also: {', '.join(all_cands[1:4])}){tag}")
                else:
                    print(f"    {w} → {first}{tag}")
        else:
            def first_candidate(w):
                c = lookup_word_candidates(english_word=w.lower())
                return (c[0], c) if c else (f"[{w.lower()}?]", c)
            results = [first_candidate(w) for w in words]
            print(f"[{direction}] '{' '.join(words)}'")
            mirad_parts = [r[0] for r in results]
            print(f"  → {' '.join(mirad_parts)}")
            for w, (first, all_cands) in zip(words, results):
                tag = "" if all_cands else " [no match]"
                if all_cands and len(all_cands) > 1:
                    print(f"    {w.lower()} → {first} (also: {', '.join(all_cands[1:4])}){tag}")
                else:
                    print(f"    {w.lower()} → {first}{tag}")


def cmd_search(word: str, reverse: bool, top_k: int, min_similarity: float) -> None:
    from mirad_translator.semantic_lexicon import semantic_lookup, semantic_lookup_mirad

    direction = "Mirad → English" if reverse else "English → Mirad"
    print(f"[{direction}] semantic top-{top_k} for '{word.strip()}' (min_sim={min_similarity})")

    try:
        if reverse:
            hits = semantic_lookup_mirad(
                mirad_word=word.strip(),
                top_k=top_k,
                min_similarity=min_similarity,
                include_exact=True,
            )
            if not hits:
                print("  (no results above threshold)")
                return
            for h in hits:
                exact_tag = " [EXACT]" if h["is_exact"] else ""
                print(f"  {h['mirad']} → {h['english']}  (sim={h['cosine_similarity']:.3f}){exact_tag}")
        else:
            hits = semantic_lookup(
                english_word=word.strip().lower(),
                top_k=top_k,
                min_similarity=min_similarity,
                include_exact=True,
            )
            if not hits:
                print("  (no results above threshold)")
                return
            for h in hits:
                exact_tag = " [EXACT]" if h["is_exact"] else ""
                print(f"  {h['english']} → {h['mirad']}  (sim={h['cosine_similarity']:.3f}){exact_tag}")
    except Exception as e:
        print(f"  Error: {e}")
        sys.exit(1)


def cmd_stats() -> None:
    from mirad_translator.lexicon_db import get_stats

    stats = get_stats()
    print(f"Lexicon statistics")
    print(f"  English → Mirad entries : {stats['total']:,}")
    print(f"  Mirad  → English entries : {stats['reverse_total']:,}")
    print(f"  English alphabet coverage : {len(stats['by_letter'])} letters")
    print(f"  Mirad  alphabet coverage  : {len(stats['reverse_by_letter'])} letters")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mirad lexicon lookup: exact match and semantic search.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "command",
        choices=["lookup", "search", "stats"],
        help="lookup=exact match, search=semantic top-k, stats=show counts",
    )
    parser.add_argument("word", nargs="?", help="Word to look up")
    parser.add_argument(
        "-r", "--reverse",
        action="store_true",
        help="Reverse direction: Mirad → English (default: English → Mirad)",
    )
    parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=3,
        metavar="N",
        help="Number of results for 'search' command (default: 3)",
    )
    parser.add_argument(
        "-m", "--min-sim",
        type=float,
        default=0.3,
        metavar="FLOAT",
        help="Minimum cosine similarity for 'search' (default: 0.3)",
    )

    args = parser.parse_args()

    if args.command == "stats":
        cmd_stats()
        return

    if not args.word:
        parser.error(f"'{args.command}' requires a word argument")
        return

    if args.command == "lookup":
        cmd_lookup(args.word, args.reverse)
    elif args.command == "search":
        cmd_search(args.word, args.reverse, args.top_k, args.min_sim)


if __name__ == "__main__":
    main()