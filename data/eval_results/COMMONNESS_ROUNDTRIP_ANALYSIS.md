# Commonness-Weighted Round-Trip Analysis

**Date:** 2026-05-19  
**Samples:** 250/1000 completed (resume-safe CSV in progress)  
**Sampling:** Log-prob weighted (1/log(i+2)) from 1.99M sentences sorted by commonness (descending)  
**Method:** En→Mir→En round-trip using compiled DSPy programs (DeepSeek-V4-Flash), jina-v5 embeddings  

---

## 1. Aggregate Results

| Metric | Value |
|--------|-------|
| Total completed | 250/1000 |
| Exact match (case/punct-tolerant) | 59/250 (23.6%) |
| Mean semantic similarity | 0.9026 |
| Median semantic similarity | 0.9595 |
| Commonness range in sample | 1.73 – 6.70 |

### Semantic Similarity by Commonness Quartile

| Quartile | Commonness Range | N | Mean Sem Sim | Median Sem Sim |
|----------|-----------------|---|-------------|----------------|
| Q1 (rarest) | 1.73 – 5.38 | 63 | 0.8645 | 0.9392 |
| Q2 | 5.38 – 5.47 | 64 | 0.8982 | 0.9595 |
| Q3 | 5.47 – 5.68 | 63 | 0.9339 | 0.9717 |
| Q4 (common) | 5.68 – 6.70 | 63 | 0.9125 | 0.9616 |

Q3 (mid-frequency) performs best. Rare sentences (Q1) perform worst (0.86 mean), likely due to OOV words and rare constructions. Very common sentences (Q4) dip slightly, possibly because common phrases have more valid Mirad translations, increasing ambiguity.

### Semantic Similarity Distribution

| Threshold | Count | Percentage |
|-----------|-------|-----------|
| ≥ 0.98 | 97 | 38.8% |
| ≥ 0.95 | 139 | 55.6% |
| ≥ 0.90 | 166 | 66.4% |
| ≥ 0.85 | 190 | 76.0% |
| ≥ 0.70 | 229 | 91.6% |

---

## 2. Error Attribution: En→Mir vs Mir→En

Of 250 round-trip translations:

| Attribution | Count | % | Description |
|------------|-------|---|-------------|
| **Exact match** | 59 | 23.6% | Round-trip matches original exactly |
| **Style only** | 55 | 22.0% | Meaning preserved, only minor padding ("it" → "that thing") |
| **Mir→En errors** | 11 | 4.4% | Mirad was correct; back-translation introduced errors |
| **En→Mir errors** | 4 | 1.6% | English→Mirad introduced errors |
| **Ambiguous** | 121 | 48.4% | Cannot cleanly attribute to one direction |

### Mir→En Errors (4.4%)

| Error Type | Count | Description |
|-----------|-------|-------------|
| **Tense lost** | 9 | Mirad has past-tense marker (-a), but Mir→En outputs present tense |
| **Pronoun role swap** | 1 | "want ME to tell YOU" → "want to tell ME" — same pronouns in Mirad, wrong roles in English |
| **Deictic swap** | 1 | "this way" → "that way" — `huyen` (this-way) read as distal |

**Root cause:** The Mir→En model misreads verb suffixes and pronoun case assignments. Mirad's tense system (-a past, -e present, -o future) is systematic but the back-translation model often ignores the suffix, defaulting to present tense. Pronoun role is encoded by position in Mirad, not by case marking, making it easy for the LM to misassign subject/object roles.

### En→Mir Errors (1.6%)

| Error Type | Count | Description |
|-----------|-------|-------------|
| **Tense not conveyed** | 4 | English past tense → Mirad present tense |

**Root cause:** The En→Mir model sometimes fails to add the past-tense suffix `-a` to the main verb, producing present tense instead. This is particularly common with the "used to" construction and perfect tenses.

---

## 3. Error Taxonomy

### Category 1: Tense Errors (5.2% of total, 7% of divergences)

**Most common pattern:** Past-tense English → present-tense Mirad → present-tense English.

Examples:
- "The horse **did** not want to get inside" → "The horse **does** not want to go into" (Mirad: `voy fa` present)
- "Over time, he **got** used to" → "Eventually, he **felt** comfortable in" (different meaning!)
- "I'm not the same man I **used to** be" → "I am not the same man I **saw**" (semantic shift)

**Attribution:** Roughly 2:1 Mir→En vs En→Mir. The Mir→En model drops past-tense markers more often than En→Mir omits them.

### Category 2: Pronoun Role Errors (0.4%)

**Pattern:** Subject/object roles of pronouns get reassigned during back-translation.

Example:
- EN: "Do you want **me** to tell **you**" → MIR: `Duven et fe der at et hos...` → RT: "Do you want to tell **me**"
  - The Mirad has `at` (I/me) and `et` (you) in the right positions, but the Mir→En model re-interprets who is telling whom.
  - **sem = 0.98** despite complete meaning inversion!

### Category 3: Deictic Shifts (0.4%)

**Pattern:** Proximal/distal deictics (`this`/`that`, `here`/`there`) get swapped.

Example:
- EN: "I've felt **this** way" → MIR: `...toswa huyen` (this-way) → RT: "I felt **that** way" (sem=0.98)
  - `huyen` (this-way/proximal) is correctly in Mirad, but Mir→En outputs "that way" (distal).

### Category 4: Quantifier Drift (0.4%)

**Pattern:** Mirad quantifiers have multiple valid English renderings; the Mir→En model picks the wrong one.

Example:
- EN: "**at least** three times" → MIR: `gwo ay iwa jodi` (minimum and three times) → RT: "**as few as possible** and three times"
  - `gwo` means both "at least" and "at most / minimum"; Mir→En chose the wrong disambiguation.

### Category 5: Negation Preservation (2.4%)

Most negation changes are **preservation of meaning with style shift** (e.g., "can't" → "cannot", "have no time" → "do not have time"). Only 2 out of 6 negation cases involved actual meaning change, and those were lower sem sim (0.68, 0.85).

### Category 6: Modal Drift (0.4%)

- "We **should** study" → `Yat yeyfe tixer` → "We **must** study" (sem=0.97)
  - `yeyfe` can mean "should" or "must" — correct Mirad, wrong English disambiguation by Mir→En.

### Category 7: Style/Padding Only (22.0%)

These are meaning-preserving divergences where the round-trip adds filler words or expands contractions:
- "it" → "that thing" (`hus` → "that thing")
- "can't" → "cannot"
- "I'm" → "I am"
- "don't" → "do not"
- Added "that" as complementizer

These have no impact on meaning and reflect Mirad's systematic determiner/complementizer system.

---

## 4. Critical Finding: Semantic Similarity Masks Meaning Inversion

The most important finding is that **semantic similarity scores ≥0.95 can mask complete meaning inversion**:

| # | Original | Round-trip | Sem | Error Type |
|---|----------|-----------|-----|------------|
| 1 | "Do you want **me** to tell **you**" | "Do you want to tell **me**" | 0.98 | Pronoun swap |
| 2 | "**this** way" | "**that** way" | 0.98 | Deictic swap |
| 3 | "**at least** three times" | "**as few as possible** and three times" | 0.94 | Quantifier inversion |
| 4 | "We **should** study" | "We **must** study" | 0.97 | Modal drift |
| 5 | "he **got** used to" | "he **felt** comfortable in" | 0.87 | Tense + semantic drift |

Cases 1–3 are **meaning inversions** at sem ≥ 0.94. The embedding model sees overlapping topic words and gives high similarity, but the factual content (who did what, which thing, how much) is wrong.

**Implication:** Semantic similarity measures **topic overlap**, not **factual accuracy**. It cannot detect:
- Pronoun role swaps (who did what to whom)
- Deictic inversions (this/that, here/there)
- Quantifier inversions (at least → at most)
- Modal drift (should → must, can → may)

---

## 5. Attribution Summary

```
Round-trip divergences (191/250 not exact match):
  ┌─────────────────────────────────────┬───────┬────────┐
  │ Attribution                         │ Count │    %    │
  ├─────────────────────────────────────┼───────┼────────┤
  │ Style/padding only (meaning OK)    │    55 │  22.0% │
  │ Mir→En errors (meaning changed)    │    11 │   4.4% │
  │   - Tense lost in back-translation │     9 │   3.6% │
  │   - Pronoun role swap              │     1 │   0.4% │
  │   - Deictic (this/that) swap       │     1 │   0.4% │
  │ En→Mir errors (meaning changed)    │     4 │   1.6% │
  │   - Tense not conveyed             │     4 │   1.6% │
  │ Ambiguous / both directions        │   121 │  48.4% │
  │   - Synonym substitution           │  ~60  │  ~24%  │
  │   - Tense shift (unattributed)     │  ~15  │   ~6%  │
  │   - Negation style shift           │     6 │   2.4% │
  │   - Other meaning change           │  ~40  │  ~16% │
  └─────────────────────────────────────┴───────┴────────┘
```

**Key takeaway:** Mir→En is the **weaker link**. Of the clearly attributable errors, roughly **3∶1** are Mir→En (back-translation) rather than En→Mir (forward translation). The Mir→En model:
1. Drops tense markers (9 cases)
2. Misassigns pronoun roles (1 case, but sem=0.98!)
3. Confuses proximal/distal deictics (1 case)
4. Picks wrong quantifier disambiguation (1 case)

En→Mir errors are simpler — mostly failing to convey English past tense.

---

## 6. Implications for Translation Quality Assessment

1. **Semantic similarity alone is insufficient** for quality assessment. It cannot detect meaning inversions at scores ≥0.94.

2. **The Mir→En model is the bottleneck.** Improving Mir→En (especially tense preservation and pronoun role accuracy) would improve round-trip quality more than improving En→Mir.

3. **A useful quality metric would combine:**
   - Semantic similarity (catches topic divergence)
   - Tense consistency check (binary: same tense or not?)
   - Pronoun role check (compare subject/object assignments)
   - Negation check (same polarity or not?)
   - Quantifier/logical operator check (at least vs at most, all vs some, etc.)

4. **For rare sentences (Q1), quality drops noticeably** (median 0.94 vs 0.97 for mid-frequency). This suggests the LM handles common patterns well but struggles with rare constructions and vocabulary.

---

## 7. Files

| File | Description |
|------|-------------|
| `data/phrases/english_sentences.csv` | 1.99M sentences, annotated with `commonness` column, sorted descending |
| `data/phrases/commonness_roundtrip_results.csv` | Round-trip results (250/1000 completed, resume-safe) |
| `packages/translator/scripts/commonness_roundtrip_eval.py` | Script: annotate, sample, translate, measure — resume-safe |

**To resume:** Run `python commonness_roundtrip_eval.py --skip-annotation` to continue translating remaining 750 sentences.