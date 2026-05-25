from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable
import re


Direction = str
ExampleLike = dict[str, Any]


@dataclass(frozen=True)
class RetrievalStrategyConfig:
    max_lexicon_pairs: int = 12
    max_grammar_rules: int = 4
    max_few_shot_examples: int = 3
    semantic_top_k_per_word: int = 2
    semantic_max_total_pairs: int = 12
    semantic_min_similarity: float = 0.5
    include_exact_semantic_matches: bool = True


@dataclass(frozen=True)
class RetrievalWarning:
    phase: str
    message: str


@dataclass(frozen=True)
class LexiconPair:
    source: str
    target: str
    match_type: str


@dataclass(frozen=True)
class GrammarRuleMatch:
    rule_id: str
    passage: str
    source_section: str = "grammar"


@dataclass(frozen=True)
class FewShotExampleRef:
    id: str
    direction: str
    source_text: str
    expected_text: str
    taxonomy_focus: list[str] = field(default_factory=list)
    score: int = 0


@dataclass(frozen=True)
class ExampleRetrievalResult:
    example_id: str
    direction: str
    normalized_search_terms: list[str]
    lexicon_pairs: list[LexiconPair]
    grammar_rules: list[GrammarRuleMatch]
    few_shot_examples: list[FewShotExampleRef]
    warnings: list[RetrievalWarning]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def build_retrieval_payload(
    example: ExampleLike,
    *,
    config: RetrievalStrategyConfig | None = None,
    comparison_examples: Iterable[ExampleLike] | None = None,
    semantic_lookup_multi_fn: Callable[..., dict[str, str]] | None = None,
    exact_lookup_fn: Callable[..., str | None] | None = None,
    reverse_lookup_fn: Callable[..., str | None] | None = None,
    retrieve_all_fn: Callable[..., dict[str, list[dict[str, Any]]]] | None = None,
) -> dict[str, Any]:
    """Build direction-aware retrieval inputs for one S01 dev-set example.

    This function is intentionally import-safe: provider imports are resolved lazily
    only when a caller does not inject a test double.
    """
    resolved_config = config or RetrievalStrategyConfig()
    warnings: list[RetrievalWarning] = []

    direction = str(example.get("direction") or "").strip()
    if direction not in {"en_to_mir", "mir_to_en"}:
        raise ValueError(f"Unsupported direction: {direction!r}")

    source_text = str(example.get("source_text") or "")
    normalized_terms = _build_search_terms(example)

    lexicon_pairs = (
        _lexicon_pairs_en_to_mir(
            source_text,
            config=resolved_config,
            warnings=warnings,
            semantic_lookup_multi_fn=semantic_lookup_multi_fn,
            exact_lookup_fn=exact_lookup_fn,
        )
        if direction == "en_to_mir"
        else _lexicon_pairs_mir_to_en(
            source_text,
            config=resolved_config,
            reverse_lookup_fn=reverse_lookup_fn,
            warnings=warnings,
        )
    )

    grammar_rules = _retrieve_grammar_rules(
        example,
        search_terms=normalized_terms,
        config=resolved_config,
        retrieve_all_fn=retrieve_all_fn,
        warnings=warnings,
    )

    few_shot_examples = _select_few_shot_examples(
        example,
        comparison_examples=comparison_examples,
        max_examples=resolved_config.max_few_shot_examples,
    )

    result = ExampleRetrievalResult(
        example_id=str(example.get("id") or ""),
        direction=direction,
        normalized_search_terms=normalized_terms,
        lexicon_pairs=lexicon_pairs,
        grammar_rules=grammar_rules,
        few_shot_examples=few_shot_examples,
        warnings=warnings,
    )
    return result.to_dict()


def _build_search_terms(example: ExampleLike) -> list[str]:
    seen: set[str] = set()
    terms: list[str] = []

    def add(value: str) -> None:
        item = value.strip().lower()
        if item and item not in seen:
            seen.add(item)
            terms.append(item)

    for tag in example.get("taxonomy_focus") or []:
        if isinstance(tag, str):
            add(tag.replace("_", "-").replace(" ", "-"))

    for token in _WORD_RE.findall(str(example.get("source_text") or "")):
        if len(token) > 2:
            add(token)

    if not terms:
        add(str(example.get("direction") or ""))

    return terms


def _lexicon_pairs_en_to_mir(
    source_text: str,
    *,
    config: RetrievalStrategyConfig,
    warnings: list[RetrievalWarning],
    semantic_lookup_multi_fn: Callable[..., dict[str, str]] | None,
    exact_lookup_fn: Callable[..., str | None] | None,
) -> list[LexiconPair]:
    semantic_lookup_multi_fn = semantic_lookup_multi_fn or _default_semantic_lookup_multi
    exact_lookup_fn = exact_lookup_fn or _default_exact_lookup

    pairs: list[LexiconPair] = []
    seen: set[tuple[str, str]] = set()

    try:
        semantic_pairs = semantic_lookup_multi_fn(
            source_text,
            top_k_per_word=config.semantic_top_k_per_word,
            max_total_pairs=config.semantic_max_total_pairs,
            min_similarity=config.semantic_min_similarity,
            include_exact=config.include_exact_semantic_matches,
        )
        for source, target in (semantic_pairs or {}).items():
            key = (str(source).lower(), str(target))
            if key not in seen:
                seen.add(key)
                pairs.append(LexiconPair(source=str(source), target=str(target), match_type="semantic"))
    except Exception as exc:  # dependency/index failures must not escape
        warnings.append(RetrievalWarning(phase="lexicon_semantic", message=str(exc)))

    if not pairs:
        for token in _tokenize(source_text):
            target = exact_lookup_fn(english_word=token)
            if not target:
                continue
            key = (token.lower(), str(target))
            if key not in seen:
                seen.add(key)
                pairs.append(LexiconPair(source=token.lower(), target=str(target), match_type="exact"))

    return pairs[: config.max_lexicon_pairs]


def _lexicon_pairs_mir_to_en(
    source_text: str,
    *,
    config: RetrievalStrategyConfig,
    reverse_lookup_fn: Callable[..., str | None],
    warnings: list[RetrievalWarning],
) -> list[LexiconPair]:
    reverse_lookup_fn = reverse_lookup_fn or _default_reverse_lookup
    pairs: list[LexiconPair] = []
    seen: set[tuple[str, str]] = set()

    for token in _tokenize(source_text, lowercase=False):
        try:
            target = reverse_lookup_fn(mirad_word=token)
        except Exception as exc:
            warnings.append(RetrievalWarning(phase="lexicon_reverse", message=str(exc)))
            continue
        if not target:
            continue
        key = (token, str(target))
        if key not in seen:
            seen.add(key)
            pairs.append(LexiconPair(source=token, target=str(target), match_type="reverse_exact"))

    return pairs[: config.max_lexicon_pairs]


def _retrieve_grammar_rules(
    example: ExampleLike,
    *,
    search_terms: list[str],
    config: RetrievalStrategyConfig,
    retrieve_all_fn: Callable[..., dict[str, list[dict[str, Any]]]] | None,
    warnings: list[RetrievalWarning],
) -> list[GrammarRuleMatch]:
    retrieve_all_fn = retrieve_all_fn or _default_retrieve_all
    query = ", ".join(search_terms[:6]) or str(example.get("source_text") or "")
    try:
        result = retrieve_all_fn(query, top_k=config.max_grammar_rules)
    except Exception as exc:
        warnings.append(RetrievalWarning(phase="grammar_retrieval", message=str(exc)))
        return []

    matches: list[GrammarRuleMatch] = []
    seen_rule_ids: set[str] = set()
    seen_passages: set[str] = set()

    for item in (result or {}).get("grammar", []):
        rule = item.get("rule") or item
        rule_id = str(rule.get("id") or item.get("metadata", {}).get("rule_id") or "").strip()
        description = str(rule.get("description") or item.get("text") or "").strip()
        if not description:
            continue
        if rule_id and rule_id in seen_rule_ids:
            continue
        if description in seen_passages:
            continue
        seen_passages.add(description)
        if rule_id:
            seen_rule_ids.add(rule_id)
        matches.append(
            GrammarRuleMatch(
                rule_id=rule_id,
                passage=description,
                source_section=str(item.get("metadata", {}).get("source_section") or "grammar"),
            )
        )
        if len(matches) >= config.max_grammar_rules:
            break

    return matches


def _select_few_shot_examples(
    example: ExampleLike,
    *,
    comparison_examples: Iterable[ExampleLike] | None,
    max_examples: int,
) -> list[FewShotExampleRef]:
    if not comparison_examples or max_examples <= 0:
        return []

    direction = example.get("direction")
    example_id = example.get("id")
    taxonomy = set(str(v) for v in (example.get("taxonomy_focus") or []))
    source_terms = set(_build_search_terms(example))

    ranked: list[tuple[int, str, ExampleLike]] = []
    for candidate in comparison_examples:
        if candidate.get("id") == example_id:
            continue
        if candidate.get("direction") != direction:
            continue
        candidate_taxonomy = set(str(v) for v in (candidate.get("taxonomy_focus") or []))
        candidate_terms = set(_build_search_terms(candidate))
        score = len(taxonomy & candidate_taxonomy) * 10 + len(source_terms & candidate_terms)
        ranked.append((score, str(candidate.get("id") or ""), candidate))

    ranked.sort(key=lambda item: (-item[0], item[1]))

    refs: list[FewShotExampleRef] = []
    for score, _, candidate in ranked[:max_examples]:
        refs.append(
            FewShotExampleRef(
                id=str(candidate.get("id") or ""),
                direction=str(candidate.get("direction") or ""),
                source_text=str(candidate.get("source_text") or ""),
                expected_text=str(candidate.get("expected_text") or ""),
                taxonomy_focus=[str(v) for v in (candidate.get("taxonomy_focus") or [])],
                score=score,
            )
        )
    return refs


def _tokenize(text: str, *, lowercase: bool = True) -> list[str]:
    tokens = _WORD_RE.findall(text or "")
    normalized: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        item = token.lower() if lowercase else token
        if item not in seen:
            seen.add(item)
            normalized.append(item)
    return normalized


def _default_semantic_lookup_multi(*args: Any, **kwargs: Any) -> dict[str, str]:
    from mirad_translator.semantic_lexicon import semantic_lookup_multi

    return semantic_lookup_multi(*args, **kwargs)


def _default_exact_lookup(*, english_word: str) -> str | None:
    from mirad_translator.lexicon_db import lookup_word

    return lookup_word(english_word=english_word)


def _default_reverse_lookup(*, mirad_word: str) -> str | None:
    from mirad_translator.lexicon_db import lookup_mirad_word

    return lookup_mirad_word(mirad_word=mirad_word)


def _default_retrieve_all(query: str, top_k: int) -> dict[str, list[dict[str, Any]]]:
    from mirad_translator.retrieval import retrieve_all

    return retrieve_all(query, top_k=top_k)
