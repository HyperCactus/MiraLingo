# Translation Evaluation Report

**Date:** 2026-05-26T15:40:14.156893 | **Model:** deepseek-ai/DeepSeek-V4-Flash
**Direction:** en_to_mir | **Samples:** 30
**Data:** data/eval/test.json
**Parallelism:** 8 workers

## Metrics Summary

| Metric | Score | Count |
|---|---|---|
| Normalized Match | 43.3% | 13/30 |
| Word Overlap F1 | 73.9% | 17/30 (≥0.7) |
| Avg Time/Sample | 31751ms | — |

## All Results

| # | Source | Gold | Predicted | Score | Time |
|---|---|---|---|---|---|
| 0 | i am going home | at peye tam | At se piyea be tam. | ✗ | 51518ms |
| 1 | while we are here we will work at home | je van yat so him yat yex | Je van yat se him, yat ya | ✗ | 42147ms |
| 2 | this building was a store | hia tom sa nam | Hia tom sa nam. | ✓ | 40414ms |
| 3 | our books | yata dyesi | ayata dyesi | ✗ | 48619ms |
| 4 | do we work at a grocery store near here  | duven yat yexe be tolnam  | Du aet yexe be nam yub bi | ✗ | 80018ms |
| 5 | i will be | at so | at so | ✓ | 49545ms |
| 6 | do not be late | von et jwosu | Du jwu! | ✗ | 52677ms |
| 7 | he or she knows | it te | it tre | ✗ | 51821ms |
| 8 | women | toybi | toybi | ✓ | 11722ms |
| 9 | even if we disagree they will support us | gey ven yat yontexe yit b | Gey ven yat oveke, yit ya | ✗ | 15480ms |
| 10 | you were very far from here | et sa gla yib bi him | et sa gla yiba bi him | ✗ | 24635ms |
| 11 | what do they do for work now | duhos yit xe av yex hij | Duhos yit xe av yex hij? | ✓ | 25352ms |
| 12 | they are bad | yit se fua | Yit se fua. | ✓ | 21953ms |
| 13 | you will do | et xo | et xo | ✓ | 19588ms |
| 14 | do you all walk to school today | duven yet tyoyapeye tista | Yet tyope bu tistam hijub | ✗ | 61040ms |
| 15 | you would come | et upu | et upu | ✓ | 22278ms |
| 16 | i did | at xa | At xa. | ✓ | 15155ms |
| 17 | those are mine | huasi se atasi | Huasi se atasi. | ✓ | 18967ms |
| 18 | we do not come | yat voy upe | Yat voy upe. | ✓ | 12082ms |
| 19 | that is mine | huas se atas | Huas se atas. | ✓ | 23342ms |
| 20 | if i want to go home i must work harder | ven at fe per tam at yefe | Ven at fe per tam, at yef | ✗ | 40713ms |
| 21 | nothing bothers that gal but no story is | hyos oboxe huyt oy hyoa d | Hyos obose hua toybet boy | ✗ | 30335ms |
| 22 | nothing bothers that gal | hyos oboxe huyt | Hyosi obose hua toybet. | ✗ | 16332ms |
| 23 | they were going home | yit peya tam | Yit pa be tam. | ✗ | 20397ms |
| 24 | he tried but he lost | it yeka oy it oka | Wit yeka oy wit losa. | ✗ | 17474ms |
| 25 | the man left for no reason but someone e | ha tob pia hyosav oy hyut | Ha twob ipa av owa sav oy | ✗ | 36144ms |
| 26 | our name is ugly | yata dyun se vua | aeta vua dyun se | ✗ | 24746ms |
| 27 | fast | iga | iga | ✓ | 12978ms |
| 28 | before this they lived in the suburbs | ja his yit tambesa ha yuz | Ja his yit besa bi ha yeb | ✗ | 26964ms |
| 29 | come play with us and stay together | upu eker bay yat ay besu  | Upu eker bay yat ay besu  | ✓ | 38099ms |