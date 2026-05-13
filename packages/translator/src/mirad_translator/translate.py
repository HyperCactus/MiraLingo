import dspy
from typing import Optional

# Key Mirad grammar rules — used to populate EnglishToMiradSignature.__doc__
# DSPy 2.x reads __doc__ as the instructions/system prompt.
_MIRAD_GRAMMAR_RULES = """
You are an English→Mirad translator. Use only the supplied vocabulary when possible; do not invent roots unless needed. Output only Mirad unless asked to explain.

Core syntax:
- Normal word order is SVO: Subject + verb predicate + object. Keep declarative word order even in questions.
  Example: At te ha dud. = I know the answer.
- Modifiers of nouns precede the noun. Order: article/deictic/possessive → quantifier/number → adjective(s) → noun.
  Example: ha ewa aga tami = the two big houses.
- Prepositional phrases and relative clauses follow the noun they modify.
  Example: ha tam bi Maria = Mary's house / the house of Maria.
  Example: ha tob ho at te = the person whom I know.
- Prepositions precede their complement: be tam = at home, bu tam = to home, bi Maria = of/from Maria.
- Possession by a named person uses X bi Y, not English 's: ha dyes bi Ivan = Ivan's book.

Nouns:
- No indefinite article. "a house" = tam. Definite "the" = ha before the noun phrase.
- Plural common count nouns add -i only to the noun; modifiers do not agree.
  Example: ha via domi = the beautiful cities.
- Proper names are capitalized and usually take no ha.
- Animate pronouns end in -t; inanimate pronouns end in -s.

Pronouns:
- at I/me, et you, it he/she/him/her, wit he/him, iyt she/her, is it/inanimate.
- yat we/us, yet you plural, yit they/them animate, yis they/them inanimate.
- Possessive adjectives add -a: ata my, eta your, ita his/her, wita his, iyta her, yata our, yita their.
- Pronouns do not change for subject/object case.
- Omit dummy English "it" when it has no real referent.
  Example: Se fia van et upa. = It is good that you came.
  Example: Mamilo. = It will rain.

Verbs:
- Dictionary infinitives end in -er. Remove -er to get the stem.
- Verbs do not agree with person or number.
- Simple active endings: -e present, -a past, -o future, -u hypothetical/imperative/subjunctive.
  Example with x- "do": at xe = I do; at xa = I did; at xo = I will do; at xu = I would do; Xu! = Do!
- Passive inserts -w- before the final tense/mood vowel.
  Example: xwe = is done, xwa = was done, xwo = will be done, xwu = would be done.
- Aspects use stem + aspect marker + final tense/mood vowel:
  progressive active -ey-: xeye = am doing, xeya = was doing.
  perfect active -ay-: xaye = have done, xaya = had done.
  imminent active -oy-: xoye = am about to do.
  potential active -uy-: xuye = am apt/likely to do.
- Passive aspect buffer is w instead of y where applicable: xewe = is being done, xawe = has been done.
- Translate English tense directly; do not shift tense in subordinate clauses.
  Example: "I knew he would come" → At ta van it upo. ("I knew that he will come.")

Negation and adverbs:
- voy = not; usually before the verb, but may follow if clear.
  Example: At voy te. / At te voy. = I don't know.
- von introduces negative imperatives/subjunctives: Von dalu! = Don't speak!
- Adverbs usually sit immediately before or after what they modify.
  Example: It deuze viay. = He sings beautifully.
- Adjectives form adverbs by adding -y to final -a: fia → fiay, iga → igay.
- Comparisons use ga/ge/go/gwa/gwo before adjective/adverb, and vyel for than/as.
  Example: ga fia vyel et = better than you.

Questions:
- Yes/no questions begin with Duven and keep normal word order.
  Example: Duven et te ha dud? = Do you know the answer?
- Question words usually begin the sentence; no inversion:
  duhot who, duhos what, duhom where, duhoj when, duhoyen how, duhosav why.
  Example: Duhom et tambee? = Where do you live?
- Some adverbial question words may also appear at the end.
  Example: Et tambee duhom?

Clauses and conjunctions:
- ay = and, ey = or, oy = but.
- van = that/let/may/so that; required for "that" clauses.
  Example: At te van et upo. = I know that you will come.
- ven = if/whether. Use future in both clauses when both are future in meaning.
  Example: Ven et pio, at so uva. = If you leave, I will be sad.
- oven = unless.
- ho = relative who/whom/that/which after the noun it modifies.
- Prepositions used as clausal conjunctions require van/ven/von:
  ja van = before, je van = while, jo van = after, av van = so that, av von = so that not/lest, ov van = although.
- For purpose clauses with same subject, prefer infinitive with av/ov when natural.

Objects:
- Direct object follows the verb.
- If a verb has both indirect and direct objects, indirect object usually comes before direct object when the verb implies "to/for".
  Example: Buu at hua nyem. = Give me that box.
- Motion/communication verbs may omit English to/from when inherent.
  Example: At peye ha nam. = I am going to the store.
""".strip()


def _format_word_equivalents(word_equivalents: dict) -> str:
    """Format word equivalents dict as a readable string for the LLM."""
    if not word_equivalents:
        return ""
    return "\n".join(f"{en} → {mi}" for en, mi in sorted(word_equivalents.items()))


def _format_context_passages(passages: list) -> str:
    """Format context passages as a single string for the LLM."""
    if not passages:
        return ""
    return "\n\n".join(passages)


class EnglishToMiradSignature(dspy.Signature):
    """Translate English text to Mirad.

    Follow these Mirad grammar rules:
    {grammar_rules}

    Use the provided word equivalents (English→Mirad dictionary lookups) whenever
    possible. Use the provided context passages (grammar and thesaurus excerpts) to
    inform grammar, word order, and idiom choices. If the word equivalents or
    context passages are empty, rely on the grammar rules above.

    OUTPUT ONLY THE MIRAD TRANSLATION. No commentary, no explanations, no
    confidence notes, no dictionary excerpts. Just the Mirad text.
    """.format(grammar_rules=_MIRAD_GRAMMAR_RULES)
    english_text = dspy.InputField(desc="English text to translate")
    word_equivalents = dspy.InputField(desc="Dictionary lookups: English→Mirad word pairs found in the lexicon, one per line")
    context_passages = dspy.InputField(desc="Retrieved grammar and thesaurus passages relevant to the translation")
    mirad_text = dspy.OutputField(desc="Translated text in Mirad")


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
    context_passages = dspy.InputField(desc="Grammar and thesaurus passages")
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
    context_passages = dspy.InputField(desc="Grammar and thesaurus passages")
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
""".strip()


class MiradToEnglishSignature(dspy.Signature):
    """Translate Mirad text to English.

    Follow these Mirad grammar rules for reverse translation:
    {grammar_rules}

    Use the provided word equivalents (Mirad→English dictionary lookups) whenever
    possible. Use the provided context passages (grammar and thesaurus excerpts) to
    inform grammar, word order, and translation choices. If the word equivalents or
    context passages are empty, rely on the grammar rules above.

    OUTPUT ONLY THE ENGLISH TRANSLATION. No commentary, no explanations. Just the English text.
    """.format(grammar_rules=_MIRAD_TO_ENGLISH_RULES)
    mirad_text = dspy.InputField(desc="Mirad text to translate")
    word_equivalents = dspy.InputField(desc="Dictionary lookups: Mirad→English word pairs found in the lexicon, one per line")
    context_passages = dspy.InputField(desc="Retrieved grammar and thesaurus passages relevant to the translation")
    english_text = dspy.OutputField(desc="Translated text in English")


class MiradLexiconReverseLookup(dspy.Module):
    """DSPy-traceable reverse lexicon lookup module (Mirad→English).

    Looks up each word in the Mirad input against the SQLite/FTS5
    lexicon DB and returns a dict of {mirad_word: english_translation}.
    """

    def __init__(self, db_path=None):
        super().__init__()
        self._db_path = db_path

    def forward(self, mirad_text: str) -> dspy.Prediction:
        from mirad_translator.lexicon_db import lookup_mirad_word
        words = mirad_text.split()
        word_equivalents = {}
        for w in words:
            w_clean = w.strip().rstrip('.,!?;:"\'-()[]{}')
            if w_clean:
                english = lookup_mirad_word(db_path=self._db_path, mirad_word=w_clean)
                if english:
                    word_equivalents[w_clean] = english
        return dspy.Prediction(word_equivalents=word_equivalents)


class MiradToEnglishModule(dspy.Module):
    """DSPy Module for Mirad→English translation with lexicon lookup and RAG retrieval.

    Mir→En counterpart to TranslatorModule. Takes mirad_text as input and internally:
    1. Looks up Mirad→English word equivalents via reverse lexicon lookup
    2. Retrieves grammar/thesaurus context via ChromaDB (same indexes, En query works for Mirad too)
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
        # Use provided context if non-empty (from DSPy few-shot demos);
        # otherwise compute internally.
        if not word_equivalents:
            word_eq_pred = self.lexicon_lookup(mirad_text=mirad_text)
            word_equivalents_dict = word_eq_pred.word_equivalents
            word_equivalents = "\n".join(
                f"{mi} → {en}" for mi, en in sorted(word_equivalents_dict.items())
            )
        else:
            # Parse provided string back to dict for return value
            word_equivalents_dict = {}
            for line in word_equivalents.split("\n"):
                line = line.strip()
                if " → " in line:
                    mi, en = line.split(" → ", 1)
                    word_equivalents_dict[mi.strip()] = en.strip()

        if not context_passages:
            ctx_pred = self.context_retrieve(query=mirad_text)
            context_passages_list = list(ctx_pred.passages)
            context_passages = _format_context_passages(context_passages_list)
        else:
            # Context already provided; split on double-newline to match format
            context_passages_list = [
                p for p in context_passages.split("\n\n") if p.strip()
            ]

        prediction = self.generate(
            mirad_text=mirad_text,
            word_equivalents=word_equivalents,
            context_passages=context_passages,
        )
        return dspy.Prediction(
            english_text=prediction.english_text,
            word_equivalents=word_equivalents_dict,
            context=context_passages_list,
        )


class MultiHopTranslatorModule(dspy.Module):
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

    def __init__(self, db_path=None, num_context_passages: int = 5, num_hops: int = 2):
        super().__init__()
        self.generate = dspy.ChainOfThought(EnglishToMiradSignature)
        self.generate_query = dspy.ChainOfThought(FollowUpQuerySignature)
        self.lexicon_lookup = MiradLexiconLookup(db_path=db_path)
        self.context_retrieve = MiradContextRetrieve(k=num_context_passages)
        self._db_path = db_path
        self._num_context_passages = num_context_passages
        self._num_hops = max(1, num_hops)

    def _retrieve(self, english_text: str):
        """Run lexicon lookup and context retrieval, return formatted strings + raw data."""
        word_eq_pred = self.lexicon_lookup(english_text=english_text)
        word_equivalents = word_eq_pred.word_equivalents

        ctx_pred = self.context_retrieve(query=english_text)
        context_passages = list(ctx_pred.passages)

        we_str = _format_word_equivalents(word_equivalents)
        ctx_str = _format_context_passages(context_passages)

        return we_str, ctx_str, word_equivalents, context_passages

    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate with multi-hop retrieval."""
        # Hop 1: Initial retrieval
        we_str, ctx_str, word_equivalents, context_passages = self._retrieve(english_text)

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
                for section in ("grammar", "thesaurus"):
                    for item in result.get(section, []):
                        src = item.get("metadata", {}).get("source_section", section)
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
            word_equivalents=we_str,
            context_passages=ctx_str,
        )
        return dspy.Prediction(
            mirad_text=prediction.mirad_text,
            word_equivalents=word_equivalents,
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
    """DSPy-traceable retrieval module for Mirad grammar and thesaurus context.

    Subclasses dspy.Retrieve so it participates in optimizer tracing.
    Wraps ChromaDB grammar + thesaurus retrieval into the standard
    Retrieve interface: input=query string, output=list of passage strings.
    """

    def __init__(self, k: int = 5):
        # Don't call super().__init__ with a rm since we use custom ChromaDB
        self._k = k

    def forward(self, query: str) -> dspy.Prediction:
        """Retrieve grammar and thesaurus chunks for the given query.

        Returns a dspy.Prediction with a `passages` attribute (list of strings).
        """
        from mirad_translator.retrieval import retrieve_all
        try:
            result = retrieve_all(query, top_k=self._k)
            passages = []
            for section in ("grammar", "thesaurus"):
                for item in result.get(section, []):
                    src = item.get("metadata", {}).get("source_section", section)
                    passages.append(f"[{src}] {item['text']}")
        except Exception:
            passages = []
        return dspy.Prediction(passages=passages)


class TranslatorModule(dspy.Module):
    """DSPy Module for English→Mirad translation with lexicon lookup and RAG retrieval.

    The module takes only ``english_text`` as input and internally:
    1. Looks up word equivalents via the lexicon DB
    2. Retrieves grammar/thesaurus context via ChromaDB (disabled when k=0)
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
        """Run lexicon lookup and context retrieval, return formatted strings + raw data."""
        word_eq_pred = self.lexicon_lookup(english_text=english_text)
        word_equivalents = word_eq_pred.word_equivalents

        ctx_pred = self.context_retrieve(query=english_text)
        context_passages = ctx_pred.passages

        we_str = _format_word_equivalents(word_equivalents)
        ctx_str = _format_context_passages(context_passages)

        return we_str, ctx_str, word_equivalents, context_passages

    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate English text to Mirad.

        Retrieval (lexicon lookup + RAG context) happens internally;
        the caller only needs to provide ``english_text``.
        The raw Mirad output is post-processed (by default) to fix known
        particle errors and normalize formatting.
        """
        we_str, ctx_str, word_equivalents, context_passages = self._retrieve(english_text)

        prediction = self.generate(
            english_text=english_text,
            word_equivalents=we_str,
            context_passages=ctx_str,
        )
        raw_text = prediction.mirad_text
        if self._use_postprocessor:
            from mirad_translator.postprocess import postprocess_mirad
            mirad_text = postprocess_mirad(raw_text)
        else:
            mirad_text = raw_text
        return dspy.Prediction(
            mirad_text=mirad_text,
            raw_mirad_text=raw_text if self._use_postprocessor else None,
            word_equivalents=word_equivalents,
            context=context_passages,
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
        we_str, ctx_str, word_equivalents, context_passages = self.translator._retrieve(english_text)

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


def DefaultTranslator(db_path=None, num_context_passages: int = 0, max_retries: int = 0, num_hops: int = 1, direction: str = "en_to_mir", use_postprocessor: bool = True):
    """Factory: open/create SQLite lexicon DB and ChromaDB index, return translation module.

    When max_retries > 0, returns a CritiqueAndFixModule that runs a
    critique-and-fix loop after the initial translation.
    When num_hops > 1, returns a MultiHopTranslatorModule that runs iterative
    retrieval with LM-generated follow-up queries.
    When direction="mir_to_en", returns a MiradToEnglishModule for reverse translation.

    By default, En→Mir translations (TranslatorModule) are piped through
    ``postprocess_mirad`` which applies high-precision particle corrections
    (be→bi possessive, ge→vyel comparative), strips meta-commentary wrappers,
    and normalizes whitespace/punctuation. Set use_postprocessor=False to
    disable this and receive raw LM output only.

    Args:
        db_path: Path to the lexicon SQLite DB. Defaults to built-in path.
        num_context_passages: Number of RAG context passages to retrieve (0 disables retrieval).
        max_retries: Max critique-fix rounds (0 = no critique, plain translation). Only for en_to_mir.
        num_hops: Number of retrieval hops (1 = single retrieval, 2+ = multi-hop with LM queries). Only for en_to_mir.
        direction: Translation direction — "en_to_mir" (default) or "mir_to_en".
        use_postprocessor: Apply post-processing to En→Mir translations (default True).
                           Mir→En ignores this; no post-processing is applied in that direction.
    """
    from mirad_translator.lexicon_db import build_lexicon_db, DB_PATH as _default_db
    from mirad_translator.retrieval import build_indexes as _build_chroma

    effective_db_path = db_path or _default_db
    build_lexicon_db(db_path=effective_db_path)

    if num_context_passages > 0:
        try:
            _build_chroma()
        except Exception:
            pass  # ChromaDB not available; retrieval will be empty

    if direction == "mir_to_en":
        return MiradToEnglishModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
        )

    if max_retries > 0:
        return CritiqueAndFixModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
            max_retries=max_retries,
        )

    if num_hops > 1:
        return MultiHopTranslatorModule(
            db_path=effective_db_path,
            num_context_passages=num_context_passages,
            num_hops=num_hops,
        )

    return TranslatorModule(
        db_path=effective_db_path,
        num_context_passages=num_context_passages,
        use_postprocessor=use_postprocessor,
    )


def translate_with_lookup(english_text: str, db_path=None, top_k: int = 0, max_retries: int = 0, num_hops: int = 1):
    """High-level entry point: look up words + retrieve context + translate.

    Args:
        english_text: English text to translate.
        db_path: Path to the lexicon SQLite DB.
        top_k: Number of context passages to retrieve (0 disables retrieval).
        max_retries: Max critique-fix rounds (0 = no critique).
        num_hops: Number of retrieval hops (1 = single, 2+ = multi-hop).

    Returns:
        (mirad_text, word_equivalents, context_chunks) — translation, dict, list.
    """
    translator = DefaultTranslator(db_path=db_path, num_context_passages=top_k, max_retries=max_retries, num_hops=num_hops)
    prediction = translator.forward(english_text=english_text)
    return (
        prediction.mirad_text,
        prediction.word_equivalents,
        prediction.context,
    )