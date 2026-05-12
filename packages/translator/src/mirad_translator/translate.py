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
    word_equivalents = dspy.InputField(desc="Dict of English word → Mirad translation from lexicon")
    context = dspy.InputField(desc="Retrieved grammar and thesaurus chunks relevant to the input")
    mirad_text = dspy.OutputField(desc="Translated text in Mirad")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1")


class TranslatorModule(dspy.Module):
    def __init__(self, lexicon_db_path=None, chroma_retriever=None):
        super().__init__()
        self.generate = dspy.ChainOfThought(EnglishToMiradSignature)
        self._lexicon_db_path = lexicon_db_path
        self._chroma_retriever = chroma_retriever

    def forward(self, english_text: str, word_equivalents: dict = None, context: list = None) -> dspy.Prediction:
        """Translate English text to Mirad with lexicon lookup and RAG context."""
        prediction = self.generate(
            english_text=english_text,
            word_equivalents=word_equivalents or {},
            context=context or []
        )
        return dspy.Prediction(
            mirad_text=prediction.mirad_text,
            confidence=prediction.confidence
        )


def DefaultTranslator(lexicon_db_path=None, chroma_retriever=None):
    """Factory: open/create SQLite lexicon DB and ChromaDB index, return TranslatorModule."""
    # Import here to avoid hard dependency when module is loaded without DB
    from mirad_translator.lexicon_db import build_lexicon_db, DB_PATH as _default_db
    from mirad_translator.retrieval import build_indexes as _build_chroma

    db_path = lexicon_db_path or _default_db
    build_lexicon_db(db_path=db_path)

    if chroma_retriever is None:
        try:
            _build_chroma()
        except Exception:
            pass  # ChromaDB not available; retrieval will be empty

    return TranslatorModule(
        lexicon_db_path=db_path,
        chroma_retriever=chroma_retriever
    )


def translate_with_lookup(english_text: str, db_path=None, top_k: int = 5):
    """High-level entry point: look up words + retrieve context + translate.

    Returns (mirad_text, confidence, word_equivalents, context_chunks).
    """
    from mirad_translator.lexicon_db import lookup_word
    from mirad_translator.retrieval import retrieve_all

    # Build word_equivalents dict
    words = english_text.split()
    word_equivalents = {}
    for w in words:
        w_clean = w.strip().rstrip('.,!?;:"\'-()[]{}')
        if w_clean:
            mirad = lookup_word(db_path=db_path, english_word=w_clean)
            if mirad:
                word_equivalents[w_clean.lower()] = mirad

    # Retrieve context chunks
    try:
        retrieval_result = retrieve_all(english_text, top_k=top_k)
        context_chunks = []
        for section in ("grammar", "thesaurus"):
            for item in retrieval_result.get(section, []):
                src = item.get("metadata", {}).get("source_section", section)
                context_chunks.append(f"[{src}] {item['text']}")
    except Exception:
        context_chunks = []

    # Translate
    translator = DefaultTranslator(lexicon_db_path=db_path)
    prediction = translator.forward(
        english_text=english_text,
        word_equivalents=word_equivalents,
        context=context_chunks
    )
    return (
        prediction.mirad_text,
        prediction.confidence,
        word_equivalents,
        context_chunks
    )