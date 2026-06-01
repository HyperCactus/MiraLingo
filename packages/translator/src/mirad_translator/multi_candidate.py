"""
Multi-candidate translation with judge-based selection (no back-translation).

Architecture:
  1. Generate 2 translation candidates at temperatures [0.1, 0.7].
     Uses TranslatorModule (num_context_passages=3, top_k_per_word=0) internally.
     Retrieval is deterministic; only the generation temperature varies.
  2. CandidateJudge (dspy.Module) scores each candidate directly on Mirad grammar
     compliance — no back-translation. Scores 5 dimensions: grammar,
     morphology, vocabulary, English bleed (lower = more English contamination),
     and structural completeness. Highest total_score wins.

All modules are dspy.Module subclasses and can be traced by DSPy optimizers.

Usage:
    from mirad_translator.multi_candidate import MultiCandidateTranslator

    translator = MultiCandidateTranslator(
        num_candidates=2,
        temperatures=[0.1, 0.7],
    )
    result = translator(english_text="the cat sat on the mat")
    print(result.mirad_text)    # best candidate
    print(result.total_score)   # judge total score (0-100)
    print(result.winner_index)  # index of winning candidate (0-based)
"""

from __future__ import annotations

import json, re, sys
from pathlib import Path
from typing import Optional

import dspy

_PROJECT_ROOT = Path(__file__).resolve().parents[4]

# ---------------------------------------------------------------------------
# Candidate Judge Signature
# ---------------------------------------------------------------------------

# Mirad grammar rules embedded in the judge prompt (same rules as TranslatorModule).
_JUDGE_GRAMMAR_RULES = """
Mirad grammar reference for judging En→Mir translations:

Verbs: infinitive ends -er, stem = infinitive minus -er.
  Endings: -e present, -a past, -o future, -u hypothetical/imperative/subjunctive.
  se=am/is/are, sa=was/were, so=will be, su=would be.
  Passive: -w- before tense vowel: xwe=is done, xwa=was done.
  Aspects: progressive -ey-, perfect -ay-, imminent -oy-, potential -uy-.
  Passive aspects: xewe=is being done, xawe=has been done.
  Progressive must preserve ey before tense: peye, peya, tujeye, Mamileye.
  Never truncate -eye to -ie.

Pronouns: at=I, et=you, it=he/she, wit=he, iyt=she, is=it.
  yat=we, yet=you(pl), yit=they(animate), yis=they(inanimate).
  Possessive: -a suffix: ata=my, eta=your, ita=his/her, yata=our, yita=their.

Negation: voy=not (before verb). Von=negative imperative.
Questions: Duven = yes/no question. duhot/duhos/duhom/duhoj/duhoyen/duhosav = who/what/where/when/how/why.

Prepositions: bi=of/from/possessive, be=at/in/on, bu=to/into.
Possession: X bi Y = Y's X.
Comparisons: ga=more, ge=as, go=less, gwa=most, gwo=least; link with vyel (NEVER ge).
  ga fia vyel et = better than you.
  be→bi correction: ha tam bi Maria = Mary's house.
  ha = the (definite). No indefinite article; "tam" = a house / the house.

Clauses: van=that/so that, ven=if/whether, von=lest.
  Never omit van in "that" clauses: At ta van et upo. = I knew you would come.
  ho = relative who/which/that.

Adjectives end -a; adverbs end -ay. Keep adverbial forms exact.
Word order: SVO default. Object after verb. Questions begin with question words.
Articles: ha=the. Adjectives/determiners do not agree; only noun pluralizes with -i.
""".strip()


# ---------------------------------------------------------------------------
# LM configuration helpers
# ---------------------------------------------------------------------------

def _load_env():
    """Load .env from project root if not already loaded."""
    import os
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).resolve().parents[2] / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=False)


def _get_api_key() -> str:
    _load_env()
    import os
    key = os.environ.get("DEEPINFRA_API_KEY", "")
    if not key:
        raise ValueError("DEEPINFRA_API_KEY not set. Add it to .env or environment.")
    return key


def _get_api_base() -> str:
    _load_env()
    import os
    return os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")


def _get_teacher_model() -> str:
    _load_env()
    import os
    return os.environ.get(
        "DEEPINFRA_TRANSLATION_MODEL",
        "deepseek-ai/DeepSeek-V4-Flash",
    )


def _make_lm(temperature: float) -> dspy.LM:
    """Build a DeepInfra LM at the given temperature."""
    return dspy.LM(
        model=_get_teacher_model(),
        temperature=temperature,
        cache=False,
        api_key=_get_api_key(),
        api_base=_get_api_base(),
    )


# ---------------------------------------------------------------------------
# Joint candidate verifier + deterministic reranker
# ---------------------------------------------------------------------------

_EN_TO_MIR_FAIL_CASES = [
    "semantic_mismatch",
    "missing_negation",
    "wrong_negation",
    "wrong_tense_or_aspect",
    "wrong_conjunction_particle",
    "dropped_clause_or_argument",
    "missing_required_copula_or_article",
    "invented_or_unrelated_wording",
]

_MIR_TO_EN_FAIL_CASES = [
    "semantic_mismatch",
    "missing_negation",
    "wrong_negation",
    "wrong_tense_or_aspect",
    "dropped_clause_or_argument",
    "subject_object_swap",
    "hallucinated_information",
    "direction_leakage",
]


class CandidateSetVerifierSignature(dspy.Signature):
    """Verify and rank English→Mirad candidates together.

    You see whole candidate set at once. Do NOT judge candidates independently.
    Compare them against each other and source sentence.

    Priority order for ranking:
    1. semantic fidelity
    2. morphology / tense / negation correctness
    3. grammar / style

    Hard-fail cases for English→Mirad:
    - semantic_mismatch: meaning differs materially from source
    - missing_negation or wrong_negation
    - wrong_tense_or_aspect
    - wrong_conjunction_particle (for example but -> oy, not ay)
    - dropped_clause_or_argument
    - missing_required_copula_or_article when source clearly requires it
    - invented_or_unrelated_wording

    Output STRICT JSON only with this schema:
    {
      "winner_id": "cand-2",
      "ranking": ["cand-2", "cand-1", "cand-3"],
      "winner_explanation": "short sentence",
      "candidates": [
        {
          "candidate_id": "cand-1",
          "semantic_fidelity": 0.0,
          "morphology_tense_negation": 0.0,
          "grammar_style": 0.0,
          "hard_failures": ["wrong_negation"],
          "soft_errors": ["awkward_style"],
          "justification": "short sentence"
        }
      ]
    }

    Scores must be between 0 and 1. Empty arrays allowed. No markdown fences.
    """
    original_english = dspy.InputField(desc="Original English source text")
    candidate_payload_json = dspy.InputField(desc="JSON array of candidate_id + candidate_mirad text")
    verifier_json = dspy.OutputField(desc="Strict JSON object matching schema")


class MiradToEnglishCandidateSetVerifierSignature(dspy.Signature):
    """Verify and rank Mirad→English candidates together.

    Compare all candidates jointly against source. Do NOT use back-translation.

    Priority order for ranking:
    1. semantic fidelity
    2. morphology / tense / negation correctness
    3. grammar / style

    Hard-fail cases for Mirad→English:
    - semantic_mismatch
    - missing_negation or wrong_negation
    - wrong_tense_or_aspect
    - dropped_clause_or_argument
    - subject_object_swap
    - hallucinated_information
    - direction_leakage (Mirad patterns leaking into English)

    Output STRICT JSON only with same schema as English→Mirad variant, but
    candidate text is English and fail cases come from Mirad→English list.
    """
    original_mirad = dspy.InputField(desc="Original Mirad source text")
    candidate_payload_json = dspy.InputField(desc="JSON array of candidate_id + candidate_english text")
    verifier_json = dspy.OutputField(desc="Strict JSON object matching schema")


class CandidateSetVerifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self._verify = dspy.ChainOfThought(CandidateSetVerifierSignature)

    def forward(self, *, original_english: str, candidate_payload_json: str) -> dict:
        pred = self._verify(
            original_english=original_english,
            candidate_payload_json=candidate_payload_json,
        )
        return _parse_verifier_payload(getattr(pred, "verifier_json", ""), direction="en_to_mir")


class MiradToEnglishCandidateSetVerifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self._verify = dspy.ChainOfThought(MiradToEnglishCandidateSetVerifierSignature)

    def forward(self, *, original_mirad: str, candidate_payload_json: str) -> dict:
        pred = self._verify(
            original_mirad=original_mirad,
            candidate_payload_json=candidate_payload_json,
        )
        return _parse_verifier_payload(getattr(pred, "verifier_json", ""), direction="mir_to_en")


def _parse_verifier_payload(raw: str, *, direction: str) -> dict:
    allowed_fails = set(_EN_TO_MIR_FAIL_CASES if direction == "en_to_mir" else _MIR_TO_EN_FAIL_CASES)
    text = str(raw or "").strip()
    if "```" in text:
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {"winner_id": None, "ranking": [], "winner_explanation": "Verifier returned no parseable JSON.", "candidates": []}
    try:
        payload = json.loads(text[start:end + 1])
    except Exception:
        return {"winner_id": None, "ranking": [], "winner_explanation": "Verifier JSON parse failed.", "candidates": []}

    candidates = []
    for row in payload.get("candidates", []) or []:
        if not isinstance(row, dict):
            continue
        hard_failures = [
            str(item).strip() for item in (row.get("hard_failures") or [])
            if str(item).strip() in allowed_fails
        ]
        soft_errors = [str(item).strip() for item in (row.get("soft_errors") or []) if str(item).strip()]
        candidates.append({
            "candidate_id": str(row.get("candidate_id", "")).strip(),
            "semantic_fidelity": _clamp01(row.get("semantic_fidelity", 0.0)),
            "morphology_tense_negation": _clamp01(row.get("morphology_tense_negation", 0.0)),
            "grammar_style": _clamp01(row.get("grammar_style", 0.0)),
            "hard_failures": hard_failures,
            "soft_errors": soft_errors,
            "justification": str(row.get("justification", "")).strip(),
        })

    return {
        "winner_id": str(payload.get("winner_id", "")).strip() or None,
        "ranking": [str(x).strip() for x in (payload.get("ranking") or []) if str(x).strip()],
        "winner_explanation": str(payload.get("winner_explanation", "")).strip(),
        "candidates": candidates,
    }


def _clamp01(value) -> float:
    try:
        x = float(value)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))


def _normalize_simple(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _contains_any(text: str, needles: list[str]) -> bool:
    hay = _normalize_simple(text)
    return any(n in hay for n in needles)


def _rule_precheck_en_to_mir(original_english: str, candidate_mirad: str) -> dict:
    text_en = _normalize_simple(original_english)
    text_mir = _normalize_simple(candidate_mirad)
    hard_failures: list[str] = []
    soft_errors: list[str] = []
    notes: list[str] = []

    english_has_neg = _contains_any(text_en, [" not ", "n't", " never ", " no "]) or text_en.startswith("not ")
    mirad_has_neg = " voy " in f" {text_mir} " or text_mir.startswith("voy ")
    if english_has_neg and not mirad_has_neg:
        hard_failures.append("missing_negation")
        notes.append("English source is negative but Mirad candidate lacks voy.")

    if " but " in f" {text_en} " and " oy " not in f" {text_mir} ":
        hard_failures.append("wrong_conjunction_particle")
        notes.append("English source contains 'but' but candidate lacks oy.")

    if any(token in text_en.split() for token in ["is", "are", "am", "was", "were"]) and " se " not in f" {text_mir} " and " sa " not in f" {text_mir} ":
        soft_errors.append("possible_missing_copula")
        notes.append("Copular English source but candidate lacks obvious se/sa copula.")

    if re.search(r"\bthe\b", text_en) and " ha " not in f" {text_mir} ":
        soft_errors.append("possible_missing_article")
        notes.append("English source contains 'the' but candidate lacks obvious ha article.")

    if re.search(r"\b(will|going to)\b", text_en) and not re.search(r"\b\w+o\b", text_mir):
        soft_errors.append("possible_future_tense_mismatch")
        notes.append("English source looks future but candidate lacks obvious -o verb ending.")
    if re.search(r"\b(was|were|did|had)\b", text_en) and not re.search(r"\b\w+a\b", text_mir):
        soft_errors.append("possible_past_tense_mismatch")
        notes.append("English source looks past but candidate lacks obvious -a verb ending.")

    return {"hard_failures": hard_failures, "soft_errors": soft_errors, "notes": notes}


def _rule_precheck_mir_to_en(original_mirad: str, candidate_english: str) -> dict:
    text_mir = _normalize_simple(original_mirad)
    text_en = _normalize_simple(candidate_english)
    hard_failures: list[str] = []
    soft_errors: list[str] = []
    notes: list[str] = []

    mirad_has_neg = " voy " in f" {text_mir} " or text_mir.startswith("voy ")
    english_has_neg = _contains_any(text_en, [" not ", "n't", " never ", " no "]) or text_en.startswith("not ")
    if mirad_has_neg and not english_has_neg:
        hard_failures.append("missing_negation")
        notes.append("Mirad source is negative but English candidate is not.")

    if " ay " in f" {text_mir} " and " but " in f" {text_en} ":
        hard_failures.append("semantic_mismatch")
        notes.append("Candidate maps ay as 'but', likely conjunction confusion.")

    if re.search(r"\b(ha|voy|van|ven|duven)\b", text_en):
        hard_failures.append("direction_leakage")
        notes.append("English candidate leaks Mirad function words.")

    if re.search(r"\b\w+a\b", text_mir) and not re.search(r"\b(was|were|did|had)\b", text_en):
        soft_errors.append("possible_past_tense_mismatch")
        notes.append("Mirad source may be past-tense but English candidate lacks obvious past marking.")
    if re.search(r"\b\w+o\b", text_mir) and not re.search(r"\b(will|going to)\b", text_en):
        soft_errors.append("possible_future_tense_mismatch")
        notes.append("Mirad source may be future-tense but English candidate lacks obvious future marking.")

    return {"hard_failures": hard_failures, "soft_errors": soft_errors, "notes": notes}


def _rerank_verified_candidates(
    candidates: list[dict],
    verifier_payload: dict,
    *,
    direction: str,
    source_text: str,
) -> tuple[int, float, str, list[dict]]:
    by_id = {str(c.get("candidate_id", f"cand-{i}")): c for i, c in enumerate(candidates)}
    verifier_rows = {row.get("candidate_id"): row for row in verifier_payload.get("candidates", []) if row.get("candidate_id")}

    enriched: list[dict] = []
    for i, cand in enumerate(candidates):
        candidate_id = cand.get("candidate_id") or f"cand-{i + 1}"
        row = verifier_rows.get(candidate_id, {})
        semantic = _clamp01(row.get("semantic_fidelity", 0.0))
        morph = _clamp01(row.get("morphology_tense_negation", 0.0))
        grammar = _clamp01(row.get("grammar_style", 0.0))
        llm_hard_failures = list(row.get("hard_failures") or [])
        llm_soft_errors = list(row.get("soft_errors") or [])
        rule_precheck = (
            _rule_precheck_en_to_mir(source_text, cand.get("mirad_text", ""))
            if direction == "en_to_mir"
            else _rule_precheck_mir_to_en(source_text, cand.get("english_text", ""))
        )
        hard_failures = list(dict.fromkeys(rule_precheck["hard_failures"] + llm_hard_failures))
        soft_errors = list(dict.fromkeys(rule_precheck["soft_errors"] + llm_soft_errors))
        weighted = (semantic * 0.6) + (morph * 0.3) + (grammar * 0.1)
        total_score = max(0.0, min(100.0, round(weighted * 100 - len(hard_failures) * 25 - len(soft_errors) * 3, 2)))
        enriched_cand = dict(cand)
        enriched_cand["rule_precheck"] = rule_precheck
        enriched_cand["verifier"] = {
            "semantic_fidelity": semantic,
            "morphology_tense_negation": morph,
            "grammar_style": grammar,
            "hard_failures": hard_failures,
            "soft_errors": soft_errors,
            "weighted_score": round(weighted, 4),
            "justification": str(row.get("justification", "")).strip(),
            "llm_hard_failures": llm_hard_failures,
            "llm_soft_errors": llm_soft_errors,
        }
        enriched_cand["judge"] = {
            "semantic_fidelity": round(semantic * 20, 1),
            "morphology_score": round(morph * 20, 1),
            "grammar_score": round(grammar * 20, 1),
            "total_score": total_score,
            "rationale": str(row.get("justification", "")).strip(),
        }
        enriched.append(enriched_cand)

    ranking_order = [candidate_id for candidate_id in verifier_payload.get("ranking", []) if candidate_id in by_id]
    ranking_index = {candidate_id: idx for idx, candidate_id in enumerate(ranking_order)}

    def sort_key(cand: dict):
        candidate_id = cand["candidate_id"]
        v = cand["verifier"]
        return (
            len(v["hard_failures"]),
            -v["semantic_fidelity"],
            -v["morphology_tense_negation"],
            -v["grammar_style"],
            ranking_index.get(candidate_id, 10_000),
            -cand["judge"]["total_score"],
        )

    ranked = sorted(enriched, key=sort_key)
    winner = ranked[0]
    winner_id = winner["candidate_id"]
    winner_explanation = verifier_payload.get("winner_explanation") or winner["verifier"].get("justification") or "Highest semantic fidelity after hard-constraint reranking."
    winner_score = winner["judge"]["total_score"]

    rank_by_id = {cand["candidate_id"]: idx for idx, cand in enumerate(ranked)}
    for cand in enriched:
        cand["rank"] = rank_by_id[cand["candidate_id"]]
        cand["winner"] = cand["candidate_id"] == winner_id

    return winner["index"], winner_score, winner_explanation, enriched


# ---------------------------------------------------------------------------
# Multi-candidate translator
# ---------------------------------------------------------------------------

class MultiCandidateTranslator(dspy.Module):
    """Generate N translation candidates at different temperatures and pick the best via judge.

    The candidate generation loop is Python-sequential.
    Each candidate uses the same TranslatorModule settings (num_context_passages,
    top_k_per_word) — only the generation temperature varies. Retrieval is
    deterministic and run once per forward pass; the result is reused for all
    candidates.

    The judge module scores each candidate and the highest total_score wins.
    No back-translation is used — the judge scores Mirad grammar compliance
    directly, including an explicit English-bleed dimension to catch candidates
    that look like English with Mirad words.

    Args:
        num_candidates: Number of candidates to generate (default 2).
        temperatures: List of temperatures, one per candidate (default [0.1, 0.7]).
        db_path: Path to lexicon SQLite DB (default: built-in).
        num_context_passages: Grammar retrieval k (default 3, the winning value).
        use_compiled: Load compiled translator program (default False).
        top_k_per_word: Semantic lexicon k (default 0 = disabled).
    """

    def __init__(
        self,
        num_candidates: int = 2,
        temperatures: Optional[list[float]] = None,
        db_path=None,
        num_context_passages: int = 3,
        use_compiled: bool = False,
        top_k_per_word: int = 0,
    ):
        super().__init__()
        self.num_candidates = num_candidates
        self.temperatures = (
            list(temperatures)
            if temperatures is not None
            else [0.1, 0.7]
        )
        self.num_context_passages = num_context_passages
        self._db_path = db_path
        self._use_compiled = use_compiled
        self._top_k_per_word = top_k_per_word

        # Modules (built lazily on first forward to allow dspy.trace-ability)
        self._translator: Optional[dspy.Module] = None
        self._judge = CandidateSetVerifier()

    def _ensure_translator(self):
        if self._translator is not None:
            return
        from mirad_translator.translate import (
            DefaultTranslator,
            load_compiled_translator,
        )
        if self._use_compiled:
            try:
                self._translator = load_compiled_translator(
                    top_k_per_word=self._top_k_per_word,
                )
                # Swap to fresh signature to avoid stale bootstrap demos
                from mirad_translator.translate import EnglishToMiradSignature
                import dspy
                self._translator.generate = dspy.ChainOfThought(EnglishToMiradSignature)
                return
            except FileNotFoundError:
                pass
        self._translator = DefaultTranslator(
            db_path=self._db_path,
            num_context_passages=self.num_context_passages,
            top_k_per_word=self._top_k_per_word,
            use_compiled=False,
            semantic_lexicon=False,
        )

    def _get_lm(self, temperature: float):
        """Prime the global LM for the given temperature.

        Called once before eval loop begins (main thread only).
        Sets dspy.settings.lm for this thread so the translator can be created.
        """
        lm = _make_lm(temperature)
        dspy.settings.configure(lm=lm)
        return lm

    def _generate_candidate(
        self,
        english_text: str,
        temperature: float,
    ) -> str:
        """Generate a single candidate at the given temperature.

        Uses dspy.context to set a fresh LM at the target temperature within
        the block. dspy.context is thread-safe (unlike dspy.settings.configure)
        and allows per-call LM overrides from any thread.
        """
        self._ensure_translator()
        with dspy.context(lm=_make_lm(temperature)):
            pred = self._translator(english_text=english_text)
        return str(getattr(pred, "mirad_text", ""))

    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate with multi-candidate selection.

        Returns a dspy.Prediction with fields:
          mirad_text          — best Mirad translation
          winner_index        — index of winning candidate (0-based)
          total_score         — judge's total score for the winner (0-100)
          candidates          — list of all candidate dicts
          rationale           — judge's rationale for the winner
        """
        self._ensure_translator()

        candidates: list[dict] = []
        for i in range(self.num_candidates):
            temperature = self.temperatures[i % len(self.temperatures)]
            candidate_text = self._generate_candidate(english_text, temperature)
            candidates.append({
                "index": i,
                "candidate_id": f"cand-{i + 1}",
                "temperature": temperature,
                "mirad_text": candidate_text,
            })

        verifier_payload = json.dumps(
            [
                {
                    "candidate_id": cand["candidate_id"],
                    "candidate_mirad": cand["mirad_text"],
                }
                for cand in candidates
            ],
            ensure_ascii=False,
        )
        verifier_result = self._judge(
            original_english=english_text,
            candidate_payload_json=verifier_payload,
        )
        winner_index, winner_score, winner_rationale, ranked_candidates = _rerank_verified_candidates(
            candidates,
            verifier_result,
            direction="en_to_mir",
            source_text=english_text,
        )

        best = next(c for c in ranked_candidates if c["index"] == winner_index)
        return dspy.Prediction(
            mirad_text=best["mirad_text"],
            winner_index=winner_index,
            total_score=winner_score,
            candidates=ranked_candidates,
            rationale=winner_rationale,
        )


# ---------------------------------------------------------------------------
# Mirad→English multi-candidate translator
# ---------------------------------------------------------------------------

class MiradToEnglishMultiCandidateTranslator(dspy.Module):
    """Mirad→English counterpart to MultiCandidateTranslator.

    Generates N translation candidates at different temperatures via
    MiradToEnglishModule and picks the best via MiradToEnglishCandidateJudge.

    Args:
        num_candidates: Number of candidates to generate (default 2).
        temperatures: List of temperatures (default [0.1, 0.7]).
        db_path: Path to lexicon SQLite DB.
        num_context_passages: Grammar retrieval k (default 3).
        top_k_per_word: Semantic lexicon k (default 0 = disabled).
    """

    def __init__(
        self,
        num_candidates: int = 2,
        temperatures: Optional[list[float]] = None,
        db_path=None,
        num_context_passages: int = 3,
        top_k_per_word: int = 0,
    ):
        super().__init__()
        self.num_candidates = num_candidates
        self.temperatures = (
            list(temperatures)
            if temperatures is not None
            else [0.1, 0.7]
        )
        self.num_context_passages = num_context_passages
        self._db_path = db_path
        self._top_k_per_word = top_k_per_word
        self._translator: Optional[dspy.Module] = None
        self._judge = MiradToEnglishCandidateSetVerifier()

    def _ensure_translator(self):
        if self._translator is not None:
            return
        from mirad_translator.translate import (
            DefaultTranslator,
        )
        self._translator = DefaultTranslator(
            db_path=self._db_path,
            num_context_passages=self.num_context_passages,
            top_k_per_word=self._top_k_per_word,
            direction="mir_to_en",
            use_compiled=False,
            semantic_lexicon=False,
        )

    def _generate_candidate(self, mirad_text: str, temperature: float) -> str:
        self._ensure_translator()
        with dspy.context(lm=_make_lm(temperature)):
            pred = self._translator(mirad_text=mirad_text)
        return str(getattr(pred, "english_text", ""))

    def forward(self, mirad_text: str) -> dspy.Prediction:
        self._ensure_translator()

        candidates: list[dict] = []
        for i in range(self.num_candidates):
            temperature = self.temperatures[i % len(self.temperatures)]
            candidate_text = self._generate_candidate(mirad_text, temperature)
            candidates.append({
                "index": i,
                "candidate_id": f"cand-{i + 1}",
                "temperature": temperature,
                "english_text": candidate_text,
            })

        verifier_payload = json.dumps(
            [
                {
                    "candidate_id": cand["candidate_id"],
                    "candidate_english": cand["english_text"],
                }
                for cand in candidates
            ],
            ensure_ascii=False,
        )
        verifier_result = self._judge(
            original_mirad=mirad_text,
            candidate_payload_json=verifier_payload,
        )
        winner_index, winner_score, winner_rationale, ranked_candidates = _rerank_verified_candidates(
            candidates,
            verifier_result,
            direction="mir_to_en",
            source_text=mirad_text,
        )

        best = next(c for c in ranked_candidates if c["index"] == winner_index)
        return dspy.Prediction(
            english_text=best["english_text"],
            mirad_text=best["english_text"],  # mirror field name for eval compat
            winner_index=winner_index,
            total_score=winner_score,
            candidates=ranked_candidates,
            rationale=winner_rationale,
        )


# ---------------------------------------------------------------------------
# CLI evaluation runner
# ---------------------------------------------------------------------------

def run_mc_eval(
    n_samples: int = 100,
    seed: int = 20260526,
    min_english_words: int = 0,
    out_dir: Optional[Path] = None,
    num_candidates: int = 2,
    temperatures: Optional[list[float]] = None,
    parallel: int = 1,
) -> dict:
    """Run MultiCandidateTranslator eval on n_samples from data/eval/train.json.

    Parallel evaluation (parallel > 1) uses ThreadPoolExecutor to run multiple
    samples concurrently. Each thread uses its own LM instance via dspy.context,
    which is thread-safe in DSPy 3.x.

    Args:
        n_samples: Number of samples to evaluate (0 = all).
        seed: Random seed for sampling.
        min_english_words: Minimum English words per sentence.
        out_dir: Output directory (auto-generated if None).
        num_candidates: Number of candidates per sample.
        temperatures: Candidate temperatures.
        parallel: Number of parallel workers.

    Returns:
        Summary dict with metrics, timing, counts.
    """
    import os, random, time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from datetime import datetime

    import yaml
    with open("scripts/eval_config.yaml") as f:
        config = yaml.safe_load(f)

    model_cfg = config.get("model", {})
    lm_model = model_cfg.get("model", "deepseek-ai/DeepSeek-V4-Flash")

    # Load evaluation samples
    data_path = "data/eval/train.json"
    with open(data_path) as f:
        raw = json.load(f)

    # Support both {"pairs": [...]} and flat list formats
    if isinstance(raw, dict) and "pairs" in raw:
        all_data = raw["pairs"]
    elif isinstance(raw, list):
        all_data = raw
    else:
        raise ValueError(f"Unexpected train.json format: {type(raw)}")

    # Normalize to {english, mirad} keys (handles "source/target" or "english/mirad")
    def normalize(d):
        english = d.get("english") or d.get("source") or ""
        mirad = d.get("mirad") or d.get("target") or ""
        return {"english": english, "mirad": mirad, "id": d.get("id", "")}

    filtered = [
        normalize(d) for d in all_data
        if len(d.get("english", "").split()) >= min_english_words
        or len(d.get("source", "").split()) >= min_english_words
    ]
    rng = random.Random(seed)
    rng.shuffle(filtered)
    samples = filtered[:n_samples] if n_samples > 0 else filtered

    if out_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(f"data/eval_results/mc_eval_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.md").write_text("")  # touch
    report_path = out_dir / "report.md"

    # Configure the global LM once before building the translator.
    # Each _generate_candidate call will call _get_lm(temperature) which
    # reconfigures the LM (replacing it with a fresh instance at the target temp).
    # We set temperature=0 so the first invocation doesn't produce noise.
    shared_mc = MultiCandidateTranslator(
        num_candidates=num_candidates,
        temperatures=temperatures,
        num_context_passages=3,
    )
    # Prime dspy.settings.lm so the translator module can be created
    # (DefaultTranslator calls build_lexicon_db which may trigger DSPy module init).
    shared_mc._get_lm(0.0)

    print(f"[mc_eval] Building shared MultiCandidateTranslator (k=3, {num_candidates} candidates, {temperatures})...")
    t0 = time.time()

    def eval_one(sample: dict) -> dict:
        english = sample["english"]
        gold = sample["mirad"]
        pred = shared_mc(english_text=english)
        mirad_pred = pred.mirad_text

        # Scores
        def nmatch(a, b):
            a_n = re.sub(r"[^a-z0-9]", " ", a.lower())
            b_n = re.sub(r"[^a-z0-9]", " ", b.lower())
            a_n = " ".join(a_n.split())
            b_n = " ".join(b_n.split())
            return a_n == b_n

        nm = 1.0 if nmatch(mirad_pred, gold) else 0.0
        em = 1.0 if mirad_pred.strip() == gold.strip() else 0.0

        # Candidate summaries for examples.json
        cand_summaries = []
        for c in pred.candidates:
            j = c.get("judge", {})
            cand_summaries.append({
                "temp": c["temperature"],
                "mirad": c["mirad_text"],
                "total_score": j.get("total_score", 0),
                "grammar": j.get("grammar_score", 0),
                "morphology": j.get("morphology_score", 0),
                "vocab": j.get("vocabulary_score", 0),
                "bleed": j.get("english_bleed_score", 0),
                "complete": j.get("completeness_score", 0),
            })

        return {
            "id": sample.get("id", ""),
            "idx": sample.get("idx", 0),
            "english_text": english,
            "gold": gold,
            "pred": mirad_pred,
            "exact_match": bool(em),
            "normalized_match": bool(nm),
            "winner_index": pred.winner_index,
            "total_score": pred.total_score,
            "rationale": pred.rationale,
            "candidates": cand_summaries,
        }

    if parallel <= 1:
        examples = [eval_one(s) for s in samples]
    else:
        with ThreadPoolExecutor(max_workers=parallel) as ex:
            futures = {ex.submit(eval_one, s): i for i, s in enumerate(samples)}
            examples = [None] * len(samples)
            for future in as_completed(futures):
                i = futures[future]
                examples[i] = future.result()

    elapsed = time.time() - t0

    # Compute metrics
    nm_count = sum(1 for e in examples if e["normalized_match"])
    em_count = sum(1 for e in examples if e["exact_match"])
    n = len(examples)
    nm_rate = nm_count / n if n else 0
    em_rate = em_count / n if n else 0
    avg_score = sum(e["total_score"] for e in examples) / n if n else 0

    summary = {
        "config": {
            "num_candidates": num_candidates,
            "temperatures": temperatures or [0.1, 0.7],
            "num_context_passages": 3,
            "top_k_per_word": 0,
            "parallel": parallel,
        },
        "metrics": {
            "normalized_match": nm_rate,
            "exact_match": em_rate,
            "avg_judge_score": avg_score,
        },
        "counts": {
            "total": n,
            "normalized_match_correct": nm_count,
            "exact_match_correct": em_count,
        },
        "timing": {
            "total_wall_s": round(elapsed, 1),
            "avg_per_sample_s": round(elapsed / n, 2) if n else 0,
        },
    }

    # Write outputs
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))
    (out_dir / "examples.json").write_text(json.dumps(examples, indent=2, ensure_ascii=False))

    # Build report
    rows = []
    for e in examples:
        nm = "✓" if e["normalized_match"] else "✗"
        score = e["total_score"]
        winner_temp = "?"
        if e["candidates"]:
            winner_temp = e["candidates"][e["winner_index"]]["temp"]
        rows.append(f"| {e['idx']:3d} | {nm} | {score:5.1f} | T={winner_temp} | {e['english_text'][:50]} → {e['pred'][:40]} |")

    report = f"""# Multi-Candidate Translation Eval

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Model:** {lm_model}  
**Samples:** {n} (seed={seed})  
**Candidates:** {num_candidates} @ {temperatures or [0.1, 0.7]}  
**Config:** num_context_passages=3, top_k_per_word=0  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | {nm_rate:.1%} ({nm_count}/{n}) |
| Exact Match | {em_rate:.1%} ({em_count}/{n}) |
| Avg Judge Score | {avg_score:.1f}/100 |

## Timing

| | |
|-|---|
| Total wall time | {elapsed:.0f}s |
| Avg per sample | {elapsed/n:.1f}s |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
{chr(10).join(rows)}
"""
    report_path.write_text(report)

    print(f"[mc_eval] Done. NM: {nm_rate:.1%}, EM: {em_rate:.1%}, avg judge score: {avg_score:.1f}")
    print(f"[mc_eval] Output: {out_dir}")
    return summary


if __name__ == "__main__":
    import argparse, yaml
    p = argparse.ArgumentParser(description="Run multi-candidate translation eval")
    p.add_argument("--n", type=int, default=100, help="Number of samples (0=all)")
    p.add_argument("--seed", type=int, default=20260526)
    p.add_argument("--min-words", type=int, default=0)
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--num-candidates", type=int, default=5)
    p.add_argument("--parallel", type=int, default=2, help="Parallel workers")
    args = p.parse_args()

    temps = [0.1, 0.3, 0.5, 0.7, 0.9]
    run_mc_eval(
        n_samples=args.n,
        seed=args.seed,
        min_english_words=args.min_words,
        out_dir=args.out_dir,
        num_candidates=args.num_candidates,
        temperatures=temps,
        parallel=args.parallel,
    )