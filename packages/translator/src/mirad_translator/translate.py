import dspy
from typing import Optional
from pathlib import Path

# Key Mirad grammar rules — used to populate EnglishToMiradSignature.__doc__
# DSPy 2.x reads __doc__ as the instructions/system prompt.

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
COMPILED_PROGRAM_DIR = _PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_bootstrap_fast_program"
COMPILED_PROGRAM_PKL = COMPILED_PROGRAM_DIR / "program.pkl"
COMPILED_MIR2EN_PROGRAM_DIR = _PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_mir2en_program"
COMPILED_MIR2EN_PROGRAM_PKL = COMPILED_MIR2EN_PROGRAM_DIR / "program.pkl"
_MIRAD_GRAMMAR_RULES = """
You are an English→Mirad translator. Vocabulary/idioms may be supplied separately; use those exact Mirad words first. Do not invent plausible roots, compress, or substitute near-synonyms. Output only Mirad.

Sentence order:
- Default is SVO: subject + finite verb + object. Do not move object pronouns before the verb.
  I pity you. = At [verb] et.
- Direct object follows the verb. If there is both indirect and direct object, use V + indirect + direct when the verb implies "to/for"; otherwise use bu/av.
  Buu at hua nyem. = Give me that box. / Buu hua nyem bu at.
- Keep normal word order in questions.

Noun phrases:
- Modifier order: article/deictic/possessive → quantifier/number → adjective/adverbial degree → noun.
  ha ewa aga tami = the two big houses.
- Adjectives/determiners do not agree; only the noun pluralizes with -i.
- ha = the. No indefinite article.
- Proper names usually take no ha.
- Possession/association/"of" uses X bi Y: ha tam bi Maria = Mary's house.
- Use bi, not be, for "of/from/possessive/partitive" and for superlative domains like "best in/of the school": ha gwa fia tuxut bi ha tistam.
- Use be only for location "at/in/on": be Paris, be tam.
- Use ayv for "about" unless a supplied idiom says otherwise: te ayv et = know about you.

Pronouns:
- at I/me, et you, it he/she/him/her, wit he/him, iyt she/her, is it/inanimate.
- yat we/us, yet you-pl, yit they/them animate, yis they/them inanimate.
- Possessive adjectives add -a: ata my, eta your, ita his/her, yata our, yita their.
- Pronouns do not change for case; case comes from position or preposition.
- Do not add a dummy "it" when English it has no referent:
  Mamileye. = It is raining. / Se fia van et upa. = It is good that you came.

Verbs:
- Infinitive ends -er. Stem = infinitive minus -er.
- Verbs never agree with person/number.
- Simple active endings: -e present, -a past, -o future, -u hypothetical/imperative/subjunctive.
- Simple active: stem + e present, a past, o future, u hypothetical/imperative/subjunctive.
  se = am/is/are; sa = was/were; so = will be; su = would be / Be!
  xe = do/does; xa = did; xo = will do; xu = would do / Do!
- Imperative has no subject and uses -u: Pu tam! = Go home. Negative imperative uses von: Von dalu! = Don't speak!
- Passive inserts w before final vowel: xwe is done, xwa was done.
- Progressive must preserve ey before tense vowel: stem + ey + e/a/o/u.
  peye = is going; peya = was going; tujeye = is sleeping; Mamileye = is raining.
  Never truncate progressive -eye to -ie.
- Perfect uses ay: paye = has gone. Imminent uses oy: poye = is about to go. Potential uses uy: puye = is apt to go.
- If English says "am/is/are VERB-ing", use progressive unless the supplied idiom says otherwise.

Negation/adverbs:
- voy = not, usually before the verb: At voy se eta ted. = I am not your parent/father as supplied.
- Do not add hus/is as subject just because English has "it" unless it refers to a real thing.
- Adjectives end -a; many adverbs end -ay. But if the supplied/few-shot form uses a bare adverb/root, keep it exactly.
  "as quickly as possible" may be the idiom gwa ig, not *has gwa ig.

Comparisons:
- Degree words: ga more, ge as/equally, go less, gwa most, gwo least.
- In comparative/equalative phrases, the linker after the adjective/adverb is vyel, never a repeated ge/ga/go.
  ga fia vyel et = better than you.
  ge aga vyel atas = as big as mine.
  go via vyel etas = less beautiful than yours.
- Superlative: gwa + adjective + noun + bi/be domain as appropriate.
  ha gwa aga tam bi yata yubem = the biggest house in our neighborhood.

Clauses:
- van = that/let/may/so that; do not omit it in "that" clauses.
  At ta van et upo. = I knew that you would come.
- Mirad keeps true tense in subordinate clauses; do not backshift like English.
- ven = if/whether. von = lest/that-not/don't.
- ho = relative who/which/that after the noun.
- If English "to me/for me" is a required indirect complement and not implied by the verb, preserve bu/av:
  Tease bu at van... = It seems to me that...

Questions/exclamations:
- Yes/no questions begin Duven and keep normal order.
- Question words usually start the sentence: duhot who, duhos what, duhom where, duhoj when, duhoyen how, duhosav why.
- Do not use Hyey as a generic filler. Use it only for actual "Oh!/What a..." interjection when intended. For idiomatic exclamation patterns, follow supplied examples exactly.

Final self-check before output:
1. Did every verb get the correct tense/aspect ending, especially progressive -eye?
2. Did every object stay after the verb unless it is a legitimate indirect-before-direct pattern?
3. Did every comparison use vyel after ga/ge/go + adjective/adverb?
4. Did I preserve required particles: bi, be, bu, ayv, van?
5. Did I use supplied vocabulary exactly instead of a plausible alternate?

Here are some translation examples for reference:
english,mirad
before this i lived in the suburbs but now i live downtown,ja his at tambesa ha yuzdom oy at tambese zedom hij
the students are walking to school today and the teachers are going home,ha tixuti tyoyapeye tistam hijub ay ha tuxuti peye tam
it is good to win but it is not fair to prejudge someone,se fia aker oy voy se yeva jayevder hes
i did not know whether they would come,at voy ta ven yit upo
i can see myself in the mirror,at yafe teater aut be ha sinzyef
he did it because he wanted to show us something,it xa has hosav it fa teatuer yat hes
they work at a grocery store near here and they will be there until the end of the season,yit yexe be tolnam yub bi him ay yit so hum ju ha uj bi ha jeb
""".strip()


def _format_word_equivalents(word_equivalents: dict, relevant_words: dict | None = None, back_translation: dict | None = None) -> str:
    """Format word equivalents dict as a readable string for the LLM.

    When relevant_words and back_translation are provided, formats three sections:
    word equivalents, relevant words, and back translations.
    """
    if not word_equivalents and not relevant_words and not back_translation:
        return ""

    sections = []

    # Section 1: Word equivalents (exact matches)
    if word_equivalents:
        lines = [f"{en} → {mi}" for en, mi in sorted(word_equivalents.items())]
        sections.append("WORD EQUIVALENTS (exact matches):\n" + "\n".join(lines))

    # Section 2: Relevant words (semantic neighbors)
    if relevant_words:
        lines = [f"{en} → {mi}" for en, mi in sorted(relevant_words.items())]
        sections.append("RELEVANT WORDS (closest translations):\n" + "\n".join(lines))

    # Section 3: Back translation (reverse lookups for context)
    if back_translation:
        lines = [f"{mi} → {en}" for mi, en in sorted(back_translation.items())]
        sections.append("BACK TRANSLATION (Mirad → English for context):\n" + "\n".join(lines))

    return "\n\n".join(sections)


def _format_context_passages(passages: list) -> str:
    """Format context passages as a single string for the LLM."""
    if not passages:
        return ""
    return "\n\n".join(passages)


def _split_search_terms(value) -> list[str]:
    """Parse DSPy text/list outputs into short retrieval terms."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        raw_items = [str(v) for v in value]
    else:
        raw = str(value)
        raw_items = []
        for line in raw.replace(";", "\n").split("\n"):
            raw_items.extend(part.strip() for part in line.split(","))
    terms = []
    for item in raw_items:
        item = item.strip().strip("-•0123456789. )(")
        if item and item.lower() not in {"none", "n/a", "na"}:
            terms.append(item)
    return terms


def _format_rule_context(rules: list[dict]) -> str:
    """Format retrieved structured grammar rules for the translator prompt.

    Each rule is formatted as its own passage to keep them atomic and clearly
    separated in the prompt context.
    """
    if not rules:
        return ""
    blocks = []
    for item in rules:
        rule = item.get("rule", item)
        rule_id = rule.get("id", "")
        description = rule.get("description", "")
        pseudocode = rule.get("pseudocode", "")
        examples = rule.get("examples") or []

        ex_lines = []
        for ex in examples[:3]:
            if isinstance(ex, dict):
                mirad = ex.get("mirad", "")
                english = ex.get("english", "")
                analysis = ex.get("analysis", "")
                parts = [f"Mirad: {mirad}", f"English: {english}"]
                if analysis:
                    parts.append(f"Note: {analysis}")
                ex_lines.append(f"- {' | '.join(parts)}")
            else:
                ex_lines.append(f"- {ex}")

        # Format each rule as a single self-contained passage
        rule_text = f"Rule ID: {rule_id}\nDescription: {description}"
        if pseudocode:
            rule_text += f"\nPseudocode: {pseudocode}"
        if ex_lines:
            rule_text += "\nExamples:\n" + "\n".join(ex_lines)

        # Include importance and combined score if available
        importance = item.get("importance")
        combined_score = item.get("combined_score")
        if importance is not None or combined_score is not None:
            score_parts = []
            if combined_score is not None:
                score_parts.append(f"score={combined_score:.3f}")
            if importance is not None:
                score_parts.append(f"importance={importance:.2f}")
            rule_text += f"\n[{', '.join(score_parts)}]"

        blocks.append(rule_text)

    return "\n\n".join(blocks)


def _extract_rule_ids(rules: list[dict]) -> list[str]:
    ids = []
    for item in rules or []:
        rule = item.get("rule", item)
        rid = rule.get("id") or item.get("metadata", {}).get("rule_id")
        if rid and rid not in ids:
            ids.append(str(rid))
    return ids


class TranslationAnalysisSignature(dspy.Signature):
    """Analyze text before translation.

    Identify normalized input structure, grammar-rule search terms, and vocabulary
    search terms. Keep search terms concise and aligned with Mirad grammar concepts
    such as verb tense, progressive aspect, possession, comparison, pronouns,
    word order, negation, questions, clauses, prepositions, and noun phrases.
    """
    source_text = dspy.InputField(desc="Text to translate")
    direction = dspy.InputField(desc="Translation direction: en_to_mir or mir_to_en")
    normalized_structure = dspy.OutputField(desc="Normalized structural analysis of the input sentence(s)")
    grammar_search_terms = dspy.OutputField(desc="Comma-separated grammar concepts/rules to retrieve")
    vocabulary_search_terms = dspy.OutputField(desc="Comma-separated words/phrases to look up in the lexicon")


class EnglishToMiradSignature(dspy.Signature):
    """Translate English text to Mirad.

    Follow these Mirad grammar rules:
    {grammar_rules}

    VOCABULARY RULE: Use the provided word equivalents (English→Mirad dictionary
    lookups) EXACTLY. Never substitute a plausible-sounding Mirad root when the
    dictionary provides a specific word. If the dictionary says "house → tam",
    output "tam", not "dom" or any other root.

    Use the provided structured grammar rules and vocabulary context to
    inform grammar, word order, and idiom choices. Grammar rules are retrieved
    by semantic similarity over rule retrieval_tags and include rule IDs.

    OUTPUT THE MIRAD TRANSLATION, then a second line exactly like:
    USED_RULE_IDS: id.one, id.two
    If no retrieved rules were used, write USED_RULE_IDS: none.
    """.format(grammar_rules=_MIRAD_GRAMMAR_RULES)
    english_text = dspy.InputField(desc="English text to translate")
    normalized_structure = dspy.InputField(desc="Pre-translation structural analysis")
    word_equivalents = dspy.InputField(desc="Dictionary lookups: English→Mirad word pairs found in the lexicon, one per line")
    context_passages = dspy.InputField(desc="Retrieved structured grammar rules relevant to the translation")
    mirad_text = dspy.OutputField(desc="Translated text in Mirad")
    used_rule_ids = dspy.OutputField(desc="Comma-separated IDs of retrieved grammar rules used")


class CritiqueSignature(dspy.Signature):
    """Review a candidate English→Mirad translation for correctness.

    You are a Mirad grammar expert. Given the original English text, dictionary
    lookups, grammar references, and a candidate Mirad translation, check for:

    1. **Grammar violations**: wrong word order, missing/extra articles, wrong
       verb tense endings (-e/-a/-o/-u), wrong aspect markers (-ey-/-ay-/-oy-/-uy-),
       missing or wrong passive (-w-), wrong pronoun forms.
    2. **Vocabulary errors**: words not in the dictionary lookups that seem
       invented, or dictionary lookups ignored when they should have been used.
    3. **Morphology errors**: wrong noun plural (-i), wrong possessive (-a),
       wrong comparative/superlative (ga/ge/go/gwa/gwo + vyel), wrong adverb
       formation (-y from -a adjectives).
    4. **Structural errors**: wrong preposition (be/bu/bi), missing van/ven in
       subordinate clauses, wrong conjunction (ay/ey/oy), missing/voy negation.
    5. **Idiom mismatches**: literal translations of English idioms where Mirad
       has a different construction.

    Grammar rules for reference:
    {grammar_rules}

    Set pass=True only if the translation is fully correct. If any issue is
    found, set pass=False and provide specific, actionable feedback describing
    exactly what is wrong and how to fix it.
    """.format(grammar_rules=_MIRAD_GRAMMAR_RULES)
    english_text = dspy.InputField(desc="Original English text")
    word_equivalents = dspy.InputField(desc="Dictionary lookups: English→Mirad word pairs")
    context_passages = dspy.InputField(desc="Structured grammar-rule passages")
    candidate_translation = dspy.InputField(desc="The candidate Mirad translation to review")
    pass_ = dspy.OutputField(desc="True if the translation is correct, False if there are issues")
    feedback = dspy.OutputField(desc="If pass_ is False, describe the specific errors and how to fix them")


class FixTranslationSignature(dspy.Signature):
    """Fix a Mirad translation based on critique feedback.

    You are an English→Mirad translator. You previously produced a candidate
    translation that was reviewed and found to have issues. Produce a corrected
    Mirad translation that addresses all the feedback.

    Follow these Mirad grammar rules:
    {grammar_rules}

    Use the provided word equivalents and context passages. Address every point
    in the feedback. OUTPUT ONLY THE CORRECTED MIRAD TRANSLATION. No commentary.
    """.format(grammar_rules=_MIRAD_GRAMMAR_RULES)
    english_text = dspy.InputField(desc="English text to translate")
    word_equivalents = dspy.InputField(desc="Dictionary lookups: English→Mirad word pairs")
    context_passages = dspy.InputField(desc="Structured grammar-rule passages")
    previous_attempt = dspy.InputField(desc="The previous Mirad translation that had issues")
    feedback = dspy.InputField(desc="Specific feedback on what was wrong and how to fix it")
    mirad_text = dspy.OutputField(desc="Corrected Mirad translation")


class FollowUpQuerySignature(dspy.Signature):
    """Generate a follow-up retrieval query for Mirad grammar and vocabulary.

    Given the original English text to translate and the context already
    retrieved, produce a focused follow-up query that will find grammar rules
    or vocabulary entries NOT already covered by the initial retrieval.

    Focus on specific grammar patterns, preposition usage, verb morphology,
    or idiomatic constructions that appear in the source text but may not
    be well-covered by the initial context. Keep the query short and specific.

    If the initial context already covers all grammar patterns and vocabulary
    needed, output an empty string to signal that no further retrieval is needed.
    """
    english_text = dspy.InputField(desc="English text to translate")
    initial_context = dspy.InputField(desc="Context passages already retrieved")
    word_equivalents = dspy.InputField(desc="Dictionary lookups already found")
    follow_up_query = dspy.OutputField(desc="A focused follow-up query for grammar/vocabulary not yet covered, or empty string if no more retrieval is needed")


# =====================================================================
# Mirad→English translation (reverse direction)
# =====================================================================

_MIRAD_TO_ENGLISH_RULES = """
You are a Mirad→English translator. Translate Mirad text to natural English.
Use the supplied vocabulary (Mirad→English dictionary lookups) when available.
If vocabulary or context is empty, rely on the grammar rules below.
Output ONLY the English translation. No commentary, no explanations.

Core Mirad grammar (for reverse translation):
- Mirad word order is SVO, same as English. Translate directly.
- Articles: ha = the (definite). No indefinite article in Mirad; "tam" = "a house" or "the house" depending on context; use "the" when ha is present.
- Plural: -i suffix on count nouns. ha via domi = the beautiful cities.
- Pronouns: at=I, et=you, it=he/she, wit=he, iyt=she, is=it(inanimate). yat=we, yet=you(pl), yit=they(animate), yis=they(inanimate).
  Possessive: -a suffix: ata=my, eta=your, ita=his/her, wita=his, iyta=her, yata=our, yita=their.
- Verbs: Dictionary form ends in -er. Remove -er to get stem.
  Endings: -e=present, -a=past, -o=future, -u=hypothetical/imperative/subjunctive.
  Passive: -w- before tense vowel: xwe=is done, xwa=was done.
  Aspects: progressive -ey-, perfect -ay-, imminent -oy-, potential -uy-.
  Passive aspects use w buffer: xewe=is being done, xawe=has been done.
- Negation: voy = not. Von = don't (negative imperative).
- Adverbs: Adjective + -y (from -a ending): fia→fiay beautifully, iga→igay quickly.
- Comparisons: ga=more, ge=as/like, go=less, gwa=most/greatest, gwo=least; vyel=than/as.
- Questions: Duven = yes/no question starter. Question words: duhot=who, duhos=what, duhom=where, duhoj=when, duhoyen=how, duhosav=why.
- Conjunctions: ay=and, ey=or, oy=but. van=that/so that, ven=if, oven=unless.
- Relative: ho=who/whom/which. ho at te = whom I know.
- Prepositions: be=at/in/on, bu=to/into, bi=of/from, ba=with, bo=without, van/ven/von as clausal conjunctions.
- Possession: X bi Y = Y's X (literally: the X of Y). ha dyes bi Ivan = Ivan's book.
- Omit dummy "it": Se fia van et upa. = It is good that you came.

Here are some translation examples for reference:
english,mirad
before this i lived in the suburbs but now i live downtown,ja his at tambesa ha yuzdom oy at tambese zedom hij
the students are walking to school today and the teachers are going home,ha tixuti tyoyapeye tistam hijub ay ha tuxuti peye tam
it is good to win but it is not fair to prejudge someone,se fia aker oy voy se yeva jayevder hes
i did not know whether they would come,at voy ta ven yit upo
i can see myself in the mirror,at yafe teater aut be ha sinzyef
he did it because he wanted to show us something,it xa has hosav it fa teatuer yat hes
they work at a grocery store near here and they will be there until the end of the season,yit yexe be tolnam yub bi him ay yit so hum ju ha uj bi ha jeb
""".strip()


class MiradToEnglishSignature(dspy.Signature):
    """Translate Mirad text to English.

    Follow these Mirad grammar rules for reverse translation:
    {grammar_rules}

    Use the provided word equivalents (Mirad→English dictionary lookups) whenever
    possible. Use the provided structured grammar rules and vocabulary context to
    inform grammar, word order, and translation choices. Grammar rules are retrieved
    by semantic similarity over rule retrieval_tags and include rule IDs.

    OUTPUT THE ENGLISH TRANSLATION, then a second line exactly like:
    USED_RULE_IDS: id.one, id.two
    If no retrieved rules were used, write USED_RULE_IDS: none.
    """.format(grammar_rules=_MIRAD_TO_ENGLISH_RULES)
    mirad_text = dspy.InputField(desc="Mirad text to translate")
    normalized_structure = dspy.InputField(desc="Pre-translation structural analysis")
    word_equivalents = dspy.InputField(desc="Dictionary lookups: Mirad→English word pairs found in the lexicon, one per line")
    context_passages = dspy.InputField(desc="Retrieved structured grammar rules relevant to the translation")
    english_text = dspy.OutputField(desc="Translated text in English")
    used_rule_ids = dspy.OutputField(desc="Comma-separated IDs of retrieved grammar rules used")


class StructuredRetrievalMixin:
    """Shared analysis + retrieval helpers for both translation directions."""

    def _ensure_structured_pipeline(self):
        if not hasattr(self, "analyze"):
            self.analyze = dspy.ChainOfThought(TranslationAnalysisSignature)

    def _fallback_terms(self, text: str) -> list[str]:
        words = [w.strip().strip('.,!?;:"\'-()[]{}') for w in text.split()]
        words = [w for w in words if w]
        return words[:12]

    def _analyze_text(self, text: str, direction: str) -> tuple[str, list[str], list[str]]:
        self._ensure_structured_pipeline()
        try:
            analysis = self.analyze(source_text=text, direction=direction)
            normalized = str(getattr(analysis, "normalized_structure", "") or "")
            grammar_terms = _split_search_terms(getattr(analysis, "grammar_search_terms", ""))
            vocab_terms = _split_search_terms(getattr(analysis, "vocabulary_search_terms", ""))
        except Exception:
            normalized = f"Source text: {text}"
            grammar_terms = []
            vocab_terms = []

        fallback = self._fallback_terms(text)
        if not grammar_terms:
            grammar_terms = fallback
        if not vocab_terms:
            vocab_terms = fallback
        return normalized, grammar_terms, vocab_terms

    def _retrieve_context_for_terms(self, grammar_terms: list[str], direction: str) -> tuple[list[str], list[dict]]:
        passages: list[str] = []
        rules_by_id: dict[str, dict] = {}
        seen_passages: set[str] = set()
        for term in grammar_terms[:6]:
            ctx_pred = self.context_retrieve(query=f"{direction} {term}")
            for item in getattr(ctx_pred, "grammar_rules", []) or []:
                rid = item.get("rule", {}).get("id") or item.get("metadata", {}).get("rule_id")
                if rid and rid not in rules_by_id:
                    rules_by_id[str(rid)] = item
            for passage in getattr(ctx_pred, "passages", []) or []:
                if passage not in seen_passages:
                    seen_passages.add(passage)
                    passages.append(passage)
        return passages, list(rules_by_id.values())

    def _parse_used_rule_ids(self, value, fallback_rules: list[dict]) -> list[str]:
        text = str(value or "").strip()
        if not text or text.lower() in {"none", "n/a", "na"}:
            return _extract_rule_ids(fallback_rules)
        ids = _split_search_terms(text.replace("USED_RULE_IDS:", ""))
        return ids or _extract_rule_ids(fallback_rules)


def _clean_lookup_token(value: str) -> str:
    return value.strip().strip('.,!?;:"\'-()[]{}').lower()


def _join_candidates(candidates: list[str]) -> str:
    return ", ".join(candidates)


class MiradLexiconReverseLookup(dspy.Module):
    """DSPy-traceable reverse lexicon lookup module (Mirad→English).

    Looks up each word in the Mirad input against the SQLite/FTS5
    lexicon DB and returns a dict of {mirad_word: english_translation}.
    """

    def __init__(self, db_path=None):
        super().__init__()
        self._db_path = db_path

    def forward(self, mirad_text: str) -> dspy.Prediction:
        from mirad_translator.lexicon_db import lookup_mirad_word_candidates
        words = mirad_text.split()
        word_equivalents = {}
        for w in words:
            w_clean = _clean_lookup_token(w)
            if w_clean:
                english_candidates = lookup_mirad_word_candidates(db_path=self._db_path, mirad_word=w_clean)
                if english_candidates:
                    word_equivalents[w_clean] = _join_candidates(english_candidates)
        return dspy.Prediction(word_equivalents=word_equivalents)


class MiradSemanticReverseLexiconLookup(dspy.Module):
    """Reverse lookup that enriches exact Mirad→English matches with semantic English neighbors.

    The reverse path must first resolve Mirad tokens exactly, because the semantic
    lexicon is indexed by English entries. Each exact English equivalent is then
    used as the semantic query so the prompt receives nearby English↔Mirad
    vocabulary without pulling broad thesaurus chunks into grammar context.
    """

    def __init__(self, db_path=None, top_k_per_word: int = 0, max_total_pairs: int = 50, min_similarity: float = 0.5):
        super().__init__()
        self._db_path = db_path
        self._top_k_per_word = top_k_per_word
        self._max_total_pairs = max_total_pairs
        self._min_similarity = min_similarity

    def forward(self, mirad_text: str) -> dspy.Prediction:
        from mirad_translator.lexicon_db import lookup_mirad_word_candidates, lookup_word_candidates

        words = mirad_text.split()
        word_equivalents: dict[str, str] = {}
        english_queries: list[str] = []
        for word in words:
            mirad_word = _clean_lookup_token(word)
            if not mirad_word or mirad_word in word_equivalents:
                continue
            english_candidates = lookup_mirad_word_candidates(db_path=self._db_path, mirad_word=mirad_word)
            if english_candidates:
                word_equivalents[mirad_word] = _join_candidates(english_candidates)
                english_queries.extend(english_candidates)

        if english_queries:
            try:
                from mirad_translator.semantic_lexicon import semantic_lookup

                for english_query in english_queries:
                    for hit in semantic_lookup(
                        english_query,
                        top_k=self._top_k_per_word,
                        min_similarity=self._min_similarity,
                        include_exact=True,
                    ):
                        english = hit["english"]
                        mirad_candidates = lookup_word_candidates(db_path=self._db_path, english_word=english)
                        if not mirad_candidates:
                            mirad_candidates = [hit["mirad"]]
                        if english not in word_equivalents:
                            word_equivalents[english] = _join_candidates(mirad_candidates)
                        if len(word_equivalents) >= self._max_total_pairs:
                            break
                    if len(word_equivalents) >= self._max_total_pairs:
                        break
            except Exception:
                pass

        return dspy.Prediction(word_equivalents=word_equivalents)


class MiradToEnglishModule(StructuredRetrievalMixin, dspy.Module):
    """DSPy Module for Mirad→English translation with lexicon lookup and RAG retrieval.

    Mir→En counterpart to TranslatorModule. Takes mirad_text as input and internally:
    1. Looks up Mirad→English word equivalents via reverse lexicon lookup
    2. Retrieves grammar-rule context via ChromaDB (same grammar index, Mirad query works too)
    3. Passes text, word equivalents, and context to ChainOfThought for translation

    Args:
        db_path: Path to the lexicon SQLite DB.
        num_context_passages: Number of RAG context passages (0 disables retrieval).
    """

    def __init__(self, db_path=None, num_context_passages: int = 0, use_postprocessor: bool = False):
        super().__init__()
        self.generate = dspy.ChainOfThought(MiradToEnglishSignature)
        self.lexicon_lookup = MiradLexiconReverseLookup(db_path=db_path)
        self.context_retrieve = MiradContextRetrieve(k=num_context_passages)
        self._db_path = db_path
        self._num_context_passages = num_context_passages
        # Mir→En post-processing is a no-op by default (reserved for future use).
        # Mirad particle corrections (be→bi, ge→vyel) would corrupt English output.
        self._use_postprocessor = use_postprocessor

    def forward(
        self,
        mirad_text: str,
        word_equivalents: str = "",
        context_passages: str = "",
    ) -> dspy.Prediction:
        """Translate Mirad text to English.

        Accepts optional ``word_equivalents`` and ``context_passages`` for DSPy
        signature compatibility (these are used when provided by DSPy demos; if
        empty the module computes them internally from the lexicon and ChromaDB).
        """
        normalized_structure, grammar_terms, vocab_terms = self._analyze_text(mirad_text, "mir_to_en")

        # Use provided context if non-empty (from DSPy demos); otherwise compute
        # internally from analysis-derived vocabulary terms.
        if not word_equivalents:
            lookup_text = " ".join(vocab_terms) if vocab_terms else mirad_text
            word_eq_pred = self.lexicon_lookup(mirad_text=lookup_text)
            word_equivalents_dict = word_eq_pred.word_equivalents
            # Build structured vocabulary for Mir→En with back-translation
            from mirad_translator.lexicon_db import lookup_word_candidates
            exact_pairs = {}
            back_translation = {}
            for mi, en_translations in word_equivalents_dict.items():
                exact_pairs[mi] = en_translations
                # Back-translation: for each English word in the translation, look up en→mir
                for en_word in [w.strip() for w in en_translations.split(",")]:
                    mir_candidates = lookup_word_candidates(english_word=en_word)
                    if mir_candidates and en_word not in back_translation:
                        # Don't include the same mirad word we started from
                        back_en = ", ".join(mir_candidates)
                        back_translation[en_word] = back_en
            relevant_words = {}  # Semantic neighbors already included in exact pairs for mir→en
            word_equivalents = _format_word_equivalents(exact_pairs, relevant_words, back_translation)
        else:
            # Parse provided string back to dict for return value
            word_equivalents_dict = {}
            for line in word_equivalents.split("\n"):
                line = line.strip()
                if " → " in line:
                    mi, en = line.split(" → ", 1)
                    word_equivalents_dict[mi.strip()] = en.strip()

        grammar_rules = []
        if not context_passages:
            context_passages_list, grammar_rules = self._retrieve_context_for_terms(grammar_terms, "mir_to_en")
            context_passages = _format_context_passages(context_passages_list)
        else:
            # Context already provided; split on double-newline to match format
            context_passages_list = [
                p for p in context_passages.split("\n\n") if p.strip()
            ]

        prediction = self.generate(
            mirad_text=mirad_text,
            normalized_structure=normalized_structure,
            word_equivalents=word_equivalents,
            context_passages=context_passages,
        )
        used_rule_ids = self._parse_used_rule_ids(getattr(prediction, "used_rule_ids", ""), grammar_rules)
        return dspy.Prediction(
            english_text=prediction.english_text,
            used_rule_ids=used_rule_ids,
            normalized_structure=normalized_structure,
            grammar_search_terms=grammar_terms,
            vocabulary_search_terms=vocab_terms,
            word_equivalents=word_equivalents_dict,
            context=context_passages_list,
        )


class MultiHopTranslatorModule(StructuredRetrievalMixin, dspy.Module):
    """Translation module with multi-hop retrieval.

    Instead of a single retrieval pass, this module:
    1. Does an initial retrieval (same as TranslatorModule)
    2. Asks the LM whether it needs more specific context, and if so, what query
    3. Retrieves additional context with the follow-up query
    4. Merges all context and generates the final translation

    Args:
        db_path: Path to the lexicon SQLite DB.
        num_context_passages: Base number of RAG context passages per hop (0 disables retrieval).
        num_hops: Number of retrieval hops (1 = single-hop like TranslatorModule, 2+ = multi-hop).
    """

    def __init__(self, db_path=None, num_context_passages: int = 3, num_hops: int = 2):
        super().__init__()
        self.generate = dspy.ChainOfThought(EnglishToMiradSignature)
        self.generate_query = dspy.ChainOfThought(FollowUpQuerySignature)
        self.lexicon_lookup = MiradLexiconLookup(db_path=db_path)
        self.context_retrieve = MiradContextRetrieve(k=num_context_passages)
        self._db_path = db_path
        self._num_context_passages = num_context_passages
        self._num_hops = max(1, num_hops)

    def _retrieve(self, english_text: str):
        """Run structured vocabulary lookup and context retrieval, return formatted strings + raw data."""
        # Use structured vocabulary lookup (exact + semantic + back-translation)
        from mirad_translator.semantic_lexicon import semantic_lookup_structured
        vocab = semantic_lookup_structured(
            english_text,
            top_k_per_word=getattr(self, '_top_k_per_word', 5),
            max_total_pairs=getattr(self, '_max_total_pairs', 50),
            min_similarity=getattr(self, '_min_similarity', 0.5),
            include_exact=True,
        )
        word_equivalents = vocab["word_equivalents"]
        relevant_words = vocab["relevant_words"]
        back_translation = vocab["back_translation"]

        # Merge all non-exact pairs for backward compatibility
        all_pairs = dict(word_equivalents)
        for k, v in relevant_words.items():
            if k not in all_pairs:
                all_pairs[k] = v

        ctx_pred = self.context_retrieve(query=english_text)
        context_passages = list(ctx_pred.passages)

        we_str = _format_word_equivalents(word_equivalents, relevant_words, back_translation)
        ctx_str = _format_context_passages(context_passages)

        return we_str, ctx_str, all_pairs, context_passages, relevant_words, back_translation

    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate with multi-hop retrieval."""
        # Hop 1: Initial retrieval
        normalized_structure, grammar_terms, vocab_terms = self._analyze_text(english_text, "en_to_mir")
        we_str, ctx_str, word_equivalents, context_passages, relevant_words, back_translation = self._retrieve(english_text)

        # Additional hops: LM generates follow-up queries for more context
        seen_ids = set()
        for passage in context_passages:
            # Deduplicate by content — track what we've seen
            seen_ids.add(hash(passage[:100]))

        all_context_passages = list(context_passages)

        for hop in range(1, self._num_hops):
            # Ask the LM if more context is needed
            query_pred = self.generate_query(
                english_text=english_text,
                initial_context=ctx_str if ctx_str else "(no initial context retrieved)",
                word_equivalents=we_str if we_str else "(no dictionary lookups found)",
            )
            follow_up = query_pred.follow_up_query.strip()

            if not follow_up:
                break  # LM says no more retrieval needed

            # Retrieve with follow-up query
            from mirad_translator.retrieval import retrieve_all
            try:
                result = retrieve_all(follow_up, top_k=self._num_context_passages)
                new_passages = []
                for item in result.get("grammar", []):
                    src = item.get("metadata", {}).get("source_section", "grammar")
                    passage_text = f"[{src}] {item['text']}"
                    # Only add if not already seen
                    content_hash = hash(passage_text[:100])
                    if content_hash not in seen_ids:
                        seen_ids.add(content_hash)
                        new_passages.append(passage_text)
            except Exception:
                new_passages = []

            if not new_passages:
                break  # No new context found

            all_context_passages.extend(new_passages)
            ctx_str = _format_context_passages(all_context_passages)

        # Generate translation with all accumulated context
        prediction = self.generate(
            english_text=english_text,
            normalized_structure=normalized_structure,
            word_equivalents=we_str,
            context_passages=ctx_str,
        )
        used_rule_ids = self._parse_used_rule_ids(getattr(prediction, "used_rule_ids", ""), [])
        return dspy.Prediction(
            mirad_text=prediction.mirad_text,
            used_rule_ids=used_rule_ids,
            normalized_structure=normalized_structure,
            grammar_search_terms=grammar_terms,
            vocabulary_search_terms=vocab_terms,
            word_equivalents=word_equivalents,
            relevant_words=relevant_words,
            back_translation=back_translation,
            context=all_context_passages,
        )


class MiradLexiconLookup(dspy.Module):
    """DSPy-traceable lexicon lookup module.

    Looks up each word in the English input against the SQLite/FTS5
    lexicon DB and returns a dict of {english_word: mirad_translation}.
    """

    def __init__(self, db_path=None):
        super().__init__()
        self._db_path = db_path

    def forward(self, english_text: str) -> dspy.Prediction:
        from mirad_translator.lexicon_db import lookup_word
        words = english_text.split()
        word_equivalents = {}
        for w in words:
            w_clean = w.strip().rstrip('.,!?;:"\'-()[]{}')
            if w_clean:
                mirad = lookup_word(db_path=self._db_path, english_word=w_clean)
                if mirad:
                    word_equivalents[w_clean.lower()] = mirad
        return dspy.Prediction(word_equivalents=word_equivalents)


class MiradContextRetrieve(dspy.Retrieve):
    """DSPy-traceable retrieval module for structured Mirad grammar rules.

    Grammar retrieval uses combined scoring (c² + i²) where c is cosine
    similarity and i is the rule's importance score. Each rule is returned
    as a separate passage — not grouped into a single block.
    Vocabulary belongs in `word_equivalents`; thesaurus chunks are intentionally
    excluded from prompt context to avoid broad noisy passages.
    """

    def __init__(self, k: int = 5):
        # Don't call super().__init__ with a rm since we use custom ChromaDB
        self._k = k

    def forward(self, query: str) -> dspy.Prediction:
        """Retrieve structured grammar rules for the query.

        Each rule is its own passage — one per rule, clearly formatted.
        """
        from mirad_translator.retrieval import retrieve_grammar
        try:
            grammar_result = retrieve_grammar(query, top_k=self._k)
            passages = []
            grammar_rules = []
            for item in grammar_result:
                grammar_rules.append(item)
                # Each rule becomes its own passage
                rule_text = _format_rule_context([item])
                if rule_text:
                    passages.append(rule_text)
        except Exception:
            passages = []
            grammar_rules = []
        return dspy.Prediction(passages=passages, grammar_rules=grammar_rules)



class TranslatorModule(StructuredRetrievalMixin, dspy.Module):
    """DSPy Module for English→Mirad translation with lexicon lookup and RAG retrieval.

    The module takes only ``english_text`` as input and internally:
    1. Looks up word equivalents via the lexicon DB
    2. Retrieves structured grammar-rule context via ChromaDB (disabled when k=0)
    3. Passes the original text, word equivalents, and context as separate
       signature fields to ChainOfThought for translation

    The signature (EnglishToMiradSignature) has ``english_text``,
    ``word_equivalents``, and ``context_passages`` as inputs — this allows
    DSPy optimizers like LabeledFewShot and BootstrapFewShot to include
    retrieved context in their demos so the model sees worked examples of
    how to use dictionary lookups and grammar references.

    Post-processing: when ``use_postprocessor=True`` (default), the raw Mirad
    output is passed through ``postprocess_mirad`` which corrects known
    particle errors (``be→bi`` in possessives, ``ge→vyel`` in comparatives),
    strips meta-commentary wrappers, and normalizes whitespace/punctuation.
    """

    def __init__(self, db_path=None, num_context_passages: int = 0, use_postprocessor: bool = True):
        super().__init__()
        self.generate = dspy.ChainOfThought(EnglishToMiradSignature)
        self.lexicon_lookup = MiradLexiconLookup(db_path=db_path)
        self.context_retrieve = MiradContextRetrieve(k=num_context_passages)
        self._db_path = db_path
        self._num_context_passages = num_context_passages
        self._use_postprocessor = use_postprocessor

    def _retrieve(self, english_text: str):
        """Run structured vocabulary lookup and context retrieval, return formatted strings + raw data."""
        # Use structured vocabulary lookup (exact + semantic + back-translation)
        from mirad_translator.semantic_lexicon import semantic_lookup_structured
        vocab = semantic_lookup_structured(
            english_text,
            top_k_per_word=getattr(self, '_top_k_per_word', 5),
            max_total_pairs=getattr(self, '_max_total_pairs', 50),
            min_similarity=getattr(self, '_min_similarity', 0.5),
            include_exact=True,
        )
        word_equivalents = vocab["word_equivalents"]
        relevant_words = vocab["relevant_words"]
        back_translation = vocab["back_translation"]

        # Merge all non-exact pairs for backward compatibility
        all_pairs = dict(word_equivalents)
        for k, v in relevant_words.items():
            if k not in all_pairs:
                all_pairs[k] = v

        ctx_pred = self.context_retrieve(query=english_text)
        context_passages = ctx_pred.passages

        we_str = _format_word_equivalents(word_equivalents, relevant_words, back_translation)
        ctx_str = _format_context_passages(context_passages)

        return we_str, ctx_str, all_pairs, context_passages, relevant_words, back_translation

    def forward(
        self,
        english_text: str,
        word_equivalents: str = "",
        context_passages: str = "",
    ) -> dspy.Prediction:
        """Translate English text to Mirad.

        Accepts optional ``word_equivalents`` and ``context_passages`` for
        DSPy demo compatibility (used when provided by DSPy demos; if empty
        the module computes them internally from the lexicon and ChromaDB).

        The raw Mirad output is post-processed (by default) to fix known
        particle errors and normalize formatting.
        """
        normalized_structure, grammar_terms, vocab_terms = self._analyze_text(english_text, "en_to_mir")

        # Use provided context if non-empty (from DSPy few-shot demos);
        # otherwise compute internally from analysis-derived vocabulary terms.
        if not word_equivalents:
            lookup_text = " ".join(vocab_terms) if vocab_terms else english_text
            # Use structured vocabulary lookup (exact + semantic + back-translation)
            from mirad_translator.semantic_lexicon import semantic_lookup_structured
            vocab = semantic_lookup_structured(
                lookup_text,
                top_k_per_word=getattr(self, '_top_k_per_word', 5),
                max_total_pairs=getattr(self, '_max_total_pairs', 50),
                min_similarity=getattr(self, '_min_similarity', 0.5),
                include_exact=True,
            )
            word_equivalents_dict = vocab["word_equivalents"]
            relevant_words = vocab["relevant_words"]
            back_translation = vocab["back_translation"]
            # Merge all pairs for backward compatibility
            all_pairs = dict(word_equivalents_dict)
            for k, v in relevant_words.items():
                if k not in all_pairs:
                    all_pairs[k] = v
            we_str = _format_word_equivalents(word_equivalents_dict, relevant_words, back_translation)
            # word_equivalents stays as the merged dict for backward compatibility;
            # relevant_words and back_translation are returned separately.
            we_dict = all_pairs
        else:
            we_str = word_equivalents
            # Parse provided string back to dict for return value
            we_dict = {}
            relevant_words = {}
            back_translation = {}
            for line in word_equivalents.split("\n"):
                line = line.strip()
                if " → " in line:
                    en, mi = line.split(" → ", 1)
                    we_dict[en.strip()] = mi.strip()

        grammar_rules = []
        if not context_passages:
            context_passages_list, grammar_rules = self._retrieve_context_for_terms(grammar_terms, "en_to_mir")
            ctx_str = _format_context_passages(context_passages_list)
        else:
            context_passages_list = [
                p for p in context_passages.split("\n\n") if p.strip()
            ]
            ctx_str = context_passages  # Already formatted string

        prediction = self.generate(
            english_text=english_text,
            normalized_structure=normalized_structure,
            word_equivalents=we_str,
            context_passages=ctx_str,
        )
        raw_text = prediction.mirad_text
        used_rule_ids = self._parse_used_rule_ids(getattr(prediction, "used_rule_ids", ""), grammar_rules)
        if self._use_postprocessor:
            from mirad_translator.postprocess import postprocess_mirad
            mirad_text = postprocess_mirad(raw_text)
        else:
            mirad_text = raw_text
        return dspy.Prediction(
            mirad_text=mirad_text,
            raw_mirad_text=raw_text if self._use_postprocessor else None,
            used_rule_ids=used_rule_ids,
            normalized_structure=normalized_structure,
            grammar_search_terms=grammar_terms,
            vocabulary_search_terms=vocab_terms,
            word_equivalents=we_dict,
            relevant_words=relevant_words,
            back_translation=back_translation,
            context=context_passages_list,
        )


class CritiqueAndFixModule(dspy.Module):
    """Translation module with a critique-and-fix loop.

    Translates English→Mirad, then runs up to ``max_retries`` rounds of
    critique (grammar/vocabulary check) and fix. If the critique signals
    pass=True, the loop stops early and returns the accepted translation.

    Args:
        db_path: Path to the lexicon SQLite DB.
        num_context_passages: Number of RAG context passages (0 disables retrieval).
        max_retries: Maximum critique-fix rounds (default 3).
    """

    def __init__(self, db_path=None, num_context_passages: int = 0, max_retries: int = 3):
        super().__init__()
        self.translator = TranslatorModule(db_path=db_path, num_context_passages=num_context_passages)
        self.critique = dspy.ChainOfThought(CritiqueSignature)
        self.fix = dspy.ChainOfThought(FixTranslationSignature)
        self._db_path = db_path
        self._num_context_passages = num_context_passages
        self._max_retries = max(0, max_retries)

    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate with critique-and-fix loop."""
        # Initial translation
        trans_pred = self.translator(english_text=english_text)
        candidate = trans_pred.mirad_text

        # Retrieve context for critique (reuse translator's retrieval)
        we_str, ctx_str, word_equivalents, context_passages, _relevant_words, _back_translation = self.translator._retrieve(english_text)

        current_translation = candidate

        for round_idx in range(self._max_retries):
            # Critique the current translation
            critique_pred = self.critique(
                english_text=english_text,
                word_equivalents=we_str,
                context_passages=ctx_str,
                candidate_translation=current_translation,
            )

            # Parse pass_ field — LM may return bool or string
            passed = critique_pred.pass_
            if isinstance(passed, str):
                passed = passed.strip().lower() in ("true", "yes", "1", "pass")

            if passed:
                # Translation accepted
                return dspy.Prediction(
                    mirad_text=current_translation,
                    word_equivalents=word_equivalents,
                    context=context_passages,
                    critique_rounds=round_idx + 1,
                    critique_passed=True,
                    feedback=getattr(critique_pred, "feedback", ""),
                )

            # Fix the translation based on feedback
            feedback = critique_pred.feedback
            fix_pred = self.fix(
                english_text=english_text,
                word_equivalents=we_str,
                context_passages=ctx_str,
                previous_attempt=current_translation,
                feedback=feedback,
            )
            current_translation = fix_pred.mirad_text

        # Exhausted retries — return the last fix attempt
        return dspy.Prediction(
            mirad_text=current_translation,
            word_equivalents=word_equivalents,
            context=context_passages,
            critique_rounds=self._max_retries,
            critique_passed=False,
            feedback=getattr(critique_pred, "feedback", ""),
        )


def load_compiled_translator(compiled_path=None, semantic_lexicon=True, top_k_per_word=0, max_total_pairs=50, min_similarity=0.5):
    """Load the pre-compiled BootstrapFewShot translator from disk.

    The compiled program has bootstrapped demos for the ChainOfThought predictor,
    which significantly improves translation quality over the uncompiled module.

    By default uses the program compiled with DeepSeek-V4-Flash stored at
    data/eval_results/optimizer_comparison/compiled_bootstrap_fast_program/program.pkl.

    Args:
        compiled_path: Path to the compiled program .pkl file. Defaults to built-in path.
        semantic_lexicon: If True (default), swap MiradLexiconLookup for MiradSemanticLexiconLookup
            (top-k semantic neighbor search instead of exact match).
        top_k_per_word: Semantic lookup neighbors per word (default 0 = disabled).
        max_total_pairs: Max total word equivalent pairs for semantic lookup (default 30).
        min_similarity: Min cosine similarity for semantic lookup neighbors (default 0.5).

    Returns:
        A compiled TranslatorModule (or module with semantic lookup swapped in).

    Raises:
        FileNotFoundError: If the compiled program file doesn't exist.
    """
    import cloudpickle

    path = Path(compiled_path) if compiled_path else COMPILED_PROGRAM_PKL
    if not path.exists():
        raise FileNotFoundError(
            f"Compiled program not found at {path}. "
            f"Run BootstrapFewShot optimization first, or set use_compiled=False."
        )

    with open(path, "rb") as f:
        module = cloudpickle.load(f)

    if semantic_lexicon:
        from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup
        module.lexicon_lookup = MiradSemanticLexiconLookup(
            db_path=None,
            top_k_per_word=top_k_per_word,
            max_total_pairs=max_total_pairs,
            min_similarity=min_similarity,
        )

    # Compiled artifacts may contain predictors compiled against the old signature.
    # Refresh the predictor so the structured pipeline fields are always present.
    module.generate = dspy.ChainOfThought(EnglishToMiradSignature)
    if not hasattr(module, "analyze"):
        module.analyze = dspy.ChainOfThought(TranslationAnalysisSignature)

    return module


def load_compiled_mir2en_translator(compiled_path=None, semantic_lexicon=True, top_k_per_word=0, max_total_pairs=50, min_similarity=0.5):
    """Load the pre-compiled BootstrapRS Mir→En translator from disk.

    The compiled program has bootstrapped demos for the ChainOfThought predictor,
    which significantly improves translation quality over the uncompiled module.

    Args:
        compiled_path: Path to the compiled program .pkl file. Defaults to built-in path.
        semantic_lexicon: If True (default), swap MiradLexiconReverseLookup for
            MiradSemanticLexiconLookup (top-k semantic neighbor search).
        top_k_per_word: Semantic lookup neighbors per word (default 0 = disabled).
        max_total_pairs: Max total word equivalent pairs for semantic lookup (default 30).
        min_similarity: Min cosine similarity for semantic lookup neighbors (default 0.5).

    Returns:
        A compiled MiradToEnglishModule (or module with semantic lookup swapped in).

    Raises:
        FileNotFoundError: If the compiled program file doesn't exist.
    """
    import cloudpickle

    path = Path(compiled_path) if compiled_path else COMPILED_MIR2EN_PROGRAM_PKL
    if not path.exists():
        raise FileNotFoundError(
            f"Compiled Mir→En program not found at {path}. "
            f"Run run_bootstrap_mir2en.py first, or set use_compiled=False."
        )

    with open(path, "rb") as f:
        module = cloudpickle.load(f)

    if semantic_lexicon:
        module.lexicon_lookup = MiradSemanticReverseLexiconLookup(
            db_path=None,
            top_k_per_word=top_k_per_word,
            max_total_pairs=max_total_pairs,
            min_similarity=min_similarity,
        )
    if not hasattr(module, "analyze"):
        module.analyze = dspy.ChainOfThought(TranslationAnalysisSignature)

    return module


def DefaultTranslator(db_path=None, num_context_passages: int = 3, max_retries: int = 0, num_hops: int = 1, direction: str = "en_to_mir", use_postprocessor: bool = True, use_compiled: bool = False, semantic_lexicon: bool = True, top_k_per_word: int = 0, max_total_pairs: int = 50, min_similarity: float = 0.5):
    """Factory: open/create SQLite lexicon DB and ChromaDB index, return translation module.

    By default this returns fresh structured-retrieval modules using semantic
    lexicon lookup and grammar rules from the rebuilt JSON-rule Chroma index.
    Set use_compiled=True only when compiled programs have been regenerated for
    the current signatures.

    When max_retries > 0, wraps the translator in a CritiqueAndFixModule that runs a
    critique-and-fix loop after the initial translation.
    When num_hops > 1, returns a MultiHopTranslatorModule that runs iterative
    retrieval with LM-generated follow-up queries.
    When direction="mir_to_en", returns a MiradToEnglishModule for reverse translation.
    When use_compiled=True and direction="mir_to_en", loads the pre-compiled
    BootstrapRS Mir→En program (falling back to an uncompiled module if not found).

    When semantic_lexicon=True (requires use_compiled=True or a plain TranslatorModule),
    swaps MiradLexiconLookup for MiradSemanticLexiconLookup, which uses embedding-based
    top-k nearest-neighbor search over English words instead of exact match. This
    helps find translations for inflected forms ("ran"→"run") and morphological variants
    ("houses"→"house").

    By default, En→Mir translations (TranslatorModule) are piped through
    ``postprocess_mirad`` which applies high-precision particle corrections
    (be→bi possessive, ge→vyel comparative), strips meta-commentary wrappers,
    and normalizes whitespace/punctuation. Set use_postprocessor=False to
    disable this and receive raw LM output only.

    Args:
        db_path: Path to the lexicon SQLite DB. Defaults to built-in path.
        num_context_passages: Number of structured grammar rules to retrieve (0 disables retrieval).
        max_retries: Max critique-fix rounds (0 = no critique, plain translation). Only for en_to_mir.
        num_hops: Number of retrieval hops (1 = single retrieval, 2+ = multi-hop with LM queries). Only for en_to_mir.
        direction: Translation direction — "en_to_mir" (default) or "mir_to_en".
        use_postprocessor: Apply post-processing to En→Mir translations (default True).
        use_compiled: Load a pre-compiled BootstrapFewShot program (default False because current structured-retrieval signatures supersede stale compiled programs).
            Falls back to an uncompiled TranslatorModule if the compiled program is not found.
        semantic_lexicon: Use semantic (embedding-based) top-k lexicon lookup instead of exact match (default True).
        top_k_per_word: Semantic lookup neighbors per word (default 0 = disabled). Only used when semantic_lexicon=True.
        max_total_pairs: Max total word equivalent pairs for semantic lookup (default 30). Only used when semantic_lexicon=True.
        min_similarity: Min cosine similarity for semantic lookup neighbors (default 0.5). Only used when semantic_lexicon=True.
    """
    from mirad_translator.lexicon_db import build_lexicon_db, DB_PATH as _default_db

    effective_db_path = db_path or _default_db
    build_lexicon_db(db_path=effective_db_path)

    # --- Reverse direction: try compiled Mir→En program first ---
    if direction == "mir_to_en":
        if use_compiled:
            try:
                return load_compiled_mir2en_translator(
                    semantic_lexicon=semantic_lexicon,
                    top_k_per_word=top_k_per_word,
                    max_total_pairs=max_total_pairs,
                    min_similarity=min_similarity,
                )
            except FileNotFoundError:
                pass  # Fall through to uncompiled module
        module = MiradToEnglishModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
        )
        if semantic_lexicon:
            module.lexicon_lookup = MiradSemanticReverseLexiconLookup(
                db_path=effective_db_path,
                top_k_per_word=top_k_per_word,
                max_total_pairs=max_total_pairs,
                min_similarity=min_similarity,
            )
        return module

    # --- Forward direction (en_to_mir) ---

    # Try loading compiled program when use_compiled=True and no extra wrappers
    if use_compiled and max_retries == 0 and num_hops == 1:
        try:
            return load_compiled_translator(
                semantic_lexicon=semantic_lexicon,
                top_k_per_word=top_k_per_word,
                max_total_pairs=max_total_pairs,
                min_similarity=min_similarity,
            )
        except FileNotFoundError:
            pass  # Fall through to uncompiled module

    # --- Build fresh module ---
    if max_retries > 0:
        module = CritiqueAndFixModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
            max_retries=max_retries,
        )
    elif num_hops > 1:
        module = MultiHopTranslatorModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
            num_hops=num_hops,
        )
    else:
        module = TranslatorModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
            use_postprocessor=use_postprocessor,
        )

    # Swap in semantic lexicon if requested
    if semantic_lexicon:
        from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup
        if hasattr(module, 'translator'):
            # CritiqueAndFixModule wraps a translator
            module.translator.lexicon_lookup = MiradSemanticLexiconLookup(
                db_path=effective_db_path,
                top_k_per_word=top_k_per_word,
                max_total_pairs=max_total_pairs,
                min_similarity=min_similarity,
            )
        elif hasattr(module, 'lexicon_lookup'):
            module.lexicon_lookup = MiradSemanticLexiconLookup(
                db_path=effective_db_path,
                top_k_per_word=top_k_per_word,
                max_total_pairs=max_total_pairs,
                min_similarity=min_similarity,
            )

    return module


def translate_with_lookup(english_text: str, db_path=None, top_k: int = 5, max_retries: int = 0, num_hops: int = 1, use_compiled: bool = False, semantic_lexicon: bool = True):
    """High-level entry point: look up words + retrieve context + translate.

    By default uses the current structured grammar-rule retrieval and semantic lexicon pipeline.

    Args:
        english_text: English text to translate.
        db_path: Path to the lexicon SQLite DB.
        top_k: Number of context passages to retrieve (0 disables retrieval).
        max_retries: Max critique-fix rounds (0 = no critique).
        num_hops: Number of retrieval hops (1 = single, 2+ = multi-hop).
        use_compiled: Load compiled program (default False).
        semantic_lexicon: Use semantic (embedding-based) top-k lexicon lookup (default True).

    Returns:
        (mirad_text, word_equivalents, context_chunks) — translation, dict, list.
    """
    translator = DefaultTranslator(
        db_path=db_path,
        num_context_passages=top_k,
        max_retries=max_retries,
        num_hops=num_hops,
        use_compiled=use_compiled,
        semantic_lexicon=semantic_lexicon,
    )
    prediction = translator.forward(english_text=english_text)
    return (
        prediction.mirad_text,
        prediction.word_equivalents,
        prediction.context,
    )