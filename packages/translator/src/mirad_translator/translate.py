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


class EnglishToMiradSignature(dspy.Signature):
    """Translate English text to Mirad.

    Follow these Mirad grammar rules:
    {grammar_rules}
    """.format(grammar_rules=_MIRAD_GRAMMAR_RULES)
    english_text = dspy.InputField(desc="English text to translate")
    mirad_text = dspy.OutputField(desc="Translated text in Mirad")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1")


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
    """DSPy Module for English→Mirad translation with RAG retrieval.

    The module takes only ``english_text`` as input and internally:
    1. Looks up word equivalents via the lexicon DB
    2. Retrieves grammar/thesaurus context via ChromaDB
    3. Formats a rich prompt with retrieved context + grammar rules
    4. Generates Mirad translation via ChainOfThought

    The signature (EnglishToMiradSignature) only has ``english_text`` as
    input — retrieval is an internal module concern, not a signature field.
    This makes BootstrapFewShot work correctly: eval Examples only need
    ``english_text`` and ``mirad_text``, and the optimizer traces the full
    retrieval→generate pipeline to produce bootstrapped demos.
    """

    def __init__(self, db_path=None, num_context_passages: int = 5):
        super().__init__()
        self.generate = dspy.ChainOfThought(EnglishToMiradSignature)
        self.lexicon_lookup = MiradLexiconLookup(db_path=db_path)
        self.context_retrieve = MiradContextRetrieve(k=num_context_passages)
        self._db_path = db_path

    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate English text to Mirad.

        Retrieval (lexicon lookup + RAG context) happens internally;
        the caller only needs to provide ``english_text``.
        """
        # Step 1: lexicon lookup
        word_eq_pred = self.lexicon_lookup(english_text=english_text)
        word_equivalents = word_eq_pred.word_equivalents

        # Step 2: RAG context retrieval
        ctx_pred = self.context_retrieve(query=english_text)
        context_passages = ctx_pred.passages

        # Step 3: build enriched prompt for the LLM
        # Inject word equivalents and context directly into the english_text
        # so the ChainOfThought sees everything in one input field.
        parts = [english_text]
        if word_equivalents:
            eq_lines = [f"  {en} → {mi}" for en, mi in sorted(word_equivalents.items())]
            parts.append("\nWord equivalents (use these Mirad words when possible):")
            parts.append("\n".join(eq_lines))
        if context_passages:
            parts.append("\nRelevant grammar and thesaurus context:")
            parts.append("\n\n".join(context_passages))
        enriched_text = "\n".join(parts)

        # Step 4: generate translation
        prediction = self.generate(english_text=enriched_text)
        return dspy.Prediction(
            mirad_text=prediction.mirad_text,
            confidence=prediction.confidence,
            word_equivalents=word_equivalents,
            context=context_passages,
        )


def DefaultTranslator(db_path=None, num_context_passages: int = 5):
    """Factory: open/create SQLite lexicon DB and ChromaDB index, return TranslatorModule."""
    from mirad_translator.lexicon_db import build_lexicon_db, DB_PATH as _default_db
    from mirad_translator.retrieval import build_indexes as _build_chroma

    effective_db_path = db_path or _default_db
    build_lexicon_db(db_path=effective_db_path)

    if num_context_passages > 0:
        try:
            _build_chroma()
        except Exception:
            pass  # ChromaDB not available; retrieval will be empty

    return TranslatorModule(
        db_path=effective_db_path,
        num_context_passages=num_context_passages,
    )


def translate_with_lookup(english_text: str, db_path=None, top_k: int = 5):
    """High-level entry point: look up words + retrieve context + translate.

    Returns (mirad_text, confidence, word_equivalents, context_chunks).
    """
    translator = DefaultTranslator(db_path=db_path, num_context_passages=top_k)
    prediction = translator.forward(english_text=english_text)
    return (
        prediction.mirad_text,
        prediction.confidence,
        prediction.word_equivalents,
        prediction.context,
    )