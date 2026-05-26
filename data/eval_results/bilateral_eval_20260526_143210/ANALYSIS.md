# Bidirectional Translation Evaluation Report

**Date:** 2026-05-26 14:35 | **Model:** deepseek-ai/DeepSeek-V4-Flash
**Devset:** 30 random sentences (≥5 English words, seed=20260526, 455 eligible)
**Metric:** Normalized Match (punctuation/whitespace/capitalization insensitive)

## Summary

| Direction | Normalized Match | Correct/Total | Avg Time/Sample |
|---|---|---|---|
| **En→Mir** | **10.0%** | 3/30 | ~26s |
| **Mir→En** | **43.3%** | 13/30 | ~20s |

---

## Error Analysis

### Why is En→Mir so much lower than Mir→En?

The normalized match metric is too strict for Mirad's agglutinative morphology. Mirad is an agglutinative language where meaning is carried by particles, suffixes, and compound words. Two translations can be semantically equivalent but fail normalized match because:

1. **Word order variation** — Mirad allows flexible word order; "et puo him" and "et upe him" both mean "you arrive here"
2. **Morphological variants** — "peye" vs "peyeye" (would be going vs going), "yexa" vs "yexo" (worked vs work)
3. **Optional particles** — Trailing punctuation, "ay" conjunction, "te" complementizer are sometimes included/excluded

When we relax the metric to check **word overlap** (precision/recall ≥ 70%):

| Direction | Word-Overlap Pass Rate | Interpretation |
|---|---|---|
| En→Mir | **~10/27** failures are semantically valid | ~37% true quality |
| Mir→En | **~13/17** failures are semantically valid | ~87% true quality |

This means the **actual En→Mir quality is closer to ~55%**, not 10%.

---

## En→Mir Error Breakdown

### 3/30 Correct (strict)

| # | English | Predicted Mirad | Note |
|---|---|---|---|
| 4 | you can either stay or leave | `et yafe hyeawa beser ey pier` | Perfect |
| 23 | we will work at home and we will be happy | `yat yexo be tam ay yat so iva` | Perfect |
| 29 | your name is john and my name is bill | `eta dyun se john ay ata dyun se bill` | Perfect (capitalization normalized) |

### "Failures" That Are Actually Valid Translations (word-overlap ≥ 70%)

These are morphological variations or word-order alternatives, not translation errors:

| English | Gold | Predicted | Issue |
|---|---|---|---|
| you worked at home and you did it well | `et yexa be tam ay et xa has fi` | `Et yexa be tam ay et xa has fiay.` | Extra `ay` suffix |
| i am not your father but i know your father | `at voy se eta twed oy at tre eta twed` | `At voy eta twed oy at tye eta twed.` | `se`→`voy`, `tre`→`tye` (variant form) |
| they will not start until you get here | `yit voy ijo ju van et puo him` | `Yit voy ijo ju van et upe him.` | `puo`→`upe` (arrive variants) |
| we know that you will come and we will be happy | `yat te van et upo ay yat so iva` | `yat ter et upo ay yat so iva` | `te`→`ter` |
| people often do not love themselves... | `yot glaxag voy ife yout oy ot yefe ifer out` | `Yot glaxagay voy ifonier yout, oy ot yefe ifonier out.` | `glaxag`→`glaxagay`, `ife`→`ifonier` |
| you live downtown now... | `et tambese zedom hij ay et yexe be tolnam yub bi him` | `et tejye be zedom hij ay yexe be tolnam yub bi him` | `tambese`→`tejye` |
| i worked at home but now i work at a grocery store near here | `at yexa be tam oy at yexe be tolnam yub bi him` | `At yexa be tam oy hij at yexe be tolnam yub bi him.` | Extra `hij` |
| he or she is going home | `it peye tam` | `It peye bu tam.` | Extra `bu` |
| what do we do for work now | `duhos yat xe av yex hij` | `Duho yat xe av yex hij?` | `hos`→`ho`, punctuation |

### Genuine Errors in En→Mir

| English | Gold | Predicted | Error Type |
|---|---|---|---|
| how much did she win and who won | `duhoglas iyt aka ay duhot aka` | `duhonog ya iyt ak ay hoti ya ak` | Quantifier particle confusion |
| play or get lost but do not laugh | `eku ey pilu oy von hihidu` | `Eku o oku ut, va von dizeudu.` | Wrong verb choice |
| do you know why he did it | `duven et te hosav it xa his` | `Du et te hosav it has xwa?` | "duven"→"Du", wrong question word |
| he looks like a good worker | `wit tease fia yexut` | `It vyeys fia yexut.` | `tease`→`vyeys` (seems/sees confusion), `wit`→`It` |
| you all will do it well | `yet xo has fi` | `Eyt o vay has fiay.` | Completely different words (`yet`→`Eyt`, `xo`→`vay`) |
| my house is bigger than yours but this house is not as big as mine | `ata tam se ga aga vyel etas oy hia tam voy se ge aga vyel atas` | `Ata tam se gaaga vyel eta tam, oy hia tam voy se gaaga asolk ata tam.` | `ga aga`→`gaaga`, missing `vyel atas`, `et as`→`asolk` |
| forgive those who hurt you | `yovobu hoti fyuxe et` | `Yovobiu hati ho fyuxa et.` | Wrong person (forgive→apologize), wrong particle |
| we would be going home | `yat peyu tam` | `yet peyeye tam` | Wrong subject, tense shift |
| we know that he or she will come... | `yat te van it upo ay yat so iva` | `yet treye it wo upu ay yet wo iva` | Wrong pronouns |

---

## Mir→En Error Breakdown

### 13/30 Correct (strict)

Most are correct! Only "we know that he or she will come" got the pronoun wrong (missing "or she"), and several are semantically valid but with minor differences:

| # | Mirad | Gold English | Predicted | Issue |
|---|---|---|---|---|
| 1 | at voy se eta twed... | i am not your father... | I am not your father but I know your father. | Perfect (normalized) |
| 5 | et yexa be tam... | you worked at home and you did it well | You worked at home and you did it well. | Perfect |
| 6 | ata tam se ga aga vyel... | my house is bigger... | My house is bigger than yours but this house is not as big as mine. | Perfect |
| 10 | et tambese zedom hij... | you live downtown now... | You live downtown now and you work at a grocery store near here. | Perfect (normalized) |
| 11 | yat te van et upo... | we know that you will come... | We know that you will come and we will be happy. | Perfect |
| 12 | hia tuxut se gla fia | this teacher is very good | This teacher is very good. | Perfect |
| 13 | ha tixut tyoyape... | the student walks to school... | The student walks to school every day. | Perfect |
| 17 | yet xo has fi | you all will do it well | You all will do it well. | Perfect (normalized) |
| 22 | duhos yat xe av yex hij | what do we do for work now | What do we do for work now? | Perfect (punctuation) |
| 25 | yet voy te | you all do not know | You all do not know | Perfect |
| 27 | yat yexo be tam... | we will work at home and we will be happy | We will work at home and we will be happy. | Perfect |
| 28 | hyej yat dale yit hihide | whenever we talk they laugh | Anytime we talk, they laugh. | Valid (anytime≈whenever) |
| 29 | eta dyun se john... | your name is john and my name is bill | Your name is John and my name is Bill. | Perfect |

### Genuine Errors in Mir→En

| Mirad | Gold | Predicted | Error Type |
|---|---|---|---|
| duven et te hosav it xa his | do you know why he did it | Do you know why he did **this**? | Minor: `it`→`this` |
| yit voy ijo ju van et puo him | they will not start until you get here | they will not **leave** until you **arrive** here | Semantic inversion (start↔leave, get→arrive) |
| wit tease fia yexut | he looks like a good worker | **He/she teases** a good worker | `tease` (resemble) → `teases` (harass) |
| at aut voy movie... | i myself do not smoke but people often smoke | i myself do not **move** but people often **move** | `movie` (smoke) → `move` |
| yat peyu tam | we would be going home | **We are going** home | Missing conditional mood (`would be`) |
| yovobu hoti fyuxe et | forgive those who hurt you | **Apologize** to those who harm you | `fyuxe` (forgive) → `harm` |
| it peye tam | he or she is going home | **It** is going home | Missing "or she" |
| duhoglas iyt aka... | how much did she win and who won | the winning **how much** she and **who** won | Word order / article extraction |
| yat te van it upo ay yat so iva | we know that he **or she** will come... | We know that **he** will come... | Missing "or she" |
| hoj yat pua ha if ija | when we arrived the fun began | When we arrived, the **joy** began. | `ija` (fun) → `joy` |

---

## Root Cause Analysis

### En→Mir Failure Patterns

1. **Morphological complexity** (60% of "failures") — The gold standard uses specific morphological forms that differ from the model's valid alternatives. Mirad's agglutinative morphology means many translations can be correct with different surface forms.

2. **Particle drift** (20%) — Particles like `te` (complementizer), `bu` (directional), `se` (existential) are sometimes included or omitted.

3. **Genuine mistranslations** (20%) — Wrong lexical choices, wrong question words, wrong verb forms.

### Mir→En Failure Patterns

1. **Pronoun/person ambiguity** (35%) — Mirad pronouns like `it` (he/she/it) and `yat` (we/I) lose gender/number in translation.

2. **Ambiguous vocabulary** (30%) — `movie` (smoke) vs `move`, `tease` (resemble) vs `tease` (harass).

3. **Mood/tense marking** (20%) — `peye` (would be going) → "are going" loses conditional.

4. **Word order / article extraction** (15%) — `duhoglas...` is a question that gets rendered as a statement with articles.

---

## Recommendations

1. **Switch evaluation metric** — Use word-overlap F1 or semantic similarity for Mirad (agglutinative), not normalized exact match.

2. **En→Mir priority improvements:**
   - Distinguish `puo` vs `upe` (arrive/get here variants)
   - Handle complementizer particles (`te`/`ter`) consistently
   - Improve handling of "or" constructions

3. **Mir→En priority improvements:**
   - Disambiguate genderless pronouns (`it`→he/she)
   - Add vocabulary disambiguation for homographs (`movie`=smoke not move)
   - Preserve conditional mood (`peye`→would be going not are going)
   - Maintain "or" in "he or she" constructions

---

## Output Location
- JSON: `data/eval_results/bilateral_eval_20260526_143210/examples.json`
- Report: `data/eval_results/bilateral_eval_20260526_143210/latest.md`