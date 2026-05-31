# 3-Candidate Translation Eval

**Date:** 2026-05-27 09:59
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526)
**Candidates:** 3 @ [0.1, 0.5, 0.9]
**Config:** num_context_passages=3, top_k_per_word=0
**Parallelism:** 32 workers
**Errors:** 0/100

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 43.0% (43/100) |
| Exact Match | 33.0% (33/100) |
| Avg Judge Score | 88.0/100 |

## Timing

| | |
|--|--|
| Total wall time | 620s |
| Avg per sample | 6.2s |
| Samples/sec | 0.2 |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  93.0 | T=0.5 | whose book is this and whose are these books → Duhotas dyes hias, ay duhotasi dyesi hia |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  73.0 | T=0.9 | do you all walk to school → Duven yet hya tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.5 | our teacher is good but their teacher is bad → Yata tuxut se fia oy yita tuxut se fua. |
|   4 | ✗ |  88.0 | T=0.9 | this guy s house is on fire → Hia twoba tam se magsea. |
|   5 | ✓ | 100.0 | T=0.5 | we were → yat sa |
|   6 | ✗ |  58.0 | T=0.5 | unless they say otherwise we will be silent → Gob van yit du hyuyen, yat so dola. |
|   7 | ✓ |  88.0 | T=0.1 | the teacher is good and the student is bad → ha tuxut se fia ay ha tixut se fua |
|   8 | ✗ |  88.0 | T=0.5 | do you know the answer → Du et te ha dud? |
|   9 | ✗ | 100.0 | T=0.9 | justice → doyevan |
|  10 | ✓ | 100.0 | T=0.1 | this teacher is very good → hia tuxut se gla fia |
|  11 | ✗ | 100.0 | T=0.1 | play or get lost but do not laugh → Eku ey oksu oy voy dizeudu. |
|  12 | ✗ |  80.0 | T=0.5 | are the stars bright but the night cold → Duven ha mari se mana oy ha moj se oma? |
|  13 | ✓ |  35.0 | T=0.1 | he or she will come → it upo |
|  14 | ✗ | 100.0 | T=0.5 | do → xe |
|  15 | ✗ | 100.0 | T=0.1 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✓ | 100.0 | T=0.5 | do they work at home → Duven yit yexe be tam? |
|  17 | ✗ | 100.0 | T=0.5 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.1 | these persons → hia tobi |
|  19 | ✓ | 100.0 | T=0.1 | you are not my father but you know my father → Et voy se ata twed oy et tre ata twed. |
|  20 | ✓ |  70.0 | T=0.1 | the name → ha dyun |
|  21 | ✗ |  90.0 | T=0.9 | the houses are ugly → ha vua tami se |
|  22 | ✓ | 100.0 | T=0.5 | that house is beautiful → hua tam se via |
|  23 | ✗ | 100.0 | T=0.1 | this person → hia aot |
|  24 | ✓ | 100.0 | T=0.5 | they know → yit te |
|  25 | ✗ | 100.0 | T=0.9 | it is not fair to prejudge someone → Voy se yeva javyaker het. |
|  26 | ✓ |  90.0 | T=0.1 | that teacher is bad → hua tuxut se fua |
|  27 | ✓ |  88.0 | T=0.1 | the teacher is good → ha tuxut se fia |
|  28 | ✗ | 100.0 | T=0.1 | this building is a store but this building was a store  → hia tom se nam oy hia tom sa nam za |
|  29 | ✗ |  68.0 | T=0.9 | you live in the neighborhood → Et bese bi ha yubem. |
|  30 | ✗ |  80.0 | T=0.1 | he looks like a good worker → it se gel fia yexut |
|  31 | ✓ | 100.0 | T=0.9 | you will work at home → et yexo be tam |
|  32 | ✗ |  95.0 | T=0.5 | thanks you were very kind → Hyay! et sa gla fitipa. |
|  33 | ✗ |  35.0 | T=0.9 | you all do not come → Yet voy upu. |
|  34 | ✗ |  98.0 | T=0.9 | this person is beautiful and that one is ugly → Hia aot se via ay huat se vua. |
|  35 | ✓ | 100.0 | T=0.1 | i do not know → At voy te. |
|  36 | ✓ | 100.0 | T=0.9 | people often do not love themselves → Yot glaxag voy ife yout. |
|  37 | ✗ |  71.0 | T=0.1 | do you know why he did it → Et tie hosav it xa is? |
|  38 | ✗ |  92.0 | T=0.1 | i did not know you were coming → At voy ta van et sa upea. |
|  39 | ✗ |  76.0 | T=0.5 | unless i say otherwise you will be silent → Ven voy at de hyuyen, et so dola. |
|  40 | ✓ |  75.0 | T=0.1 | the small house → ha oga tam |
|  41 | ✗ |  70.0 | T=0.5 | everywhere i go you are there → Hyam ho at pe, et se be hum. |
|  42 | ✓ | 100.0 | T=0.5 | we worked at home → yat yexa be tam |
|  43 | ✗ |  76.0 | T=0.5 | our house is bigger than yours but this house is not as → Aeta tam se ga aga vyel aetas oy hia tam |
|  44 | ✗ |  90.0 | T=0.5 | come to the grocery store sometime → Upu bu tolnam hej. |
|  45 | ✗ | 100.0 | T=0.5 | ugly things → vua suni |
|  46 | ✓ |  98.0 | T=0.1 | this desk is small but good and that desk is big but ba → hia dresem se oga oy fia ay hua dresem s |
|  47 | ✗ |  78.0 | T=0.1 | they do not know where he or she went but they know whe → Yit voy te hem it pa oy yit te hem yat b |
|  48 | ✗ | 100.0 | T=0.1 | captive → pixlawat |
|  49 | ✗ | 100.0 | T=0.9 | every man must do his part → Hyatob yefe xer ita gon. |
|  50 | ✓ | 100.0 | T=0.1 | you all were happy → yet sa iva |
|  51 | ✗ |  86.0 | T=0.1 | we will be there until the end of the season → Yat so be hum ju ha uj bi ha jeb. |
|  52 | ✗ |  88.0 | T=0.5 | both cities have grown and any color will be fine → Hyaewa domi agxa ay hyea volz so fia. |
|  53 | ✗ |  77.0 | T=0.5 | before this you lived in the suburbs → Ja his et besa bi ha yuzdom. |
|  54 | ✗ |  71.0 | T=0.1 | they will give it to us after we pay → jo van yat nuxe, yit buo yat is |
|  55 | ✓ |  95.0 | T=0.9 | that is a good student → Hus se fia tixut. |
|  56 | ✗ |  49.0 | T=0.1 | you all will do it well → Yet xo is fiay. |
|  57 | ✓ | 100.0 | T=0.9 | they came → yit upa |
|  58 | ✓ | 100.0 | T=0.1 | we were happy → yat sa iva |
|  59 | ✗ | 100.0 | T=0.9 | maybe i may go but i do not know → vey at afu per oy at voy te |
|  60 | ✗ | 100.0 | T=0.1 | harmful → bukuyea |
|  61 | ✓ | 100.0 | T=0.1 | i would go → at pu |
|  62 | ✓ |  70.0 | T=0.9 | i would do → at xu |
|  63 | ✓ |  86.0 | T=0.1 | the teachers are good → ha tuxuti se fia |
|  64 | ✓ |  83.0 | T=0.5 | the teachers → ha tuxuti |
|  65 | ✗ |  92.0 | T=0.1 | do they know where we went and where you live → Duven yit te duhom yat pa ay duhom et te |
|  66 | ✗ |  74.0 | T=0.9 | while they are here they will do some work for us → Je van yit se be him, yit xo gle yex av  |
|  67 | ✗ |  90.0 | T=0.9 | i do not know where they went but i know where you live → At voy te hem yit pa oy at te hem et tej |
|  68 | ✓ |  90.0 | T=0.9 | the student is good → ha tixut se fia |
|  69 | ✓ |   0.0 | T=0.1 | he or she will be → it so |
|  70 | ✗ |  78.0 | T=0.5 | you should tell her that → Et yeyfe der iyta van. |
|  71 | ✓ | 100.0 | T=0.1 | they come → yit upe |
|  72 | ✓ |  95.0 | T=0.9 | he or she would go → it pu |
|  73 | ✗ | 100.0 | T=0.1 | i am not your father but i know your father → at voy se eta twed oy at te eta twed |
|  74 | ✓ | 100.0 | T=0.5 | yours are worth more than mine → Etasi naze ga vyel atasi. |
|  75 | ✗ |  90.0 | T=0.9 | whenever you talk i laugh → Hyejod ho et dale, at dizeude. |
|  76 | ✓ |  91.0 | T=0.1 | that student is good → hua tixut se fia |
|  77 | ✓ |  86.0 | T=0.5 | the dog bit me → Ha yepet teupixa at. |
|  78 | ✓ | 100.0 | T=0.5 | they know that we will come and they will be happy → yit te van yat upo ay yit so iva |
|  79 | ✗ |  98.0 | T=0.5 | we were indeed there → yat sa vay be hum |
|  80 | ✓ | 100.0 | T=0.5 | your teacher is good → eta tuxut se fia |
|  81 | ✗ |  70.0 | T=0.1 | he sings beautifully → It deuze viay. |
|  82 | ✗ |  95.0 | T=0.9 | this book is my favorite → hia dyes se ata gaifwas. |
|  83 | ✗ |  88.0 | T=0.5 | the students walk to school every day → Ha tixuti tyope bu tistam hya jub. |
|  84 | ✓ | 100.0 | T=0.1 | fathers → twedi |
|  85 | ✗ |  88.0 | T=0.1 | these words are prohibited but this book is my favorite → Hia dyuni se ofwa oy hia dyes se ata gai |
|  86 | ✓ | 100.0 | T=0.9 | is that student bad → Duven hua tixut se fua? |
|  87 | ✗ |  70.0 | T=0.5 | he or she is going home but he or she will work at home → It pe bu tam oy it yexo be tam. |
|  88 | ✗ |  91.0 | T=0.1 | the sun has risen so you must get up out of bed → Amar yapa, ay et yefe yabuper oyeb bi su |
|  89 | ✗ | 100.0 | T=0.1 | they sing beautifully → yit deuze viay |
|  90 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | birds → pati |
|  92 | ✗ |  88.0 | T=0.9 | are the stars bright → Duven ha mari se mana? |
|  93 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|  94 | ✗ |  49.0 | T=0.5 | he or she was going home → It sa pea tam. |
|  95 | ✗ |  87.0 | T=0.9 | will you ever come back → Et hyej zoyupo? |
|  96 | ✗ |  79.0 | T=0.1 | are you married → Du et se taduwa? |
|  97 | ✓ | 100.0 | T=0.1 | be good → Su fia. |
|  98 | ✓ | 100.0 | T=0.9 | the cars → ha puri |
|  99 | ✗ |  64.0 | T=0.5 | every man must do his part and every person must love o → Hyawa twob yefe xer ita gon ay hya tob y |
