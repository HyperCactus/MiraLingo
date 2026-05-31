# 3-Candidate Translation Eval

**Date:** 2026-05-27 10:56
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 32 workers
**Errors:** 0/100

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 40.0% (40/100) |
| Exact Match | 28.0% (28/100) |
| Avg Judge Score | 87.1/100 |

## Timing

| | |
|--|--|
| Total wall time | 633s |
| Avg per sample | 6.3s |
| Samples/sec | 0.2 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  92.0 | T=0.9 | whose book is this and whose are these books → Hotas se hia dyes ay hotasi se hisi dyes |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  95.0 | T=0.5 | do you all walk to school → Du yet tyope bu tistam? |
|   3 | ✗ | 100.0 | T=0.1 | our teacher is good but their teacher is bad → yata tuxut se fia ay yita tuxut se fua |
|   4 | ✗ | 100.0 | T=0.9 | this guy s house is on fire → hia twoba tam se magsea |
|   5 | ✓ | 100.0 | T=0.5 | we were → yat sa |
|   6 | ✗ |  62.0 | T=0.5 | unless they say otherwise we will be silent → Ven voy yit du hyus, yat dolo. |
|   7 | ✓ |  88.0 | T=0.1 | the teacher is good and the student is bad → ha tuxut se fia ay ha tixut se fua |
|   8 | ✓ |  84.0 | T=0.9 | do you know the answer → Duven et te ha dud? |
|   9 | ✓ | 100.0 | T=0.5 | justice → yevan |
|  10 | ✗ | 100.0 | T=0.1 | this teacher is very good → hia tuxut gla fia |
|  11 | ✗ |  95.0 | T=0.1 | play or get lost but do not laugh → Eku ey mepoksu oy voy dizeudu. |
|  12 | ✗ |  95.0 | T=0.9 | are the stars bright but the night cold → Se mari manaza oy se moj oma? |
|  13 | ✓ |  40.0 | T=0.9 | he or she will come → it upo |
|  14 | ✓ |  98.0 | T=0.1 | do → Xu. |
|  15 | ✗ | 100.0 | T=0.1 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✓ | 100.0 | T=0.1 | do they work at home → Duven yit yexe be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.1 | these persons → hiati |
|  19 | ✗ | 100.0 | T=0.5 | you are not my father but you know my father → et voy se ata twed, oy et te ata twed |
|  20 | ✗ | 100.0 | T=0.1 | the name → dyun |
|  21 | ✓ |  88.0 | T=0.5 | the houses are ugly → ha tami se vua |
|  22 | ✓ | 100.0 | T=0.5 | that house is beautiful → hua tam se via |
|  23 | ✗ | 100.0 | T=0.1 | this person → hia aot |
|  24 | ✓ | 100.0 | T=0.1 | they know → yit te |
|  25 | ✗ |  81.0 | T=0.1 | it is not fair to prejudge someone → Voy vyata jayevder het. |
|  26 | ✓ | 100.0 | T=0.1 | that teacher is bad → hua tuxut se fua |
|  27 | ✓ |  88.0 | T=0.1 | the teacher is good → ha tuxut se fia |
|  28 | ✗ | 100.0 | T=0.9 | this building is a store but this building was a store  → hia tom se nam oy hia tom sa nam zaj |
|  29 | ✗ |  88.0 | T=0.9 | you live in the neighborhood → et teje bi ha yubyem |
|  30 | ✗ |  25.0 | T=0.1 | he looks like a good worker → It tease gel fia yexut. |
|  31 | ✓ | 100.0 | T=0.1 | you will work at home → et yexo be tam |
|  32 | ✗ | 100.0 | T=0.1 | thanks you were very kind → Hyay et sa gla tipifa. |
|  33 | ✓ |  43.0 | T=0.5 | you all do not come → yet voy upe |
|  34 | ✗ |  75.0 | T=0.1 | this person is beautiful and that one is ugly → Hia aot se via ay huat se vua. |
|  35 | ✓ | 100.0 | T=0.1 | i do not know → At voy te. |
|  36 | ✓ | 100.0 | T=0.5 | people often do not love themselves → Yot glaxag voy ife yout. |
|  37 | ✗ |  74.0 | T=0.1 | do you know why he did it → Et te duhosav it xa is? |
|  38 | ✗ |  94.0 | T=0.5 | i did not know you were coming → At voy tea van et upaya. |
|  39 | ✗ |  27.0 | T=0.5 | unless i say otherwise you will be silent → Oven at de hyuyen, dolu. |
|  40 | ✗ | 100.0 | T=0.9 | the small house → oga tam |
|  41 | ✗ |  86.0 | T=0.9 | everywhere i go you are there → Hyam ho at pe, et se be hum. |
|  42 | ✓ | 100.0 | T=0.5 | we worked at home → yat yexa be tam |
|  43 | ✗ |  82.0 | T=0.1 | our house is bigger than yours but this house is not as → Aeta tam se ga aga vyel aetas oy hia tam |
|  44 | ✓ |  88.0 | T=0.5 | come to the grocery store sometime → Upu ha tolnam hej. |
|  45 | ✗ | 100.0 | T=0.1 | ugly things → vua suni |
|  46 | ✓ |  98.0 | T=0.1 | this desk is small but good and that desk is big but ba → hia dresem se oga oy fia ay hua dresem s |
|  47 | ✗ |  77.0 | T=0.1 | they do not know where he or she went but they know whe → Yit voy te hom it pa oy yit te hom yat b |
|  48 | ✓ | 100.0 | T=0.1 | captive → yuva |
|  49 | ✗ |  92.0 | T=0.5 | every man must do his part → hya twob yefe xer ita gon |
|  50 | ✗ | 100.0 | T=0.5 | you all were happy → Yet sa ivra. |
|  51 | ✗ |  88.0 | T=0.9 | we will be there until the end of the season → Yat so be hum ju ha uj bi ha jeb. |
|  52 | ✗ |  78.0 | T=0.9 | both cities have grown and any color will be fine → hyaewa domi aga ay hyea volz so fia |
|  53 | ✗ | 100.0 | T=0.9 | before this you lived in the suburbs → Ja his et besa be yuzdomi. |
|  54 | ✗ |  68.0 | T=0.5 | they will give it to us after we pay → Yit buo bu yat has jo van yat nuxe. |
|  55 | ✗ |  84.0 | T=0.9 | that is a good student → Huat se fia tixut. |
|  56 | ✗ |  30.0 | T=0.9 | you all will do it well → yet xo is fiay |
|  57 | ✓ | 100.0 | T=0.5 | they came → yit upa |
|  58 | ✓ | 100.0 | T=0.1 | we were happy → yat sa iva |
|  59 | ✗ | 100.0 | T=0.9 | maybe i may go but i do not know → Vey at afe per oy at voy te. |
|  60 | ✗ | 100.0 | T=0.5 | harmful → buka |
|  61 | ✗ | 100.0 | T=0.1 | i would go → at peru |
|  62 | ✓ | 100.0 | T=0.1 | i would do → at xu |
|  63 | ✓ |  90.0 | T=0.1 | the teachers are good → Ha tuxuti se fia. |
|  64 | ✗ | 100.0 | T=0.9 | the teachers → tuxuti |
|  65 | ✗ |  41.0 | T=0.1 | do they know where we went and where you live → Du yit te hem yat pa ay hem et teje? |
|  66 | ✗ |  72.0 | T=0.1 | while they are here they will do some work for us → Je van yit se be him, yit xo gle yex av  |
|  67 | ✗ |  98.0 | T=0.1 | i do not know where they went but i know where you live → At voy te hom yit pa oy at te hom et tej |
|  68 | ✓ |  88.0 | T=0.1 | the student is good → ha tixut se fia |
|  69 | ✗ |  55.0 | T=0.5 | he or she will be → so |
|  70 | ✗ |  75.0 | T=0.9 | you should tell her that → Et yeyfe der iyt van. |
|  71 | ✓ | 100.0 | T=0.1 | they come → yit upe |
|  72 | ✓ |  30.0 | T=0.1 | he or she would go → it pu |
|  73 | ✗ |  95.0 | T=0.5 | i am not your father but i know your father → At voy se eta twed oy at te eta twed. |
|  74 | ✓ | 100.0 | T=0.5 | yours are worth more than mine → Etasi naze ga vyel atasi. |
|  75 | ✗ |  90.0 | T=0.1 | whenever you talk i laugh → Hyejod ho et dale, at dizeude. |
|  76 | ✓ |  95.0 | T=0.9 | that student is good → hua tixut se fia |
|  77 | ✓ |  86.0 | T=0.1 | the dog bit me → Ha yepet teupixa at. |
|  78 | ✓ | 100.0 | T=0.1 | they know that we will come and they will be happy → Yit te van yat upo ay yit so iva. |
|  79 | ✓ | 100.0 | T=0.5 | we were indeed there → Yat vay sa hum. |
|  80 | ✓ | 100.0 | T=0.5 | your teacher is good → eta tuxut se fia |
|  81 | ✗ |  60.0 | T=0.9 | he sings beautifully → It deuze viay. |
|  82 | ✗ |  86.0 | T=0.9 | this book is my favorite → hia dyes se ata gaifwa |
|  83 | ✗ |  80.0 | T=0.1 | the students walk to school every day → Ha tixuti tyope bu tistam hya jub. |
|  84 | ✓ |  80.0 | T=0.9 | fathers → twedi |
|  85 | ✗ | 100.0 | T=0.5 | these words are prohibited but this book is my favorite → he'i duni se ofwa oy he dyes se ata gaif |
|  86 | ✗ | 100.0 | T=0.9 | is that student bad → Se hua tixut fua? |
|  87 | ✗ |  70.0 | T=0.5 | he or she is going home but he or she will work at home → It pe be tam oy it yexo be tam. |
|  88 | ✗ |  71.0 | T=0.9 | the sun has risen so you must get up out of bed → Ha amar yapya, gay et yefe sumper oyeb b |
|  89 | ✗ | 100.0 | T=0.5 | they sing beautifully → yit deuze viay |
|  90 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | birds → pati |
|  92 | ✗ |  66.0 | T=0.1 | are the stars bright → Du ha mari se mana? |
|  93 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|  94 | ✗ |  40.0 | T=0.1 | he or she was going home → It pa be tam. |
|  95 | ✗ |  82.0 | T=0.1 | will you ever come back → Du et hyoj zoyupo? |
|  96 | ✗ |  95.0 | T=0.5 | are you married → Duven et se taduwa? |
|  97 | ✓ |  95.0 | T=0.1 | be good → Su fia! |
|  98 | ✓ |  80.0 | T=0.1 | the cars → ha puri |
|  99 | ✗ |  88.0 | T=0.9 | every man must do his part and every person must love o → Hya twob yefe xer wita gon ay hya aot ye |
