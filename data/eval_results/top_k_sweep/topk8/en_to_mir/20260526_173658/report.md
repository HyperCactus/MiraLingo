# Translation Evaluation Report

**Date:** 2026-05-26T17:38:13.820377 | **Model:** deepseek-ai/DeepSeek-V4-Flash
**Direction:** en_to_mir | **Samples:** 30
**Data:** /mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine/data/eval/train.json
**Parallelism:** 8 workers

## Metrics Summary

| Metric | Score | Count |
|---|---|---|
| Normalized Match | 10.0% | 3/30 |
| Word Overlap F1 | 62.4% | 13/30 (≥0.7) |
| Avg Time/Sample | 16702ms | — |

## All Results

| # | Source | Gold | Predicted | Score | Time |
|---|---|---|---|---|---|
| 0 | this guy s house is on fire | hwuta tam magseye | Hia twoba tam magsea. | ✗ | 59910ms |
| 1 | go to the store and buy me a book | pe ha nam ay nusbiu at dy | Pu bu nam ay nixu at dyes | ✗ | 59617ms |
| 2 | if i want to get results i must work har | ven at fe iber ixuni at y | Ven at fone ier isi, at y | ✗ | 69259ms |
| 3 | you all do not work at home | yet voy yexe be tam | Yet hya voy be tam yexe. | ✗ | 46570ms |
| 4 | this building will be a store and this b | hia tom so nam ay hia tom | hia tom so nam ay hia tom | ✓ | 57631ms |
| 5 | this teacher is possibly better than tha | hia tuxut se vey ga fia v | Hia tuxut se veay ga fia  | ✗ | 46384ms |
| 6 | while you are here you will work at home | je van et so him et yexo  | je van et se be him, et y | ✗ | 61403ms |
| 7 | the teacher is good and the student is b | ha tuxut se fia ay ha tix | ha tuxut se fia ay ha tix | ✓ | 59302ms |
| 8 | i know that he or she will come and i wi | at te van it upo ay at so | At tru it u upu ay at u i | ✗ | 1378ms |
| 9 | he or she would go | it pu | it piu | ✗ | 1427ms |
| 10 | you all will do it well | yet xo has fi | Eyt o vay has fiay. | ✗ | 1156ms |
| 11 | this teacher is very good | hia tuxut se gla fia | hiatuxut gla fia | ✗ | 1143ms |
| 12 | both cities have grown and any color wil | hyaewa domi agsaye ay hye | Hyaewa domi agxwa se ay h | ✗ | 1437ms |
| 13 | they will not start until you get here | yit voy ijo ju van et puo | yit voy oij ju van et pu  | ✗ | 1486ms |
| 14 | yours are worth more than mine | etasi naze ga vyel atasi | Etas ga nazea vyel atas. | ✗ | 1331ms |
| 15 | we knew that you would come but we did n | yat ta van et upo oy yat  | Yat twa van et upo, yat v | ✗ | 1414ms |
| 16 | do we know where you went and where they | duven yat te hom et pa ay | Yes ay hem et pa ay hem y | ✗ | 1836ms |
| 17 | play or get lost but do not laugh | eku ey pilu oy von hihidu | Ek ey Mepoku je du dizeud | ✗ | 1374ms |
| 18 | you will do it well | et xo has fi | Et oxer has fiay. | ✗ | 1125ms |
| 19 | he or she is going home but he or she wi | it peye tam oy it yexo be | it peye bu tam oy it yexo | ✗ | 1640ms |
| 20 | you all were going home but you all came | yet peya tam oy yet upa h | Yet hya paya tam oy yet h | ✗ | 1648ms |
| 21 | unless we say otherwise they will be sil | oven yat do hyuyen yit do | ven voy yit du hyuay, yit | ✗ | 1375ms |
| 22 | do they walk to school today | duven yit tyoyapeye tista | Duven yit tyope bu tistam | ✗ | 1534ms |
| 23 | whenever you talk i laugh | hyej et dale at hihide | hyej ho et dal, at dizeud | ✗ | 1585ms |
| 24 | my name is bill and your name is john | ata dyun se bill ay eta d | Ata dyun se Bil ay eta dy | ✗ | 2791ms |
| 25 | they will work at home and they will be  | yit yexo be tam ay yit so | Yit yexo be tam ay yit iv | ✗ | 3104ms |
| 26 | do you know the answer | duven et te ha dud | Du et ter ha dud? | ✗ | 2856ms |
| 27 | the students walk to school every day | ha tixuti tyoyape tistam  | Ha tixuti tyope bu tistam | ✗ | 3415ms |
| 28 | they know that we will come and they wil | yit te van yat upo ay yit | yit te van yat upo ay yit | ✓ | 3120ms |
| 29 | do they know where we went and where you | duven yit te hom yat pa a | Duven yit twa hem yat pya | ✗ | 2806ms |