"""Deterministic MiraLingo card content import pipeline.

This module is intentionally pure at the import boundary: callers provide source
paths and may inject word-candidate and lexicon providers for tests, commands, or
API handlers.  Results expose structured counts so failures can be displayed
without stacktrace parsing.
"""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_WORD_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

CardType = str
Card = dict[str, str]
LexiconLookup = Callable[[str], str | None]
WordCandidateProvider = Callable[[], Iterable[str]]


class CardContentImportError(RuntimeError):
    """Structured importer diagnostic for source/provider failures."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        phase: str,
        source_type: str | None = None,
        source_path: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.phase = phase
        self.source_type = source_type
        self.source_path = source_path


class CardContentSourceMissingError(FileNotFoundError):
    """Raised when a required importer source file is missing."""

    def __init__(self, source_path: Path, *, source_type: str, phase: str) -> None:
        super().__init__(f"Missing {source_type} source for {phase}: {source_path}")
        self.code = "source_missing"
        self.phase = phase
        self.source_type = source_type
        self.source_path = str(source_path)


@dataclass(frozen=True)
class CardContentImportResult:
    """Imported cards plus importer diagnostics suitable for CLI/API display."""

    cards: list[Card]
    counts: dict[str, Any]
    sources: dict[str, str | None] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if key == "cards":
            return self.cards
        if key == "counts":
            return self.counts
        if key == "sources":
            return self.sources
        raise KeyError(key)


@dataclass
class _ImportState:
    cards: list[Card]
    counts: dict[str, Any]
    seen_pairs: set[tuple[str, str]]


def import_card_content(
    *,
    phrase_csv_path: str | Path,
    beginner_json_path: str | Path | None = None,
    numbers_json_path: str | Path | None = None,
    word_candidates: Iterable[str] | None = None,
    word_candidate_provider: WordCandidateProvider | None = None,
    lexicon_lookup: LexiconLookup | None = None,
    word_limit: int = 500,
) -> CardContentImportResult:
    """Import phrase and word cards from deterministic local providers.

    Beginner module pairs are imported first when ``beginner_json_path`` is
    provided.  They are one-to-one English/Mirad pairs annotated with
    ``beginner_order`` so the scheduler can exhaust their direction-specific
    cards before falling back to the stochastic unseen pool.  Number module pairs
    are annotated with ``numbers_order`` so the scheduler can introduce them at a
    controlled rate after beginner cards are exhausted.

    Phrase rows come from a CSV with ``english`` and ``mirad`` columns.  A phrase
    card is imported only when English has at least two word tokens and Mirad is
    non-empty.  Word cards are imported in provider order, looked up through the
    supplied or default lexicon provider, and bounded by ``word_limit``.
    Duplicate English/Mirad pairs are suppressed across all sources.
    """

    phrase_path = Path(phrase_csv_path)
    beginner_path = Path(beginner_json_path) if beginner_json_path is not None else None
    numbers_path = Path(numbers_json_path) if numbers_json_path is not None else None
    counts = _new_counts()
    state = _ImportState(cards=[], counts=counts, seen_pairs=set())

    if beginner_path is not None:
        _import_ordered_module(beginner_path, state, module_name="beginner", order_field="beginner_order")
    if numbers_path is not None:
        _import_ordered_module(numbers_path, state, module_name="numbers", order_field="numbers_order")
    _import_phrases(phrase_path, state)

    candidates, word_candidate_source = _resolve_word_candidates(
        word_candidates=word_candidates,
        word_candidate_provider=word_candidate_provider,
        word_limit=word_limit,
    )
    lookup = lexicon_lookup or _default_lexicon_lookup
    _import_words(candidates, lookup, state)

    return CardContentImportResult(
        cards=state.cards,
        counts=counts,
        sources={
            "beginner_json": str(beginner_path) if beginner_path is not None else None,
            "numbers_json": str(numbers_path) if numbers_path is not None else None,
            "phrase_csv": str(phrase_path),
            "word_candidates": word_candidate_source,
        },
    )


def _new_counts() -> dict[str, Any]:
    return {
        "beginner": {
            "imported": 0,
            "skipped": {
                "blank_english": 0,
                "blank_mirad": 0,
                "malformed_item": 0,
            },
            "duplicate": 0,
            "source_error": 0,
        },
        "numbers": {
            "imported": 0,
            "skipped": {
                "blank_english": 0,
                "blank_mirad": 0,
                "malformed_item": 0,
            },
            "duplicate": 0,
            "source_error": 0,
        },
        "phrase": {
            "imported": 0,
            "skipped": {
                "blank_english": 0,
                "blank_mirad": 0,
                "malformed_row": 0,
                "one_word_english": 0,
            },
            "missed": {},
            "duplicate": 0,
            "source_error": 0,
        },
        "word": {
            "imported": 0,
            "skipped": {},
            "missed": {"lexicon_miss": 0},
            "duplicate": 0,
            "source_error": 0,
        },
    }


def _import_ordered_module(module_path: Path, state: _ImportState, *, module_name: str, order_field: str) -> None:
    if not module_path.exists():
        state.counts[module_name]["source_error"] += 1
        raise CardContentSourceMissingError(
            module_path,
            source_type=f"{module_name}_json",
            phase=f"{module_name}_import",
        )

    try:
        raw = json.loads(module_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        state.counts[module_name]["source_error"] += 1
        raise CardContentImportError(
            f"Malformed {module_name} JSON during {module_name}_import: {module_path}: {exc}",
            code="source_error",
            phase=f"{module_name}_import",
            source_type=f"{module_name}_json",
            source_path=str(module_path),
        ) from exc

    pairs = raw.get("pairs") if isinstance(raw, dict) else raw
    if not isinstance(pairs, list):
        state.counts[module_name]["source_error"] += 1
        raise CardContentImportError(
            f"Malformed {module_name} JSON during {module_name}_import: expected a list or object with pairs: {module_path}",
            code="source_error",
            phase=f"{module_name}_import",
            source_type=f"{module_name}_json",
            source_path=str(module_path),
        )

    for order, item in enumerate(pairs):
        if not isinstance(item, dict):
            state.counts[module_name]["skipped"]["malformed_item"] += 1
            continue
        english = str(item.get("english") or "").strip()
        mirad = str(item.get("mirad") or "").strip()
        if not english:
            state.counts[module_name]["skipped"]["blank_english"] += 1
            continue
        if not mirad:
            state.counts[module_name]["skipped"]["blank_mirad"] += 1
            continue
        card_type = "phrase" if any(ch.isspace() for ch in english) else "word"
        english_variants = _english_prompt_variants(english) if card_type == "word" else [english]
        accepted_english = ", ".join(english_variants)
        for variant_index, english_variant in enumerate(english_variants):
            metadata: dict[str, int | str | bool] = {order_field: order}
            if variant_index > 0:
                metadata["english_to_mirad_only"] = True
            added = _add_card(
                state,
                card_type,
                english_variant,
                mirad,
                follow_up_english=accepted_english if len(english_variants) > 1 and variant_index == 0 else None,
                order_metadata=metadata,
            )
            if added:
                state.counts[module_name]["imported"] += 1
            else:
                state.counts[module_name]["duplicate"] += 1


def _english_prompt_variants(english: str) -> list[str]:
    variants = [part.strip() for part in english.split(",") if part.strip()]
    return variants or [english]


def _import_phrases(phrase_path: Path, state: _ImportState) -> None:
    if not phrase_path.exists():
        state.counts["phrase"]["source_error"] += 1
        raise CardContentSourceMissingError(
            phrase_path,
            source_type="phrase_csv",
            phase="phrase_import",
        )

    try:
        with phrase_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row.get(None):
                    state.counts["phrase"]["skipped"]["malformed_row"] += 1
                    continue
                english = (row.get("english") or "").strip()
                mirad = (row.get("mirad") or "").strip()
                if not english:
                    state.counts["phrase"]["skipped"]["blank_english"] += 1
                    continue
                if not mirad:
                    state.counts["phrase"]["skipped"]["blank_mirad"] += 1
                    continue
                if len(_WORD_TOKEN_RE.findall(english)) < 2:
                    state.counts["phrase"]["skipped"]["one_word_english"] += 1
                    continue
                _add_card(state, "phrase", english, mirad)
    except CardContentSourceMissingError:
        raise
    except csv.Error as exc:
        state.counts["phrase"]["source_error"] += 1
        raise CardContentImportError(
            f"Malformed phrase CSV during phrase_import: {phrase_path}: {exc}",
            code="source_error",
            phase="phrase_import",
            source_type="phrase_csv",
            source_path=str(phrase_path),
        ) from exc


def _resolve_word_candidates(
    *,
    word_candidates: Iterable[str] | None,
    word_candidate_provider: WordCandidateProvider | None,
    word_limit: int,
) -> tuple[list[str], str]:
    if word_limit < 0:
        raise ValueError("word_limit must be non-negative")
    try:
        if word_candidates is not None:
            candidates = word_candidates
            source = "injected"
        elif word_candidate_provider is not None:
            candidates = word_candidate_provider()
            source = "injected"
        else:
            candidates = _default_word_candidates(word_limit)
            source = "wordfreq:en"
        return list(candidates)[:word_limit], source
    except CardContentImportError:
        raise
    except Exception as exc:  # pragma: no cover - defensive provider wrapper
        raise CardContentImportError(
            f"Word candidate provider failed during word_candidates: {type(exc).__name__}: {exc}",
            code="provider_error",
            phase="word_candidates",
            source_type="word_candidates",
        ) from exc


def _import_words(candidates: Iterable[str], lookup: LexiconLookup, state: _ImportState) -> None:
    for candidate in candidates:
        english = str(candidate).strip()
        if not english:
            continue
        try:
            mirad = lookup(english)
        except Exception as exc:  # pragma: no cover - defensive provider wrapper
            state.counts["word"]["source_error"] += 1
            raise CardContentImportError(
                f"Lexicon lookup failed during word_lookup for {english!r}: {type(exc).__name__}: {exc}",
                code="provider_error",
                phase="word_lookup",
                source_type="lexicon",
            ) from exc
        if not mirad:
            state.counts["word"]["missed"]["lexicon_miss"] += 1
            continue
        _add_word_cards(state, english, mirad.strip())


def _add_word_cards(state: _ImportState, english: str, mirad: str) -> None:
    english_terms = _split_translation_terms(english)
    mirad_terms = _split_translation_terms(mirad)
    if not english_terms or not mirad_terms:
        state.counts["word"]["missed"]["lexicon_miss"] += 1
        return

    follow_up_english = ", ".join(english_terms)
    follow_up_mirad = ", ".join(mirad_terms)
    for english_term in english_terms:
        for mirad_term in mirad_terms:
            _add_card(
                state,
                "word",
                english_term,
                mirad_term,
                follow_up_english=follow_up_english,
                follow_up_mirad=follow_up_mirad,
            )


def _split_translation_terms(value: str) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for part in str(value).split(","):
        term = part.strip()
        normalized = _normalize_text(term)
        if term and normalized not in seen:
            terms.append(term)
            seen.add(normalized)
    return terms


def _add_card(
    state: _ImportState,
    card_type: CardType,
    english: str,
    mirad: str,
    *,
    follow_up_english: str | None = None,
    follow_up_mirad: str | None = None,
    order_metadata: dict[str, int | str | bool] | None = None,
) -> bool:
    key = (_normalize_text(english), _normalize_text(mirad))
    if key in state.seen_pairs:
        state.counts[card_type]["duplicate"] += 1
        return False
    state.seen_pairs.add(key)
    card = {"type": card_type, "english": english, "mirad": mirad}
    if card_type == "word" and (
        (follow_up_mirad and follow_up_mirad != mirad)
        or (follow_up_english and follow_up_english != english)
    ):
        card["id"] = f"word:{_id_slug(english)}-{_id_slug(mirad)}"
    if follow_up_english and follow_up_english != english:
        card["follow_up_english"] = follow_up_english
    if follow_up_mirad and follow_up_mirad != mirad:
        card["follow_up_mirad"] = follow_up_mirad
    if order_metadata:
        for key, value in order_metadata.items():
            card[key] = str(value) if key.endswith("_order") else value
    state.cards.append(card)
    state.counts[card_type]["imported"] += 1
    return True


def _id_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", _normalize_text(value)).strip("-")
    return slug or "untitled"


def _normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _default_lexicon_lookup(english: str) -> str | None:
    try:
        from mirad_translator.lexicon_db import lookup_word
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise CardContentImportError(
            f"Default lexicon provider unavailable: {exc}",
            code="provider_unavailable",
            phase="word_lookup",
            source_type="lexicon",
        ) from exc
    return lookup_word(english_word=english)


def _default_word_candidates(word_limit: int) -> list[str]:
    """Return ranked common-English word candidates from ``wordfreq``.

    Import ``wordfreq`` at call time so deterministic tests can monkeypatch the
    provider and so API/CLI failures surface as structured importer diagnostics
    instead of silently falling back to placeholder content.
    """

    try:
        from wordfreq import top_n_list
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - environment dependent
        raise CardContentImportError(
            f"Default word candidate provider unavailable: {exc}",
            code="provider_unavailable",
            phase="word_candidates",
            source_type="wordfreq",
        ) from exc

    if not callable(top_n_list):
        raise CardContentImportError(
            "Default word candidate provider unavailable: wordfreq.top_n_list is not callable",
            code="provider_unavailable",
            phase="word_candidates",
            source_type="wordfreq",
        )

    return list(top_n_list("en", word_limit))


__all__ = [
    "Card",
    "CardContentImportError",
    "CardContentImportResult",
    "CardContentSourceMissingError",
    "LexiconLookup",
    "WordCandidateProvider",
    "import_card_content",
]
