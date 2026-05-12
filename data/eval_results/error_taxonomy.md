# Error Taxonomy — DeepSeek-V4-Flash LabeledFewShot k=5
**Eval set:** 39 gold pairs | **Hits:** 22 (56.4%) | **Misses:** 17 (43.6%)**

Baseline: `labeled_fewshot_k5.json` — DeepSeek-V4-Flash, 5 retrieval passages, k=5 few-shot examples

---

## A. Particle Confusion (2 errors)

### A1: be ↔ bi — index 0
**English:** "This is the biggest house in our neighborhood."
| | Text |
|---|---|
| Gold | `His se ha gwa aga tam bi yata yubem.` |
| Predicted | `His se ha gwa aga tam be yata yubyem.` |

Particle `bi` (benefactive/associative) rendered as `be`. Also note `yubyem` vs gold `yubem` (possible variant form).

### A2: ge → vyel — index 3
**English:** "This house is not as big as mine."
| | Text |
|---|---|
| Gold | `Hia tam voy se ge aga vyel atas.` |
| Predicted | `Hia tam voy se ge aga ge atas.` |

Comparative particle `vyel` collapsed to `ge` (a different word entirely). The model repeated `ge` instead of inserting the comparative linker.

---

## B. Progressive Morphology — -ye Suffix (2 errors)

### B1: missing -ye on sleeping verb — index 14
**English:** "The baby is still sleeping."
| | Text |
|---|---|
| Gold | `Ha tobud gaj tujeye.` |
| Predicted | `Ha tajyat gaj tujeye.` |

`tobud` (baby) mistranslated as `tajyat` (wrong lexicon), but the progressive `-ye` suffix on `tujeye` is correctly produced.

### B2: -ye suffix dropped on weather verb — index 34
**English:** "It is raining."
| | Text |
|---|---|
| Gold | `Mamileye.` |
| Predicted | `Mamilie.` |

Stem `mamili-` is present but the final `-eye` progressive suffix is truncated to `-ie`. Likely the model is producing a different conjugation than the canonical `-eye` form.

---

## C. Lexicon Gaps / Wrong Word (6 errors)

The model selected a plausible but incorrect Mirad word from its lexicon.

### C1: unnecessary insertion — index 2
**English:** "You must do it as quickly as possible."
| | Text |
|---|---|
| Gold | `Et yefe xer gwa ig.` |
| Predicted | `Et yefe xer has gwa ig.` |

Gold is a compressed idiom meaning "do it quickly." The model inserted `has` (a verb?) where none should exist.

### C2: ayv dropped — index 8
**English:** "The whole world knows about you."
| | Text |
|---|---|
| Gold | `Ha ayna mir te ayv et.` |
| Predicted | `Ha ayna mir te be et.` |

`ayv` (second-person pronoun object) was dropped; `be` is a generic placeholder.

### C3: ese → amilk — index 11
**English:** "I think, therefore I am."
| | Text |
|---|---|
| Gold | `At texe, av hus, at ese.` |
| Predicted | `At texe, av hus at amilk.` |

`ese` (copula "I am") is replaced by `amilk` (water/named entity?). Completely different lexeme.

### C4: ted → twed — index 16
**English:** "I am not your father."
| | Text |
|---|---|
| Gold | `At voy se eta ted.` |
| Predicted | `At voy se eta twed.` |

`ted` (father) rendered as `twed` — possibly the model confused consonant clusters or applied wrong word choice.

### C5: bu dropped — index 22
**English:** "It seems to me that..."
| | Text |
|---|---|
| Gold | `Tease bu at van...` |
| Predicted | `Tease at van...` |

`bu` (indirect object particle) dropped entirely, changing the semantics.

### C6: object-verb order inversion — index 35
**English:** "I pity you."
| | Text |
|---|---|
| Gold | `At yantipuvse et.` |
| Predicted | `At et yantipuvie.` |

Model produced a different conjugation (`yantipuvie` vs `yantipuvse`) AND placed object `et` before the verb — a structural inversion.

---

## D. Structural / Hallucination (7 errors)

The model's output is substantially wrong — different sentence structure, nonsensical words, or severe compression.

### D1: exclamation structure hallucinated — index 7
**English:** "How glad I am that you came!"
| | Text |
|---|---|
| Gold | `Hoogla iva se at van et upa!` |
| Predicted | `Hyey, duhogla iva at se van et upa!` |

Gold uses `Hoogla` (how-adverb form) with exclamation particle `upa`. Predicted uses `Hyey` (greeting) and `duhogla` (different root). Entire structure is different.

### D2: idiom hallucinated — index 12
**English:** "Let the buyer beware!"
| | Text |
|---|---|
| Gold | `Van ha nuxbiut bikiu!` |
| Predicted | `Afu ha niut biksu!` |

No overlap between gold and prediction. Both are completely different vocabulary and structure.

### D3: exclamation compression hallucinated — index 13
**English:** "What a day this has been!"
| | Text |
|---|---|
| Gold | `Hooa jub his saye!` |
| Predicted | `Hyey hia jub sa!` |

`Hyey` (greeting) appears again instead of exclamation particle. The gold `Hooa` (what) is missing. `saye` vs `sa` — compressed/shortened.

### D4: swim → different verb form — index 15
**English:** "I swim better than you."
| | Text |
|---|---|
| Gold | `At pipe ga fi vyel et.` |
| Predicted | `At milzyepe ga fiay vyel et.` |

`pipe` (swim) replaced by `milzyepe` — wrong word. Also `fi` vs `fiay` (variant form).

### D5: positive construction used instead of negative — index 23
**English:** "It doesn't bother me."
| | Text |
|---|---|
| Gold | `Voy tepoboxe at.` |
| Predicted | `Hus voy obose at.` |

Gold is the correct negative form. Prediction uses `Hus voy obose` (it [subject] not [verb]) — subject-verb order inversion with `hust` absent. Completely different structure.

### D6: motion verb hallucinated — index 25
**English:** "Go around the block."
| | Text |
|---|---|
| Gold | `Yuzper ha tomyan.` |
| Predicted | `Pu yuz bi ha domgones.` |

No overlap. `Yuzper` (go-around) replaced by `Pu` (go) + `yuz` + wrong noun `domgones` vs `tomyan`.

### D7: water verb wrong form — index 29
**English:** "To water the plants."
| | Text |
|---|---|
| Gold | `Miluer ha vobi.` |
| Predicted | `Miler ha fobi.` |

`miluer` (water-verb) replaced by `miler`; `vobi` (plants) replaced by `fobi` (different word).

---

## Summary Table

| Category | Count | % of total | Description |
|---|---|---|---|
| Particle confusion | 2 | 5.1% | be↔bi, ge→vyel particle errors |
| Progressive morphology | 2 | 5.1% | -ye suffix dropped |
| Lexicon gaps/wrong word | 6 | 15.4% | Plausible but wrong lexeme chosen |
| Structural/hallucination | 7 | 17.9% | Sentence structure broken or total hallucination |
| **Total misses** | **17** | **43.6%** | |
| Hits | 22 | 56.4% | Correct translations |

---

## Key Patterns for Post-Processor

1. **Particle rules**: `bi` vs `be` disambiguation; `vyel` comparative must appear when `ge aga` (as ... as) pattern present
2. **-ye suffix preservation**: Weather/stative verbs in -eye must not be truncated to -ie
3. **bu preservation**: Subordinate clause particle `bu` must not be dropped
4. **Structural templates**: Hallucination category suggests the model sometimes ignores the example prompt format; a constrained-output post-processor could enforce sentence-boundary rules