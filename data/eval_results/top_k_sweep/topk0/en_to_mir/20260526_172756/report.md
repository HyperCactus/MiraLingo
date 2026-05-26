# Translation Evaluation Report

**Date:** 2026-05-26T17:29:25.470904 | **Model:** deepseek-ai/DeepSeek-V4-Flash
**Direction:** en_to_mir | **Samples:** 30
**Data:** /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval/train.json
**Parallelism:** 8 workers

## Metrics Summary

| Metric | Score | Count |
|---|---|---|
| Normalized Match | 13.3% | 4/30 |
| Word Overlap F1 | 62.4% | 14/30 (≥0.7) |
| Avg Time/Sample | 17366ms | — |

## All Results

| # | Source | Gold | Predicted | Score | Time |
|---|---|---|---|---|---|
| 0 | this guy s house is on fire | hwuta tam magseye | Hia aota tam se ap mag. | ✗ | 47665ms |
| 1 | go to the store and buy me a book | pe ha nam ay nusbiu at dy | Pu bu ha nam ay nixu at d | ✗ | 47627ms |
| 2 | if i want to get results i must work har | ven at fe iber ixuni at y | Ven at foner ixuni, at ye | ✗ | 46719ms |
| 3 | you all do not work at home | yet voy yexe be tam | yet voy yexe be tam | ✓ | 81320ms |
| 4 | this building will be a store and this b | hia tom so nam ay hia tom | hia tom so nam ay hia tom | ✓ | 48215ms |
| 5 | this teacher is possibly better than tha | hia tuxut se vey ga fia v | Hia tuxut se veay ga fia  | ✗ | 48418ms |
| 6 | while you are here you will work at home | je van et so him et yexo  | je van et beser him et oy | ✗ | 47175ms |
| 7 | the teacher is good and the student is b | ha tuxut se fia ay ha tix | Ha tuxut se fia ay ha tix | ✓ | 49752ms |
| 8 | i know that he or she will come and i wi | at te van it upo ay at so | At tru it u upu ay at u i | ✗ | 4845ms |
| 9 | he or she would go | it pu | it piu | ✗ | 5241ms |
| 10 | you all will do it well | yet xo has fi | Eyt o vay has fiay. | ✗ | 4612ms |
| 11 | this teacher is very good | hia tuxut se gla fia | hiatuxut gla fia | ✗ | 4410ms |
| 12 | both cities have grown and any color wil | hyaewa domi agsaye ay hye | Hyaewa domi agxwa se ay h | ✗ | 5817ms |
| 13 | they will not start until you get here | yit voy ijo ju van et puo | yit voy oij ju van et pu  | ✗ | 5528ms |
| 14 | yours are worth more than mine | etasi naze ga vyel atasi | Etas ga nazea vyel atas. | ✗ | 4486ms |
| 15 | we knew that you would come but we did n | yat ta van et upo oy yat  | Yat twa van et upo, yat v | ✗ | 5039ms |
| 16 | do we know where you went and where they | duven yat te hom et pa ay | Yes ay hem et pa ay hem y | ✗ | 5843ms |
| 17 | play or get lost but do not laugh | eku ey pilu oy von hihidu | Ek ey Mepoku je du dizeud | ✗ | 4395ms |
| 18 | you will do it well | et xo has fi | Et oxer has fiay. | ✗ | 3795ms |
| 19 | he or she is going home but he or she wi | it peye tam oy it yexo be | it peye bu tam oy it yexo | ✗ | 5590ms |
| 20 | you all were going home but you all came | yet peya tam oy yet upa h | Yet hya paya tam oy yet h | ✗ | 5385ms |
| 21 | unless we say otherwise they will be sil | oven yat do hyuyen yit do | ven voy yit du hyuay, yit | ✗ | 4746ms |
| 22 | do they walk to school today | duven yit tyoyapeye tista | Duven yit tyope bu tistam | ✗ | 5013ms |
| 23 | whenever you talk i laugh | hyej et dale at hihide | hyej ho et dal, at dizeud | ✗ | 5263ms |
| 24 | my name is bill and your name is john | ata dyun se bill ay eta d | Ata dyun se Bil ay eta dy | ✗ | 4317ms |
| 25 | they will work at home and they will be  | yit yexo be tam ay yit so | Yit yexo be tam ay yit iv | ✗ | 4796ms |
| 26 | do you know the answer | duven et te ha dud | Du et ter ha dud? | ✗ | 3508ms |
| 27 | the students walk to school every day | ha tixuti tyoyape tistam  | Ha tixuti tyope bu tistam | ✗ | 4157ms |
| 28 | they know that we will come and they wil | yit te van yat upo ay yit | yit te van yat upo ay yit | ✓ | 4307ms |
| 29 | do they know where we went and where you | duven yit te hom yat pa a | Duven yit twa hem yat pya | ✗ | 2981ms |