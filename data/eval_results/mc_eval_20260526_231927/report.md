# Multi-Candidate Translation Eval

**Date:** 2026-05-27 00:15  
**Model:** deepseek-ai/DeepSeek-V4-Flash  
**Samples:** 100 (seed=20260526)  
**Candidates:** 2 @ [0.1, 0.7]  
**Config:** num_context_passages=3, top_k_per_word=0  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 41.0% (41/100) |
| Exact Match | 30.0% (30/100) |
| Avg Judge Score | 83.5/100 |

## Timing

| | |
|-|---|
| Total wall time | 3359s |
| Avg per sample | 33.6s |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
|   0 | ✗ |  84.0 | T=0.7 | whose book is this and whose are these books → Hotas dyes se hias ay hotasi se hiasi dy |
|   0 | ✓ | 100.0 | T=0.1 | small houses → oga tami |
|   0 | ✗ |  72.0 | T=0.1 | do you all walk to school → Du yet tyope bu tistam? |
|   0 | ✓ | 100.0 | T=0.1 | our teacher is good but their teacher is bad → yata tuxut se fia oy yita tuxut se fua |
|   0 | ✗ |  71.0 | T=0.1 | this guy s house is on fire → Hia twoba tam se magsea. |
|   0 | ✓ | 100.0 | T=0.1 | we were → yat sa |
|   0 | ✗ |  98.0 | T=0.7 | unless they say otherwise we will be silent → Ven voy yit du hyus, yat so dunuka. |
|   0 | ✓ |  88.0 | T=0.1 | the teacher is good and the student is bad → Ha tuxut se fia ay ha tixut se fua. |
|   0 | ✗ |  82.0 | T=0.7 | do you know the answer → Duven et tere ha dud? |
|   0 | ✗ | 100.0 | T=0.1 | justice → doyevan |
|   0 | ✓ | 100.0 | T=0.1 | this teacher is very good → hia tuxut se gla fia |
|   0 | ✗ |  88.0 | T=0.7 | play or get lost but do not laugh → Eku ey mepoku oy voy dizeudu. |
|   0 | ✗ |  81.0 | T=0.7 | are the stars bright but the night cold → Mari se maaza oy moj se oma? |
|   0 | ✓ |  40.0 | T=0.1 | he or she will come → it upo |
|   0 | ✗ | 100.0 | T=0.1 | do → xe |
|   0 | ✗ | 100.0 | T=0.1 | everyone s drinks contain ice → Hyata tili bexe yom. |
|   0 | ✓ | 100.0 | T=0.7 | do they work at home → Duven yit yexe be tam? |
|   0 | ✗ | 100.0 | T=0.7 | easy easily → yuka yukay |
|   0 | ✗ | 100.0 | T=0.1 | these persons → hia tobi |
|   0 | ✗ | 100.0 | T=0.1 | you are not my father but you know my father → Et voy se ata twed oy et te ata twed. |
|   0 | ✓ |  70.0 | T=0.7 | the name → ha dyun |
|   0 | ✗ |  62.0 | T=0.7 | the houses are ugly → ha fua tami se |
|   0 | ✓ | 100.0 | T=0.1 | that house is beautiful → hua tam se via |
|   0 | ✗ | 100.0 | T=0.1 | this person → hia tob |
|   0 | ✓ | 100.0 | T=0.1 | they know → yit te |
|   0 | ✗ | 100.0 | T=0.7 | it is not fair to prejudge someone → voy se yeva jayevder het |
|   0 | ✓ |  95.0 | T=0.7 | that teacher is bad → hua tuxut se fua |
|   0 | ✓ |  88.0 | T=0.1 | the teacher is good → ha tuxut se fia |
|   0 | ✗ |  98.0 | T=0.1 | this building is a store but this building was a s → hia tom se nam oy hia tom sa nam ja |
|   0 | ✗ |  89.0 | T=0.7 | you live in the neighborhood → et bese bi ha yubem |
|   0 | ✗ |  72.0 | T=0.7 | he looks like a good worker → wit teatyene gel fia yexut |
|   0 | ✓ |  98.0 | T=0.7 | you will work at home → et yexo be tam |
|   0 | ✗ |  86.0 | T=0.7 | thanks you were very kind → Bayse, et sa gla tipifa. |
|   0 | ✗ |  30.0 | T=0.1 | you all do not come → Yet du upu |
|   0 | ✗ |  88.0 | T=0.1 | this person is beautiful and that one is ugly → Hiat se via ay hut se vua. |
|   0 | ✓ | 100.0 | T=0.1 | i do not know → At voy te. |
|   0 | ✓ |  88.0 | T=0.1 | people often do not love themselves → yot glaxag voy ife yout |
|   0 | ✗ |  30.0 | T=0.1 | do you know why he did it → Du et te hosav it xa is? |
|   0 | ✗ |  95.0 | T=0.7 | i did not know you were coming → At voy ta et upeya. |
|   0 | ✗ |  28.0 | T=0.1 | unless i say otherwise you will be silent → Oven at de hyuay, et so dola. |
|   0 | ✓ |  75.0 | T=0.7 | the small house → ha oga tam |
|   0 | ✗ |  76.0 | T=0.1 | everywhere i go you are there → Hyam at pe, et se be hum. |
|   0 | ✓ | 100.0 | T=0.7 | we worked at home → yat yexa be tam |
|   0 | ✗ |  65.0 | T=0.1 | our house is bigger than yours but this house is n → Aeta tam se ga aga vyel yetas, va hia ta |
|   0 | ✗ |  81.0 | T=0.1 | come to the grocery store sometime → Upu bu ha tolnam hej. |
|   0 | ✗ |  75.0 | T=0.7 | ugly things → vua bexunyani |
|   0 | ✗ |  84.0 | T=0.1 | this desk is small but good and that desk is big b → hia dresem se oga ay fia ay hua dresem s |
|   0 | ✗ |  78.0 | T=0.1 | they do not know where he or she went but they kno → Yit voy te hem it pa, oy yit te hem yat  |
|   0 | ✗ | 100.0 | T=0.1 | captive → pixlawat |
|   0 | ✗ | 100.0 | T=0.1 | every man must do his part → hya twob yefe xer ita gon |
|   0 | ✓ | 100.0 | T=0.1 | you all were happy → yet sa iva |
|   0 | ✓ |  86.0 | T=0.7 | we will be there until the end of the season → Yat so hum ju ha uj bi ha jeb. |
|   0 | ✗ |  81.0 | T=0.7 | both cities have grown and any color will be fine → Hyaewa domi agsa ay hyea volz so fia. |
|   0 | ✗ |  81.0 | T=0.7 | before this you lived in the suburbs → Ja his et teja bi ha yuzdomi. |
|   0 | ✗ |  64.0 | T=0.1 | they will give it to us after we pay → Yit buo is bu yat jo van yat nuxe. |
|   0 | ✗ |  88.0 | T=0.7 | that is a good student → Huat se fia tixut. |
|   0 | ✗ |  26.0 | T=0.1 | you all will do it well → Yet xo fi. |
|   0 | ✓ | 100.0 | T=0.1 | they came → yit upa |
|   0 | ✓ | 100.0 | T=0.1 | we were happy → Yat sa iva. |
|   0 | ✗ | 100.0 | T=0.1 | maybe i may go but i do not know → Vey at afu per, oy at voy te. |
|   0 | ✗ | 100.0 | T=0.1 | harmful → bukuyea |
|   0 | ✓ |  55.0 | T=0.1 | i would go → at pu |
|   0 | ✓ | 100.0 | T=0.1 | i would do → at xu |
|   0 | ✓ |  88.0 | T=0.1 | the teachers are good → ha tuxuti se fia |
|   0 | ✓ |  75.0 | T=0.7 | the teachers → ha tuxuti |
|   0 | ✗ |  62.0 | T=0.7 | do they know where we went and where you live → Du yit te hom yat peya ay hom et teje? |
|   0 | ✗ |  65.0 | T=0.1 | while they are here they will do some work for us → Je van yit se be him, yit xo yex av yat. |
|   0 | ✗ |  76.0 | T=0.7 | i do not know where they went but i know where you → At voy te hem ho yit pa oy at te hem ho  |
|   0 | ✓ |  88.0 | T=0.1 | the student is good → ha tixut se fia |
|   0 | ✓ |   0.0 | T=0.1 | he or she will be → it so |
|   0 | ✗ |  79.0 | T=0.1 | you should tell her that → Et yefe der iyt hus. |
|   0 | ✓ | 100.0 | T=0.1 | they come → yit upe |
|   0 | ✓ |   4.0 | T=0.7 | he or she would go → it pu |
|   0 | ✗ | 100.0 | T=0.7 | i am not your father but i know your father → At voy se eta twed oy at te eta twed. |
|   0 | ✓ | 100.0 | T=0.1 | yours are worth more than mine → Etasi naze ga vyel atasi. |
|   0 | ✗ |  90.0 | T=0.7 | whenever you talk i laugh → Hyejod ho et dale, at dizeude. |
|   0 | ✓ |  95.0 | T=0.1 | that student is good → hua tixut se fia |
|   0 | ✓ |  86.0 | T=0.1 | the dog bit me → Ha yepet teupixa at. |
|   0 | ✓ | 100.0 | T=0.1 | they know that we will come and they will be happy → Yit te van yat upo ay yit so iva. |
|   0 | ✗ |  90.0 | T=0.7 | we were indeed there → aet vay sa be hum |
|   0 | ✓ | 100.0 | T=0.7 | your teacher is good → eta tuxut se fia. |
|   0 | ✗ |  65.0 | T=0.7 | he sings beautifully → it deuze viay |
|   0 | ✗ | 100.0 | T=0.1 | this book is my favorite → hia dyes se ata gaifwa |
|   0 | ✗ |  86.0 | T=0.1 | the students walk to school every day → Ha tixuti tyope bu tistam hya jub. |
|   0 | ✓ |  80.0 | T=0.1 | fathers → twedi |
|   0 | ✗ |  84.0 | T=0.1 | these words are prohibited but this book is my fav → hia duni se ofwa oy hia dyes se ata gaif |
|   0 | ✓ | 100.0 | T=0.1 | is that student bad → Duven hua tixut se fua? |
|   0 | ✗ |  58.0 | T=0.7 | he or she is going home but he or she will work at → it pe be tam oy it yexo be tam |
|   0 | ✗ |  82.0 | T=0.1 | the sun has risen so you must get up out of bed → Amar yapia, ay et yefe yabpier oyeb bi s |
|   0 | ✗ | 100.0 | T=0.1 | they sing beautifully → yit deuze viay |
|   0 | ✓ | 100.0 | T=0.1 | a teacher → tuxut |
|   0 | ✓ | 100.0 | T=0.1 | birds → pati |
|   0 | ✗ |  98.0 | T=0.7 | are the stars bright → Duven ha mari manaya? |
|   0 | ✓ | 100.0 | T=0.1 | mothers → teydi |
|   0 | ✗ |  45.0 | T=0.1 | he or she was going home → it peya be tam |
|   0 | ✗ |  86.0 | T=0.7 | will you ever come back → Et hyej zoyupo? |
|   0 | ✗ | 100.0 | T=0.1 | are you married → Duven et se taduwa? |
|   0 | ✓ | 100.0 | T=0.7 | be good → Su fia. |
|   0 | ✓ |  75.0 | T=0.1 | the cars → ha puri |
|   0 | ✗ |  62.0 | T=0.1 | every man must do his part and every person must l → Hyatwob yefe xer ita gon ay hyatob yefe  |
