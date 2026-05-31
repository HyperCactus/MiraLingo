# Multi-Candidate Translation Eval (with Retrieval Context)

**Date:** 2026-05-28 17:04
**Model:** deepseek-ai/DeepSeek-V4-Flash
**Samples:** 100 (seed=20260526, from train.json)
**Direction:** English → Mirad
**Candidates:** 3 @ [0.1, 0.3, 0.7]
**Config:** n_parallel=32, n_candidates=3, top_k_grammar_rules=3, top_k_relevant_words=0

## Metrics
| Metric | Value |
|--------|-------|
| Normalized Match | 39.0% (39/100) |
| Exact Match | 30.0% (30/100) |
| Avg Judge Score | 90.4/100 (excluding errors) |
| Errors | 0/100 |

## Timing
| | |
|-|--|
| Total wall time | 536s |
| Avg per sample | 5.4s |

## Results  (WE=word_equivalents, RW=relevant_words, GP=grammar_passages)
| # | NM | Judge | Temp | Context | Sample |
|---|----|-------|------|---------|--------|
|   0 | ✗ |  83.0 | T=0.1 | WE:7 RW:0 GP:3 | whose book is this and whose are these books → Duhota dyes se hia? ay duhotasi se hisi  |
|   1 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | small houses → oga tami |
|   2 | ✗ |  63.0 | T=0.7 | WE:6 RW:0 GP:3 | do you all walk to school → Du yet tyope bu tistam? |
|   3 | ✓ | 100.0 | T=0.1 | WE:7 RW:0 GP:3 | our teacher is good but their teacher is bad → Yata tuxut se fia oy yita tuxut se fua. |
|   4 | ✗ |  89.0 | T=0.3 | WE:6 RW:0 GP:3 | this guy s house is on fire → Hia twoba tam magsea. |
|   5 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | we were → yat sa |
|   6 | ✗ |  30.0 | T=0.1 | WE:7 RW:0 GP:3 | unless they say otherwise we will be silent → oven yit du hyuay yat dolo |
|   7 | ✓ | 100.0 | T=0.1 | WE:7 RW:0 GP:3 | the teacher is good and the student is bad → ha tuxut se fia ay ha tixut se fua |
|   8 | ✗ |  40.0 | T=0.1 | WE:4 RW:0 GP:3 | do you know the answer → Duho et te ha dud? |
|   9 | ✗ | 100.0 | T=0.3 | WE:1 RW:0 GP:3 | justice → doyev |
|  10 | ✓ | 100.0 | T=0.1 | WE:5 RW:0 GP:3 | this teacher is very good → hia tuxut se gla fia |
|  11 | ✗ | 100.0 | T=0.1 | WE:6 RW:0 GP:3 | play or get lost but do not laugh → Eku ey oku oy voy dizeudu. |
|  12 | ✗ |  90.0 | T=0.1 | WE:6 RW:0 GP:3 | are the stars bright but the night cold → Ha mari se maa, oy ha moj se oma. |
|  13 | ✓ | 100.0 | T=0.3 | WE:5 RW:0 GP:3 | he or she will come → it upo |
|  14 | ✗ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | do → xer |
|  15 | ✗ | 100.0 | T=0.7 | WE:2 RW:0 GP:3 | everyone s drinks contain ice → Hyata tili bexe yom. |
|  16 | ✓ |  93.0 | T=0.7 | WE:5 RW:0 GP:3 | do they work at home → Duven yit yexe be tam? |
|  17 | ✗ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | easy easily → yuka yukay |
|  18 | ✗ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | these persons → hia tobi |
|  19 | ✗ | 100.0 | T=0.1 | WE:5 RW:0 GP:3 | you are not my father but you know my father → et se voy ata twed oy et te ata twed |
|  20 | ✓ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | the name → ha dyun |
|  21 | ✗ | 100.0 | T=0.1 | WE:3 RW:0 GP:3 | the houses are ugly → ha vua tami se |
|  22 | ✗ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | that house is beautiful → hua via tam se |
|  23 | ✗ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | this person → hia aot |
|  24 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | they know → yit te |
|  25 | ✗ | 100.0 | T=0.1 | WE:5 RW:0 GP:3 | it is not fair to prejudge someone → Voy se yeva javyexer het. |
|  26 | ✓ | 100.0 | T=0.3 | WE:4 RW:0 GP:3 | that teacher is bad → Hua tuxut se fua. |
|  27 | ✓ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | the teacher is good → ha tuxut se fia |
|  28 | ✗ | 100.0 | T=0.1 | WE:6 RW:0 GP:3 | this building is a store but this building was a s → Hia tom se nam oy hia tom sa nam ja. |
|  29 | ✗ |  78.0 | T=0.7 | WE:5 RW:0 GP:3 | you live in the neighborhood → Et bese yeb ha yubyem. |
|  30 | ✗ |  30.0 | T=0.3 | WE:4 RW:0 GP:3 | he looks like a good worker → It tease gel fia yexut. |
|  31 | ✓ | 100.0 | T=0.1 | WE:5 RW:0 GP:3 | you will work at home → et yexo be tam |
|  32 | ✗ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | thanks you were very kind → Hyay! et sa gla tipifa. |
|  33 | ✗ |  50.0 | T=0.3 | WE:4 RW:0 GP:3 | you all do not come → yet voy upu |
|  34 | ✗ |  98.0 | T=0.1 | WE:8 RW:0 GP:3 | this person is beautiful and that one is ugly → Hia aot se via ay huat se vua. |
|  35 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | i do not know → At voy te. |
|  36 | ✗ | 100.0 | T=0.1 | WE:5 RW:0 GP:3 | people often do not love themselves → Tyod glaxag voy ife yout. |
|  37 | ✗ |  58.0 | T=0.7 | WE:5 RW:0 GP:3 | do you know why he did it → Et te duho it xa has? |
|  38 | ✗ |  91.0 | T=0.7 | WE:2 RW:0 GP:3 | i did not know you were coming → at voy ta van et upa |
|  39 | ✗ |  30.0 | T=0.7 | WE:6 RW:0 GP:3 | unless i say otherwise you will be silent → Oven at de hyuyen, et so dola. |
|  40 | ✓ | 100.0 | T=0.1 | WE:3 RW:0 GP:3 | the small house → ha oga tam |
|  41 | ✗ |  86.0 | T=0.7 | WE:4 RW:0 GP:3 | everywhere i go you are there → hyami at pe, et se be hum |
|  42 | ✓ | 100.0 | T=0.1 | WE:3 RW:0 GP:3 | we worked at home → yat yexa be tam |
|  43 | ✗ | 100.0 | T=0.3 | WE:10 RW:0 GP:3 | our house is bigger than yours but this house is n → yata tam se ga aga vyel yetas oy hia tam |
|  44 | ✗ | 100.0 | T=0.1 | WE:5 RW:0 GP:3 | come to the grocery store sometime → Upu bu ha tolnam hej. |
|  45 | ✗ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | ugly things → vua soni |
|  46 | ✓ | 100.0 | T=0.1 | WE:10 RW:0 GP:3 | this desk is small but good and that desk is big b → hia dresem se oga oy fia ay hua dresem s |
|  47 | ✗ |  82.0 | T=0.1 | WE:9 RW:0 GP:3 | they do not know where he or she went but they kno → Yit voy te hom it ey iyt pa oy yit te ho |
|  48 | ✗ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | captive → pixlawat |
|  49 | ✗ |  98.0 | T=0.1 | WE:6 RW:0 GP:3 | every man must do his part → hya twob yefe xer ita gon |
|  50 | ✗ |  98.0 | T=0.3 | WE:3 RW:0 GP:3 | you all were happy → yet iva sa |
|  51 | ✓ | 100.0 | T=0.7 | WE:9 RW:0 GP:3 | we will be there until the end of the season → Yat so hum ju ha uj bi ha jeb. |
|  52 | ✗ |  94.0 | T=0.1 | WE:8 RW:0 GP:3 | both cities have grown and any color will be fine → Hyaewa domi agsa ay hyea volz so fia. |
|  53 | ✗ |  94.0 | T=0.1 | WE:5 RW:0 GP:3 | before this you lived in the suburbs → ja his et teja bi ha yuzdom |
|  54 | ✗ |  92.0 | T=0.3 | WE:8 RW:0 GP:3 | they will give it to us after we pay → Yit buo is bu yat jo van yat nuxe. |
|  55 | ✗ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | that is a good student → Huat se fia tixut. |
|  56 | ✗ |   0.0 | T=0.1 | WE:6 RW:0 GP:3 | you all will do it well → yet xo is fiay |
|  57 | ✓ | 100.0 | T=0.3 | WE:1 RW:0 GP:3 | they came → yit upa |
|  58 | ✓ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | we were happy → yat sa iva |
|  59 | ✗ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | maybe i may go but i do not know → Vey at afu per, oy at voy te. |
|  60 | ✗ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | harmful → bukuyea |
|  61 | ✓ | 100.0 | T=0.7 | WE:0 RW:0 GP:3 | i would go → at pu |
|  62 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | i would do → at xu |
|  63 | ✓ | 100.0 | T=0.1 | WE:3 RW:0 GP:3 | the teachers are good → ha tuxuti se fia |
|  64 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | the teachers → ha tuxuti |
|  65 | ✗ |  86.0 | T=0.1 | WE:7 RW:0 GP:3 | do they know where we went and where you live → Duven yit te hem yat pa ay hem et teje? |
|  66 | ✗ |  64.0 | T=0.3 | WE:10 RW:0 GP:3 | while they are here they will do some work for us → Je van yit se be him, yit xo glay yex av |
|  67 | ✗ | 100.0 | T=0.7 | WE:6 RW:0 GP:3 | i do not know where they went but i know where you → At voy te hom yit pa, oy at te hom et te |
|  68 | ✓ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | the student is good → ha tixut se fia |
|  69 | ✓ |   0.0 | T=0.1 | WE:5 RW:0 GP:3 | he or she will be → it so |
|  70 | ✗ |  78.0 | T=0.7 | WE:4 RW:0 GP:3 | you should tell her that → Et yeyfe der iyt van. |
|  71 | ✓ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | they come → yit upe |
|  72 | ✓ |   0.0 | T=0.1 | WE:3 RW:0 GP:3 | he or she would go → it pu |
|  73 | ✗ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | i am not your father but i know your father → At voy se eta twed oy at te eta twed. |
|  74 | ✓ | 100.0 | T=0.1 | WE:6 RW:0 GP:3 | yours are worth more than mine → Etasi naze ga vyel atasi. |
|  75 | ✗ | 100.0 | T=0.3 | WE:4 RW:0 GP:3 | whenever you talk i laugh → Hyejod ho et dale, at dizeude. |
|  76 | ✓ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | that student is good → hua tixut se fia |
|  77 | ✓ | 100.0 | T=0.1 | WE:4 RW:0 GP:3 | the dog bit me → Ha yepet teupixa at. |
|  78 | ✓ | 100.0 | T=0.1 | WE:8 RW:0 GP:3 | they know that we will come and they will be happy → Yit te van yat upo ay yit so iva. |
|  79 | ✗ |  89.0 | T=0.1 | WE:3 RW:0 GP:3 | we were indeed there → yat vay sa be hum |
|  80 | ✓ | 100.0 | T=0.3 | WE:4 RW:0 GP:3 | your teacher is good → eta tuxut se fia |
|  81 | ✗ |  99.0 | T=0.1 | WE:2 RW:0 GP:3 | he sings beautifully → it deuze viay |
|  82 | ✗ | 100.0 | T=0.3 | WE:5 RW:0 GP:3 | this book is my favorite → Hia dyes se ata gaifwas. |
|  83 | ✗ | 100.0 | T=0.7 | WE:6 RW:0 GP:3 | the students walk to school every day → ha tixuti tyope bu tistam hyajub |
|  84 | ✓ | 100.0 | T=0.1 | WE:0 RW:0 GP:3 | fathers → twedi |
|  85 | ✗ | 100.0 | T=0.7 | WE:9 RW:0 GP:3 | these words are prohibited but this book is my fav → hia duni se ofwa oy hia dyes se ata gaif |
|  86 | ✗ | 100.0 | T=0.7 | WE:4 RW:0 GP:3 | is that student bad → Hua tixut se fua? |
|  87 | ✗ |  87.0 | T=0.1 | WE:10 RW:0 GP:3 | he or she is going home but he or she will work at → it pe be tam oy it yexo be tam |
|  88 | ✗ |  95.0 | T=0.7 | WE:10 RW:0 GP:3 | the sun has risen so you must get up out of bed → Ha amar yapa, so et yefe yaper oyeb bi s |
|  89 | ✗ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | they sing beautifully → Yit deuze viay. |
|  90 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | a teacher → tuxut |
|  91 | ✓ | 100.0 | T=0.1 | WE:0 RW:0 GP:3 | birds → pati |
|  92 | ✗ | 100.0 | T=0.3 | WE:3 RW:0 GP:3 | are the stars bright → Duven ha mari se maa? |
|  93 | ✓ | 100.0 | T=0.1 | WE:0 RW:0 GP:3 | mothers → teydi |
|  94 | ✓ |  92.0 | T=0.3 | WE:5 RW:0 GP:3 | he or she was going home → it peya tam |
|  95 | ✗ |  92.0 | T=0.1 | WE:5 RW:0 GP:3 | will you ever come back → Et zoyupo hyej? |
|  96 | ✗ | 100.0 | T=0.3 | WE:3 RW:0 GP:3 | are you married → Du et se tadxwa? |
|  97 | ✓ | 100.0 | T=0.1 | WE:2 RW:0 GP:3 | be good → Su fia. |
|  98 | ✓ | 100.0 | T=0.1 | WE:1 RW:0 GP:3 | the cars → ha puri |
|  99 | ✗ |  91.0 | T=0.1 | WE:10 RW:0 GP:3 | every man must do his part and every person must l → Hyatwob yefe xer twoba gon ay hyaot yefe |

## Retrieval Detail (first 10 examples)

### Example 0: whose book is this and whose are these books
- **Pred:** Duhota dyes se hia? ay duhotasi se hisi dyesi?  **Gold:** duhota dyes se his ay duhotasi se hia dyesi  **Score:** 83
- **Word equivalents (7):** {'whose': 'hatas, heta, hota, hotas', 'book': 'draves, dyes', 'is': 'se', 'this': 'hi-, hia, hinog', 'and': 'ay', 'are': 'se', 'these': 'hi-, hia, hiati'}
- **Grammar passages (3):**
  [1] Rule ID: determiner.demonstrative_hia_hua
Description: hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and pl...
  [2] Rule ID: pronoun.possessive_add_a_s_si
Description: Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s ...
  [3] Rule ID: determiner.interrogative_duh_forms
Description: Interrogative deictic determiners are built with duh- plus a category ending: duhot? who/whom, duhos? what, duhota? whose, duhom? where, duhoj?...

