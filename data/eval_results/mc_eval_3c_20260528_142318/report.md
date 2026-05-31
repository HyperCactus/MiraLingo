# 3-Candidate Translation Eval

**Date:** 2026-05-28 14:23
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 32 workers
**Errors:** 0/100

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 24.0% (24/100) |
| Exact Match | 18.0% (18/100) |
| Avg Judge Score | 86.5/100 |

## Timing

| | |
|--|--|
| Total wall time | 690s |
| Avg per sample | 6.9s |
| Samples/sec | 0.1 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  59.0 | T=0.5 | whose book is this and whose are these books → Hota dyes hia ay hotas hia dyesi? |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  83.0 | T=0.9 | do you all walk to school → Eyt tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.5 | our teacher is good but their teacher is bad → yata tuxut se fia oy yita tuxut se fua |
|   4 | ✗ |  71.0 | T=0.9 | this guy s house is on fire → Hia twoba tam magsunaye. |
|   5 | ✗ | 100.0 | T=0.5 | we were → aet sa |
|   6 | ✗ |  84.0 | T=0.5 | unless they say otherwise we will be silent → Ven voy yit de hyuay, yat so dola. |
|   7 | ✗ | 100.0 | T=0.1 | the teacher is good and the student is bad → Ha tuxut fia ay ha tixut fua. |
|   8 | ✗ |  73.0 | T=0.1 | do you know the answer → Du et te ha dud? |
|   9 | ✗ | 100.0 | T=0.1 | justice → doyevan |
|  10 | ✓ | 100.0 | T=0.5 | this teacher is very good → hia tuxut se gla fia |
|  11 | ✗ |  86.0 | T=0.5 | play or get lost but do not laugh → eku ey mepok oy du von dizeudu |
|  12 | ✗ |  62.0 | T=0.5 | are the stars bright but the night cold → Duho? ha mar se manaya oy ha moj oma? |
|  13 | ✗ |  48.0 | T=0.9 | he or she will come → has upo |
|  14 | ✓ | 100.0 | T=0.1 | do → Xu! |
|  15 | ✗ | 100.0 | T=0.1 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✗ |  93.0 | T=0.1 | do they work at home → Du yit yex be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka; yukay |
|  18 | ✗ | 100.0 | T=0.1 | these persons → hiati tobi |
|  19 | ✗ | 100.0 | T=0.5 | you are not my father but you know my father → et voy ata twed oy et tre ata twed |
|  20 | ✓ | 100.0 | T=0.1 | the name → ha dyun |
|  21 | ✓ | 100.0 | T=0.9 | the houses are ugly → ha tami se vua |
|  22 | ✗ |  90.0 | T=0.1 | that house is beautiful → hua tam via |
|  23 | ✗ | 100.0 | T=0.1 | this person → hia aot |
|  24 | ✗ |  20.0 | T=0.1 | they know → yit ter |
|  25 | ✗ |  75.0 | T=0.5 | it is not fair to prejudge someone → Has voy se yeva yizavyader het. |
|  26 | ✓ |  98.0 | T=0.9 | that teacher is bad → Hua tuxut se fua. |
|  27 | ✓ | 100.0 | T=0.1 | the teacher is good → ha tuxut se fia |
|  28 | ✗ |  99.0 | T=0.1 | this building is a store but this building was a store  → hia tom se nam oy hia tom sa nam za |
|  29 | ✗ | 100.0 | T=0.1 | you live in the neighborhood → Et teje be doeym. |
|  30 | ✗ |  51.0 | T=0.5 | he looks like a good worker → it se gel fia yexut |
|  31 | ✗ |  84.0 | T=0.1 | you will work at home → et oyexo be tam |
|  32 | ✗ |  84.0 | T=0.1 | thanks you were very kind → Fyadil. et sa gla tipifa. |
|  33 | ✗ |  45.0 | T=0.9 | you all do not come → Hya eyt du voy upu |
|  34 | ✗ |  75.0 | T=0.1 | this person is beautiful and that one is ugly → Hia aot via ay hua aot vua. |
|  35 | ✗ | 100.0 | T=0.5 | i do not know → At vo ter. |
|  36 | ✗ | 100.0 | T=0.1 | people often do not love themselves → Yot glaxagay oifone yout. |
|  37 | ✗ | 100.0 | T=0.5 | do you know why he did it → Duven et te hosav it xa has? |
|  38 | ✗ |  84.0 | T=0.1 | i did not know you were coming → At voy twa van et upyea. |
|  39 | ✗ |  83.0 | T=0.5 | unless i say otherwise you will be silent → Ven voy at de hyuay, et so dola. |
|  40 | ✓ | 100.0 | T=0.9 | the small house → ha oga tam |
|  41 | ✗ |  55.0 | T=0.1 | everywhere i go you are there → Hyam at pe, et se be hum. |
|  42 | ✗ | 100.0 | T=0.1 | we worked at home → Yet yexa be tam. |
|  43 | ✗ |  83.0 | T=0.1 | our house is bigger than yours but this house is not as → Yata tam se agaga vyel yetasi oy hia tam |
|  44 | ✗ | 100.0 | T=0.1 | come to the grocery store sometime → Upu bu tolnam hej. |
|  45 | ✗ |  35.0 | T=0.1 | ugly things → vua bexunyani |
|  46 | ✓ | 100.0 | T=0.1 | this desk is small but good and that desk is big but ba → hia dresem se oga oy fia ay hua dresem s |
|  47 | ✗ |  79.0 | T=0.9 | they do not know where he or she went but they know whe → Yit voy tere duhom it peya oy yit tere h |
|  48 | ✗ | 100.0 | T=0.1 | captive → pixlawat |
|  49 | ✗ | 100.0 | T=0.9 | every man must do his part → Hyawa twob yef xer ita gon. |
|  50 | ✗ | 100.0 | T=0.1 | you all were happy → Hya eyt sa iva. |
|  51 | ✗ |  96.0 | T=0.1 | we will be there until the end of the season → Yat so be hum ju ha uj bi ha jeb. |
|  52 | ✗ |  93.0 | T=0.1 | both cities have grown and any color will be fine → Hyaewa domi aagye ay hyea volz so fia. |
|  53 | ✗ |  83.0 | T=0.9 | before this you lived in the suburbs → Ja hia et teja bi ha domyubem. |
|  54 | ✗ |  82.0 | T=0.9 | they will give it to us after we pay → yit buo has bu yat jo van yat nux |
|  55 | ✓ | 100.0 | T=0.9 | that is a good student → hus se fia tixut |
|  56 | ✗ |  94.0 | T=0.9 | you all will do it well → Yet oj xer has fiay. |
|  57 | ✗ | 100.0 | T=0.5 | they came → Yit upya. |
|  58 | ✓ | 100.0 | T=0.1 | we were happy → Yat sa iva. |
|  59 | ✗ |  92.0 | T=0.5 | maybe i may go but i do not know → vey at afu per oy at voy te |
|  60 | ✗ | 100.0 | T=0.1 | harmful → bukuyea |
|  61 | ✗ |  65.0 | T=0.1 | i would go → at pey |
|  62 | ✗ |  55.0 | T=0.9 | i would do → At venxer. |
|  63 | ✓ | 100.0 | T=0.9 | the teachers are good → ha tuxuti se fia |
|  64 | ✓ | 100.0 | T=0.1 | the teachers → ha tuxuti |
|  65 | ✗ | 100.0 | T=0.9 | do they know where we went and where you live → Duven yit tre duhom yat pa ay duhom et t |
|  66 | ✗ |  77.0 | T=0.5 | while they are here they will do some work for us → Je yit beye him, yit yexo av yat. |
|  67 | ✗ |  98.0 | T=0.1 | i do not know where they went but i know where you live → At voy tru hom yit pa oy at tru hom et t |
|  68 | ✗ |  83.0 | T=0.9 | the student is good → tixuta se fia |
|  69 | ✗ |  30.0 | T=0.5 | he or she will be → itoso |
|  70 | ✗ |  68.0 | T=0.5 | you should tell her that → Et yeyfe der iyt van |
|  71 | ✓ |  93.0 | T=0.1 | they come → yit upe |
|  72 | ✗ |  25.0 | T=0.9 | he or she would go → it puuyer |
|  73 | ✗ | 100.0 | T=0.1 | i am not your father but i know your father → At voy se eta twed oy at te eta twed. |
|  74 | ✗ |  65.0 | T=0.5 | yours are worth more than mine → Yetasi ga naz vyel atas. |
|  75 | ✗ |  91.0 | T=0.1 | whenever you talk i laugh → Hyej ho et dale, at dizeude. |
|  76 | ✗ |  90.0 | T=0.1 | that student is good → Hua tixut fia. |
|  77 | ✓ | 100.0 | T=0.1 | the dog bit me → ha yepet teupixa at |
|  78 | ✓ | 100.0 | T=0.1 | they know that we will come and they will be happy → Yit te van yat upo ay yit so iva. |
|  79 | ✗ | 100.0 | T=0.5 | we were indeed there → yat vay sa be hum |
|  80 | ✓ |  95.0 | T=0.1 | your teacher is good → eta tuxut se fia. |
|  81 | ✗ |  70.0 | T=0.1 | he sings beautifully → it deuze viay |
|  82 | ✗ |  84.0 | T=0.1 | this book is my favorite → Hia dyes se ata gaifwa. |
|  83 | ✗ | 100.0 | T=0.1 | the students walk to school every day → Tixuti tyope bu tistam hya jub. |
|  84 | ✓ | 100.0 | T=0.1 | fathers → twedi |
|  85 | ✗ |  69.0 | T=0.9 | these words are prohibited but this book is my favorite → hisi duni se ofdwa ja his dyes se ata ga |
|  86 | ✗ | 100.0 | T=0.9 | is that student bad → Duven hua tixut fua? |
|  87 | ✗ |  91.0 | T=0.1 | he or she is going home but he or she will work at home → it peyea be tam oy it yexo be tam |
|  88 | ✗ |  92.0 | T=0.9 | the sun has risen so you must get up out of bed → Ha amar yapxa, huyen et yef yabpiu oyeb  |
|  89 | ✗ | 100.0 | T=0.1 | they sing beautifully → yit deuze viay |
|  90 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | birds → pati |
|  92 | ✗ |  90.0 | T=0.5 | are the stars bright → Duven ha mari maa? |
|  93 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|  94 | ✗ |  35.0 | T=0.9 | he or she was going home → it peyea sa be tam |
|  95 | ✗ |  90.0 | T=0.9 | will you ever come back → Duven et hyej zoyupo? |
|  96 | ✗ | 100.0 | T=0.5 | are you married → Duven et tadiwa? |
|  97 | ✓ | 100.0 | T=0.1 | be good → Su fia. |
|  98 | ✓ | 100.0 | T=0.5 | the cars → ha puri |
|  99 | ✗ |  58.0 | T=0.5 | every man must do his part and every person must love o → Hyawa twob yefe vayen ita gon ay hyawa a |
