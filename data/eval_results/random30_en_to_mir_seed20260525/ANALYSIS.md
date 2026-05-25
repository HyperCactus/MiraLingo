# Random 30 English→Mirad Live Evaluation Analysis

- Source CSV: `data/phrases/english-mirad-sentence-pairs.csv`
- Sample file: `data/eval/devset_random30_en_to_mir_seed20260525.json`
- Seed: `20260525`
- Sample size: 30 of 997 CSV rows
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Output dir: `data/eval_results/random30_en_to_mir_seed20260525/`

## Run Summary

| Metric | Value |
|---|---:|
| Live API failures | 0 |
| Exact matches | 14/30 |
| Normalized matches | 18/30 |
| Normalized mismatch count | 12/30 |
| Retrieval context passages | 102 |
| Thesaurus context passages | 0 |
| Word-equivalent entries recorded | 589 |
| Elapsed | 743111 ms |

## Error Taxonomy

| Category | Count | Examples | Notes |
|---|---:|---|---|
| Lexicon/gold disagreement or multi-candidate lexical choice | 5 | r30-04, r30-12, r30-20, r30-21, r30-22 | Model often chose a current lexicon candidate that differs from CSV gold. These are useful for validating whether the CSV or lexicon should be canonical. |
| Grammar particle/order error | 3 | r30-14, r30-17, r30-29 | Missing `ha`, extra `av`, degree/adverb order and negation placement around `gre/gro`. |
| Verb stem/tense/aspect error | 3 | r30-25, r30-27, r30-28 | `upa→pua`, `tambese→besee`, embedded-clause verb forms drift. |
| Question/embedded-clause complexity | 1 | r30-28 | Long question with multiple embedded where-clauses and pronoun roles caused several coupled errors. |

Counts overlap conceptually, but each mismatch is assigned to its dominant cause.

## Mismatch Review

### r30-04-csv-0046

- Input: `the people`
- Gold: `ha tobi`
- Prediction: `hati`
- Taxonomy: lexicon/gold disagreement
- Evidence: word equivalents include `the people → hati`; model followed lexicon. Candidate for dev-set inclusion if goal is to surface CSV-vs-lexicon conflict, otherwise fix/retire pair.

### r30-12-csv-0306

- Input: `come to the grocery store sometime`
- Gold: `Upu ha tolnam hej.`
- Prediction: `Upu telnunam hej.`
- Taxonomy: multi-candidate lexical choice plus article omission
- Evidence: `store → nam, nunam, nyebam`, semantic vocab adds grocery-related candidates. Model chose a specific grocery-store form instead of CSV `ha tolnam`. Good representative for lexical specificity drift.

### r30-14-csv-0374

- Input: `this teacher is the least good`
- Gold: `Hia tuxut se ha gwo fia.`
- Prediction: `Hia tuxut se gwo fia.`
- Taxonomy: grammar article omission
- Evidence: missing `ha` in superlative predicate. Good compact grammar test.

### r30-16-csv-0439

- Input: `go to the store`
- Gold: `Pe ha nam.`
- Prediction: `Pu ha nam.`
- Taxonomy: tense/mood ambiguity
- Evidence: model interpreted bare English as imperative (`Pu`) while CSV expects present/simple (`Pe`). Good representative for imperative-vs-infinitive ambiguity, but source text is ambiguous.

### r30-17-csv-0443

- Input: `buy me a book`
- Gold: `Nusbiu at dyes.`
- Prediction: `Nuxbiu av at dyes.`
- Taxonomy: indirect object/preposition error
- Evidence: extra `av`; wrong/alternate buy root. Good representative for double-object/beneficiary construction.

### r30-20-csv-0609

- Input: `easy easily`
- Gold: `gyua gyuay`
- Prediction: `yuka yukay`
- Taxonomy: lexicon/gold disagreement
- Evidence: word equivalents include `easy → yuka...`, `easily → yukay...`; model followed lexicon. Candidate for CSV-vs-lexicon cleanup, not ideal as model-error dev item.

### r30-21-csv-0611

- Input: `personal personally`
- Gold: `auta autay`
- Prediction: `aota aotay`
- Taxonomy: lexicon/gold disagreement
- Evidence: word equivalents include `personal → aota`, `personally → aotay`; model followed lexicon. Candidate for CSV-vs-lexicon cleanup.

### r30-22-csv-0645

- Input: `your desk is clean`
- Gold: `Eta dresem se vyia.`
- Prediction: `Eta yexsem se vyia.`
- Taxonomy: multi-candidate lexical choice
- Evidence: word equivalents include `desk → dresem, dreutsom, xemsem, yexsem, zyiun`; model chose one valid candidate but not CSV gold. Useful representative for multi-candidate disambiguation.

### r30-25-csv-0718

- Input: `did you come`
- Gold: `Duven et upa?`
- Prediction: `Duven et pua?`
- Taxonomy: verb stem error
- Evidence: exact lexicon includes `come → upya`; model emitted transposed/malformed stem. Good representative for high-priority verb morphology check.

### r30-27-csv-0820

- Input: `we do not know where he or she went, but we know where you live`
- Gold: `Yat voy te hom it pa, oy yat te hom et tambese.`
- Prediction: `Yat voy te hom it pa, oy yat te hom et besee.`
- Taxonomy: verb/locative construction error
- Evidence: first clause correct; second clause loses `tam` in `tambese`. Good representative for embedded where-clause with locative verb.

### r30-28-csv-0827

- Input: `do they know where we went and where you live`
- Gold: `Duven yit te hom yat pa ay hom et tambese?`
- Prediction: `Duven yit te hom yata pen ay hom eta besen?`
- Taxonomy: embedded-clause complexity, pronoun possessive drift, verb tense drift
- Evidence: `yat→yata`, `et→eta`, `pa→pen`, `tambese→besen`. Good representative for complex question and embedded clauses.

### r30-29-csv-0888

- Input: `this teacher is good enough, but that teacher is not good enough`
- Gold: `Hia tuxut se gre fia, oy hua tuxut se gro fia.`
- Prediction: `Hia tuxut se fia gre, oy hua tuxut se voy fia gre.`
- Taxonomy: degree-word ordering and negated-degree idiom
- Evidence: model uses English-like `good enough` order and literal `not good enough`; gold uses `gre/gro + adjective`. Excellent representative for grammar-rule retrieval and idiom behavior.

## Recommended Future Dev Set Candidates

For a smaller representative deterministic set, prefer items that test distinct failure modes and avoid cases where CSV conflicts with current lexicon unless that conflict is the target.

Recommended 8-item set:

1. `r30-14-csv-0374` — article with superlative predicate: `ha gwo fia`.
2. `r30-17-csv-0443` — double-object / beneficiary construction.
3. `r30-22-csv-0645` — multi-candidate lexical disambiguation (`desk`).
4. `r30-25-csv-0718` — verb stem and past question: `upa`.
5. `r30-27-csv-0820` — embedded where-clause with `tambese`.
6. `r30-28-csv-0827` — complex yes/no question with two embedded clauses.
7. `r30-29-csv-0888` — `enough/not enough` degree-word idiom.
8. `r30-12-csv-0306` — grocery-store lexical specificity, if we want one lexicon ambiguity sample.

Optional CSV/lexicon conflict set for cleanup, not model scoring:

- `r30-04-csv-0046` — `the people`: CSV `ha tobi`, lexicon `hati`.
- `r30-20-csv-0609` — `easy/easily`: CSV `gyua`, lexicon `yuka`.
- `r30-21-csv-0611` — `personal/personally`: CSV `auta`, lexicon `aota`.

## Takeaways

1. Retrieval wiring works: examples record word equivalents, grammar context stays thesaurus-free, and live run had 0 API failures.
2. Vocabulary expansion is now visible enough to debug model choices.
3. Main remaining issue is not lack of context; many misses have relevant candidates present but model chooses alternate candidates or ignores grammatical ordering constraints.
4. Future representative dev set should include both model-error cases and a separate lexicon-vs-CSV audit set so scoring does not punish correct use of current lexicon.
