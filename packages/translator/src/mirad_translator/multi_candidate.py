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
# Candidate Judge Signature
# ---------------------------------------------------------------------------

class CandidateJudgeSignature(dspy.Signature):
    """Judge an English→Mirad translation. Be strict. Wrong translations: 40-65 pts. Correct: 80-100.

    Scoring rubric (each 0-20 pts):

    1. Grammar: SVO order, bi/be/bu prepositions, no dummy "it" or English article words.

    2. Verb morphology: correct tense (-e/-a/-o/-u), progressive -eye not -ie, passive -w-, no invented roots.

    3. Vocabulary: dictionary lookups used correctly, correct -i noun plural, -a pronoun possessive.

    4. English bleed: 20=zero bleed (all-lowercase, no period), 0=lots of bleed.

    5. Completeness: all source meaning components present, required particles (se, bi, voy) not dropped.

    PENALTIES: deduct from TOTAL score after summing the 5 dimensions above.
    - WRONG CONJUNCTION PARTICLE: if English has "but" but Mirad uses "ay" (not "oy"), -15.
    - MISSING HA ARTICLE: if gold has "ha" before noun but candidate drops it, -10.
    - MISSING SE COPULA: if predicate adjective missing required "se", -10.
    - COMPLETELY WRONG WORDS: if candidate uses unrelated words, -20.

    Output: grammar_score, morphology_score, vocabulary_score, english_bleed_score,
    completeness_score (all 0-20), total_score (0-100 after penalties), rationale.
    """
    original_english    = dspy.InputField(desc="Original English source text")
    candidate_mirad     = dspy.InputField(desc="Candidate Mirad translation")
    grammar_score       = dspy.OutputField(desc="Integer 0-20: grammar correctness")
    morphology_score    = dspy.OutputField(desc="Integer 0-20: verb morphology")
    vocabulary_score    = dspy.OutputField(desc="Integer 0-20: word choice / vocabulary")
    english_bleed_score = dspy.OutputField(desc="Integer 0-20: LOWER = more English bleed (20=perfect Mirad style)")
    completeness_score  = dspy.OutputField(desc="Integer 0-20: structural completeness vs source")
    total_score         = dspy.OutputField(desc="Integer 0-100: sum minus any penalties")
    rationale           = dspy.OutputField(desc="One-sentence explanation of main weaknesses")


class CandidateJudge(dspy.Module):
    """DSPy Module that judges a candidate translation.

    Wraps CandidateJudgeSignature with ChainOfThought reasoning.
    The judge has Mirad grammar rules embedded in its docstring so it can
    evaluate morphology and idiom correctness accurately without needing
    grammar retrieval passed as context.
    """

    def __init__(self):
        super().__init__()
        self._judge = dspy.ChainOfThought(CandidateJudgeSignature)

    def forward(
        self,
        original_english: str,
        candidate_mirad: str,
    ) -> dspy.Prediction:
        pred = self._judge(
            original_english=original_english,
            candidate_mirad=candidate_mirad,
        )
        return dspy.Prediction(
            grammar_score=self._parse_float(getattr(pred, "grammar_score", "0"), default=0),
            morphology_score=self._parse_float(getattr(pred, "morphology_score", "0"), default=0),
            vocabulary_score=self._parse_float(getattr(pred, "vocabulary_score", "0"), default=0),
            english_bleed_score=self._parse_float(getattr(pred, "english_bleed_score", "0"), default=0),
            completeness_score=self._parse_float(getattr(pred, "completeness_score", "0"), default=0),
            total_score=self._parse_float(getattr(pred, "total_score", "0"), default=0),
            rationale=str(getattr(pred, "rationale", "")),
        )

    def _parse_float(self, value, default: float = 0.0) -> float:
        try:
            s = str(value).strip()
            # Extract first number (can be float or integer)
            m = re.search(r"-?\d+(?:\.\d+)?", s)
            if m:
                return float(m.group())
            return default
        except Exception:
            return default


# ---------------------------------------------------------------------------
# Mirad→English Candidate Judge
# ---------------------------------------------------------------------------

class MiradToEnglishCandidateJudgeSignature(dspy.Signature):
    """Judge a Mirad→English translation. Be strict. Wrong translations: 40-65 pts. Correct: 80-100.

    Scoring rubric (each 0-20 pts):

    1. Semantic Fidelity: does the English capture all meaning components from the Mirad?
       Check: correct verb tense/aspect, correct pronoun reference, correct negation, not missing
       required arguments. Deduct for subject/object swaps, quantifier errors, missing clauses.

    2. Grammar: natural English word order (SVO), correct subject-verb agreement,
       correct article usage (a/an/the), correct preposition choices.

    3. Direction Correctness: no Mirad grammar patterns leaking into English output.
       Mirad has no "it" dummy subjects, no "ha" articles, no verb-fronting for questions.
       If any Mirad-specific construct appears in the English, deduct.

    4. Literalness: translate what Mirad says, not what you think it means.
       Don't add information not in the source. Don't omit required subjects/objects.
       "ata" = "my/mine" not "I have". "se fia" = "is good" not "it is good".

    Output: semantic_fidelity, grammar_score, direction_correctness, literalness
    (all 0-20), total_score (0-100), rationale.
    """
    original_mirad     = dspy.InputField(desc="Original Mirad source text")
    candidate_english  = dspy.InputField(desc="Candidate English translation")
    semantic_fidelity  = dspy.OutputField(desc="Integer 0-20: meaning preserved vs Mirad source")
    grammar_score      = dspy.OutputField(desc="Integer 0-20: natural English grammar")
    direction_correctness = dspy.OutputField(desc="Integer 0-20: no Mirad patterns leaking into English")
    literalness        = dspy.OutputField(desc="Integer 0-20: translation is literal, not interpretive")
    total_score        = dspy.OutputField(desc="Integer 0-100: sum of four dimensions")
    rationale          = dspy.OutputField(desc="One-sentence explanation of main weaknesses")


class MiradToEnglishCandidateJudge(dspy.Module):
    """DSPy Module that judges a Mirad→English candidate translation.

    Wraps MiradToEnglishCandidateJudgeSignature with ChainOfThought reasoning.
    The judge has Mirad grammar knowledge embedded so it can catch direction errors
    (e.g., dummy "it" added, "ha" treated as English article) without needing
    grammar retrieval passed as context.
    """

    def __init__(self):
        super().__init__()
        self._judge = dspy.ChainOfThought(MiradToEnglishCandidateJudgeSignature)

    def forward(
        self,
        original_mirad: str,
        candidate_english: str,
    ) -> dspy.Prediction:
        pred = self._judge(
            original_mirad=original_mirad,
            candidate_english=candidate_english,
        )
        return dspy.Prediction(
            semantic_fidelity=self._parse_float(getattr(pred, "semantic_fidelity", "0"), default=0),
            grammar_score=self._parse_float(getattr(pred, "grammar_score", "0"), default=0),
            direction_correctness=self._parse_float(getattr(pred, "direction_correctness", "0"), default=0),
            literalness=self._parse_float(getattr(pred, "literalness", "0"), default=0),
            total_score=self._parse_float(getattr(pred, "total_score", "0"), default=0),
            rationale=str(getattr(pred, "rationale", "")),
        )

    def _parse_float(self, value, default: float = 0.0) -> float:
        try:
            s = str(value).strip()
            m = re.search(r"-?\d+(?:\.\d+)?", s)
            if m:
                return float(m.group())
            return default
        except Exception:
            return default


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
        self._judge = CandidateJudge()

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

        # Generate all candidates
        candidates: list[dict] = []
        for i in range(self.num_candidates):
            temperature = self.temperatures[i % len(self.temperatures)]
            candidate_text = self._generate_candidate(english_text, temperature)
            candidates.append({
                "index": i,
                "temperature": temperature,
                "mirad_text": candidate_text,
            })

        # Judge each candidate and pick the highest total_score
        winner_index = 0
        winner_score = -1
        winner_rationale = ""

        for i, cand in enumerate(candidates):
            mirad = cand["mirad_text"]
            judge_pred = self._judge(
                original_english=english_text,
                candidate_mirad=mirad,
            )
            total = judge_pred.total_score
            cand["judge"] = {
                "grammar_score": judge_pred.grammar_score,
                "morphology_score": judge_pred.morphology_score,
                "vocabulary_score": judge_pred.vocabulary_score,
                "english_bleed_score": judge_pred.english_bleed_score,
                "completeness_score": judge_pred.completeness_score,
                "total_score": total,
                "rationale": judge_pred.rationale,
            }

            if total > winner_score:
                winner_score = total
                winner_index = i
                winner_rationale = judge_pred.rationale

        best = candidates[winner_index]
        return dspy.Prediction(
            mirad_text=best["mirad_text"],
            winner_index=winner_index,
            total_score=winner_score,
            candidates=candidates,
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
        self._judge = MiradToEnglishCandidateJudge()

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
                "temperature": temperature,
                "english_text": candidate_text,
            })

        winner_index = 0
        winner_score = -1
        winner_rationale = ""

        for i, cand in enumerate(candidates):
            english = cand["english_text"]
            judge_pred = self._judge(
                original_mirad=mirad_text,
                candidate_english=english,
            )
            total = judge_pred.total_score
            cand["judge"] = {
                "semantic_fidelity": judge_pred.semantic_fidelity,
                "grammar_score": judge_pred.grammar_score,
                "direction_correctness": judge_pred.direction_correctness,
                "literalness": judge_pred.literalness,
                "total_score": total,
                "rationale": judge_pred.rationale,
            }

            if total > winner_score:
                winner_score = total
                winner_index = i
                winner_rationale = judge_pred.rationale

        best = candidates[winner_index]
        return dspy.Prediction(
            english_text=best["english_text"],
            mirad_text=best["english_text"],  # mirror field name for eval compat
            winner_index=winner_index,
            total_score=winner_score,
            candidates=candidates,
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