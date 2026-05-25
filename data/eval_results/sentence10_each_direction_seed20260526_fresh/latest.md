# M006 S01 Baseline Inspection Report

## Run Metadata

- started_at: 2026-05-25T13:24:21.921980+00:00
- completed_at: 2026-05-25T13:28:04.502285+00:00
- mode: live
- model: deepseek-ai/DeepSeek-V4-Flash
- api_preflight: ok
- devset_size: 20
- elapsed: 222580 ms (222.58 s)
- failed_example_count: 0
- failed_example_ids: none

## Preflight Call and Cost Estimate

- estimated_total_calls: 20
- estimated_cost_usd: $0.000000
- total_calls_recorded: 20
- english_to_mirad_examples: 10
- mirad_to_english_examples: 10

## Score Summary by Direction

| Direction | Examples | Normalized Matches | Errors | Success Rate |
|-----------|----------|--------------------|--------|--------------|
| English → Mirad | 10 | 2 | 0 | 20.0% |
| Mirad → English | 10 | 4 | 0 | 40.0% |

## Failure Taxonomy Legend

| Label | Example Count |
|-------|---------------|
| `csv_index:522` | 2 |
| `csv_index:749` | 2 |
| `csv_index:802` | 2 |
| `csv_index:808` | 2 |
| `csv_index:861` | 2 |
| `csv_index:878` | 2 |
| `csv_index:906` | 2 |
| `csv_index:947` | 2 |
| `csv_index:979` | 2 |
| `csv_index:990` | 2 |
| `en_to_mir` | 10 |
| `mir_to_en` | 10 |
| `sentence-min5` | 20 |

## Per-Example Table

| ID | Direction | Status | Phase | Exact | Normalized | Failure Labels | Rule IDs | Elapsed |
|----|-----------|--------|-------|-------|------------|----------------|----------|---------|
| sent10-en-01-csv-0522 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:522 | verb.simple.active_suffixes, verb.no_person_number_agreement | 19832 ms |
| sent10-en-02-csv-0749 | English → Mirad | ok | complete | yes | yes | sentence-min5, en_to_mir, csv_index:749 | verb.simple.active_suffixes, verb.no_person_number_agreement | 937 ms |
| sent10-en-03-csv-0802 | English → Mirad | ok | complete | no | yes | sentence-min5, en_to_mir, csv_index:802 | verb.progressive.active_ey_plus_tense, verb.conditional_imperative_u_subject, verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, verb.no_person_number_agreement, verb.infinitive_er_stem | 1438 ms |
| sent10-en-04-csv-0808 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:808 | verb.simple.active_suffixes, pronoun.english_it.translation_rules, conjunction.coordinate_ay_ey_oy, verb.no_person_number_agreement, syntax.object.after_predicate | 1911 ms |
| sent10-en-05-csv-0861 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:861 | verb.simple.active_suffixes, verb.no_person_number_agreement, syntax.object.after_predicate, verb.infinitive_er_stem, syntax.basic_svo | 1030 ms |
| sent10-en-06-csv-0878 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:878 | verb.simple.active_suffixes, conjunction.subordinate_van_that, verb.conditional_imperative_u_subject | 1187 ms |
| sent10-en-07-csv-0906 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:906 | determiner.demonstrative_hia_hua, adjective.descriptive.ends_a, adjective.position.before_noun, noun.modifiers.order_no_agreement, conjunction.coordinate_ay_ey_oy, syntax.basic_svo, verb.no_person_number_agreement | 1326 ms |
| sent10-en-08-csv-0947 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:947 | pronoun.gender.optional_w_y, verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, verb.simple.passive_suffixes | 1740 ms |
| sent10-en-09-csv-0979 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:979 | determiner.demonstrative_hia_hua, determiner.animate_t_thing_s_plural_i, verb.no_person_number_agreement, noun.article.definite_ha, conjunction.coordinate_ay_ey_oy, pronoun.possessive_add_a_s_si, verb.stative_complement_after_ser | 1507 ms |
| sent10-en-10-csv-0990 | English → Mirad | ok | complete | no | no | sentence-min5, en_to_mir, csv_index:990 | verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, preposition.boy_without | 1404 ms |
| sent10-mi-01-csv-0522 | Mirad → English | ok | complete | no | no | sentence-min5, mir_to_en, csv_index:522 | verb.simple.active_suffixes, syntax.basic_svo | 39591 ms |
| sent10-mi-02-csv-0749 | Mirad → English | ok | complete | no | no | sentence-min5, mir_to_en, csv_index:749 | verb.simple.active_suffixes, verb.no_person_number_agreement | 15782 ms |
| sent10-mi-03-csv-0802 | Mirad → English | ok | complete | no | no | sentence-min5, mir_to_en, csv_index:802 | verb.modal_hypothetical_mitigates, verb.stative_complement_after_ser, conjunction.coordinate_ay_ey_oy | 23071 ms |
| sent10-mi-04-csv-0808 | Mirad → English | ok | complete | no | no | sentence-min5, mir_to_en, csv_index:808 | verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, conjunction.subordinate_van_that, verb.stative_complement_after_ser, verb.no_person_number_agreement | 18895 ms |
| sent10-mi-05-csv-0861 | Mirad → English | ok | complete | no | yes | sentence-min5, mir_to_en, csv_index:861 | verb.simple.active_suffixes | 17780 ms |
| sent10-mi-06-csv-0878 | Mirad → English | ok | complete | no | no | sentence-min5, mir_to_en, csv_index:878 | verb.simple.active_suffixes, conjunction.subordinate_van_that, syntax.basic_svo | 14662 ms |
| sent10-mi-07-csv-0906 | Mirad → English | ok | complete | no | yes | sentence-min5, mir_to_en, csv_index:906 | conjunction.coordinate_ay_ey_oy, determiner.demonstrative_hia_hua | 11613 ms |
| sent10-mi-08-csv-0947 | Mirad → English | ok | complete | no | yes | sentence-min5, mir_to_en, csv_index:947 | verb.simple.active_suffixes, verb.infinitive_er_stem, verb.no_person_number_agreement, conjunction.coordinate_ay_ey_oy, pronoun.gender.optional_w_y | 13622 ms |
| sent10-mi-09-csv-0979 | Mirad → English | ok | complete | no | yes | sentence-min5, mir_to_en, csv_index:979 | conjunction.coordinate_ay_ey_oy, determiner.demonstrative_hia_hua, pronoun.possessive_add_a_s_si | 10229 ms |
| sent10-mi-10-csv-0990 | Mirad → English | ok | complete | no | no | sentence-min5, mir_to_en, csv_index:990 | conjunction.coordinate_ay_ey_oy, verb.simple.active_suffixes | 25023 ms |

## Detailed Examples

### sent10-en-01-csv-0522

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 19832
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:522
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

unless you say otherwise I will be silent

#### Expected Output

Oven et do hyuyen, at dolo.

#### Prediction

Oven et du hyuay, at dolso.

#### Word Equivalents

- be → baelk
- beamed → naudxwa
- behest → avan
- being → sat, sea, sean, seat, sen, zapuen
- being silent → dolsea, dolsen
- else → ey, ogel hus, ven voy
- elsewise → hyuyen
- except → boy, gob, goy, ovabiwa, oy, oyebexea, oyebexwa, oyebiwa, yon bi
- how else → duhohyuyen
- keeping silent → oden
- not if → voy ven
- other than → hyu vyel, ogel vyel
- otherwise → hyuay, hyugel, hyuyen, ogel hus, ven voy
- said → dwa
- sayer → dut
- saying → ajdun, den, vyandun, vyanegdwas
- silenced → doluwa
- silent → dola, dolea, oseuxdwa, seuxoya, seuxuka, xeusoya, xeusuka
- silently → dolay
- they say... → Ot de...
- to be → ser
- to say → der
- to will → fer
- unless → gob van, oven
- will → fan, fon, fwas, uja fondras
- willful → fonaya, fonika
- willfully → fonay, fonikay
- williwaw → ommapaz
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion
2. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
3. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.stative_complement_after_ser
Description: Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.
Pseudocode: if verb == ser or verb.is_stative_intransitive:
    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause
    clause = subject + verb + complement
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: derivation.noun.gerund_en
Description: The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.
Pseudocode: if verb_stem nominalized_as_action:
    noun = verb_stem + 'en'
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
4. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

### sent10-en-02-csv-0749

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 937
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: sentence-min5, en_to_mir, csv_index:749
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

you do not work at home

#### Expected Output

Et voy yexe be tam.

#### Prediction

Et voy yexe be tam.

#### Word Equivalents

- at → atulk
- at least → gwoay
- atilt → abaea
- atonally → oyseuzay
- atto → goralyi-, goralyu-
- home → be tam, taam, tam
- home sweet home → taamif
- homey → taamyena, yukoma
- house → tam
- to have a home → embexer
- to work → exer, yexer
- travail → yeex
- work → yex
- working → exea, yexea, yexen
- works → yexyan
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.
Pseudocode: if adjective.can_take_o_negation and not ambiguous:
    form = 'o' + adjective
else if adjective.begins_with_consonant:
    form = 'lo' + adjective
else:
    form = 'ol' + adjective
if meaning == hostile_or_anti:
    form = one_of(['lyo' + adjective, 'ov' + adjective])
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: adjective.opposites.vowel_switching
Description: Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.
Pseudocode: if adjective.pattern == i_u_contrast:
    positive = stem_with('i')
    negative = stem_with('u')
if adjective.pattern == a_e_o_scale:
    positive = stem_with('a')
    intermediate = stem_with('e')
    negative = stem_with('o')
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er
3. [grammar_rules]
Rule ID: verb.motion_communication_omit_direction_preposition
Description: Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.
Pseudocode: if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:
    omit preposition
    place object according_to verb_complement_rules
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.
Pseudocode: choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal
choose category_suffix by circumstance: place/time/manner
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: preposition.bi_of_possession_partitive
Description: bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.
Pseudocode: if relation in ['of', 'possessive', 'partitive']:
    use head + 'bi' + complement
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: pronoun.personal.invariant_case
Description: Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.
Pseudocode: pronoun_form = lookup_person_number_animacy_gender()
do_not_inflect_for_case
determine_case_from_position_or_preposition
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition
4. [grammar_rules]
Rule ID: pronoun.personal.invariant_case
Description: Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.
Pseudocode: pronoun_form = lookup_person_number_animacy_gender()
do_not_inflect_for_case
determine_case_from_position_or_preposition
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

### sent10-en-03-csv-0802

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1438
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: sentence-min5, en_to_mir, csv_index:802
- retrieval_rule_ids: verb.progressive.active_ey_plus_tense, verb.conditional_imperative_u_subject, verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, verb.no_person_number_agreement, verb.infinitive_er_stem
- retrieval_warning: none
- error_summary: none

#### Input

we would be going home, but we would be happy here

#### Expected Output

Yat peyu tam, oy yat su iva him.

#### Prediction

yat peyu tam, oy yat su iva him

#### Word Equivalents

- be → baelk
- beamed → naudxwa
- behest → avan
- being → sat, sea, sean, seat, sen, zapuen
- feeling happy → ivtosea, ivtosen
- from here → bi him
- go in → per yeb
- goer → put
- going → pea, pen
- happily → ivay
- happiness → ivan
- happy → fikyeoja, iva
- here → be him, hiim, him
- here and there → huim
- hereof → bi hiis
- home → be tam, taam, tam
- home sweet home → taamif
- homey → taamyena, yukoma
- house → tam
- let go → lobexwa, lopexwa, yivafxwa
- our → aeta, ayet, ayita, yata
- progress → zapas, zaynog, zayp, zaypan, zaypas
- progressing → zaypasea
- progressive → tepyiva, zapasyea, zaypasina, zaypasyea
- progressively → zapaseay, zaypasyeay
- progressiveness → tepyivan, zaypasinan, zaypasyean
- to be → ser
- to get happy → ivser
- to go → per
- to have a home → embexer
- to here → bu hem
- to wee → tiyabiler
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o
2. [grammar_rules]
Rule ID: verb.progressive.passive_ew_plus_tense
Description: The passive progressive inserts e plus passive/buffer w before the final tense/mood vowel: -ewe, -ewa, -ewo, -ewu.
Pseudocode: if aspect == progressive and voice == passive:
    form = stem + 'ew' + final_tense_vowel
Examples:
- Mirad: Has xewe. | English: It is being done. | Note: x- + ew + e
- Mirad: Has xewa. | English: It was being done. | Note: x- + ew + a

Rule ID: verb.progressive.active_ey_plus_tense
Description: The active progressive inserts the present aspect vowel e plus buffer y between the stem and final tense/mood vowel: -eye, -eya, -eyo, -eyu.
Pseudocode: if aspect == progressive and voice == active:
    form = stem + 'ey' + final_tense_vowel
Examples:
- Mirad: at xeye | English: I am doing | Note: x- + ey + e
- Mirad: at xeya | English: I was doing | Note: x- + ey + a
- Mirad: at xeyo | English: I will be doing | Note: x- + ey + o

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: derivation.noun.gerund_en
Description: The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.
Pseudocode: if verb_stem nominalized_as_action:
    noun = verb_stem + 'en'
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
3. [grammar_rules]
Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o
4. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o
5. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

### sent10-en-04-csv-0808

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1911
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:808
- retrieval_rule_ids: verb.simple.active_suffixes, pronoun.english_it.translation_rules, conjunction.coordinate_ay_ey_oy, verb.no_person_number_agreement, syntax.object.after_predicate
- retrieval_warning: none
- error_summary: none

#### Input

we know that he or she will come and we will be happy

#### Expected Output

Yat te van it upo ay yat so iva.

#### Prediction

Yat te van it upo ay yat ivso.

#### Word Equivalents

- and → ay
- and/or → aey
- anded → ayxwa
- anding → ayxen
- both...and → hyaewa...ay, vay...ay
- come → upya
- come with → uper bay
- coming → upea, upen, yup
- complement → fyid, gaun, iksag, ikxus
- complementary → gauna, iksaga, ikxusa
- complementing → gaunxea, gaunxen
- compliment → fid, fidun, vid
- feeling happy → ivtosea, ivtosen
- happily → ivay
- happiness → ivan
- happy → fikyeoja, iva
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- her whom → hoyt
- it → has, his, hus, is
- its → hasa, hisa, husa, isa, ita
- know that → ter van
- knowing → tea, ten
- known → trawa, twa
- neuter → evtooba, otooba
- neutered → otoobaxwa
- neutering → otoobaxen
- neutral → eva, tepeva
- our → aeta, ayet, ayita, yata
- personal pronoun → aota avdun
- possessive pronoun → bexena avdyun
- pronominal → avduna
- pronoun → avdun
- she who → hoyt
- something known → twas
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- to come → uper
- to come about → kaxwer, kyeser, vyamser
- to complement → gaunxer
- to get happy → ivser
- to know → ter
- to neuter → otoobaxer
- to pronominalize → avdunxer
- to wee → tiyabiler
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
2. [grammar_rules]
Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: syntax.object.after_predicate
Description: In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.
Pseudocode: predicate = finite_verb + optional_adverbs
if direct_object: place after predicate
if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase
3. [grammar_rules]
Rule ID: pronoun.personal.invariant_case
Description: Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.
Pseudocode: pronoun_form = lookup_person_number_animacy_gender()
do_not_inflect_for_case
determine_case_from_position_or_preposition
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: syntax.object.after_predicate
Description: In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.
Pseudocode: predicate = finite_verb + optional_adverbs
if direct_object: place after predicate
if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object
4. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees
5. [grammar_rules]
Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
6. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: adjective.opposites.vowel_switching
Description: Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.
Pseudocode: if adjective.pattern == i_u_contrast:
    positive = stem_with('i')
    negative = stem_with('u')
if adjective.pattern == a_e_o_scale:
    positive = stem_with('a')
    intermediate = stem_with('e')
    negative = stem_with('o')
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

### sent10-en-05-csv-0861

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1030
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:861
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement, syntax.object.after_predicate, verb.infinitive_er_stem, syntax.basic_svo
- retrieval_warning: none
- error_summary: none

#### Input

even if I disagree, you will support me

#### Expected Output

Gey ven at yontexe, et bolo at.

#### Prediction

Gel ven at yontexe, et bolo at.

#### Word Equivalents

- as if → gel ven, hoyen ven
- disagreeably → loifxeay, oyansanseay
- disagreed → yontexwa
- disagreeing → yontexea, yontexen
- disagreement → yontex
- even → euna, gea, geeksaga, geneda, genega, gey, nega, negxwa, yeza, zyifa, zyima, zyina
- even number → euna sag
- even- → ge-
- evened → zyimxwa
- getting even → yevkexen, zoyyevaxen
- if → ven
- if not → ven voy
- if so → ven vay
- if yes → ven va
- support → baun, boar, bol, bolar, bolmuf, bolun, obun, yabex, yabexar
- supportability → bolyafwan
- supported → bolwa, bowa, obunwa, yabexwa
- supporting → bolea, bolen, yabexea, yabexen
- to disagree → yontexer
- to support → boler, obuner, yabexer

#### Retrieval Context

1. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
3. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
4. [grammar_rules]
Rule ID: syntax.object.after_predicate
Description: In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.
Pseudocode: predicate = finite_verb + optional_adverbs
if direct_object: place after predicate
if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: verb.ditransitive.indirect_before_direct
Description: Many common transitive verbs imply a directional preposition. When both indirect and direct objects are present, the indirect object comes before the direct object without an explicit preposition. A prepositional paraphrase can also be used.
Pseudocode: if verb.implies_direction and has_indirect_object and has_direct_object:
    order = verb + indirect_object + direct_object
else if preposition_needed:
    order = verb + direct_object + preposition + indirect_object
Examples:
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object at before direct object hua nyem
- Mirad: Du it doler. | English: Tell him to be quiet. | Note: it is indirect object
- Mirad: Nusbiu at dyes. | English: Buy me a book. | Note: indirect before direct

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
5. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

### sent10-en-06-csv-0878

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1187
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:878
- retrieval_rule_ids: verb.simple.active_suffixes, conjunction.subordinate_van_that, verb.conditional_imperative_u_subject
- retrieval_warning: none
- error_summary: none

#### Input

before we leave, say hi

#### Expected Output

Du hay ja van yat pio.

#### Prediction

Ja van yat ipu, haydu.

#### Word Equivalents

- before → ja van, za
- before that → ja hus
- before then → ja huj
- before this → ja his
- hi! → Hay!
- hi-fi → y.v., yaba vyayuvan
- hi-rise → glamosa, tomag
- leave → ip, ponjob
- leaver → piut
- leaving → empien, ipea, ipen, lobexen, oyepen, pien, pilen
- our → aeta, ayet, ayita, yata
- prior to → ja
- said → dwa
- sayer → dut
- saying → ajdun, den, vyandun, vyanegdwas
- saying hi → hayden
- they say... → Ot de...
- to leave → empier, iper, lobexer, oyeper, pier, piler
- to leave behind → zoylobexer
- to say → der
- to say hi → hayder
- to wee → tiyabiler
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
2. [grammar_rules]
Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object
3. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: preposition.bay_with_company
Description: bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.
Pseudocode: if relation == accompaniment:
    use 'bay' + companion_np
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company

Rule ID: preposition.av_for_beneficiary
Description: av corresponds to English 'for' in beneficiary or advantage contexts.
Pseudocode: if relation == beneficiary_or_for:
    use 'av' + beneficiary_np
Examples:
- Mirad: His se av et. | English: This is for you. | Note: av marks beneficiary
- Mirad: Nusbiu dyes av at. | English: Buy a book for me. | Note: prepositional paraphrase
4. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun
5. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: orthography.alphabet.roman_no_diacritics
Description: Native Mirad words are written with the Latin alphabet and no diacritics. Capitalization is used like English for sentence starts, proper nouns, and acronyms.
Pseudocode: if token.is_native_mirad:
    require token.characters subset_of latin_letters
    reject diacritics
if token.is_sentence_initial or token.is_proper_noun or token.is_acronym:
    capitalize as in English
Examples:
- Mirad: Mirad | English: Mirad | Note: proper name capitalized
- Mirad: Ferad | English: French language | Note: language name capitalized

### sent10-en-07-csv-0906

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1326
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:906
- retrieval_rule_ids: determiner.demonstrative_hia_hua, adjective.descriptive.ends_a, adjective.position.before_noun, noun.modifiers.order_no_agreement, conjunction.coordinate_ay_ey_oy, syntax.basic_svo, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

this teacher is good, but that student is bad

#### Expected Output

Hia tuxut se fia, oy hua tixut se fua.

#### Prediction

hia fia tuxut se fia, oy hua fua tixut se fua

#### Word Equivalents

- bad → fua
- bad thing → fuas
- badly → fu, fuay
- badness → fuan
- but → boy, oy
- butch → toobyena
- butting → teyubuxen
- butyl → butyl
- college student → itistamut, tutaymut
- educator → tuuxut, tuxtut
- good → fia, nuun, nyuun
- good thing → fis
- good- → fi-
- goodly → ayga
- high school student → etistamut
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- school teacher → tistam tuxut
- schoolteacher → tistamtuxut
- secondary school student → etistamut
- since this → ji his
- something bad → fuas, fusun
- something good → fis, fisun
- student → tixut
- student teacher → tiea tuxut
- teacher → tuxut
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- this → hi-, hia, hinog
- this kind → hisaun
- this kind of → higela, hisauna, hiyena
- this one → hias, hiat, hiawa, hiawas
- university student → utistamat

#### Retrieval Context

1. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.motion_communication_omit_direction_preposition
Description: Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.
Pseudocode: if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:
    omit preposition
    place object according_to verb_complement_rules
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: orthography.punctuation.direct_quote_colon
Description: Mirad uses a colon before direct speech where English often uses a comma.
Pseudocode: if clause.introduces_direct_quote:
    place ':' after reporting clause
    quote_content = quoted_sentence
Examples:
- Mirad: It da: "Van esu man." | English: He said, "Let there be light." | Note: colon introduces the quote

Rule ID: preposition.boy_without
Description: boy links a noun phrase to express lack or absence, corresponding to English 'without'.
Pseudocode: if relation == absence_or_without:
    use head + 'boy' + complement
Examples:
- Mirad: nyandras boy eta dyun | English: a list without your name | Note: boy = without
2. [grammar_rules]
Rule ID: determiner.deictic_begin_h
Description: All deictic determiners begin with h. Following letters specify category such as interrogative, indefinite, proximal, distal, universal, negative, person, thing, place, time, manner, degree, etc.
Pseudocode: if word.is_deictic_determiner:
    require word.starts_with('h')
    parse prefix_after_h for deixis_type
    parse suffix for semantic_category
Examples:
- Mirad: hia | English: this | Note: proximal deictic
- Mirad: hua | English: that | Note: distal deictic
- Mirad: duhot? | English: who? | Note: interrogative animate deictic

Rule ID: determiner.categories
Description: Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.
Pseudocode: classify determiner by semantic_function:
    deictic | possessive | quantitative | numerical
classify by syntactic_function:
    adjective | pronoun | adverb
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: adjective.descriptive.ends_a
Description: All descriptive adjectives end in the adjectival marker -a. Adjectives can be derived from qualitative roots, nouns, passive verb stems, and prepositions.
Pseudocode: if target_part_of_speech == descriptive_adjective:
    form = stem + 'a'
Examples:
- Mirad: fia | English: good | Note: fi- + -a
- Mirad: pura | English: vehicular | Note: pur 'vehicle' + -a
- Mirad: dalwa | English: spoken | Note: passive verb stem + -a

Rule ID: determiner.demonstrative_hia_hua
Description: hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.
Pseudocode: if referent.is_near_speaker: base = 'hi'
if referent.is_far_or_contextual: base = 'hu'
if used_as_adjective: form = base + 'a'
if used_as_thing_pronoun: form = base + 'as' or base + 'asi'
if used_as_person_pronoun: form = base + 'at' or base + 'ati'
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
3. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
4. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

### sent10-en-08-csv-0947

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1740
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:947
- retrieval_rule_ids: pronoun.gender.optional_w_y, verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, verb.simple.passive_suffixes
- retrieval_warning: none
- error_summary: none

#### Input

she played but lost, and he tried but lost

#### Expected Output

Iyt eka oy oka, ay wit yeka oy oka.

#### Prediction

Iyt eka oy oka, ay wit yekwa oy oka.

#### Word Equivalents

- and → ay
- and/or → aey
- anded → ayxwa
- anding → ayxen
- both...and → hyaewa...ay, vay...ay
- but → boy, oy
- butch → toobyena
- butting → teyubuxen
- butyl → butyl
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- he himself → it iut, wit iut
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- let past → yizafxwa
- letting past → yizafxen
- loosing → lonyafxen, loyuvxen, yivlaxen, yugsaxen
- losing → okea, oken
- loss → ok, okon
- lost → mepokya, okwa, vyoembwa
- making tense → yignaxen
- past → aj, aja, ajbwa, ajna, ajpya, yiz-, yiza, yizbwa
- play → dezun, ebnig, ek, ekun, ifek
- playact → dezekun
- played → ekwa, ifekwa, ifekxwa
- playing → eken, ifeken
- seine → pitnef
- she → hayt, hiyt, huyt, it, iyt
- she herself → it iut, iyt iut
- she who → hoyt
- shearing → goflaren, goflen
- taking past → yizben
- tense → erdunjob, yigna
- tensed → yignaxwa
- tenseless → erdunjoboya, erdunjobuka
- to let past → yizafxer
- to lose → lobewer, oker, vyoember
- to make tense → yignaxer
- to play → eker
- to try → doyevyeker, xefer, yaovyeker, yeker
- tried → doyevyekwa, vyaoyekwa, yaovyekwa, yekteexwa, yekwa, yevsonteexwa
- try → yek
- trying → doyevyeken, vyaoyeken, xefen, yaovyeken, yekea, yeken, yekteexen, yekuea
- tryingly → yekueay

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.perfect.passive_aw_plus_tense
Description: The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.
Pseudocode: if aspect == perfect and voice == passive:
    form = stem + 'aw' + final_tense_vowel
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o

Rule ID: verb.passive.insert_w_before_tense
Description: In finite passive forms, the passive marker w is inserted between the verb stem and the final tense/mood vowel. Passive forms translate English 'be/get + past participle' when a patient is subject.
Pseudocode: if voice == passive and aspect == simple:
    form = stem + 'w' + tense_or_mood_vowel
Examples:
- Mirad: Has xwe. | English: It is done. | Note: x- + w + e
- Mirad: Has xwa. | English: It was done. | Note: x- + w + a
- Mirad: Has xwo. | English: It will be done. | Note: x- + w + o
2. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: preposition.bay_with_company
Description: bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.
Pseudocode: if relation == accompaniment:
    use 'bay' + companion_np
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause
3. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
4. [grammar_rules]
Rule ID: pronoun.gender.optional_w_y
Description: The gender-neutral third-person animate pronoun it can become wit for masculine or iyt for feminine. Gender marking is optional and used when needed to distinguish referents.
Pseudocode: if pronoun == third_singular_animate:
    if gender == masculine: use 'wit'
    else if gender == feminine: use 'iyt'
    else: use 'it'
Examples:
- Mirad: it | English: he/she/him/her | Note: gender-neutral animate
- Mirad: wit | English: he/him | Note: masculine
- Mirad: iyt | English: she/her | Note: feminine

Rule ID: pronoun.animate_t_inanimate_s
Description: Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.
Pseudocode: if antecedent.is_animate:
    use pronoun ending '-t'
if antecedent.is_inanimate:
    use pronoun ending '-s'
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
5. [grammar_rules]
Rule ID: pronoun.gender.optional_w_y
Description: The gender-neutral third-person animate pronoun it can become wit for masculine or iyt for feminine. Gender marking is optional and used when needed to distinguish referents.
Pseudocode: if pronoun == third_singular_animate:
    if gender == masculine: use 'wit'
    else if gender == feminine: use 'iyt'
    else: use 'it'
Examples:
- Mirad: it | English: he/she/him/her | Note: gender-neutral animate
- Mirad: wit | English: he/him | Note: masculine
- Mirad: iyt | English: she/her | Note: feminine

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.animate_t_inanimate_s
Description: Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.
Pseudocode: if antecedent.is_animate:
    use pronoun ending '-t'
if antecedent.is_inanimate:
    use pronoun ending '-s'
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
6. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: derivation.noun.gerund_en
Description: The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.
Pseudocode: if verb_stem nominalized_as_action:
    noun = verb_stem + 'en'
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

### sent10-en-09-csv-0979

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1507
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:979
- retrieval_rule_ids: determiner.demonstrative_hia_hua, determiner.animate_t_thing_s_plural_i, verb.no_person_number_agreement, noun.article.definite_ha, conjunction.coordinate_ay_ey_oy, pronoun.possessive_add_a_s_si, verb.stative_complement_after_ser
- retrieval_warning: none
- error_summary: none

#### Input

this is a good thing and that is mine

#### Expected Output

His se fis ay huas se atas.

#### Prediction

Hias se fis ay huas se atas.

#### Word Equivalents

- artic → yibzameram
- article → drases, drenes, nunes, syunes
- feature article → agna drenes
- good → fia, nuun, nyuun
- good thing → fis
- good- → fi-
- goodly → ayga
- indefinable → tesdyofwa, ujnadryofwa
- indefinably → tesdyofway, ujnadryofway
- indefinite → ovyakyoxwa
- indefiniteness → ovyakyoxwan
- indeterminately → ovlakaxway
- lead article → agna drenes
- mine → atas, atasi, aytas, aytasi, mukiblem, mumyex, watas, watasi
- mined → mukiblawa, oybdopyunbwa
- miner → mukiblut
- news article → jubdindrenes
- since this → ji his
- something good → fis, fisun
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- the thing → has, hason, hasun
- the thing's → hasa
- the things → hasi, hasoni, hasuni
- thing → son, sun
- things → bexunyan
- this → hi-, hia, hinog
- this kind → hisaun
- this kind of → higela, hisauna, hiyena
- this one → hias, hiat, hiawa, hiawas
- tin mine → sonilk mukiblem
- to mine → mukibler

#### Retrieval Context

1. [grammar_rules]
Rule ID: determiner.deictic_begin_h
Description: All deictic determiners begin with h. Following letters specify category such as interrogative, indefinite, proximal, distal, universal, negative, person, thing, place, time, manner, degree, etc.
Pseudocode: if word.is_deictic_determiner:
    require word.starts_with('h')
    parse prefix_after_h for deixis_type
    parse suffix for semantic_category
Examples:
- Mirad: hia | English: this | Note: proximal deictic
- Mirad: hua | English: that | Note: distal deictic
- Mirad: duhot? | English: who? | Note: interrogative animate deictic

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: determiner.demonstrative_hia_hua
Description: hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.
Pseudocode: if referent.is_near_speaker: base = 'hi'
if referent.is_far_or_contextual: base = 'hu'
if used_as_adjective: form = base + 'a'
if used_as_thing_pronoun: form = base + 'as' or base + 'asi'
if used_as_person_pronoun: form = base + 'at' or base + 'ati'
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun
2. [grammar_rules]
Rule ID: verb.stative_complement_after_ser
Description: Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.
Pseudocode: if verb == ser or verb.is_stative_intransitive:
    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause
    clause = subject + verb + complement
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object
3. [grammar_rules]
Rule ID: pronoun.possessive_add_a_s_si
Description: Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.
Pseudocode: possessive_adjective = pronoun + 'a'
if possessed_referent == inanimate_singular:
    possessive_pronoun = pronoun + 'as'
if possessed_referent == inanimate_plural:
    possessive_pronoun = pronoun + 'asi'
if possessed_referent == animate:
    replace final_s_with_t in possessive_pronoun
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural
4. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
5. [grammar_rules]
Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: noun.article.definite_ha
Description: Mirad has one definite article, ha. It precedes the noun and any adjectives. It does not change for gender, number, or case. There is no indefinite article.
Pseudocode: if english_np.definiteness == definite:
    mirad_np = 'ha' + modifiers + noun
else if english_np.has_indefinite_article:
    omit_article_in_mirad
Examples:
- Mirad: tam | English: a house | Note: indefinite; no article
- Mirad: ha tam | English: the house | Note: definite marked with ha
- Mirad: ha tami | English: the houses | Note: ha unchanged before plural noun
6. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: syntax.object.after_predicate
Description: In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.
Pseudocode: predicate = finite_verb + optional_adverbs
if direct_object: place after predicate
if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

### sent10-en-10-csv-0990

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1404
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, en_to_mir, csv_index:990
- retrieval_rule_ids: verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, preposition.boy_without
- retrieval_warning: none
- error_summary: none

#### Input

the man left for no reason, but someone else won

#### Expected Output

Ha tob pia hyosav, oy hyut aka.

#### Prediction

Ha twob ipa boy tesyob, oy heawa hyut aka.

#### Word Equivalents

- else → ey, ogel hus, ven voy
- elsewise → hyuyen
- for the reason that.... → av tesyob van....
- how else → duhohyuyen
- leave → ip, ponjob
- leaver → piut
- leaving → empien, ipea, ipen, lobexen, oyepen, pien, pilen
- man → tob, twob
- man's → twoba
- otherwise → hyuay, hyugel, hyuyen, ogel hus, ven voy
- reason → sav, tesdud, tesyob, vyatex
- reasoning → tesyobxen, vyatexen
- some man → hetwob
- somebody → het, hetob
- someone → heawa tob, heawat, het, hetob, heyt
- someone's → heta, hetoba, hetobas, hetobasi, heyta
- that person → hut
- the person → hat
- the reason → hasav
- this man → hitwob
- to → bu
- to and → ayxer
- to don → aber, tofaber
- to leave → empier, iper, lobexer, oyeper, pier, piler
- to leave behind → zoylobexer
- to man → tobuer
- to or → eyxer
- to reason → tesyobxer, vyatexer
- to sup → telogier
- when else? → du ha hyua job?, duhohyuj?
- win → ak
- wince → novyixzyuk
- winning → akea
- wino → gravafiliut
- winy → vafilyena

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.
Pseudocode: if adjective.can_take_o_negation and not ambiguous:
    form = 'o' + adjective
else if adjective.begins_with_consonant:
    form = 'lo' + adjective
else:
    form = 'ol' + adjective
if meaning == hostile_or_anti:
    form = one_of(['lyo' + adjective, 'ov' + adjective])
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: preposition.boy_without
Description: boy links a noun phrase to express lack or absence, corresponding to English 'without'.
Pseudocode: if relation == absence_or_without:
    use head + 'boy' + complement
Examples:
- Mirad: nyandras boy eta dyun | English: a list without your name | Note: boy = without
3. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
4. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
5. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: orthography.alphabet.roman_no_diacritics
Description: Native Mirad words are written with the Latin alphabet and no diacritics. Capitalization is used like English for sentence starts, proper nouns, and acronyms.
Pseudocode: if token.is_native_mirad:
    require token.characters subset_of latin_letters
    reject diacritics
if token.is_sentence_initial or token.is_proper_noun or token.is_acronym:
    capitalize as in English
Examples:
- Mirad: Mirad | English: Mirad | Note: proper name capitalized
- Mirad: Ferad | English: French language | Note: language name capitalized

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

### sent10-mi-01-csv-0522

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 39591
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, mir_to_en, csv_index:522
- retrieval_rule_ids: verb.simple.active_suffixes, syntax.basic_svo
- retrieval_warning: none
- error_summary: none

#### Input

Oven et do hyuyen, at dolo.

#### Expected Output

unless you say otherwise I will be silent

#### Prediction

Unless you say otherwise, I will be quiet.

#### Word Equivalents

- another way → hyumep
- any other way → hyehyuyen
- at → I, me
- do → musical note do
- else → ey, ogel hus, ven voy
- elsewise → hyuyen
- et → thee, thou, you
- except → boy, gob, goy, ovabiwa, oy, oyebexea, oyebexwa, oyebiwa, yon bi
- how else → duhohyuyen
- hyuyen → elsewise, in another manner, otherwise, some other way, somehow other, strangely
- in another manner → hyuyen
- in other ways → hyuyeni
- musical note → duz nod
- musical note do → do
- musical note fa → fa
- musical note mi → mi
- musical note re → re
- not if → voy ven
- other → hyua, hyuta, logela
- other than → hyu vyel, ogel vyel
- otherwise → hyuay, hyugel, hyuyen, ogel hus, ven voy
- oven → unless
- some other → hehyua
- some other kind of → hehyusauna, hyuyena
- some other way → hyuyen
- somehow other → hehyuyen, hyuyen
- strange → hyusauna, hyuyena, oyebema, oyebsana, yonyena
- strange thing → hyusaunas, oyebsanas, yonyenas
- strangely → hyusaunay, hyuyen, hyuyenay, oyebsanay, yonyenay
- teehee → hihi, ozivseux
- that other way → huhyuyen
- the other → ha hyua, hahyua, hyua, hyut
- theca → abnyeb
- thee → et
- thew → yuvat
- thine → eta
- this other way → hihyuyen
- thitherto → bu hum
- thou → et
- throe → byook
- throes → byook
- thy → eta
- unless → gob van, oven
- weirdly → dotoegay, tepozetay, yizoetay
- when else? → du ha hyua job?, duhohyuj?
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause
2. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
3. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause
4. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: preposition.bay_with_company
Description: bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.
Pseudocode: if relation == accompaniment:
    use 'bay' + companion_np
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
5. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

### sent10-mi-02-csv-0749

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 15782
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, mir_to_en, csv_index:749
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

Et voy yexe be tam.

#### Expected Output

you do not work at home

#### Prediction

You are not working at home.

#### Word Equivalents

- abode → besam, embesam, tam, tejam
- at → atulk
- at least → gwoay
- atilt → abaea
- atonally → oyseuzay
- atto → goralyi-, goralyu-
- be → at
- certainly not → vlay voy, vlo, vloy
- dwelling → besam, besea, besen, embesam, embesea, tambesen, toym
- habitation → embesen, tambexen, toom
- hausa → Haud
- home → be tam, taam, tam
- home sweet home → taamif
- homebody → taambesut, tambexlut
- homey → taamyena, yukoma
- house → tam
- housed → embesuwa, tambuwa, tamuwa
- let not → ofu, von
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- row house → naba tam, nabtam
- tam → abode, home, house
- the house → tim bi avembiuti, yembiutyanim
- to have a home → embexer
- to house → embesuer, tambuer, tamuer
- voy → not

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
2. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.
Pseudocode: if adjective.can_take_o_negation and not ambiguous:
    form = 'o' + adjective
else if adjective.begins_with_consonant:
    form = 'lo' + adjective
else:
    form = 'ol' + adjective
if meaning == hostile_or_anti:
    form = one_of(['lyo' + adjective, 'ov' + adjective])
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
3. [grammar_rules]
Rule ID: preposition.bi_of_possession_partitive
Description: bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.
Pseudocode: if relation in ['of', 'possessive', 'partitive']:
    use head + 'bi' + complement
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: verb.motion_communication_omit_direction_preposition
Description: Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.
Pseudocode: if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:
    omit preposition
    place object according_to verb_complement_rules
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: preposition.av_for_beneficiary
Description: av corresponds to English 'for' in beneficiary or advantage contexts.
Pseudocode: if relation == beneficiary_or_for:
    use 'av' + beneficiary_np
Examples:
- Mirad: His se av et. | English: This is for you. | Note: av marks beneficiary
- Mirad: Nusbiu dyes av at. | English: Buy a book for me. | Note: prepositional paraphrase

Rule ID: preposition.bay_with_company
Description: bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.
Pseudocode: if relation == accompaniment:
    use 'bay' + companion_np
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company
4. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: adjective.negation_o_lo_ol
Description: Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.
Pseudocode: if adjective.can_take_o_negation and not ambiguous:
    form = 'o' + adjective
else if adjective.begins_with_consonant:
    form = 'lo' + adjective
else:
    form = 'ol' + adjective
if meaning == hostile_or_anti:
    form = one_of(['lyo' + adjective, 'ov' + adjective])
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

### sent10-mi-03-csv-0802

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 23071
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, mir_to_en, csv_index:802
- retrieval_rule_ids: verb.modal_hypothetical_mitigates, verb.stative_complement_after_ser, conjunction.coordinate_ay_ey_oy
- retrieval_warning: none
- error_summary: none

#### Input

Yat peyu tam, oy yat su iva him.

#### Expected Output

we would be going home, but we would be happy here

#### Prediction

We would stay at home, but we would be happy here.

#### Word Equivalents

- abode → besam, embesam, tam, tejam
- although → ov van, yan van
- but → boy, oy
- butch → toobyena
- butting → teyubuxen
- butyl → butyl
- dwelling → besam, besea, besen, embesam, embesea, tambesen, toym
- everything except → hyas oy
- except → boy, gob, goy, ovabiwa, oy, oyebexea, oyebexwa, oyebiwa, yon bi
- excepted → oyebexwa, oyebiwa
- exception → oyebexen, oyevien, vobien
- excluding → oyebexea, oyebexlea, oyebyujbea, oyebyujben, yeboysea
- gay → fritipa, getoobifa, iva, tipifa, tipiva
- gayness → fritipan, getoobifan, ivan, tipifan, tipivan
- habitation → embesen, tambexen, toom
- hausa → Haud
- him → here, hither, this place
- home → be tam, taam, tam
- home sweet home → taamif
- homebody → taambesut, tambexlut
- homey → taamyena, yukoma
- house → tam
- housed → embesuwa, tambuwa, tamuwa
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- iva → gay, gleeful, happy, joyful
- nevertheless → gey bay hus, gey bay van, gey ov hus, je hus, ov hus
- not yet → voy gaj
- oy → but, except, however, yet
- people → tyod, yot
- people's → tyoda, yota, yotas, yotasi
- pro-gay → avhyitoobifa
- row house → naba tam, nabtam
- sou → ogrun, su
- sough → igilpseux
- souped → yiksonuwa
- soupy → teilyena
- su → sou
- tam → abode, home, house
- the house → tim bi avembiuti, yembiutyanim
- the people → hati
- the people... → Yat
- those people → huati, huti
- though → fi van
- to have a home → embexer
- to house → embesuer, tambuer, tamuer
- to sough → igilpseuxer
- yat → the people...
- yet → gaj, gajob, gey bay hus, gey bay van, gey ov hus, ov hus, oy
- yet again → ga awa jod
- yet more → gay ga

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.progressive.passive_ew_plus_tense
Description: The passive progressive inserts e plus passive/buffer w before the final tense/mood vowel: -ewe, -ewa, -ewo, -ewu.
Pseudocode: if aspect == progressive and voice == passive:
    form = stem + 'ew' + final_tense_vowel
Examples:
- Mirad: Has xewe. | English: It is being done. | Note: x- + ew + e
- Mirad: Has xewa. | English: It was being done. | Note: x- + ew + a

Rule ID: verb.progressive.active_ey_plus_tense
Description: The active progressive inserts the present aspect vowel e plus buffer y between the stem and final tense/mood vowel: -eye, -eya, -eyo, -eyu.
Pseudocode: if aspect == progressive and voice == active:
    form = stem + 'ey' + final_tense_vowel
Examples:
- Mirad: at xeye | English: I am doing | Note: x- + ey + e
- Mirad: at xeya | English: I was doing | Note: x- + ey + a
- Mirad: at xeyo | English: I will be doing | Note: x- + ey + o

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
2. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
3. [grammar_rules]
Rule ID: verb.stative_complement_after_ser
Description: Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.
Pseudocode: if verb == ser or verb.is_stative_intransitive:
    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause
    clause = subject + verb + complement
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: derivation.noun.gerund_en
Description: The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.
Pseudocode: if verb_stem nominalized_as_action:
    noun = verb_stem + 'en'
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
4. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation
5. [grammar_rules]
Rule ID: verb.motion_communication_omit_direction_preposition
Description: Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.
Pseudocode: if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:
    omit preposition
    place object according_to verb_complement_rules
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.
Pseudocode: choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal
choose category_suffix by circumstance: place/time/manner
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: preposition.bi_of_possession_partitive
Description: bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.
Pseudocode: if relation in ['of', 'possessive', 'partitive']:
    use head + 'bi' + complement
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: pronoun.personal.invariant_case
Description: Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.
Pseudocode: pronoun_form = lookup_person_number_animacy_gender()
do_not_inflect_for_case
determine_case_from_position_or_preposition
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

### sent10-mi-04-csv-0808

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 18895
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, mir_to_en, csv_index:808
- retrieval_rule_ids: verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy, conjunction.subordinate_van_that, verb.stative_complement_after_ser, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

Yat te van it upo ay yat so iva.

#### Expected Output

we know that he or she will come and we will be happy

#### Prediction

We know that he will come and we will be happy.

#### Word Equivalents

- -let → -es
- and → ay
- and/or → aey
- anded → ayxwa
- anding → ayxen
- as a matter of fact → gel vyanson, vray
- ay → and
- because of → be ux bi, be vyatex bi, bey ux bi, bey xuun bi, hasav bi, yefwa bu
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- he himself → it iut, wit iut
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- her herself → it iut, iyt iut
- hereto → bu hiis
- hers → haytas, haytasi, hiytas, hiytasi, huytas, huytasi, iytas, iytasi
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- him himself → it iut, wit iut
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- in addition to the fact that → gab van
- in consideration of the fact that.... → be tepien van....
- it → he, her, him, she
- iva → gay, gleeful, happy, joyful
- let → afu, ojbuwa
- let's → van
- let... → van
- letting → nasyefuen, ojbuen
- may → afu
- may... → van
- may...not... → von...
- maybe → ve, vey
- people → tyod, yot
- people's → tyoda, yota, yotas, yotasi
- seine → pitnef
- she → hayt, hiyt, huyt, it, iyt
- she herself → it iut, iyt iut
- she who → hoyt
- shearing → goflaren, goflen
- so → s, the letter s
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- the fact that → van
- the people → hati
- the people... → Yat
- those people → huati, huti
- to let → jobnixer, jobnuxyafwa, nasyefuer, ojbiyafwa, ojbuer, ojnuxier
- to may → afer
- van → let's, let..., may..., that, the fact that
- yat → the people...

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
2. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
3. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
4. [grammar_rules]
Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
5. [grammar_rules]
Rule ID: verb.stative_complement_after_ser
Description: Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.
Pseudocode: if verb == ser or verb.is_stative_intransitive:
    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause
    clause = subject + verb + complement
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: derivation.noun.gerund_en
Description: The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.
Pseudocode: if verb_stem nominalized_as_action:
    noun = verb_stem + 'en'
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
6. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: derivation.noun.gerund_en
Description: The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.
Pseudocode: if verb_stem nominalized_as_action:
    noun = verb_stem + 'en'
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

### sent10-mi-05-csv-0861

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 17780
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: sentence-min5, mir_to_en, csv_index:861
- retrieval_rule_ids: verb.simple.active_suffixes
- retrieval_warning: none
- error_summary: none

#### Input

Gey ven at yontexe, et bolo at.

#### Expected Output

even if I disagree, you will support me

#### Prediction

Even if I disagree, you will support me.

#### Word Equivalents

- as if → gel ven, hoyen ven
- at → I, me
- bear → gapyot
- bearably → bolyafway
- bearer → belut
- bearing → bolen, tapyen
- boler → to bear, to bolster, to endure, to hold up, to prop up, to stanch, to stand, to support, to sustain, to underset, to uphold
- bolster → yagsuam
- bolstered → bolwa
- bolstering → bolea, bolyea
- disagreeably → loifxeay, oyansanseay
- disagreed → yontexwa
- disagreeing → yontexea, yontexen
- disagreement → yontex
- dissent → ovtos, yontex, yontos
- dissenter → ovtosut, yontexdut, yontosdut, yontosut
- dissenting → yontexea, yontexen, yontexyea, yontosea, yontosen
- dissentious → ovtosyea, yontexdyea, yontosdyea
- endured → xolwa
- et → thee, thou, you
- even → euna, gea, geeksaga, geneda, genega, gey, nega, negxwa, yeza, zyifa, zyima, zyina
- even number → euna sag
- even- → ge-
- evened → zyimxwa
- getting even → yevkexen, zoyyevaxen
- gey → even
- held up → bowa, ojbwa, yabexwa
- hold-up → jwobiun, jwox, vyobiun
- holding up → bolen, yabexen
- if → ven
- if not → ven voy
- if so → ven vay
- if yes → ven va
- is → se
- tell me whether...? → Duven...?
- to bear → beler, boler, tajber, tejber
- to bolster → boler
- to boost → azonuer, igankyaxer, zombuxer
- to disagree → yontexer
- to dissent → ovtoser, yontexder, yontexer, yontosder, yontoser
- to endure → boler, jeser, jesyafer, kyojeser, xoler, yagjeser
- to hold → bexer
- to hold up → boler, yabexer
- to undergo → keser, xoler
- to undergo suffering → blokier
- to withstand → ibexer
- ven → if, whether
- whether → ven
- yes or no? → Vao?
- yontexer → to disagree, to dissent

#### Retrieval Context

1. [grammar_rules]
Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
2. [grammar_rules]
Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: derivation.noun.tool_ar_ir_ur
Description: The suffixes -ar, -ir, and -ur form instruments, tools, machines, engines, or vehicles, usually from verb stems. Exact nuance depends on the lexical family.
Pseudocode: if target == tool_or_instrument:
    form = verb_stem + one_of(['ar','ir','ur']) according_to_instrument_class
Examples:
- Mirad: drer → drar | English: to write → pencil | Note: writing tool
- Mirad: gobler → goblar | English: to cut → knife | Note: cutting tool
- Mirad: per → pur | English: to go → car | Note: vehicle

Rule ID: adverb.degree.same_as_adjectives
Description: Adverbs are compared by placing quantitative degree words before them, parallel to adjective comparison. vyel introduces the comparison standard.
Pseudocode: if adverb.comparison:
    form = degree_quantifier + adverb + optional('vyel' + standard)
Examples:
- Mirad: Dalu ge azay vyel et yafe. | English: Speak as loudly as you can. | Note: ge + adverb + vyel
3. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: derivation.adjective_verb_participles_ea_wa_oa_ua
Description: Verb-derived adjectives use -ea for active/present -ing, -yea for tending to/-ive, -wa for passive/past -ed, -oa for about to/apt to, and -ua for able/potentially causing.
Pseudocode: if meaning == active_present_participle: form = verb_stem + 'ea'
if meaning == tendency: form = verb_stem + 'yea'
if meaning == passive_past_participle: form = verb_stem + 'wa'
if meaning == about_to: form = verb_stem + 'oa'
if meaning == able_or_potential: form = verb_stem + 'ua'
Examples:
- Mirad: tej- → tejea | English: live → living/alive | Note: -ea
- Mirad: dal- → dalyea | English: talk → talkative | Note: -yea
- Mirad: dal- → dalwa | English: talk → spoken | Note: -wa

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
4. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
5. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.possessive_add_a_s_si
Description: Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.
Pseudocode: possessive_adjective = pronoun + 'a'
if possessed_referent == inanimate_singular:
    possessive_pronoun = pronoun + 'as'
if possessed_referent == inanimate_plural:
    possessive_pronoun = pronoun + 'asi'
if possessed_referent == animate:
    replace final_s_with_t in possessive_pronoun
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: derivation.adjective_noun_to_adj_suffixes
Description: Noun-derived adjectives use -a for relating to/of, -aya or -ika for full of/-ful/-ous, -oya or -uka for lacking/-less/-free, and -yena for like/-ish/-y.
Pseudocode: if relation == 'relating_to': form = noun + 'a'
if relation == 'full_of': form = noun + one_of(['aya','ika'])
if relation == 'empty_of_or_without': form = noun + one_of(['oya','uka'])
if relation == 'like': form = noun + 'yena'
Examples:
- Mirad: dom → doma | English: city → urban | Note: relational -a
- Mirad: mil → milaya | English: water → watery | Note: full of
- Mirad: tes → tesoya | English: meaning → meaningless | Note: without

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive
6. [grammar_rules]
Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

### sent10-mi-06-csv-0878

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 14662
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, mir_to_en, csv_index:878
- retrieval_rule_ids: verb.simple.active_suffixes, conjunction.subordinate_van_that, syntax.basic_svo
- retrieval_warning: none
- error_summary: none

#### Input

Du hay ja van yat pio.

#### Expected Output

before we leave, say hi

#### Prediction

Say hello before we leave.

#### Word Equivalents

- -ant → -ea
- -let → -es
- afar → Aarod
- afore → ja, za
- aforethought → zatex
- ant → xapelt
- ante- → ja-, za-
- anterior → jaa, jana, zakun, zakuna, zana, zaneda
- antic → ifeyk
- because of → be ux bi, be vyatex bi, bey ux bi, bey xuun bi, hasav bi, yefwa bu
- before → ja van, za
- before that → ja hus
- before then → ja huj
- duer → to propose, to suggest
- fore → zaa
- fore- → ja-, za-
- in addition to the fact that → gab van
- in consideration of the fact that.... → be tepien van....
- ja → afore, ante, prior to
- let → afu, ojbuwa
- let's → van
- let... → van
- letting → nasyefuen, ojbuen
- may → afu
- may... → van
- may...not... → von...
- maybe → ve, vey
- pier → to depart, to leave, to run along, to set out, to take leave of
- prior to → ja
- prior to that → ja hus
- proposal → budel, dudras, duun, duwas, vaduun
- proposed → avdwa, budelwa, duwa
- proposing → avden, budelen, duen
- something suggested → duwas
- suggested → duwa, tesuwa, tyunuwa
- suggesting → duen, tesuen, tyunuen
- suggestion → duen, duun, tesuen, tesuun, texuen, texuun, tyunuen, tyunuun
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- the fact that → van
- to let → jobnixer, jobnuxyafwa, nasyefuer, ojbiyafwa, ojbuer, ojnuxier
- to may → afer
- to propose → avder, budeler, duer
- to propound → doduer
- to suggest → duer, tesuer, tyunuer
- van → let's, let..., may..., that, the fact that
- yat → the people...

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.conditional_imperative_u_subject
Description: A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.
Pseudocode: if finite_verb.ends_with('u'):
    if clause.has_explicit_subject:
        interpret_as conditional_hypothetical
    else:
        interpret_as imperative
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
2. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
3. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.
Pseudocode: choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal
choose category_suffix by circumstance: place/time/manner
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
4. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: syntax.object.after_predicate
Description: In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.
Pseudocode: predicate = finite_verb + optional_adverbs
if direct_object: place after predicate
if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object
5. [grammar_rules]
Rule ID: conjunction.subordinate_van_that
Description: van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.
Pseudocode: if embedded_clause.is_declarative:
    introduce_with 'van' when clarity or grammar requires
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: syntax.subject.noun_phrase_structure
Description: The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.
Pseudocode: subject = noun_phrase | pronoun | coordinated_subject
noun_phrase = modifiers* + head_noun + optional_post_head_phrases
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.transitive.direct_object_after_verb
Description: A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.
Pseudocode: if verb.is_transitive:
    clause = subject + verb + direct_object
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: syntax.basic_svo
Description: Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.
Pseudocode: if clause.is_basic_declarative:
    order = [subject, verb_predicate, object_or_complement]
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

### sent10-mi-07-csv-0906

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 11613
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: sentence-min5, mir_to_en, csv_index:906
- retrieval_rule_ids: conjunction.coordinate_ay_ey_oy, determiner.demonstrative_hia_hua
- retrieval_warning: none
- error_summary: none

#### Input

Hia tuxut se fia, oy hua tixut se fua.

#### Expected Output

this teacher is good, but that student is bad

#### Prediction

This teacher is good, but that student is bad.

#### Word Equivalents

- al → alilk
- alright → fi, fia
- college student → itistamut, tutaymut
- counselor → fyidaluut, fyidut, fyiduut, fyiduwat, vyatuut
- educator → tuuxut, tuxtut
- fia → alright, fine, good, nice, ok
- fine → byoyk, fi, fia, gyola
- fine- → vi-
- finely → gyolay, gyoy, zyoay
- fineness → gyolan, gyoyan, vifan, zyoan
- fua → bad, crappy, crummy, lousy, piss poor
- good → fia, nuun, nyuun
- good thing → fis
- good- → fi-
- goodly → ayga
- high school student → etistamut
- instructor → extuut, tuxeb
- lecture → dyed, dyeden, dyedun, tuxun
- lectured → dyedwa
- lecturer → dyedut, tuxut
- lecturing → tuxen
- mentor → fyidut, tixut
- nice → fia, fitipa, iyfuwa
- nice- → fi-
- nice-sounding → fiseusea, fiteesa, fiteesea, viseuxa
- nicely → fi, fiay
- niceness → fitipan
- oh → Hwuy!
- ok → fi, fia, fiva
- okay → fi
- okra → byivol, vyovol
- precept → avyan, exlena vyab, vyandir
- preceptive → avyana
- preceptor → tuxut
- premedical → jabektuna
- school teacher → tistam tuxut
- schoolteacher → tistamtuxut
- secondary school student → etistamut
- something good → fis, fisun
- student → tixut
- student teacher → tiea tuxut
- teacher → tuxut
- tixut → mentor, student
- to fine → byoykuer, fyuyzuer, nasbyoykuer
- to lecture → dyeder, tuxer
- tutor → beaxut
- tutorship → tuyxutan
- tuxut → lecturer, preceptor, teacher
- university student → utistamat
- well → fi, fiay, fibaka, mumilzyeg, zyutum

#### Retrieval Context

1. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees
2. [grammar_rules]
Rule ID: determiner.demonstrative_hia_hua
Description: hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.
Pseudocode: if referent.is_near_speaker: base = 'hi'
if referent.is_far_or_contextual: base = 'hu'
if used_as_adjective: form = base + 'a'
if used_as_thing_pronoun: form = base + 'as' or base + 'asi'
if used_as_person_pronoun: form = base + 'at' or base + 'ati'
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun

Rule ID: determiner.deictic_begin_h
Description: All deictic determiners begin with h. Following letters specify category such as interrogative, indefinite, proximal, distal, universal, negative, person, thing, place, time, manner, degree, etc.
Pseudocode: if word.is_deictic_determiner:
    require word.starts_with('h')
    parse prefix_after_h for deixis_type
    parse suffix for semantic_category
Examples:
- Mirad: hia | English: this | Note: proximal deictic
- Mirad: hua | English: that | Note: distal deictic
- Mirad: duhot? | English: who? | Note: interrogative animate deictic

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: determiner.universal_hya_all_every
Description: hya means every/all. hyaha means all the. hyawa means each. Choose based on whether the English quantifier is distributive, collective, or definite collective.
Pseudocode: if English == 'every' or generic 'all': use 'hya'
if English == 'all the': use 'hyaha'
if English == 'each': use 'hyawa'
Examples:
- Mirad: Hya dom ayse tebixea suni teaxer. | English: Every city has interesting things to see. | Note: hya = every
- Mirad: Hyaha domi ayse tebixusi. | English: All the cities have things of interest. | Note: hyaha = all the
- Mirad: Hyawa dom ayse tebixun. | English: Each city has something of interest. | Note: hyawa = each

Rule ID: determiner.categories
Description: Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.
Pseudocode: classify determiner by semantic_function:
    deictic | possessive | quantitative | numerical
classify by syntactic_function:
    adjective | pronoun | adverb
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner
3. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: preposition.bay_with_company
Description: bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.
Pseudocode: if relation == accompaniment:
    use 'bay' + companion_np
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company
4. [grammar_rules]
Rule ID: adjective.position.before_noun
Description: Descriptive adjectives are placed before the nouns they modify.
Pseudocode: mirad_np = optional_article + adjective_list + noun
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: adjective.descriptive.ends_a
Description: All descriptive adjectives end in the adjectival marker -a. Adjectives can be derived from qualitative roots, nouns, passive verb stems, and prepositions.
Pseudocode: if target_part_of_speech == descriptive_adjective:
    form = stem + 'a'
Examples:
- Mirad: fia | English: good | Note: fi- + -a
- Mirad: pura | English: vehicular | Note: pur 'vehicle' + -a
- Mirad: dalwa | English: spoken | Note: passive verb stem + -a

Rule ID: noun.modifiers.order_no_agreement
Description: Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.
Pseudocode: mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun
do_not_inflect_modifiers_for_gender_number_case
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: syntax.object.after_predicate
Description: In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.
Pseudocode: predicate = finite_verb + optional_adverbs
if direct_object: place after predicate
if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: preposition.bi_of_possession_partitive
Description: bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.
Pseudocode: if relation in ['of', 'possessive', 'partitive']:
    use head + 'bi' + complement
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

### sent10-mi-08-csv-0947

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 13622
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: sentence-min5, mir_to_en, csv_index:947
- retrieval_rule_ids: verb.simple.active_suffixes, verb.infinitive_er_stem, verb.no_person_number_agreement, conjunction.coordinate_ay_ey_oy, pronoun.gender.optional_w_y
- retrieval_warning: none
- error_summary: none

#### Input

Iyt eka oy oka, ay wit yeka oy oka.

#### Expected Output

she played but lost, and he tried but lost

#### Prediction

She played but lost, and he tried but lost.

#### Word Equivalents

- attempt → yek, yekiun, yekon
- attempted → yekwa
- attempting → yekea, yeken
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- he himself → it iut, wit iut
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- her herself → it iut, iyt iut
- hereto → bu hiis
- hers → haytas, haytasi, hiytas, hiytasi, huytas, huytasi, iytas, iytasi
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- him himself → it iut, wit iut
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- in pursuit of → be joigpen bi, be kex bi
- iyt → her, she
- pursued → kexwa, zoigpya
- pursuing → kexea, kexen, yekea, yeken, zoigpea, zoigpen
- pursuit → avpen, kexun, yekun, zoigpen
- seine → pitnef
- she → hayt, hiyt, huyt, it, iyt
- she herself → it iut, iyt iut
- she who → hoyt
- shearing → goflaren, goflen
- to attempt → yeker
- to pursue → avper, kexer, yeker, zoigper
- to try → doyevyeker, xefer, yaovyeker, yeker
- to try out → teexuer
- try → yek
- trying → doyevyeken, vyaoyeken, xefen, yaovyeken, yekea, yeken, yekteexen, yekuea
- wit → he, him
- yeker → to attempt, to pursue, to try

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.no_person_number_agreement
Description: The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.
Pseudocode: verb_form = conjugate(stem, tense, aspect, mood, voice)
do_not_modify verb_form for subject.person
do_not_modify verb_form for subject.number
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
3. [grammar_rules]
Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
4. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: pronoun.personal.invariant_case
Description: Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.
Pseudocode: pronoun_form = lookup_person_number_animacy_gender()
do_not_inflect_for_case
determine_case_from_position_or_preposition
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: pronoun.gender.optional_w_y
Description: The gender-neutral third-person animate pronoun it can become wit for masculine or iyt for feminine. Gender marking is optional and used when needed to distinguish referents.
Pseudocode: if pronoun == third_singular_animate:
    if gender == masculine: use 'wit'
    else if gender == feminine: use 'iyt'
    else: use 'it'
Examples:
- Mirad: it | English: he/she/him/her | Note: gender-neutral animate
- Mirad: wit | English: he/him | Note: masculine
- Mirad: iyt | English: she/her | Note: feminine
5. [grammar_rules]
Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.gender.optional_w_y
Description: The gender-neutral third-person animate pronoun it can become wit for masculine or iyt for feminine. Gender marking is optional and used when needed to distinguish referents.
Pseudocode: if pronoun == third_singular_animate:
    if gender == masculine: use 'wit'
    else if gender == feminine: use 'iyt'
    else: use 'it'
Examples:
- Mirad: it | English: he/she/him/her | Note: gender-neutral animate
- Mirad: wit | English: he/him | Note: masculine
- Mirad: iyt | English: she/her | Note: feminine

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

### sent10-mi-09-csv-0979

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 10229
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: sentence-min5, mir_to_en, csv_index:979
- retrieval_rule_ids: conjunction.coordinate_ay_ey_oy, determiner.demonstrative_hia_hua, pronoun.possessive_add_a_s_si
- retrieval_warning: none
- error_summary: none

#### Input

His se fis ay huas se atas.

#### Expected Output

this is a good thing and that is mine

#### Prediction

This is a good thing, and that is mine.

#### Word Equivalents

- and → ay
- and/or → aey
- anded → ayxwa
- anding → ayxen
- atas → mine, my thing
- ay → and
- both...and → hyaewa...ay, vay...ay
- fis → good thing, something good
- good → fia, nuun, nyuun
- good thing → fis
- good- → fi-
- his → it, this thing
- it → has, his, hus, is
- its → hasa, hisa, husa, isa, ita
- mine → atas, atasi, aytas, aytasi, mukiblem, mumyex, watas, watasi
- mined → mukiblawa, oybdopyunbwa
- miner → mukiblut
- more of it → gas
- my own thing → autas
- my thing → atas
- my things → atasi
- passage → ajpem, ajpen, ajpun, ajpyem, dyeun, yagzyotim, zeypen
- some of it → heglas
- something good → fis, fisun
- that thing → hus
- the thing → has, hason, hasun
- the thing's → hasa
- thing → son, sun
- this thing → his, hisun
- tin mine → sonilk mukiblem
- to be a good thing → fiser
- to mine → mukibler
- your thing → etas

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: verb.modal_hypothetical_mitigates
Description: When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.
Pseudocode: if modal_verb.ending == 'u':
    translate_with_softened_modal_equivalent
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees
2. [grammar_rules]
Rule ID: pronoun.possessive_add_a_s_si
Description: Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.
Pseudocode: possessive_adjective = pronoun + 'a'
if possessed_referent == inanimate_singular:
    possessive_pronoun = pronoun + 'as'
if possessed_referent == inanimate_plural:
    possessive_pronoun = pronoun + 'asi'
if possessed_referent == animate:
    replace final_s_with_t in possessive_pronoun
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: determiner.animate_t_thing_s_plural_i
Description: Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.
Pseudocode: if referent.is_person:
    category_final = 't'
else:
    category_final = 's'
if number == plural:
    add 'i'
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: noun.possession.named_person_bi
Description: Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.
Pseudocode: if english_possessive.possessor.is_proper_name:
    mirad = possessed_np + 'bi' + possessor_name
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi
3. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: determiner.deictic_begin_h
Description: All deictic determiners begin with h. Following letters specify category such as interrogative, indefinite, proximal, distal, universal, negative, person, thing, place, time, manner, degree, etc.
Pseudocode: if word.is_deictic_determiner:
    require word.starts_with('h')
    parse prefix_after_h for deixis_type
    parse suffix for semantic_category
Examples:
- Mirad: hia | English: this | Note: proximal deictic
- Mirad: hua | English: that | Note: distal deictic
- Mirad: duhot? | English: who? | Note: interrogative animate deictic

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: determiner.demonstrative_hia_hua
Description: hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.
Pseudocode: if referent.is_near_speaker: base = 'hi'
if referent.is_far_or_contextual: base = 'hu'
if used_as_adjective: form = base + 'a'
if used_as_thing_pronoun: form = base + 'as' or base + 'asi'
if used_as_person_pronoun: form = base + 'at' or base + 'ati'
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun

Rule ID: pronoun.possessive_add_a_s_si
Description: Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.
Pseudocode: possessive_adjective = pronoun + 'a'
if possessed_referent == inanimate_singular:
    possessive_pronoun = pronoun + 'as'
if possessed_referent == inanimate_plural:
    possessive_pronoun = pronoun + 'asi'
if possessed_referent == animate:
    replace final_s_with_t in possessive_pronoun
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things
4. [grammar_rules]
Rule ID: determiner.demonstrative_hia_hua
Description: hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.
Pseudocode: if referent.is_near_speaker: base = 'hi'
if referent.is_far_or_contextual: base = 'hu'
if used_as_adjective: form = base + 'a'
if used_as_thing_pronoun: form = base + 'as' or base + 'asi'
if used_as_person_pronoun: form = base + 'at' or base + 'ati'
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: verb.modal_y_glide_reduces_strength
Description: Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.
Pseudocode: if modal_or_affective_verb.needs_weaker_meaning:
    insert_y_after_stem_vowel
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: determiner.how_disambiguation
Description: English 'how' can be manner adverb duhoyen?, adjective of kind duhoyena?, or degree expression duhonog/duhogla depending on what it modifies.
Pseudocode: if how asks manner/way: use 'duhoyen?'
if how asks quality/kind of noun/event: use 'duhoyena?'
if how asks degree of adjective: use degree form such as 'duhonog' or 'duhogla' + adjective
Examples:
- Mirad: Duhoyen wit xa hus? | English: How did he do that? | Note: manner
- Mirad: Duhoyena sa ha dyezun? | English: How was the film? | Note: kind/quality adjective
- Mirad: Duhonog aga it se? | English: How big is he? | Note: degree

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern
5. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.perfect.active_ay_plus_tense
Description: The active perfect inserts the past aspect vowel a plus buffer y before the final tense/mood vowel: -aye, -aya, -ayo, -ayu.
Pseudocode: if aspect == perfect and voice == active:
    form = stem + 'ay' + final_tense_vowel
Examples:
- Mirad: At xaye. | English: I have done. | Note: x- + ay + e
- Mirad: At xaya. | English: I had done. | Note: x- + ay + a
- Mirad: At xayo. | English: I will have done. | Note: x- + ay + o

Rule ID: verb.communication_clause_object_van
Description: Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.
Pseudocode: if verb.class in ['communication','cognition'] and complement.is_declarative_clause:
    use optional_or_required_subordinator('van') + clause
if complement.is_embedded_question:
    use interrogative_deictic + embedded_clause
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: phonology.syllable.one_vowel
Description: Each Mirad syllable contains one vowel. Glided vowels with y or w count as one complex vowel for syllabification and stress.
Pseudocode: identify vowel_nuclei including complex glides
split word so each syllable has exactly one nucleus
treat final/post-vocalic y or w as part_of preceding complex vowel when applicable
Examples:
- Mirad: ama | English: hot | Note: a-ma
- Mirad: ayma | English: warm | Note: ay-ma; ay is one complex vowel
- Mirad: vyaa | English: true | Note: vya-a; two vowel nuclei

### sent10-mi-10-csv-0990

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 25023
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: sentence-min5, mir_to_en, csv_index:990
- retrieval_rule_ids: conjunction.coordinate_ay_ey_oy, verb.simple.active_suffixes
- retrieval_warning: none
- error_summary: none

#### Input

Ha tob pia hyosav, oy hyut aka.

#### Expected Output

the man left for no reason, but someone else won

#### Prediction

The person went for no reason, but someone else won.

#### Word Equivalents

- a certain person → heawa tob, heawat, het, hetob
- although → ov van, yan van
- an → awa, hea
- but → poser, setter
- butch → toobyena
- butting → teyubuxen
- butyl → butyl
- everything except → hyas oy
- except → boy, gob, goy, ovabiwa, oy, oyebexea, oyebexwa, oyebiwa, yon bi
- excepted → oyebexwa, oyebiwa
- exception → oyebexen, oyevien, vobien
- excluding → oyebexea, oyebexlea, oyebyujbea, oyebyujben, yeboysea
- for any reason → av hyea tesyob, av hyes
- for no reason → av hos, hyosav
- for no reason whatever → hyosav
- for no rhyme or reason → boy hoa vyates
- for whatever reason → av hyea tesdud, av hyea tesyob
- ha → the
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- human → toba
- human being → tob
- humanly → tobay
- hyosav → for no reason, for no reason whatever
- hyut → alien, another, different person, someone else, stranger, the other, the other person
- man → tob, twob
- man's → twoba
- mankind → tobsaun, tobtod, tobyan
- nevertheless → gey bay hus, gey bay van, gey ov hus, je hus, ov hus
- not yet → voy gaj
- oy → but, except, however, yet
- passage → ajpem, ajpen, ajpun, ajpyem, dyeun, yagzyotim, zeypen
- person → aot, tob
- pose → ben
- poser → but, sizutbut, utbut
- posing → ben
- some man → hetwob
- that person → hut
- the → ha
- the person → hat
- there → be hum
- thew → yuvat
- this man → hitwob
- this person → hiat, hit, hitob
- though → fi van
- to man → tobuer
- tob → human being, man, person
- with no reason → bay hoa tesdud
- yet → gaj, gajob, gey bay hus, gey bay van, gey ov hus, ov hus, oy
- yet again → ga awa jod
- yet more → gay ga

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.
Pseudocode: if aspect == simple and voice == active:
    if tense == present and mood == indicative: form = stem + 'e'
    if tense == past and mood == indicative: form = stem + 'a'
    if tense == future and mood == indicative: form = stem + 'o'
    if mood == hypothetical or imperative: form = stem + 'u'
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.
Pseudocode: if aspect == simple and voice == passive:
    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.infinitive_er_stem
Description: Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.
Pseudocode: if verb.infinitive.ends_with('er'):
    stem = remove_suffix(verb.infinitive, 'er')
else:
    lookup irregular_or_nonstandard_entry
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: verb.modal_auxiliary_before_infinitive
Description: Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.
Pseudocode: modal = conjugate(modal_stem, tense_aspect_mood_voice)
main_verb = infinitive_er_form
clause_predicate = modal + ' ' + main_verb
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.
Pseudocode: if relation == conjunction: use 'ay'
if relation == alternative: use 'ey'
if relation == contrast_or_negative_alternative: use 'oy'
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: noun.linkage.prepositional_and_compound
Description: Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.
Pseudocode: if relation.is_associative_or_possessive:
    use head + preposition/conjunction + complement
if modifier_noun.functions_attributively:
    use modifier_noun + head_noun or compound(modifier, head)
if two_elements_are_equal_or_opposed:
    hyphenate(element1, element2)
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: preposition.bay_with_company
Description: bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.
Pseudocode: if relation == accompaniment:
    use 'bay' + companion_np
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company
3. [grammar_rules]
Rule ID: adverb.derive_adjective_plus_y
Description: A descriptive adjective can often be converted into an adverb by adding -y, corresponding to English -ly.
Pseudocode: if adjective modifies verb/adjective/clause as manner_or_degree:
    adverb = adjective + 'y'
Examples:
- Mirad: via → viay | English: beautiful → beautifully | Note: adverbial -y
- Mirad: azay | English: loudly / strongly | Note: adverb derived from adjective

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.
Pseudocode: choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal
choose category_suffix by circumstance: place/time/manner
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: determiner.either_neither_both_patterns
Description: Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.
Pseudocode: if construction == either_or: use 'Hyeawa' + A + 'ey' + B
if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B
if construction == both_and: use 'Hyaewa' + A + 'ay' + B
if construction == only_not: use 'Hawa' + A + ', voy' + B
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees
4. [grammar_rules]
Rule ID: pronoun.hybrid_aet_ayet
Description: aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.
Pseudocode: if referent == speaker + one_addressee:
    use 'aet'
if referent == speaker + multiple_addressees:
    use 'ayet'
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: pronoun.reflexive_insert_u
Description: Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.
Pseudocode: if pronoun.is_animate_personal and target == reflexive:
    insert 'u' before final 't'
    do_not_mark_gender
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.
Pseudocode: if pronoun.is_emphatic:
    form = personal_pronoun + ' ' + corresponding_reflexive
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.reciprocal_hyuit_hyuis
Description: hyuit means one another / each other for sentient beings. hyuis means one another / each other for inanimate objects, concepts, or abstractions. These forms do not express gender or number.
Pseudocode: if reciprocal.referents_are_animate:
    use 'hyuit'
else:
    use 'hyuis'
Examples:
- Mirad: Yat yefe ifer hyuit. | English: We must love one another. | Note: animate reciprocal
- Mirad: Meri glexag yanpyexe hyuis. | English: Planets sometimes crash into each other. | Note: inanimate reciprocal

Rule ID: pronoun.english_it.translation_rules
Description: If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.
Pseudocode: if english_it.has_antecedent:
    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')
    else: use 'is' or deictic_determiner
else if english_it.is_dummy_subject:
    omit pronoun
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
