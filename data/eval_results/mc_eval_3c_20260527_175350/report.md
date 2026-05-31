# 3-Candidate Translation Eval

**Date:** 2026-05-27 17:53
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 32 workers
**Errors:** 0/100

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 19.0% (19/100) |
| Exact Match | 15.0% (15/100) |
| Avg Judge Score | 82.9/100 |

## Timing

| | |
|--|--|
| Total wall time | 290s |
| Avg per sample | 2.9s |
| Samples/sec | 0.3 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  35.0 | T=0.9 | whose book is this and whose are these books → Hota draves hia? ay hota hia dravesi? |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ | 100.0 | T=0.5 | do you all walk to school → Duven yet tyope bu tistam? |
|   3 | ✗ |  80.0 | T=0.5 | our teacher is good but their teacher is bad → Yata tuxut fia oy yita tuxut fua. |
|   4 | ✗ |  58.0 | T=0.1 | this guy s house is on fire → Ha aota tam se be mag. |
|   5 | ✗ |  96.0 | T=0.1 | we were → aet sa |
|   6 | ✗ |  49.0 | T=0.1 | unless they say otherwise we will be silent → Oven yit der ven voy, yat oser dola. |
|   7 | ✗ | 100.0 | T=0.5 | the teacher is good and the student is bad → Ha tuxut fia ay ha tixut fua. |
|   8 | ✗ |  91.0 | T=0.1 | do you know the answer → Et te ha dud? |
|   9 | ✗ | 100.0 | T=0.5 | justice → doyev |
|  10 | ✗ |  70.0 | T=0.1 | this teacher is very good → hia tuxut gla fia |
|  11 | ✗ |  58.0 | T=0.5 | play or get lost but do not laugh → Eku ey mepoku boy du von dizeudu! |
|  12 | ✗ | 100.0 | T=0.1 | are the stars bright but the night cold → Duven ha mari maa oy ha moj oma? |
|  13 | ✗ |  25.0 | T=0.9 | he or she will come → It ay upe. |
|  14 | ✗ | 100.0 | T=0.1 | do → Xer! |
|  15 | ✗ | 100.0 | T=0.1 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✗ |  55.0 | T=0.9 | do they work at home → Du yexe yit be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.5 | these persons → hia aoti |
|  19 | ✗ | 100.0 | T=0.1 | you are not my father but you know my father → et voy se ata twed oy et te ata twed |
|  20 | ✓ | 100.0 | T=0.1 | the name → ha dyun |
|  21 | ✗ | 100.0 | T=0.9 | the houses are ugly → tami se vua |
|  22 | ✗ |  90.0 | T=0.1 | that house is beautiful → hua tam via |
|  23 | ✗ | 100.0 | T=0.1 | this person → hia aot |
|  24 | ✗ |  50.0 | T=0.9 | they know → Yit tere. |
|  25 | ✗ | 100.0 | T=0.1 | it is not fair to prejudge someone → Voy se yeva jayevder het. |
|  26 | ✗ |  90.0 | T=0.5 | that teacher is bad → Hua tuxut fua. |
|  27 | ✗ |  70.0 | T=0.5 | the teacher is good → ha tuxut fia |
|  28 | ✗ |  80.0 | T=0.1 | this building is a store but this building was a store  → hia tom se nam oy hia tom sa nam ja van |
|  29 | ✗ |  93.0 | T=0.9 | you live in the neighborhood → Et teje ha doeym. |
|  30 | ✗ |  40.0 | T=0.1 | he looks like a good worker → It teaxe gel fia yexut. |
|  31 | ✓ |  91.0 | T=0.5 | you will work at home → Et yexo be tam. |
|  32 | ✗ |  91.0 | T=0.5 | thanks you were very kind → Fyadwu, et sa gla fitipa. |
|  33 | ✗ |  60.0 | T=0.1 | you all do not come → eyt voy upya |
|  34 | ✗ |  91.0 | T=0.5 | this person is beautiful and that one is ugly → hia aot se via ay hua awa se vua |
|  35 | ✓ |  98.0 | T=0.1 | i do not know → At voy te. |
|  36 | ✗ |  88.0 | T=0.5 | people often do not love themselves → Yot glaxagay oifone yout. |
|  37 | ✗ |  32.0 | T=0.1 | do you know why he did it → Du et te hosav it has xa? |
|  38 | ✗ |  84.0 | T=0.9 | i did not know you were coming → At voy ta et upya. |
|  39 | ✗ |  30.0 | T=0.9 | unless i say otherwise you will be silent → Oven at hyuay de, et dolo. |
|  40 | ✓ | 100.0 | T=0.5 | the small house → ha oga tam |
|  41 | ✗ |  65.0 | T=0.9 | everywhere i go you are there → Hyam ho at pe, et se huam. |
|  42 | ✓ | 100.0 | T=0.9 | we worked at home → yat yexa be tam |
|  43 | ✗ |  46.0 | T=0.5 | our house is bigger than yours but this house is not as → Aeta tam se ga aga vyel eta, ju hia tam  |
|  44 | ✗ | 100.0 | T=0.1 | come to the grocery store sometime → Upu bu ha nam hej. |
|  45 | ✗ |  89.0 | T=0.1 | ugly things → soni vua |
|  46 | ✓ | 100.0 | T=0.9 | this desk is small but good and that desk is big but ba → Hia dresem se oga oy fia ay hua dresem s |
|  47 | ✗ |  73.0 | T=0.5 | they do not know where he or she went but they know whe → Yit voy te hem it pa oy yit te hem yat t |
|  48 | ✗ | 100.0 | T=0.1 | captive → pixlawat |
|  49 | ✗ |  62.0 | T=0.1 | every man must do his part → Hyawa twob yef vay ita gon. |
|  50 | ✗ | 100.0 | T=0.5 | you all were happy → eyt sa iva |
|  51 | ✗ | 100.0 | T=0.5 | we will be there until the end of the season → Yat beso be hum ju ha jeb uj. |
|  52 | ✗ | 100.0 | T=0.1 | both cities have grown and any color will be fine → Hyaewa domi agaye ay hyea volz so fia. |
|  53 | ✗ |  91.0 | T=0.5 | before this you lived in the suburbs → Ja hia et tejya be yuzdomi. |
|  54 | ✗ | 100.0 | T=0.9 | they will give it to us after we pay → Yit ojbu has bu yat jo van yat nux. |
|  55 | ✗ |  95.0 | T=0.1 | that is a good student → hua se fia tixut |
|  56 | ✗ |  63.0 | T=0.9 | you all will do it well → eyt has fiay xeyo |
|  57 | ✗ | 100.0 | T=0.9 | they came → Yit upya. |
|  58 | ✓ |  90.0 | T=0.5 | we were happy → yat sa iva |
|  59 | ✗ | 100.0 | T=0.5 | maybe i may go but i do not know → Vey at afu per oy at voy ter. |
|  60 | ✗ | 100.0 | T=0.1 | harmful → bukaya |
|  61 | ✗ |  40.0 | T=0.9 | i would go → At puy. |
|  62 | ✗ | 100.0 | T=0.5 | i would do → At xayu. |
|  63 | ✗ |  85.0 | T=0.5 | the teachers are good → ha tuxuti fia |
|  64 | ✓ | 100.0 | T=0.1 | the teachers → ha tuxuti |
|  65 | ✗ |  74.0 | T=0.1 | do they know where we went and where you live → Duven yit te hom yat pa ay hom et teje? |
|  66 | ✗ |  52.0 | T=0.5 | while they are here they will do some work for us → Je van yit se him, yit vay hea yex av ya |
|  67 | ✗ |  91.0 | T=0.5 | i do not know where they went but i know where you live → At ote hem yit pa oy at te hem et teje. |
|  68 | ✗ |  70.0 | T=0.5 | the student is good → ha tixut fia |
|  69 | ✗ |  12.0 | T=0.5 | he or she will be → it oj ser |
|  70 | ✗ |  64.0 | T=0.1 | you should tell her that → et yeyfe der iyta van |
|  71 | ✓ |  93.0 | T=0.9 | they come → yit upe |
|  72 | ✓ |  20.0 | T=0.5 | he or she would go → it pu |
|  73 | ✗ | 100.0 | T=0.9 | i am not your father but i know your father → At voy se eta twed oy at te eta twed. |
|  74 | ✗ | 100.0 | T=0.5 | yours are worth more than mine → Etasi se ganazaya vyel atasi. |
|  75 | ✗ |  86.0 | T=0.5 | whenever you talk i laugh → Hyej ho et dale, at dizeude. |
|  76 | ✗ |  60.0 | T=0.1 | that student is good → hua tixut fia |
|  77 | ✓ | 100.0 | T=0.1 | the dog bit me → ha yepet teupixa at |
|  78 | ✗ |  72.0 | T=0.9 | they know that we will come and they will be happy → yit tre van yat upo ay yit so iva |
|  79 | ✗ |  88.0 | T=0.9 | we were indeed there → yat sa vay hum |
|  80 | ✓ | 100.0 | T=0.1 | your teacher is good → eta tuxut se fia |
|  81 | ✗ | 100.0 | T=0.1 | he sings beautifully → it deuze viay |
|  82 | ✗ |  71.0 | T=0.5 | this book is my favorite → Hia dyes ser ata gaifwa. |
|  83 | ✗ | 100.0 | T=0.1 | the students walk to school every day → ha tixuti tyope bu tistam hya jub |
|  84 | ✓ | 100.0 | T=0.1 | fathers → twedi |
|  85 | ✗ |  75.0 | T=0.1 | these words are prohibited but this book is my favorite → hia duni se ofwa ay hia dyes se ata gaif |
|  86 | ✗ |  90.0 | T=0.1 | is that student bad → Duven hua tixut fua? |
|  87 | ✗ |  90.0 | T=0.9 | he or she is going home but he or she will work at home → Ot poye bu tam oy ot yexo be tam. |
|  88 | ✗ |  93.0 | T=0.5 | the sun has risen so you must get up out of bed → Ha amar yapa, ay et yef yabper oyeb bi s |
|  89 | ✗ | 100.0 | T=0.1 | they sing beautifully → yit deuze viay |
|  90 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | birds → pati |
|  92 | ✗ | 100.0 | T=0.9 | are the stars bright → Duven ha mari se maa? |
|  93 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|  94 | ✗ |  45.0 | T=0.5 | he or she was going home → it peye be tam |
|  95 | ✗ | 100.0 | T=0.5 | will you ever come back → Duven et hyej zoyupo? |
|  96 | ✗ | 100.0 | T=0.5 | are you married → Et se tadxwa? |
|  97 | ✓ | 100.0 | T=0.1 | be good → Su fia. |
|  98 | ✓ | 100.0 | T=0.1 | the cars → ha puri |
|  99 | ✗ |  50.0 | T=0.5 | every man must do his part and every person must love o → Hyawa twob yefe vay ita gon ay hyawa aot |
