# Multi-Candidate Translation Eval

**Date:** 2026-05-28 16:07
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526, from train.json)
**Direction:** English → Mirad
**Candidates:** 3 @ [0.1, 0.3, 0.7]
**Config:** n_parallel=32, n_candidates=3, top_k_grammar_rules=3, top_k_relevant_words=0

## Metrics
| Metric | Value |
|--------|-------|
| Normalized Match | 39.0% (39/100) |
| Exact Match | 34.0% (34/100) |
| Avg Judge Score | 88.9/100 |

## Timing
| | |
|-|--|
| Total wall time | 965s |
| Avg per sample | 9.7s |

## Results
| # | NM | Judge | Temp | Sample |
|---|----|-------|------|--------|
|   0 | ✗ |  80.0 | T=0.1 | whose book is this and whose are these books → Duhota se hia dyes? ay duhotasi se hia d |
|   1 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   2 | ✗ |  52.0 | T=0.7 | do you all walk to school → Yet tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.1 | our teacher is good but their teacher is bad → yata tuxut se fia oy yita tuxut se fua |
|   4 | ✗ |  77.0 | T=0.1 | this guy s house is on fire → hia aota tam se magijbwa |
|   5 | ✓ | 100.0 | T=0.1 | we were → yat sa |
|   6 | ✗ |  66.0 | T=0.1 | unless they say otherwise we will be silent → Gob van yit de hyuyen, yat dolso. |
|   7 | ✓ | 100.0 | T=0.1 | the teacher is good and the student is bad → ha tuxut se fia ay ha tixut se fua |
|   8 | ✗ | 100.0 | T=0.3 | do you know the answer → Du et te ha dud? |
|   9 | ✗ | 100.0 | T=0.1 | justice → doyev |
|  10 | ✓ | 100.0 | T=0.3 | this teacher is very good → hia tuxut se gla fia |
|  11 | ✗ |  81.0 | T=0.1 | play or get lost but do not laugh → Eku ey mepoku va voy dizeudu. |
|  12 | ✗ | 100.0 | T=0.1 | are the stars bright but the night cold → Ha mari se maa, oy ha moj se oma. |
|  13 | ✓ |  30.0 | T=0.7 | he or she will come → it upo |
|  14 | ✓ | 100.0 | T=0.1 | do → Xu. |
|  15 | ✗ | 100.0 | T=0.7 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✗ |  86.0 | T=0.3 | do they work at home → Duho yit yexe be tam? |
|  17 | ✗ | 100.0 | T=0.1 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.3 | these persons → hiati |
|  19 | ✗ | 100.0 | T=0.1 | you are not my father but you know my father → et voy se ata twed oy et te ata twed |
|  20 | ✓ | 100.0 | T=0.3 | the name → ha dyun |
|  21 | ✗ | 100.0 | T=0.3 | the houses are ugly → ha vua tami se |
|  22 | ✓ | 100.0 | T=0.1 | that house is beautiful → hua tam se via |
|  23 | ✗ | 100.0 | T=0.3 | this person → hia tob |
|  24 | ✓ | 100.0 | T=0.3 | they know → yit te |
|  25 | ✗ |  98.0 | T=0.3 | it is not fair to prejudge someone → Jayevder het voy se yeva. |
|  26 | ✓ | 100.0 | T=0.3 | that teacher is bad → hua tuxut se fua |
|  27 | ✓ | 100.0 | T=0.1 | the teacher is good → ha tuxut se fia |
|  28 | ✗ | 100.0 | T=0.1 | this building is a store but this building was a s → hia tom se nam oy hia tom sa ja |
|  29 | ✗ |  82.0 | T=0.1 | you live in the neighborhood → Et bese bi ha doeym. |
|  30 | ✗ |  90.0 | T=0.7 | he looks like a good worker → it teaxe gel fia yexut |
|  31 | ✓ | 100.0 | T=0.3 | you will work at home → et yexo be tam |
|  32 | ✗ | 100.0 | T=0.1 | thanks you were very kind → Hyay, et sa gla tipifa. |
|  33 | ✗ |  68.0 | T=0.7 | you all do not come → yet voy upu |
|  34 | ✗ | 100.0 | T=0.1 | this person is beautiful and that one is ugly → Hia tob se via ay huat se vua. |
|  35 | ✓ | 100.0 | T=0.3 | i do not know → At voy te. |
|  36 | ✗ | 100.0 | T=0.1 | people often do not love themselves → Yot gla jodi voy ife yout. |
|  37 | ✗ |  50.0 | T=0.1 | do you know why he did it → Duven et tede hosav it xa is? |
|  38 | ✗ |  88.0 | T=0.1 | i did not know you were coming → At voy ta van et upeya. |
|  39 | ✗ |  16.0 | T=0.7 | unless i say otherwise you will be silent → Oven at de hyuay, et dolso. |
|  40 | ✓ | 100.0 | T=0.3 | the small house → ha oga tam |
|  41 | ✗ |  84.0 | T=0.1 | everywhere i go you are there → hyam at pe et se be hum |
|  42 | ✓ | 100.0 | T=0.1 | we worked at home → yat yexa be tam |
|  43 | ✗ |  84.0 | T=0.7 | our house is bigger than yours but this house is n → Ayeta tam se gaaga vyel ayetas, oy hia t |
|  44 | ✗ | 100.0 | T=0.1 | come to the grocery store sometime → Upu bu ha tolnam hej. |
|  45 | ✗ | 100.0 | T=0.1 | ugly things → vua suni |
|  46 | ✓ | 100.0 | T=0.1 | this desk is small but good and that desk is big b → hia dresem se oga oy fia ay hua dresem s |
|  47 | ✗ |  89.0 | T=0.3 | they do not know where he or she went but they kno → Yit voy te ho it pa oy yit te ho yat tej |
|  48 | ✓ | 100.0 | T=0.3 | captive → yuva |
|  49 | ✗ | 100.0 | T=0.1 | every man must do his part → Hyawa twob yefe xer ita gon. |
|  50 | ✓ | 100.0 | T=0.1 | you all were happy → yet sa iva |
|  51 | ✗ |  99.0 | T=0.1 | we will be there until the end of the season → yat so be hum ju ha uj bi ha jeb |
|  52 | ✗ | 100.0 | T=0.3 | both cities have grown and any color will be fine → Hyaewa domi agsa ay hyea volz so fia. |
|  53 | ✗ |  92.0 | T=0.3 | before this you lived in the suburbs → Ja his et besa bi ha yuzdom. |
|  54 | ✗ |  92.0 | T=0.3 | they will give it to us after we pay → Yit buo is bu yat jo van yat nuxe. |
|  55 | ✗ | 100.0 | T=0.1 | that is a good student → Huat se fia tixut. |
|  56 | ✗ |   0.0 | T=0.1 | you all will do it well → yet is xo fiay |
|  57 | ✓ | 100.0 | T=0.7 | they came → yit upa |
|  58 | ✓ | 100.0 | T=0.1 | we were happy → yat sa iva |
|  59 | ✗ | 100.0 | T=0.3 | maybe i may go but i do not know → Vey at afe per, oy at voy te. |
|  60 | ✗ | 100.0 | T=0.7 | harmful → bukuyea |
|  61 | ✓ | 100.0 | T=0.3 | i would go → at pu |
|  62 | ✓ | 100.0 | T=0.1 | i would do → at xu |
|  63 | ✗ |  93.0 | T=0.3 | the teachers are good → ha fia tuxuti se |
|  64 | ✓ | 100.0 | T=0.1 | the teachers → ha tuxuti |
|  65 | ✗ |  73.0 | T=0.1 | do they know where we went and where you live → Duven yit te hom yat pa ay hom et teje? |
|  66 | ✗ |  69.0 | T=0.3 | while they are here they will do some work for us → Je van yit se be him, yit xo hea yex av  |
|  67 | ✗ |  98.0 | T=0.1 | i do not know where they went but i know where you → At voy te duhom yit pa, oy at te duhom e |
|  68 | ✓ | 100.0 | T=0.1 | the student is good → ha tixut se fia |
|  69 | ✓ |   0.0 | T=0.1 | he or she will be → it so |
|  70 | ✗ |  83.0 | T=0.1 | you should tell her that → et yeyfe der iyt hus |
|  71 | ✓ | 100.0 | T=0.1 | they come → yit upe |
|  72 | ✓ |  20.0 | T=0.7 | he or she would go → it pu |
|  73 | ✗ | 100.0 | T=0.1 | i am not your father but i know your father → At voy se eta twed oy at te eta twed. |
|  74 | ✗ | 100.0 | T=0.1 | yours are worth more than mine → Yetasi se ga naze vyel atasi. |
|  75 | ✗ |  95.0 | T=0.1 | whenever you talk i laugh → Hyejod ho et dale, at dizeude. |
|  76 | ✓ | 100.0 | T=0.3 | that student is good → hua tixut se fia |
|  77 | ✓ | 100.0 | T=0.1 | the dog bit me → Ha yepet teupixa at. |
|  78 | ✓ | 100.0 | T=0.1 | they know that we will come and they will be happy → yit te van yat upo ay yit so iva |
|  79 | ✗ | 100.0 | T=0.3 | we were indeed there → Yat vay sa be hum. |
|  80 | ✓ | 100.0 | T=0.3 | your teacher is good → eta tuxut se fia |
|  81 | ✗ |  88.0 | T=0.1 | he sings beautifully → It deuze viay. |
|  82 | ✗ |  95.0 | T=0.3 | this book is my favorite → hia dyes se ata gaifwas |
|  83 | ✗ | 100.0 | T=0.1 | the students walk to school every day → Ha tixuti tyope bu tistam hyawa jub. |
|  84 | ✓ |  20.0 | T=0.7 | fathers → twedi |
|  85 | ✗ |  95.0 | T=0.7 | these words are prohibited but this book is my fav → hia duni se ofwa oy hia dyes se ata gaif |
|  86 | ✓ | 100.0 | T=0.1 | is that student bad → Duven hua tixut se fua? |
|  87 | ✗ |  73.0 | T=0.7 | he or she is going home but he or she will work at → It pe be tam oy it yexo be tam. |
|  88 | ✗ |  91.0 | T=0.1 | the sun has risen so you must get up out of bed → Ha amar yapa, ay et yefe yabuper oyeb bi |
|  89 | ✗ | 100.0 | T=0.1 | they sing beautifully → Yit deuze viay. |
|  90 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | birds → pati |
|  92 | ✗ |  63.0 | T=0.3 | are the stars bright → Se ha mari maa? |
|  93 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|  94 | ✗ |  48.0 | T=0.3 | he or she was going home → it pa be tam |
|  95 | ✗ |  86.0 | T=0.7 | will you ever come back → Et zoyupo hyej? |
|  96 | ✗ | 100.0 | T=0.1 | are you married → Et se taduwa? |
|  97 | ✓ | 100.0 | T=0.1 | be good → Su fia. |
|  98 | ✓ | 100.0 | T=0.1 | the cars → ha puri |
|  99 | ✗ | 100.0 | T=0.7 | every man must do his part and every person must l → Hyetwob efxe ita gon ay hyeaot efife aut |
