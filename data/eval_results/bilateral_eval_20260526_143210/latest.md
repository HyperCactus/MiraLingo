# Bidirectional Translation Evaluation

**Date:** 2026-05-26 14:35 | **Model:** deepseek-ai/DeepSeek-V4-Flash  
**Devset:** 30 random sentences (≥5 English words, seed=20260526)  
**Metric:** Normalized Match (punctuation/whitespace/capitalization insensitive)  

## Summary
| Direction | Score | Correct/Total |
|---|---|---|
| En→Mir | 10.0% | 3/30 |
| Mir→En | 43.3% | 13/30 |

## Error Types — En→Mir (27 failures)
| Type | Count |
|---|---|
| partial_phrase_diff | 18 |
| minor_word_diff | 6 |
| major_diff | 3 |

## Error Types — Mir→En (17 failures)
| Type | Count |
|---|---|
| partial_phrase_diff | 10 |
| minor_word_diff | 5 |
| none | 1 |
| major_diff | 1 |

## Failure Cases — En→Mir

**[partial_phrase_diff]** how much did she win and who won
- Gold:     `duhoglas iyt aka ay duhot aka`
- Predicted: `duhonog ya iyt ak ay hoti ya ak`

**[major_diff]** play or get lost but do not laugh
- Gold:     `eku ey pilu oy von hihidu`
- Predicted: `Eku o oku ut, va von dizeudu.`

**[partial_phrase_diff]** my house is bigger than yours but this house is not as big as mine
- Gold:     `ata tam se ga aga vyel etas oy hia tam voy se ge aga vyel atas`
- Predicted: `Ata tam se gaaga vyel eta tam, oy hia tam voy se gaaga asolk ata tam.`

**[minor_word_diff]** you worked at home and you did it well
- Gold:     `et yexa be tam ay et xa has fi`
- Predicted: `Et yexa be tam ay et xa has fiay.`

**[partial_phrase_diff]** i am not your father but i know your father
- Gold:     `at voy se eta twed oy at tre eta twed`
- Predicted: `At voy eta twed oy at tye eta twed.`

**[minor_word_diff]** they will not start until you get here
- Gold:     `yit voy ijo ju van et puo him`
- Predicted: `Yit voy ijo ju van et upe him.`

**[partial_phrase_diff]** do you know why he did it
- Gold:     `duven et te hosav it xa his`
- Predicted: `Du et te hosav it has xwa?`

**[partial_phrase_diff]** he looks like a good worker
- Gold:     `wit tease fia yexut`
- Predicted: `It vyeys fia yexut.`

**[partial_phrase_diff]** this teacher is very good
- Gold:     `hia tuxut se gla fia`
- Predicted: `hiatuxut gla fia`

**[partial_phrase_diff]** we know that you will come and we will be happy
- Gold:     `yat te van et upo ay yat so iva`
- Predicted: `yat ter et upo ay yat so iva`

**[partial_phrase_diff]** the student walks to school every day
- Gold:     `ha tixut tyoyape tistam hyajub`
- Predicted: `ha tixut tyope pu tistam bu hya jub`

**[partial_phrase_diff]** people often do not love themselves but one must love oneself
- Gold:     `yot glaxag voy ife yout oy ot yefe ifer out`
- Predicted: `Yot glaxagay voy ifonier yout, oy ot yefe ifonier out.`

**[minor_word_diff]** you live downtown now and you work at a grocery store near here
- Gold:     `et tambese zedom hij ay et yexe be tolnam yub bi him`
- Predicted: `et tejye be zedom hij ay yexe be tolnam yub bi him`

**[partial_phrase_diff]** you all will do it well
- Gold:     `yet xo has fi`
- Predicted: `Eyt o vay has fiay.`

**[partial_phrase_diff]** i myself do not smoke but people often smoke
- Gold:     `at aut voy movie oy yot glaxag movie`
- Predicted: `At aut voy movie, oy tyod gla jodi movie.`

**[major_diff]** we know that he or she will come and we will be happy
- Gold:     `yat te van it upo ay yat so iva`
- Predicted: `yet treye it wo upu ay yet wo iva`

**[minor_word_diff]** i worked at home but now i work at a grocery store near here
- Gold:     `at yexa be tam oy at yexe be tolnam yub bi him`
- Predicted: `At yexa be tam oy hij at yexe be tolnam yub bi him.`

**[minor_word_diff]** he or she is going home
- Gold:     `it peye tam`
- Predicted: `It peye bu tam.`

**[minor_word_diff]** what do we do for work now
- Gold:     `duhos yat xe av yex hij`
- Predicted: `Duho yat xe av yex hij?`

**[partial_phrase_diff]** before this i lived in the suburbs
- Gold:     `ja his at tambesa ha yuzdom`
- Predicted: `Ja his at besa bi ha oyebdomi.`

**[partial_phrase_diff]** forgive those who hurt you
- Gold:     `yovobu hoti fyuxe et`
- Predicted: `Yovobiu hati ho fyuxa et.`

**[partial_phrase_diff]** we would be going home
- Gold:     `yat peyu tam`
- Predicted: `yet peyeye tam`

**[major_diff]** you live in the neighborhood right and you work near here
- Gold:     `et tambese ha yubem vao ay et yexe yub bi him`
- Predicted: `Et teje be doeym ay et yexe yuba him, vya?`

**[partial_phrase_diff]** when we arrived the fun began
- Gold:     `hoj yat pua ha if ija`
- Predicted: `Ha job hu yat puasa, ha if ija.`

**[partial_phrase_diff]** whenever we talk they laugh
- Gold:     `hyej yat dale yit hihide`
- Predicted: `Hyejod ho yat dale, yit dizeude.`

**[partial_phrase_diff]** we worked at home but now we work at a grocery store near here
- Gold:     `yat yexa be tam oy yat yexe be tolnam yub bi him`
- Predicted: `Yat yexa be tam oy hij yat yex bi ana telnunam yub bi him.`

**[partial_phrase_diff]** you all do not know
- Gold:     `yet voy te`
- Predicted: `Hyayt voy tru.`

## Failure Cases — Mir→En

**[partial_phrase_diff]** eku ey pilu oy von hihidu
- Gold:     `play or get lost but do not laugh`
- Predicted: `Play or flee, but don't laugh.`

**[partial_phrase_diff]** yit voy ijo ju van et puo him
- Gold:     `they will not start until you get here`
- Predicted: `They will not leave until you arrive here.`

**[none]** yot glaxag voy ife yout oy ot yefe ifer out
- Gold:     `people often do not love themselves but one must love oneself`
- Predicted: `People do not often love themselves, but one must love oneself.`

**[minor_word_diff]** duven et te hosav it xa his
- Gold:     `do you know why he did it`
- Predicted: `Do you know why he did this?`

**[partial_phrase_diff]** wit tease fia yexut
- Gold:     `he looks like a good worker`
- Predicted: `He/she teases a good worker.`

**[minor_word_diff]** at aut voy movie oy yot glaxag movie
- Gold:     `i myself do not smoke but people often smoke`
- Predicted: `I myself do not move, but people often move.`

**[partial_phrase_diff]** yat te van it upo ay yat so iva
- Gold:     `we know that he or she will come and we will be happy`
- Predicted: `We know that he will come and we will be happy.`

**[partial_phrase_diff]** yat peyu tam
- Gold:     `we would be going home`
- Predicted: `We are going home.`

**[partial_phrase_diff]** yovobu hoti fyuxe et
- Gold:     `forgive those who hurt you`
- Predicted: `Apologize to those who harm you.`

**[partial_phrase_diff]** it peye tam
- Gold:     `he or she is going home`
- Predicted: `It is going home.`

**[partial_phrase_diff]** duhoglas iyt aka ay duhot aka
- Gold:     `how much did she win and who won`
- Predicted: `the winning how much she and the winning who?`

**[minor_word_diff]** hoj yat pua ha if ija
- Gold:     `when we arrived the fun began`
- Predicted: `When we arrived, the joy began.`

**[major_diff]** ja his at tambesa ha yuzdom
- Gold:     `before this i lived in the suburbs`
- Predicted: `Let this be my home in the suburb.`

**[partial_phrase_diff]** yat yexa be tam oy yat yexe be tolnam yub bi him
- Gold:     `we worked at home but now we work at a grocery store near here`
- Predicted: `We worked at home but we work at the grocery store near here.`

**[partial_phrase_diff]** at yexa be tam oy at yexe be tolnam yub bi him
- Gold:     `i worked at home but now i work at a grocery store near here`
- Predicted: `I worked at home but I am working at a grocery store near here.`

**[minor_word_diff]** hyej yat dale yit hihide
- Gold:     `whenever we talk they laugh`
- Predicted: `Anytime we talk, they laugh.`

**[minor_word_diff]** et tambese ha yubem vao ay et yexe yub bi him
- Gold:     `you live in the neighborhood right and you work near here`
- Predicted: `Do you live in the neighborhood, and do you work near here?`

## Full Results — En→Mir
| # | English | Gold | Predicted | S |
|---|---|---|---|---|
| 0 | i am not your father but i know your father | at voy se eta twed oy at tre e | At voy eta twed oy at tye eta  | ✗ |
| 1 | how much did she win and who won | duhoglas iyt aka ay duhot aka | duhonog ya iyt ak ay hoti ya a | ✗ |
| 2 | people often do not love themselves but one must l | yot glaxag voy ife yout oy ot  | Yot glaxagay voy ifonier yout, | ✗ |
| 3 | play or get lost but do not laugh | eku ey pilu oy von hihidu | Eku o oku ut, va von dizeudu. | ✗ |
| 4 | you can either stay or leave | et yafe hyeawa beser ey pier | Et yafe hyeawa beser ey pier. | ✓ |
| 5 | you worked at home and you did it well | et yexa be tam ay et xa has fi | Et yexa be tam ay et xa has fi | ✗ |
| 6 | my house is bigger than yours but this house is no | ata tam se ga aga vyel etas oy | Ata tam se gaaga vyel eta tam, | ✗ |
| 7 | they will not start until you get here | yit voy ijo ju van et puo him | Yit voy ijo ju van et upe him. | ✗ |
| 8 | do you know why he did it | duven et te hosav it xa his | Du et te hosav it has xwa? | ✗ |
| 9 | he looks like a good worker | wit tease fia yexut | It vyeys fia yexut. | ✗ |
| 10 | you live downtown now and you work at a grocery st | et tambese zedom hij ay et yex | et tejye be zedom hij ay yexe  | ✗ |
| 11 | we know that you will come and we will be happy | yat te van et upo ay yat so iv | yat ter et upo ay yat so iva | ✗ |
| 12 | this teacher is very good | hia tuxut se gla fia | hiatuxut gla fia | ✗ |
| 13 | the student walks to school every day | ha tixut tyoyape tistam hyajub | ha tixut tyope pu tistam bu hy | ✗ |
| 14 | forgive those who hurt you | yovobu hoti fyuxe et | Yovobiu hati ho fyuxa et. | ✗ |
| 15 | we know that he or she will come and we will be ha | yat te van it upo ay yat so iv | yet treye it wo upu ay yet wo  | ✗ |
| 16 | i myself do not smoke but people often smoke | at aut voy movie oy yot glaxag | At aut voy movie, oy tyod gla  | ✗ |
| 17 | you all will do it well | yet xo has fi | Eyt o vay has fiay. | ✗ |
| 18 | we would be going home | yat peyu tam | yet peyeye tam | ✗ |
| 19 | before this i lived in the suburbs | ja his at tambesa ha yuzdom | Ja his at besa bi ha oyebdomi. | ✗ |
| 20 | i worked at home but now i work at a grocery store | at yexa be tam oy at yexe be t | At yexa be tam oy hij at yexe  | ✗ |
| 21 | he or she is going home | it peye tam | It peye bu tam. | ✗ |
| 22 | what do we do for work now | duhos yat xe av yex hij | Duho yat xe av yex hij? | ✗ |
| 23 | when we arrived the fun began | hoj yat pua ha if ija | Ha job hu yat puasa, ha if ija | ✗ |
| 24 | you live in the neighborhood right and you work ne | et tambese ha yubem vao ay et  | Et teje be doeym ay et yexe yu | ✗ |
| 25 | you all do not know | yet voy te | Hyayt voy tru. | ✗ |
| 26 | we worked at home but now we work at a grocery sto | yat yexa be tam oy yat yexe be | Yat yexa be tam oy hij yat yex | ✗ |
| 27 | we will work at home and we will be happy | yat yexo be tam ay yat so iva | Yat yexo be tam ay yat so iva. | ✓ |
| 28 | whenever we talk they laugh | hyej yat dale yit hihide | Hyejod ho yat dale, yit dizeud | ✗ |
| 29 | your name is john and my name is bill | eta dyun se john ay ata dyun s | Eta dyun se John ay ata dyun s | ✓ |

## Full Results — Mir→En
| # | Mirad | Gold | Predicted | S |
|---|---|---|---|---|
| 0 | at voy se eta twed oy at tre e | i am not your father but i know your father | I am not your father but I know your father. | ✓ |
| 1 | duhoglas iyt aka ay duhot aka | how much did she win and who won | the winning how much she and the winning who? | ✗ |
| 2 | yot glaxag voy ife yout oy ot  | people often do not love themselves but one must l | People do not often love themselves, but one must  | ✗ |
| 3 | eku ey pilu oy von hihidu | play or get lost but do not laugh | Play or flee, but don't laugh. | ✗ |
| 4 | et yafe hyeawa beser ey pier | you can either stay or leave | You can either stay or leave. | ✓ |
| 5 | et yexa be tam ay et xa has fi | you worked at home and you did it well | You worked at home and you did it well. | ✓ |
| 6 | ata tam se ga aga vyel etas oy | my house is bigger than yours but this house is no | My house is bigger than yours but this house is no | ✓ |
| 7 | yit voy ijo ju van et puo him | they will not start until you get here | They will not leave until you arrive here. | ✗ |
| 8 | duven et te hosav it xa his | do you know why he did it | Do you know why he did this? | ✗ |
| 9 | wit tease fia yexut | he looks like a good worker | He/she teases a good worker. | ✗ |
| 10 | et tambese zedom hij ay et yex | you live downtown now and you work at a grocery st | You live downtown now and you work at a grocery st | ✓ |
| 11 | yat te van et upo ay yat so iv | we know that you will come and we will be happy | We know that you will come and we will be happy. | ✓ |
| 12 | hia tuxut se gla fia | this teacher is very good | This teacher is very good. | ✓ |
| 13 | ha tixut tyoyape tistam hyajub | the student walks to school every day | The student walks to school every day. | ✓ |
| 14 | yovobu hoti fyuxe et | forgive those who hurt you | Apologize to those who harm you. | ✗ |
| 15 | yat te van it upo ay yat so iv | we know that he or she will come and we will be ha | We know that he will come and we will be happy. | ✗ |
| 16 | at aut voy movie oy yot glaxag | i myself do not smoke but people often smoke | I myself do not move, but people often move. | ✗ |
| 17 | yet xo has fi | you all will do it well | You all will do it well. | ✓ |
| 18 | yat peyu tam | we would be going home | We are going home. | ✗ |
| 19 | ja his at tambesa ha yuzdom | before this i lived in the suburbs | Let this be my home in the suburb. | ✗ |
| 20 | at yexa be tam oy at yexe be t | i worked at home but now i work at a grocery store | I worked at home but I am working at a grocery sto | ✗ |
| 21 | it peye tam | he or she is going home | It is going home. | ✗ |
| 22 | duhos yat xe av yex hij | what do we do for work now | What do we do for work now? | ✓ |
| 23 | hoj yat pua ha if ija | when we arrived the fun began | When we arrived, the joy began. | ✗ |
| 24 | et tambese ha yubem vao ay et  | you live in the neighborhood right and you work ne | Do you live in the neighborhood, and do you work n | ✗ |
| 25 | yet voy te | you all do not know | You all do not know | ✓ |
| 26 | yat yexa be tam oy yat yexe be | we worked at home but now we work at a grocery sto | We worked at home but we work at the grocery store | ✗ |
| 27 | yat yexo be tam ay yat so iva | we will work at home and we will be happy | We will work at home and we will be happy. | ✓ |
| 28 | hyej yat dale yit hihide | whenever we talk they laugh | Anytime we talk, they laugh. | ✗ |
| 29 | eta dyun se john ay ata dyun s | your name is john and my name is bill | Your name is John and my name is Bill. | ✓ |