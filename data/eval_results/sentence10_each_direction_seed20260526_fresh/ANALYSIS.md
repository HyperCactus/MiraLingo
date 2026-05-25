# Sentence 10 Each Direction Evaluation Analysis

- Devset: `data/eval/devset_sentence10_each_direction_seed20260526.json`
- Source CSV: `data/phrases/english-mirad-sentence-pairs.csv`
- Seed: `20260526`
- Eligibility filter: English source has at least 5 words and Mirad source has at least 5 tokens.
- Sample: 10 CSV rows, evaluated in both directions.
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Retrieval: fresh uncompiled modules, structured grammar-rule retrieval from rebuilt `grammar_rules` ChromaDB collection.
- Artifacts: `data/eval_results/sentence10_each_direction_seed20260526_fresh/`

## Retrieval Pipeline Verification

The prior issue was real but subtle: the index was already rule-level (`grammar_rules`, 88 entries), but JSON rule payload flattening was wrong. The loader treated nested `rule` objects as strings, so descriptions were stored like Python dict representations and pseudocode was empty. That made returned rules less structured than intended.

Current behavior after fix and rebuild:

1. The translator first analyzes source text with `TranslationAnalysisSignature` to identify grammar concepts and vocabulary terms.
2. Grammar concept terms are sent to `MiradContextRetrieve`.
3. `retrieve_grammar()` searches the ChromaDB `grammar_rules` collection.
4. Each indexed document is one JSON grammar rule from `data/mirad-docs/nirad_grammer_rules.json`.
5. Embeddings are computed from that rule's `retrieval_tags` only.
6. Returned prompt context includes:
   - rule ID
   - description
   - pseudocode
   - examples
   - retrieval tags in metadata
7. Thesaurus chunks are excluded from translator prompt context.

Index rebuild result:

```text
before {'grammar': 88, 'grammar_rules': 88, 'thesaurus': 329}
build {'grammar_rules': 88, 'thesaurus_chunks': 329}
after {'grammar': 88, 'grammar_rules': 88, 'thesaurus': 329}
```

Example retrieval after rebuild for embedded question/clause query:

```text
verb.communication_clause_object_van
- description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object...
- pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:

determiner.interrogative_duh_forms
- description: Interrogative deictic determiners are built with duh-...
- pseudocode: if asking_for_person: use 'duhot?'
```

## Run Summary

| Direction | Examples | Exact match | Normalized match | Estimated true-valid | Notes |
|---|---:|---:|---:|---:|---|
| English → Mirad | 10 | 1/10 | 2/10 | ~2/10 | Most failures are genuine Mirad grammar/morphology errors, not just alternate valid translations. |
| Mirad → English | 10 | 0/10 | 4/10 | ~8-9/10 | Many outputs are valid English equivalents but fail normalized CSV match due punctuation, synonym, or allowed ambiguity. |

Additional retrieval stats:

| Direction | Word-equivalent entries | Context passages | Thesaurus passages |
|---|---:|---:|---:|
| English → Mirad | 333 | 50 | 0 |
| Mirad → English | 440 | 49 | 0 |

## English → Mirad Details

### sent10-en-01-csv-0522

- Input: `unless you say otherwise I will be silent`
- Gold: `Oven et do hyuyen, at dolo.`
- Prediction: `Oven et du hyuay, at dolso.`
- CSV normalized match: no
- True-valid estimate: no
- Error: lexical/form choice and future morphology. `hyuyen` was available but model chose `hyuay`; `dolo` became `dolso`, which does not match the gold future construction.

### sent10-en-02-csv-0749

- Input: `you do not work at home`
- Gold: `Et voy yexe be tam.`
- Prediction: `Et voy yexe be tam.`
- CSV normalized match: yes
- True-valid estimate: yes

### sent10-en-03-csv-0802

- Input: `we would be going home, but we would be happy here`
- Gold: `Yat peyu tam, oy yat su iva him.`
- Prediction: `yat peyu tam, oy yat su iva him`
- CSV normalized match: yes
- True-valid estimate: yes
- Note: exact failed only due capitalization/punctuation.

### sent10-en-04-csv-0808

- Input: `we know that he or she will come and we will be happy`
- Gold: `Yat te van it upo ay yat so iva.`
- Prediction: `Yat te van it upo ay yat ivso.`
- CSV normalized match: no
- True-valid estimate: no
- Error: fused/incorrect `ivso`; should preserve `so iva`.

### sent10-en-05-csv-0861

- Input: `even if I disagree, you will support me`
- Gold: `Gey ven at yontexe, et bolo at.`
- Prediction: `Gel ven at yontexe, et bolo at.`
- CSV normalized match: no
- True-valid estimate: likely no
- Error: `even` equivalent drift. Lexicon supplied `gey`; model emitted `Gel`.

### sent10-en-06-csv-0878

- Input: `before we leave, say hi`
- Gold: `Du hay ja van yat pio.`
- Prediction: `Ja van yat ipu, haydu.`
- CSV normalized match: no
- True-valid estimate: no
- Error: clause ordering/imperative idiom. Translation shifts to something closer to `before we leave, goodbye`, not gold meaning.

### sent10-en-07-csv-0906

- Input: `this teacher is good, but that student is bad`
- Gold: `Hia tuxut se fia, oy hua tixut se fua.`
- Prediction: `hia fia tuxut se fia, oy hua fua tixut se fua`
- CSV normalized match: no
- True-valid estimate: no
- Error: duplicated predicate adjectives as noun modifiers: `good teacher is good`, `bad student is bad`.

### sent10-en-08-csv-0947

- Input: `she played but lost, and he tried but lost`
- Gold: `Iyt eka oy oka, ay wit yeka oy oka.`
- Prediction: `Iyt eka oy oka, ay wit yekwa oy oka.`
- CSV normalized match: no
- True-valid estimate: no
- Error: `tried` became passive-like/malformed `yekwa` instead of `yeka`.

### sent10-en-09-csv-0979

- Input: `this is a good thing and that is mine`
- Gold: `His se fis ay huas se atas.`
- Prediction: `Hias se fis ay huas se atas.`
- CSV normalized match: no
- True-valid estimate: likely no
- Error: `this thing` pronoun form drift: `His` became `Hias`.

### sent10-en-10-csv-0990

- Input: `the man left for no reason, but someone else won`
- Gold: `Ha tob pia hyosav, oy hyut aka.`
- Prediction: `Ha twob ipa boy tesyob, oy heawa hyut aka.`
- CSV normalized match: no
- True-valid estimate: no
- Error: multiple lexical and syntactic drifts. `for no reason` equivalent `hyosav` was available but not used; `left` form wrong; `someone else` expanded awkwardly.

## Mirad → English Details

### sent10-mi-01-csv-0522

- Input: `Oven et do hyuyen, at dolo.`
- Gold: `unless you say otherwise I will be silent`
- Prediction: `Unless you say otherwise, I will be quiet.`
- CSV normalized match: no
- True-valid estimate: yes
- Reason: `quiet` is a valid synonym for `silent`; punctuation/case differs.

### sent10-mi-02-csv-0749

- Input: `Et voy yexe be tam.`
- Gold: `you do not work at home`
- Prediction: `You are not working at home.`
- CSV normalized match: no
- True-valid estimate: borderline yes
- Reason: Present simple vs present progressive differs in English aspect, but for this context it is likely an acceptable natural translation. Count as technically valid if lenient, invalid if strict aspect preservation is required.

### sent10-mi-03-csv-0802

- Input: `Yat peyu tam, oy yat su iva him.`
- Gold: `we would be going home, but we would be happy here`
- Prediction: `We would stay at home, but we would be happy here.`
- CSV normalized match: no
- True-valid estimate: no
- Error: `peyu tam` should preserve going home, not staying at home.

### sent10-mi-04-csv-0808

- Input: `Yat te van it upo ay yat so iva.`
- Gold: `we know that he or she will come and we will be happy`
- Prediction: `We know that he will come and we will be happy.`
- CSV normalized match: no
- True-valid estimate: likely yes
- Reason: `it` can map to he/she/him/her. The CSV expands gender ambiguity as `he or she`; prediction chooses `he`. Valid if gender is unspecified and context permits masculine default, but less explicitly faithful than CSV.

### sent10-mi-05-csv-0861

- Input: `Gey ven at yontexe, et bolo at.`
- Gold: `even if I disagree, you will support me`
- Prediction: `Even if I disagree, you will support me.`
- CSV normalized match: yes
- True-valid estimate: yes

### sent10-mi-06-csv-0878

- Input: `Du hay ja van yat pio.`
- Gold: `before we leave, say hi`
- Prediction: `Say hello before we leave.`
- CSV normalized match: no
- True-valid estimate: yes
- Reason: Same imperative meaning with natural English word order.

### sent10-mi-07-csv-0906

- Input: `Hia tuxut se fia, oy hua tixut se fua.`
- Gold: `this teacher is good, but that student is bad`
- Prediction: `This teacher is good, but that student is bad.`
- CSV normalized match: yes
- True-valid estimate: yes

### sent10-mi-08-csv-0947

- Input: `Iyt eka oy oka, ay wit yeka oy oka.`
- Gold: `she played but lost, and he tried but lost`
- Prediction: `She played but lost, and he tried but lost.`
- CSV normalized match: yes
- True-valid estimate: yes

### sent10-mi-09-csv-0979

- Input: `His se fis ay huas se atas.`
- Gold: `this is a good thing and that is mine`
- Prediction: `This is a good thing, and that is mine.`
- CSV normalized match: yes
- True-valid estimate: yes

### sent10-mi-10-csv-0990

- Input: `Ha tob pia hyosav, oy hyut aka.`
- Gold: `the man left for no reason, but someone else won`
- Prediction: `The person went for no reason, but someone else won.`
- CSV normalized match: no
- True-valid estimate: yes
- Reason: `tob` can mean human/person/man and `pia` can naturally be `went/left`; core semantics preserved.

## Estimated True Accuracy

These are manual estimates from row-level review, not an automated metric.

| Direction | Strict normalized accuracy | Estimated true-valid accuracy | Rationale |
|---|---:|---:|---|
| English → Mirad | 2/10 = 20% | ~2/10 = 20% | Most failures are actual Mirad generation errors: wrong forms, invented/fused words, word-order errors. |
| Mirad → English | 4/10 = 40% | ~8/10 strict, ~9/10 lenient | Several failures are valid paraphrases or synonym choices; one is a real meaning error (`going home` → `stay at home`), one is aspect-borderline. |

## Main Failure Modes

### English → Mirad

1. Ignores supplied exact vocabulary under sentence pressure.
   - `hyosav` available but output `boy tesyob`.
   - `gey` available but output `Gel`.
2. Morphology fusion or invented forms.
   - `so iva` → `ivso`.
   - `yeka` → `yekwa`.
   - `His` → `Hias`.
3. Predicate adjective duplication.
   - `this teacher is good` → `good teacher is good`.
4. Imperative/subordinate-clause ordering remains fragile.
   - `before we leave, say hi` reordered incorrectly.

### Mirad → English

1. Valid paraphrases fail CSV normalized match.
   - `silent` → `quiet`.
   - `say hi` → `say hello`.
   - `man left` → `person went`.
2. Gender ambiguity can be collapsed.
   - `it` as `he/she` became `he`.
3. One clear semantic error.
   - `peyu tam` became `stay at home` instead of `going home`.
4. Aspect may be over-interpreted.
   - `do not work` became `are not working`.

## Recommendations

1. For English → Mirad, add a post-generation validator focused on exact vocabulary preservation and illegal fused forms. The retrieved vocabulary is often present; the model does not consistently obey it.
2. Keep using exact/normalized CSV match for regression, but add a manual or LLM-judge paraphrase validity label for Mirad → English because normalized string match underestimates quality.
3. Add focused dev examples for:
   - exact vocabulary must-use
   - predicate adjective vs noun modifier distinction
   - `so iva` / stative complement patterns
   - `peyu tam` motion/home construction
   - gender-ambiguous `it` expansion policy
4. Consider regenerating compiled DSPy programs after this retrieval change. The live baseline runner now forces fresh uncompiled modules to avoid stale signatures, but optimized compiled programs remain old until rebuilt.
