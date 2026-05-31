# 3-Candidate Translation Eval

**Date:** 2026-05-27 10:28
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 32 workers
**Errors:** 0/100

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 23.0% (23/100) |
| Exact Match | 19.0% (19/100) |
| Avg Judge Score | 86.4/100 |

## Timing

| | |
|--|--|
| Total wall time | 472s |
| Avg per sample | 4.7s |
| Samples/sec | 0.2 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  75.0 | T=0.1 | whose book is this and whose are these books → hota dyes se hia? ay hota se hiati dyesi |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  88.0 | T=0.5 | do you all walk to school → Duven yet tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.1 | our teacher is good but their teacher is bad → Yata tuxut se fia oy yita tuxut se fua. |
|   4 | ✗ |  60.0 | T=0.5 | this guy s house is on fire → Hia twoba tam abmag. |
|   5 | ✗ | 100.0 | T=0.5 | we were → aet sa |
|   6 | ✗ |  62.0 | T=0.5 | unless they say otherwise we will be silent → Oven yot hyuay de, yat so dola. |
|   7 | ✓ |  88.0 | T=0.1 | the teacher is good and the student is bad → ha tuxut se fia ay ha tixut se fua |
|   8 | ✓ |  81.0 | T=0.5 | do you know the answer → Duven et te ha dud? |
|   9 | ✗ | 100.0 | T=0.1 | justice → doyevan |
|  10 | ✓ | 100.0 | T=0.5 | this teacher is very good → hia tuxut se gla fia |
|  11 | ✗ |  96.0 | T=0.5 | play or get lost but do not laugh → ek ey oksu oy von dizeudu |
|  12 | ✗ |  86.0 | T=0.9 | are the stars bright but the night cold → Ha mari se maa oy ha moj se oma. |
|  13 | ✗ |  60.0 | T=0.5 | he or she will come → it ey it oj uper |
|  14 | ✓ | 100.0 | T=0.1 | do → xu |
|  15 | ✗ | 100.0 | T=0.5 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✗ |  98.0 | T=0.1 | do they work at home → Duho yit yex be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.1 | these persons → hia tobi |
|  19 | ✗ | 100.0 | T=0.9 | you are not my father but you know my father → Et voy se ata twed oy et te ata twed. |
|  20 | ✗ | 100.0 | T=0.5 | the name → dyun |
|  21 | ✓ |  88.0 | T=0.5 | the houses are ugly → ha tami se vua |
|  22 | ✗ |  85.0 | T=0.1 | that house is beautiful → hua tam via |
|  23 | ✗ | 100.0 | T=0.1 | this person → hia aot |
|  24 | ✓ | 100.0 | T=0.5 | they know → yit te |
|  25 | ✗ |  96.0 | T=0.5 | it is not fair to prejudge someone → Se voy yeva javatexer het. |
|  26 | ✗ |  90.0 | T=0.1 | that teacher is bad → hua tuxut fua |
|  27 | ✓ |  88.0 | T=0.1 | the teacher is good → ha tuxut se fia |
|  28 | ✗ |  88.0 | T=0.9 | this building is a store but this building was a store  → Hia tom se nam oy hia tom sa nam ja van. |
|  29 | ✗ |  88.0 | T=0.9 | you live in the neighborhood → Et beser bi ha yuzdom. |
|  30 | ✗ |  63.0 | T=0.9 | he looks like a good worker → it sa gel fia yexut |
|  31 | ✓ | 100.0 | T=0.1 | you will work at home → et yexo be tam |
|  32 | ✗ |  73.0 | T=0.5 | thanks you were very kind → Iftax, et gla tipifa. |
|  33 | ✗ |  94.0 | T=0.5 | you all do not come → Eyt voy upu |
|  34 | ✗ |  78.0 | T=0.5 | this person is beautiful and that one is ugly → Hia aot via ay hua aot vua. |
|  35 | ✗ | 100.0 | T=0.1 | i do not know → At voy ter. |
|  36 | ✗ |  87.0 | T=0.1 | people often do not love themselves → yot glaxag voy ifone yout |
|  37 | ✗ |  98.0 | T=0.5 | do you know why he did it → Duven et ter hosav it xa has? |
|  38 | ✗ |  90.0 | T=0.5 | i did not know you were coming → At voy ta van et upeya. |
|  39 | ✗ |  73.0 | T=0.9 | unless i say otherwise you will be silent → Ven voy at de hyuay, et so dola. |
|  40 | ✗ | 100.0 | T=0.1 | the small house → tam oga |
|  41 | ✗ |  58.0 | T=0.9 | everywhere i go you are there → Hyam at po, et se be hum. |
|  42 | ✗ |  85.0 | T=0.1 | we worked at home → yet yexa bi tama |
|  43 | ✗ |  81.0 | T=0.9 | our house is bigger than yours but this house is not as → Aeta tam se ga aga vyel etasi, oy hia ta |
|  44 | ✗ |  88.0 | T=0.5 | come to the grocery store sometime → upu bu nam hej |
|  45 | ✗ |  85.0 | T=0.1 | ugly things → vua bexunyan |
|  46 | ✗ |  90.0 | T=0.1 | this desk is small but good and that desk is big but ba → hia dresem oga oy fia ay hua dresem aga  |
|  47 | ✗ |  84.0 | T=0.1 | they do not know where he or she went but they know whe → Yit voy te hem it ey iyt pa, oy yit te h |
|  48 | ✗ | 100.0 | T=0.5 | captive → yuvat |
|  49 | ✗ |  90.0 | T=0.5 | every man must do his part → Hya twob yefe xer ita gon. |
|  50 | ✗ | 100.0 | T=0.5 | you all were happy → eyt sa iva |
|  51 | ✗ |  86.0 | T=0.9 | we will be there until the end of the season → Yat so be hum ju uj bi ha jeb. |
|  52 | ✗ |  97.0 | T=0.1 | both cities have grown and any color will be fine → Hyaewa domi agxa ay hyea volz so fia. |
|  53 | ✗ |  61.0 | T=0.5 | before this you lived in the suburbs → Ja his et oybdom tejaya be. |
|  54 | ✗ |  86.0 | T=0.5 | they will give it to us after we pay → Yit yubu has bu yat jo van yat nuxu. |
|  55 | ✗ |  90.0 | T=0.5 | that is a good student → hua se fia tixut |
|  56 | ✗ |  31.0 | T=0.1 | you all will do it well → eyt has oxe fi |
|  57 | ✗ |  95.0 | T=0.5 | they came → Yit upya. |
|  58 | ✓ | 100.0 | T=0.1 | we were happy → Yat sa iva. |
|  59 | ✗ |  96.0 | T=0.5 | maybe i may go but i do not know → Ve at afu per oy at voy te. |
|  60 | ✗ | 100.0 | T=0.1 | harmful → bukxyea |
|  61 | ✗ | 100.0 | T=0.1 | i would go → at peyu |
|  62 | ✗ |  70.0 | T=0.5 | i would do → at xeyu |
|  63 | ✗ |  85.0 | T=0.1 | the teachers are good → tuxuti fia |
|  64 | ✗ | 100.0 | T=0.1 | the teachers → tuxuti |
|  65 | ✗ |  70.0 | T=0.9 | do they know where we went and where you live → Duven yit te be hem yat pa ay be hem et  |
|  66 | ✗ |  59.0 | T=0.5 | while they are here they will do some work for us → Je van yit se be him, yit vayo gle yex a |
|  67 | ✗ |  71.0 | T=0.1 | i do not know where they went but i know where you live → At voy ter hem yit peya oy at ter hem et |
|  68 | ✓ |  88.0 | T=0.9 | the student is good → ha tixut se fia |
|  69 | ✗ |  30.0 | T=0.9 | he or she will be → it ey iyt zo ser |
|  70 | ✗ |  65.0 | T=0.9 | you should tell her that → yeyfe der iyt van |
|  71 | ✓ | 100.0 | T=0.1 | they come → yit upe |
|  72 | ✗ |  38.0 | T=0.1 | he or she would go → it ey iyt pu |
|  73 | ✗ | 100.0 | T=0.1 | i am not your father but i know your father → at voy se eta twed oy at te eta twed |
|  74 | ✗ | 100.0 | T=0.1 | yours are worth more than mine → Etasi se ga naz vyel atasi. |
|  75 | ✗ |  95.0 | T=0.5 | whenever you talk i laugh → Hyejod ho et dale, at dizeude. |
|  76 | ✓ | 100.0 | T=0.5 | that student is good → hua tixut se fia |
|  77 | ✓ |  88.0 | T=0.1 | the dog bit me → ha yepet teupixa at |
|  78 | ✗ |  83.0 | T=0.1 | they know that we will come and they will be happy → Yit te van yat oj upe ay yit oj se iva. |
|  79 | ✗ | 100.0 | T=0.1 | we were indeed there → yat vay sa be hum |
|  80 | ✓ | 100.0 | T=0.1 | your teacher is good → eta tuxut se fia |
|  81 | ✗ |  95.0 | T=0.9 | he sings beautifully → it deuze viay |
|  82 | ✗ |  72.0 | T=0.9 | this book is my favorite → hia dyes ata gaifwa |
|  83 | ✗ |  88.0 | T=0.1 | the students walk to school every day → tixuti tyope bu tistam hya jub |
|  84 | ✓ |  70.0 | T=0.5 | fathers → twedi |
|  85 | ✗ |  98.0 | T=0.1 | these words are prohibited but this book is my favorite → hia duni ofwa oy hia dyes ata gaifwa |
|  86 | ✓ | 100.0 | T=0.1 | is that student bad → Duven hua tixut se fua? |
|  87 | ✗ |  65.0 | T=0.1 | he or she is going home but he or she will work at home → It ey iyt pe tam oy it ey iyt oyexo be t |
|  88 | ✗ |  70.0 | T=0.9 | the sun has risen so you must get up out of bed → Ha amar yapa, av hus et yefe yabser oyeb |
|  89 | ✗ | 100.0 | T=0.1 | they sing beautifully → yit deuze viay |
|  90 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | birds → pati |
|  92 | ✗ |  80.0 | T=0.9 | are the stars bright → Ha mari maa? |
|  93 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|  94 | ✗ |  77.0 | T=0.5 | he or she was going home → it sa peyea bu tam |
|  95 | ✗ |  55.0 | T=0.1 | will you ever come back → oj et hyej zoyupier? |
|  96 | ✗ | 100.0 | T=0.1 | are you married → Duven et tadiwa? |
|  97 | ✓ | 100.0 | T=0.1 | be good → su fia |
|  98 | ✓ | 100.0 | T=0.1 | the cars → ha puri |
|  99 | ✗ |  55.0 | T=0.5 | every man must do his part and every person must love o → Hyatwob yefe xer a gon ay hya aot yefe f |
