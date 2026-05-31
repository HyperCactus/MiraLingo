# 3-Candidate Translation Eval

**Date:** 2026-05-27 09:41  
**Model:** deepseek-ai/DeepSeek-V4-Flash  
**Samples:** 100 (seed=20260526)  
**Candidates:** 3 @ [0.1, 0.5, 0.9]  
**Config:** num_context_passages=3, top_k_per_word=0  
**Parallelism:** 32 workers

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 1.0% (1/100) |
| Exact Match | 1.0% (1/100) |
| Avg Judge Score | 0.9/100 |

## Timing

| | |
|--|--|
| Total wall time | 113s |
| Avg per sample | 1.1s |
| Samples/sec | 0.9 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |   0.0 | T=? | whose book is this and whose are these books →  |
|   1 | ✗ |   0.0 | T=? | small houses →  |
|   2 | ✗ |   0.0 | T=? | do you all walk to school →  |
|   3 | ✗ |   0.0 | T=? | our teacher is good but their teacher is bad →  |
|   4 | ✗ |   0.0 | T=? | this guy s house is on fire →  |
|   5 | ✗ |   0.0 | T=? | we were →  |
|   6 | ✗ |   0.0 | T=? | unless they say otherwise we will be silent →  |
|   7 | ✗ |   0.0 | T=? | the teacher is good and the student is bad →  |
|   8 | ✗ |   0.0 | T=? | do you know the answer →  |
|   9 | ✗ |   0.0 | T=? | justice →  |
|  10 | ✗ |   0.0 | T=? | this teacher is very good →  |
|  11 | ✗ |   0.0 | T=? | play or get lost but do not laugh →  |
|  12 | ✗ |   0.0 | T=? | are the stars bright but the night cold →  |
|  13 | ✗ |   0.0 | T=? | he or she will come →  |
|  14 | ✗ |   0.0 | T=? | do →  |
|  15 | ✗ |   0.0 | T=? | everyone s drinks contain ice →  |
|  16 | ✗ |   0.0 | T=? | do they work at home →  |
|  17 | ✗ |   0.0 | T=? | easy easily →  |
|  18 | ✗ |   0.0 | T=? | these persons →  |
|  19 | ✗ |   0.0 | T=? | you are not my father but you know my father →  |
|  20 | ✗ |   0.0 | T=? | the name →  |
|  21 | ✓ |  88.0 | T=0.9 | the houses are ugly → ha tami se vua |
|  22 | ✗ |   0.0 | T=? | that house is beautiful →  |
|  23 | ✗ |   0.0 | T=? | this person →  |
|  24 | ✗ |   0.0 | T=? | they know →  |
|  25 | ✗ |   0.0 | T=? | it is not fair to prejudge someone →  |
|  26 | ✗ |   0.0 | T=? | that teacher is bad →  |
|  27 | ✗ |   0.0 | T=? | the teacher is good →  |
|  28 | ✗ |   0.0 | T=? | this building is a store but this building was a store  →  |
|  29 | ✗ |   0.0 | T=? | you live in the neighborhood →  |
|  30 | ✗ |   0.0 | T=? | he looks like a good worker →  |
|  31 | ✗ |   0.0 | T=? | you will work at home →  |
|  32 | ✗ |   0.0 | T=? | thanks you were very kind →  |
|  33 | ✗ |   0.0 | T=? | you all do not come →  |
|  34 | ✗ |   0.0 | T=? | this person is beautiful and that one is ugly →  |
|  35 | ✗ |   0.0 | T=? | i do not know →  |
|  36 | ✗ |   0.0 | T=? | people often do not love themselves →  |
|  37 | ✗ |   0.0 | T=? | do you know why he did it →  |
|  38 | ✗ |   0.0 | T=? | i did not know you were coming →  |
|  39 | ✗ |   0.0 | T=? | unless i say otherwise you will be silent →  |
|  40 | ✗ |   0.0 | T=? | the small house →  |
|  41 | ✗ |   0.0 | T=? | everywhere i go you are there →  |
|  42 | ✗ |   0.0 | T=? | we worked at home →  |
|  43 | ✗ |   0.0 | T=? | our house is bigger than yours but this house is not as →  |
|  44 | ✗ |   0.0 | T=? | come to the grocery store sometime →  |
|  45 | ✗ |   0.0 | T=? | ugly things →  |
|  46 | ✗ |   0.0 | T=? | this desk is small but good and that desk is big but ba →  |
|  47 | ✗ |   0.0 | T=? | they do not know where he or she went but they know whe →  |
|  48 | ✗ |   0.0 | T=? | captive →  |
|  49 | ✗ |   0.0 | T=? | every man must do his part →  |
|  50 | ✗ |   0.0 | T=? | you all were happy →  |
|  51 | ✗ |   0.0 | T=? | we will be there until the end of the season →  |
|  52 | ✗ |   0.0 | T=? | both cities have grown and any color will be fine →  |
|  53 | ✗ |   0.0 | T=? | before this you lived in the suburbs →  |
|  54 | ✗ |   0.0 | T=? | they will give it to us after we pay →  |
|  55 | ✗ |   0.0 | T=? | that is a good student →  |
|  56 | ✗ |   0.0 | T=? | you all will do it well →  |
|  57 | ✗ |   0.0 | T=? | they came →  |
|  58 | ✗ |   0.0 | T=? | we were happy →  |
|  59 | ✗ |   0.0 | T=? | maybe i may go but i do not know →  |
|  60 | ✗ |   0.0 | T=? | harmful →  |
|  61 | ✗ |   0.0 | T=? | i would go →  |
|  62 | ✗ |   0.0 | T=? | i would do →  |
|  63 | ✗ |   0.0 | T=? | the teachers are good →  |
|  64 | ✗ |   0.0 | T=? | the teachers →  |
|  65 | ✗ |   0.0 | T=? | do they know where we went and where you live →  |
|  66 | ✗ |   0.0 | T=? | while they are here they will do some work for us →  |
|  67 | ✗ |   0.0 | T=? | i do not know where they went but i know where you live →  |
|  68 | ✗ |   0.0 | T=? | the student is good →  |
|  69 | ✗ |   0.0 | T=? | he or she will be →  |
|  70 | ✗ |   0.0 | T=? | you should tell her that →  |
|  71 | ✗ |   0.0 | T=? | they come →  |
|  72 | ✗ |   0.0 | T=? | he or she would go →  |
|  73 | ✗ |   0.0 | T=? | i am not your father but i know your father →  |
|  74 | ✗ |   0.0 | T=? | yours are worth more than mine →  |
|  75 | ✗ |   0.0 | T=? | whenever you talk i laugh →  |
|  76 | ✗ |   0.0 | T=? | that student is good →  |
|  77 | ✗ |   0.0 | T=? | the dog bit me →  |
|  78 | ✗ |   0.0 | T=? | they know that we will come and they will be happy →  |
|  79 | ✗ |   0.0 | T=? | we were indeed there →  |
|  80 | ✗ |   0.0 | T=? | your teacher is good →  |
|  81 | ✗ |   0.0 | T=? | he sings beautifully →  |
|  82 | ✗ |   0.0 | T=? | this book is my favorite →  |
|  83 | ✗ |   0.0 | T=? | the students walk to school every day →  |
|  84 | ✗ |   0.0 | T=? | fathers →  |
|  85 | ✗ |   0.0 | T=? | these words are prohibited but this book is my favorite →  |
|  86 | ✗ |   0.0 | T=? | is that student bad →  |
|  87 | ✗ |   0.0 | T=? | he or she is going home but he or she will work at home →  |
|  88 | ✗ |   0.0 | T=? | the sun has risen so you must get up out of bed →  |
|  89 | ✗ |   0.0 | T=? | they sing beautifully →  |
|  90 | ✗ |   0.0 | T=? | a teacher →  |
|  91 | ✗ |   0.0 | T=? | birds →  |
|  92 | ✗ |   0.0 | T=? | are the stars bright →  |
|  93 | ✗ |   0.0 | T=? | mothers →  |
|  94 | ✗ |   0.0 | T=? | he or she was going home →  |
|  95 | ✗ |   0.0 | T=? | will you ever come back →  |
|  96 | ✗ |   0.0 | T=? | are you married →  |
|  97 | ✗ |   0.0 | T=? | be good →  |
|  98 | ✗ |   0.0 | T=? | the cars →  |
|  99 | ✗ |   0.0 | T=? | every man must do his part and every person must love o →  |
