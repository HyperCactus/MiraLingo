# Translation Evaluation Report

**Date:** 2026-05-26T16:10:43.916633 | **Model:** deepseek-ai/DeepSeek-V4-Flash
**Direction:** en_to_mir | **Samples:** 30
**Data:** /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval/train.json
**Parallelism:** 8 workers

## Metrics Summary

| Metric | Score | Count |
|---|---|---|
| Normalized Match | 26.7% | 8/30 |
| Word Overlap F1 | 73.8% | 17/30 (≥0.7) |
| Avg Time/Sample | 31494ms | — |

## All Results

| # | Source | Gold | Predicted | Score | Time |
|---|---|---|---|---|---|
| 0 | this guy s house is on fire | hwuta tam magseye | Hia twoba tam se be mag. | ✗ | 46126ms |
| 1 | go to the store and buy me a book | pe ha nam ay nusbiu at dy | Pu bu ha nam ay bixu at d | ✗ | 38567ms |
| 2 | if i want to get results i must work har | ven at fe iber ixuni at y | ven at fone bier xiuni, a | ✗ | 44554ms |
| 3 | you all do not work at home | yet voy yexe be tam | Yet voy be tam xe. | ✗ | 36058ms |
| 4 | this building will be a store and this b | hia tom so nam ay hia tom | Hia tom so nam ay hia tom | ✓ | 37679ms |
| 5 | this teacher is possibly better than tha | hia tuxut se vey ga fia v | Hia tuxut vey se ga fia v | ✗ | 43588ms |
| 6 | while you are here you will work at home | je van et so him et yexo  | Je van et se him, et yexo | ✗ | 46048ms |
| 7 | the teacher is good and the student is b | ha tuxut se fia ay ha tix | ha tuxut se fia ay ha tix | ✓ | 33405ms |
| 8 | i know that he or she will come and i wi | at te van it upo ay at so | At te van it upo ay at so | ✓ | 38947ms |
| 9 | he or she would go | it pu | it pu | ✓ | 28054ms |
| 10 | you all will do it well | yet xo has fi | yet xo is fiay | ✗ | 11450ms |
| 11 | this teacher is very good | hia tuxut se gla fia | hia gla fia tuxut | ✗ | 12843ms |
| 12 | both cities have grown and any color wil | hyaewa domi agsaye ay hye | Hyaewa domi agsa ay hyea  | ✗ | 40156ms |
| 13 | they will not start until you get here | yit voy ijo ju van et puo | Yit vò ijo ju van et apu  | ✗ | 29461ms |
| 14 | yours are worth more than mine | etasi naze ga vyel atasi | Eytasi naze ga vyel atasi | ✗ | 28294ms |
| 15 | we knew that you would come but we did n | yat ta van et upo oy yat  | Yat ta ad yet upo, va yat | ✗ | 25552ms |
| 16 | do we know where you went and where they | duven yat te hom et pa ay | Du yet te hem et pa ay he | ✗ | 38533ms |
| 17 | play or get lost but do not laugh | eku ey pilu oy von hihidu | Eku ey Mepoku ab Du dizeu | ✗ | 56671ms |
| 18 | you will do it well | et xo has fi | et xo is fiay | ✗ | 24466ms |
| 19 | he or she is going home but he or she wi | it peye tam oy it yexo be | it pe tam oy it yexo be t | ✗ | 42139ms |
| 20 | you all were going home but you all came | yet peya tam oy yet upa h | Yet pa bu tam oy yet upa  | ✗ | 24536ms |
| 21 | unless we say otherwise they will be sil | oven yat do hyuyen yit do | oven yet deu hyuyen, yit  | ✗ | 38436ms |
| 22 | do they walk to school today | duven yit tyoyapeye tista | Tyope yit bu tistam hijub | ✗ | 21394ms |
| 23 | whenever you talk i laugh | hyej et dale at hihide | Hyejod ho et dale, at diz | ✗ | 21942ms |
| 24 | my name is bill and your name is john | ata dyun se bill ay eta d | Ata dyun se Bill ay eta d | ✓ | 23616ms |
| 25 | they will work at home and they will be  | yit yexo be tam ay yit so | Yit yexo be tam ay yit so | ✓ | 24080ms |
| 26 | do you know the answer | duven et te ha dud | Duven et te ha dud? | ✓ | 19267ms |
| 27 | the students walk to school every day | ha tixuti tyoyape tistam  | Ha tixuti tyope bu tistam | ✗ | 20732ms |
| 28 | they know that we will come and they wil | yit te van yat upo ay yit | Yit te van yat upo ay yit | ✓ | 22432ms |
| 29 | do they know where we went and where you | duven yit te hom yat pa a | Duven yit ter duhom yat p | ✗ | 25812ms |