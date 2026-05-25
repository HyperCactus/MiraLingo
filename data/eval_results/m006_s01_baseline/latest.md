# M006 S01 Baseline Inspection Report

## Run Metadata

- started_at: 2026-05-25T11:19:26.730770+00:00
- completed_at: 2026-05-25T11:21:30.401330+00:00
- mode: live
- model: deepseek-ai/DeepSeek-V4-Flash
- api_preflight: ok
- devset_size: 12
- elapsed: 123671 ms (123.67 s)
- failed_example_count: 0
- failed_example_ids: none

## Preflight Call and Cost Estimate

- estimated_total_calls: 12
- estimated_cost_usd: $0.000000
- total_calls_recorded: 12
- english_to_mirad_examples: 6
- mirad_to_english_examples: 6

## Score Summary by Direction

| Direction | Examples | Normalized Matches | Errors | Success Rate |
|-----------|----------|--------------------|--------|--------------|
| English → Mirad | 6 | 4 | 0 | 66.7% |
| Mirad → English | 6 | 5 | 0 | 83.3% |

## Failure Taxonomy Legend

| Label | Example Count |
|-------|---------------|
| `adverb-placement` | 1 |
| `be-vs-bi` | 2 |
| `comparison-linker` | 1 |
| `distance-relation` | 1 |
| `dummy-it` | 3 |
| `embedded-clause` | 2 |
| `future-tense` | 1 |
| `imperative` | 1 |
| `impersonal-predicate` | 1 |
| `locative` | 1 |
| `negation` | 3 |
| `object-np` | 1 |
| `possessives` | 2 |
| `progressive-aspect` | 1 |
| `pronoun-object-order` | 1 |
| `pronouns` | 1 |
| `questions` | 1 |
| `subordinate-van` | 1 |
| `subordinate-ven` | 1 |
| `verb-inflection` | 1 |
| `verb-mood` | 1 |
| `vocabulary-fidelity` | 1 |
| `weather` | 1 |

## Per-Example Table

| ID | Direction | Status | Phase | Exact | Normalized | Failure Labels | Rule IDs | Elapsed |
|----|-----------|--------|-------|-------|------------|----------------|----------|---------|
| s01-001-en-to-mir-progressive-going-home | English → Mirad | ok | complete | yes | yes | progressive-aspect, verb-inflection | verb.motion_communication_omit_direction_preposition, verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.animate_t_inanimate_s | 30831 ms |
| s01-002-en-to-mir-comparison-vyel | English → Mirad | ok | complete | yes | yes | comparison-linker, possessives | pronoun.possessive_add_a_s_si, adjective.degree.quantifier_before_adjective, verb.stative_complement_after_ser, noun.modifiers.order_no_agreement, adjective.descriptive.ends_a, adverb.degree.same_as_adjectives | 3027 ms |
| s01-003-en-to-mir-dummy-it-negation | English → Mirad | ok | complete | no | no | dummy-it, negation, impersonal-predicate | derivation.noun.gerund_en, adjective.negation_o_lo_ol, verb.no_person_number_agreement, syntax.basic_svo, pronoun.english_it.translation_rules | 1995 ms |
| s01-004-en-to-mir-object-order | English → Mirad | ok | complete | yes | yes | pronoun-object-order, imperative | verb.simple.active_suffixes, verb.infinitive_er_stem, verb.ditransitive.indirect_before_direct, determiner.demonstrative_hia_hua | 2099 ms |
| s01-005-en-to-mir-subordinate-whether | English → Mirad | ok | complete | no | no | subordinate-ven, negation, embedded-clause | verb.simple.active_suffixes, verb.conditional_imperative_u_subject, pronoun.gender.optional_w_y, verb.communication_clause_object_van | 3031 ms |
| s01-006-en-to-mir-possession-book | English → Mirad | ok | complete | yes | yes | possessives, negation, object-np | verb.simple.active_suffixes, pronoun.possessive_add_a_s_si, translation.english_gender_default_neutral, verb.no_person_number_agreement | 25762 ms |
| s01-007-mir-to-en-locative-be-home | Mirad → English | ok | complete | no | yes | be-vs-bi, locative | verb.simple.active_suffixes, verb.simple.passive_suffixes, verb.modal_auxiliary_before_infinitive, pronoun.emphatic.personal_plus_reflexive, verb.no_person_number_agreement, preposition.bi_of_possession_partitive, adjective.position.before_noun, verb.motion_communication_omit_direction_preposition, preposition.av_for_beneficiary, preposition.bay_with_company, pronoun.reflexive_insert_u, pronoun.personal.invariant_case, syntax.subject.noun_phrase_structure, determiner.animate_t_thing_s_plural_i | 7040 ms |
| s01-008-mir-to-en-distance-bi-here | Mirad → English | ok | complete | yes | yes | be-vs-bi, distance-relation | verb.infinitive_er_stem, verb.stative_complement_after_ser, verb.no_person_number_agreement, pronoun.emphatic.personal_plus_reflexive, pronoun.reflexive_insert_u, adjective.deintensify_with_y_glide, verb.modal_y_glide_reduces_strength, adjective.degree.quantifier_before_adjective, adverb.degree.same_as_adjectives, preposition.bi_of_possession_partitive, noun.possession.named_person_bi, preposition.av_for_beneficiary, preposition.bay_with_company, verb.motion_communication_omit_direction_preposition, noun.linkage.prepositional_and_compound, pronoun.hybrid_aet_ayet | 13117 ms |
| s01-009-mir-to-en-question-school | Mirad → English | ok | complete | no | yes | questions, verb-mood | determiner.interrogative_duh_forms, verb.communication_clause_object_van, verb.modal_auxiliary_before_infinitive, syntax.subject.noun_phrase_structure, verb.modal_hypothetical_mitigates, verb.simple.active_suffixes, pronoun.emphatic.personal_plus_reflexive, verb.infinitive_er_stem, verb.no_person_number_agreement, pronoun.reflexive_insert_u, pronoun.personal.invariant_case, syntax.object.after_predicate, adjective.position.before_noun, noun.modifiers.order_no_agreement, syntax.basic_svo, verb.transitive.direct_object_after_verb | 8606 ms |
| s01-010-mir-to-en-weather-dummy-it | Mirad → English | ok | complete | no | yes | dummy-it, weather, future-tense | verb.infinitive_er_stem, verb.simple.active_suffixes, verb.modal_auxiliary_before_infinitive, verb.no_person_number_agreement, derivation.noun.gerund_en, pronoun.emphatic.personal_plus_reflexive, pronoun.reflexive_insert_u | 6310 ms |
| s01-011-mir-to-en-subordinate-van | Mirad → English | ok | complete | no | yes | subordinate-van, dummy-it, embedded-clause | conjunction.coordinate_ay_ey_oy, verb.modal_y_glide_reduces_strength, pronoun.reciprocal_hyuit_hyuis, verb.communication_clause_object_van, orthography.punctuation.direct_quote_colon, conjunction.subordinate_van_that, noun.linkage.prepositional_and_compound, verb.no_person_number_agreement, verb.infinitive_er_stem, verb.simple.active_suffixes, verb.simple.passive_suffixes, verb.passive.insert_w_before_tense, verb.perfect.passive_aw_plus_tense, pronoun.gender.optional_w_y, noun.gender.w_y_markers, pronoun.reflexive_insert_u, pronoun.hybrid_aet_ayet, pronoun.emphatic.personal_plus_reflexive | 10858 ms |
| s01-012-mir-to-en-pronoun-object-reference | Mirad → English | ok | complete | no | no | pronouns, adverb-placement, vocabulary-fidelity | verb.infinitive_er_stem, verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.emphatic.personal_plus_reflexive, verb.modal_auxiliary_before_infinitive, pronoun.personal.invariant_case, pronoun.reflexive_insert_u, syntax.subject.noun_phrase_structure, determiner.animate_t_thing_s_plural_i, derivation.noun.person_t_thing_s, pronoun.animate_t_inanimate_s, pronoun.english_it.translation_rules, adjective.position.before_noun, noun.modifiers.order_no_agreement, determiner.deictic_adverbs.place_time_manner, verb.transitive.direct_object_after_verb | 10995 ms |

## Detailed Examples

### s01-001-en-to-mir-progressive-going-home

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 30831
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: progressive-aspect, verb-inflection
- retrieval_rule_ids: verb.motion_communication_omit_direction_preposition, verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.animate_t_inanimate_s
- retrieval_warning: none
- error_summary: none

#### Input

he or she was going home

#### Expected Output

It peya tam.

#### Prediction

It peya tam.

#### Word Equivalents

- -or → -ut
- go in → per yeb
- going → pea, pen
- going along → baypea, baypen
- going on → jesen
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- he himself → it iut, wit iut
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- home → be tam, taam, tam
- home sweet home → taamif
- homey → taamyena, yukoma
- house → tam
- or → ey
- or'ed → eyxwa
- or'ing → eyxen
- orc → fyefutobag, tobtelifyet
- seine → pitnef
- she → hayt, hiyt, huyt, it, iyt
- she herself → it iut, iyt iut
- she who → hoyt
- shearing → goflaren, goflen
- to go → per
- to have a home → embexer
- wanted → fwa
- washrag → vyilxof
- wasp → awapelat
- waspish → awapelatyena
- waspishly → awapelatyenay

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.progressive.passive_ew_plus_tense
Description: {'description': 'The passive progressive inserts e plus passive/buffer w before the final tense/mood vowel: -ewe, -ewa, -ewo, -ewu.', 'pseudocode': ['if aspect == progressive and voice == passive:', "    form = stem + 'ew' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xewe. | English: It is being done. | Note: x- + ew + e
- Mirad: Has xewa. | English: It was being done. | Note: x- + ew + a

Rule ID: verb.perfect.passive_aw_plus_tense
Description: {'description': 'The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.', 'pseudocode': ['if aspect == perfect and voice == passive:', "    form = stem + 'aw' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er
2. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast
3. [grammar_rules]
Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: {'description': 'Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.', 'pseudocode': ['choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal', 'choose category_suffix by circumstance: place/time/manner']}
Pseudocode: 
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

### s01-002-en-to-mir-comparison-vyel

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 3027
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: comparison-linker, possessives
- retrieval_rule_ids: pronoun.possessive_add_a_s_si, adjective.degree.quantifier_before_adjective, verb.stative_complement_after_ser, noun.modifiers.order_no_agreement, adjective.descriptive.ends_a, adverb.degree.same_as_adjectives
- retrieval_warning: none
- error_summary: none

#### Input

my house is bigger than yours

#### Expected Output

Ata tam se ga aga vyel etas.

#### Prediction

Ata tam se ga aga vyel etas.

#### Word Equivalents

- are → se
- biggish → ayga
- bigness → agan
- does → vay
- getting bigger → agasea
- hausa → Haud
- house → tam
- is → se
- more than → ga vyel
- my → ata, ayta, wata
- my own → auta, autas, autasi, auyta, wauta, wautas, wautasi
- my thing → atas
- my way → autay, autyen
- myope → yogteatut
- rather → ga fi, ga gwa, gagwa, gajwa, gle
- row house → naba tam, nabtam
- than → vyegexwa bay, vyel
- thane → yuydeb
- that is → be hyua duni
- the house → tim bi avembiuti, yembiutyanim
- to get big → agaser
- to get larger → agaser
- to house → embesuer, tambuer, tamuer
- to rather → gafer
- whether → ven
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta
- your own → euta, eutas, eutasi, weuta, weutas, weutasi, yeuta, yeutas, yeutasi
- your yourselves → yet yeut
- yours → ayetas, ayetasi, etas, etasi, eyetas, eyetasi, eytas, eytasi, wetas, wetasi, yetas, yetasi

#### Retrieval Context

1. [grammar_rules]
Rule ID: pronoun.possessive_add_a_s_si
Description: {'description': 'Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.', 'pseudocode': ["possessive_adjective = pronoun + 'a'", 'if possessed_referent == inanimate_singular:', "    possessive_pronoun = pronoun + 'as'", 'if possessed_referent == inanimate_plural:', "    possessive_pronoun = pronoun + 'asi'", 'if possessed_referent == animate:', '    replace final_s_with_t in possessive_pronoun']}
Pseudocode: 
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things

Rule ID: noun.possession.named_person_bi
Description: {'description': "Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.", 'pseudocode': ['if english_possessive.possessor.is_proper_name:', "    mirad = possessed_np + 'bi' + possessor_name"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
2. [grammar_rules]
Rule ID: adverb.degree.same_as_adjectives
Description: {'description': 'Adverbs are compared by placing quantitative degree words before them, parallel to adjective comparison. vyel introduces the comparison standard.', 'pseudocode': ['if adverb.comparison:', "    form = degree_quantifier + adverb + optional('vyel' + standard)"]}
Pseudocode: 
Examples:
- Mirad: Dalu ge azay vyel et yafe. | English: Speak as loudly as you can. | Note: ge + adverb + vyel

Rule ID: adjective.degree.quantifier_before_adjective
Description: {'description': "Comparative and degree meanings are expressed by placing a quantitative determiner before the adjective. vyel introduces the comparison standard, like English 'than' or 'as'.", 'pseudocode': ['if comparison == more:', "    form = 'ga' + adjective + optional('vyel' + standard)", 'if comparison == equal:', "    form = 'ge' + adjective + optional('vyel' + standard)", 'if comparison == less:', "    form = 'go' + adjective + optional('vyel' + standard)", 'if superlative == most:', "    form = 'gwa' + adjective + optional('bi/be' + set_or_domain)"]}
Pseudocode: 
Examples:
- Mirad: ga fia | English: better / more good | Note: ga marks more
- Mirad: ge fia | English: as good | Note: ge marks equality
- Mirad: Ata tam se ga aga vyel etas. | English: My house is bigger than yours. | Note: vyel introduces standard

Rule ID: adjective.descriptive.ends_a
Description: {'description': 'All descriptive adjectives end in the adjectival marker -a. Adjectives can be derived from qualitative roots, nouns, passive verb stems, and prepositions.', 'pseudocode': ['if target_part_of_speech == descriptive_adjective:', "    form = stem + 'a'"]}
Pseudocode: 
Examples:
- Mirad: fia | English: good | Note: fi- + -a
- Mirad: pura | English: vehicular | Note: pur 'vehicle' + -a
- Mirad: dalwa | English: spoken | Note: passive verb stem + -a

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.opposites.vowel_switching
Description: {'description': 'Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.', 'pseudocode': ['if adjective.pattern == i_u_contrast:', "    positive = stem_with('i')", "    negative = stem_with('u')", 'if adjective.pattern == a_e_o_scale:', "    positive = stem_with('a')", "    intermediate = stem_with('e')", "    negative = stem_with('o')"]}
Pseudocode: 
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set
3. [grammar_rules]
Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er
4. [grammar_rules]
Rule ID: noun.linkage.prepositional_and_compound
Description: {'description': 'Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.', 'pseudocode': ['if relation.is_associative_or_possessive:', '    use head + preposition/conjunction + complement', 'if modifier_noun.functions_attributively:', '    use modifier_noun + head_noun or compound(modifier, head)', 'if two_elements_are_equal_or_opposed:', '    hyphenate(element1, element2)']}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: conjunction.subordinate_van_that
Description: {'description': "van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.", 'pseudocode': ['if embedded_clause.is_declarative:', "    introduce_with 'van' when clarity or grammar requires"]}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

### s01-003-en-to-mir-dummy-it-negation

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 1995
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: dummy-it, negation, impersonal-predicate
- retrieval_rule_ids: derivation.noun.gerund_en, adjective.negation_o_lo_ol, verb.no_person_number_agreement, syntax.basic_svo, pronoun.english_it.translation_rules
- retrieval_warning: none
- error_summary: none

#### Input

it is not fair to prejudge someone

#### Expected Output

Voy se yeva jayevder hes.

#### Prediction

Jayevden heawat se oyeva.

#### Word Equivalents

- are → se
- certainly not → vlay voy, vlo, vloy
- does → vay
- fair → namutyanup, naymyan, via, vyata, yeva
- fairly → gle, yevay
- fairness → yevan
- is → se
- it → has, his, hus, is
- its → hasa, hisa, husa, isa, ita
- let not → ofu, von
- more of it → gas
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- passage → ajpem, ajpen, ajpun, ajpyem, dyeun, yagzyotim, zeypen
- playing fair → yeveken
- prejudged → jayevdwa
- prejudgment → jayevden
- prejudiced → jayevtexika
- prejudicial → jayevdyea
- some of it → heglas
- somebody → het, hetob
- someone → heawa tob, heawat, het, hetob, heyt
- someone's → heta, hetoba, hetobas, hetobasi, heyta
- that is → be hyua duni
- that person → hut
- the person → hat
- to → bu
- to and → ayxer
- to don → aber, tofaber
- to or → eyxer
- to play fair → yeveker
- to prejudge → jayevder
- to sup → telogier
- whether → ven

#### Retrieval Context

1. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: {'description': 'Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.', 'pseudocode': ['if adjective.can_take_o_negation and not ambiguous:', "    form = 'o' + adjective", 'else if adjective.begins_with_consonant:', "    form = 'lo' + adjective", 'else:', "    form = 'ol' + adjective", 'if meaning == hostile_or_anti:', "    form = one_of(['lyo' + adjective, 'ov' + adjective])"]}
Pseudocode: 
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: adjective.opposites.vowel_switching
Description: {'description': 'Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.', 'pseudocode': ['if adjective.pattern == i_u_contrast:', "    positive = stem_with('i')", "    negative = stem_with('u')", 'if adjective.pattern == a_e_o_scale:', "    positive = stem_with('a')", "    intermediate = stem_with('e')", "    negative = stem_with('o')"]}
Pseudocode: 
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
2. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive
3. [grammar_rules]
Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
4. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: syntax.basic_svo
Description: {'description': 'Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.', 'pseudocode': ['if clause.is_basic_declarative:', '    order = [subject, verb_predicate, object_or_complement]']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

### s01-004-en-to-mir-object-order

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 2099
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: pronoun-object-order, imperative
- retrieval_rule_ids: verb.simple.active_suffixes, verb.infinitive_er_stem, verb.ditransitive.indirect_before_direct, determiner.demonstrative_hia_hua
- retrieval_warning: none
- error_summary: none

#### Input

give me that box

#### Expected Output

Buu at hua nyem.

#### Prediction

Buu at hua nyem.

#### Word Equivalents

- box → nyem
- boxed → nyebwa, nyembwa, pyexlawa, tuyebyexwa
- boxlike → nyemyena
- boxy → nyemyena
- give or take → gaob
- given → ayxwa, buwa
- giving → ayxen
- me → at, ayt
- me myself → at aut
- mealy → mekilyena
- meek → utogxea, yovla
- meitneirum → mitul
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- to box → pyexler, tuyeboveker, tuyebyexer
- to give → ayxer, buer, yugsaser
- to gyve → tyoyuvarer

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
2. [grammar_rules]
Rule ID: syntax.basic_svo
Description: {'description': 'Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.', 'pseudocode': ['if clause.is_basic_declarative:', '    order = [subject, verb_predicate, object_or_complement]']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: syntax.object.after_predicate
Description: {'description': 'In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.', 'pseudocode': ['predicate = finite_verb + optional_adverbs', 'if direct_object: place after predicate', 'if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object']}
Pseudocode: 
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.ditransitive.indirect_before_direct
Description: {'description': 'Many common transitive verbs imply a directional preposition. When both indirect and direct objects are present, the indirect object comes before the direct object without an explicit preposition. A prepositional paraphrase can also be used.', 'pseudocode': ['if verb.implies_direction and has_indirect_object and has_direct_object:', '    order = verb + indirect_object + direct_object', 'else if preposition_needed:', '    order = verb + direct_object + preposition + indirect_object']}
Pseudocode: 
Examples:
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object at before direct object hua nyem
- Mirad: Du it doler. | English: Tell him to be quiet. | Note: it is indirect object
- Mirad: Nusbiu at dyes. | English: Buy me a book. | Note: indirect before direct
3. [grammar_rules]
Rule ID: determiner.deictic_begin_h
Description: {'description': 'All deictic determiners begin with h. Following letters specify category such as interrogative, indefinite, proximal, distal, universal, negative, person, thing, place, time, manner, degree, etc.', 'pseudocode': ['if word.is_deictic_determiner:', "    require word.starts_with('h')", '    parse prefix_after_h for deixis_type', '    parse suffix for semantic_category']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: proximal deictic
- Mirad: hua | English: that | Note: distal deictic
- Mirad: duhot? | English: who? | Note: interrogative animate deictic

Rule ID: determiner.demonstrative_hia_hua
Description: {'description': 'hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.', 'pseudocode': ["if referent.is_near_speaker: base = 'hi'", "if referent.is_far_or_contextual: base = 'hu'", "if used_as_adjective: form = base + 'a'", "if used_as_thing_pronoun: form = base + 'as' or base + 'asi'", "if used_as_person_pronoun: form = base + 'at' or base + 'ati'"]}
Pseudocode: 
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

### s01-005-en-to-mir-subordinate-whether

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 3031
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: subordinate-ven, negation, embedded-clause
- retrieval_rule_ids: verb.simple.active_suffixes, verb.conditional_imperative_u_subject, pronoun.gender.optional_w_y, verb.communication_clause_object_van
- retrieval_warning: none
- error_summary: none

#### Input

I did not know whether he or she would come

#### Expected Output

At voy ta ven it upo.

#### Prediction

At o ta ven it upu.

#### Word Equivalents

- -or → -ut
- certainly not → vlay voy, vlo, vloy
- come → upya
- come with → uper bay
- coming → upea, upen, yup
- didactic → tixyea
- diddler → kovyoxut, tiyubaoxut
- do → vay
- does → vay
- had → bayswa, bexwa
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- he himself → it iut, wit iut
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- if yes → ven va
- is → se
- know that → ter van
- knowing → tea, ten
- known → trawa, twa
- let not → ofu, von
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- or → ey
- or'ed → eyxwa
- or'ing → eyxen
- orc → fyefutobag, tobtelifyet
- seine → pitnef
- she → hayt, hiyt, huyt, it, iyt
- she herself → it iut, iyt iut
- she who → hoyt
- shearing → goflaren, goflen
- something known → twas
- tell me whether...? → Duven...?
- to come → uper
- to come about → kaxwer, kyeser, vyamser
- to know → ter
- to will → fer
- whether → ven
- will → fan, fon, fwas, uja fondras
- would be able to → yafu
- would like → fu
- yes or no? → Vao?

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: adjective.negation_o_lo_ol
Description: {'description': 'Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.', 'pseudocode': ['if adjective.can_take_o_negation and not ambiguous:', "    form = 'o' + adjective", 'else if adjective.begins_with_consonant:', "    form = 'lo' + adjective", 'else:', "    form = 'ol' + adjective", 'if meaning == hostile_or_anti:', "    form = one_of(['lyo' + adjective, 'ov' + adjective])"]}
Pseudocode: 
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.passive.insert_w_before_tense
Description: {'description': "In finite passive forms, the passive marker w is inserted between the verb stem and the final tense/mood vowel. Passive forms translate English 'be/get + past participle' when a patient is subject.", 'pseudocode': ['if voice == passive and aspect == simple:', "    form = stem + 'w' + tense_or_mood_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xwe. | English: It is done. | Note: x- + w + e
- Mirad: Has xwa. | English: It was done. | Note: x- + w + a
- Mirad: Has xwo. | English: It will be done. | Note: x- + w + o
2. [grammar_rules]
Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: determiner.interrogative_duh_forms
Description: {'description': 'Interrogative deictic determiners are built with duh- plus a category ending: duhot? who/whom, duhos? what, duhota? whose, duhom? where, duhoj? when, duhoyen? how.', 'pseudocode': ["if asking_for_person: use 'duhot?'", "if asking_for_thing: use 'duhos?'", "if asking_for_possessor: use 'duhota?'", "if asking_for_place: use 'duhom?'", "if asking_for_time: use 'duhoj?'", "if asking_for_manner: use 'duhoyen?'"]}
Pseudocode: 
Examples:
- Mirad: Duhot? | English: Who? / Whom? | Note: animate interrogative
- Mirad: Duhos? | English: What? | Note: inanimate interrogative
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative

Rule ID: syntax.direct_discourse_colon
Description: {'description': 'In direct discourse, a reporting clause can introduce the quoted material with a colon.', 'pseudocode': ['if discourse == direct:', "    output reporting_clause + ':' + quoted_clause"]}
Pseudocode: 
Examples:
- Mirad: Ha tob zoyda at: "Va." | English: The man replied to me, "Yes." | Note: colon before direct quote

Rule ID: orthography.punctuation.direct_quote_colon
Description: {'description': 'Mirad uses a colon before direct speech where English often uses a comma.', 'pseudocode': ['if clause.introduces_direct_quote:', "    place ':' after reporting clause", '    quote_content = quoted_sentence']}
Pseudocode: 
Examples:
- Mirad: It da: "Van esu man." | English: He said, "Let there be light." | Note: colon introduces the quote

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
3. [grammar_rules]
Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: verb.conditional_imperative_u_subject
Description: {'description': 'A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.', 'pseudocode': ["if finite_verb.ends_with('u'):", '    if clause.has_explicit_subject:', '        interpret_as conditional_hypothetical', '    else:', '        interpret_as imperative']}
Pseudocode: 
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_y_glide_reduces_strength
Description: {'description': 'Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.', 'pseudocode': ['if modal_or_affective_verb.needs_weaker_meaning:', '    insert_y_after_stem_vowel']}
Pseudocode: 
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation
4. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.gender.optional_w_y
Description: {'description': 'The gender-neutral third-person animate pronoun it can become wit for masculine or iyt for feminine. Gender marking is optional and used when needed to distinguish referents.', 'pseudocode': ['if pronoun == third_singular_animate:', "    if gender == masculine: use 'wit'", "    else if gender == feminine: use 'iyt'", "    else: use 'it'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her | Note: gender-neutral animate
- Mirad: wit | English: he/him | Note: masculine
- Mirad: iyt | English: she/her | Note: feminine

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

### s01-006-en-to-mir-possession-book

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 25762
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: possessives, negation, object-np
- retrieval_rule_ids: verb.simple.active_suffixes, pronoun.possessive_add_a_s_si, translation.english_gender_default_neutral, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

I did not see his or her book

#### Expected Output

At voy teata ita dyes.

#### Prediction

At voy teata ita dyes.

#### Word Equivalents

- -or → -ut
- book → draves, dyes
- booker → nelut
- certainly not → vlay voy, vlo, vloy
- didactic → tixyea
- diddler → kovyoxut, tiyubaoxut
- do → vay
- does → vay
- had → bayswa, bexwa
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- her herself → it iut, iyt iut
- hereto → bu hiis
- hers → haytas, haytasi, hiytas, hiytasi, huytas, huytasi, iytas, iytasi
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- let not → ofu, von
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- or → ey
- or'ed → eyxwa
- or'ing → eyxen
- orc → fyefutobag, tobtelifyet
- paperback book → drefabaun dyes
- seeing → teatea, teaten
- seen → teatwa
- seine → pitnef
- seiner → pitnefxut
- she → hayt, hiyt, huyt, it, iyt
- softcover book → yugabaun dyes
- style book → drebyendyes
- to let see → teatuer
- to see → teater
- to sight-see → teapoper

#### Retrieval Context

1. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: {'description': 'Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.', 'pseudocode': ['if adjective.can_take_o_negation and not ambiguous:', "    form = 'o' + adjective", 'else if adjective.begins_with_consonant:', "    form = 'lo' + adjective", 'else:', "    form = 'ol' + adjective", 'if meaning == hostile_or_anti:', "    form = one_of(['lyo' + adjective, 'ov' + adjective])"]}
Pseudocode: 
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.passive.insert_w_before_tense
Description: {'description': "In finite passive forms, the passive marker w is inserted between the verb stem and the final tense/mood vowel. Passive forms translate English 'be/get + past participle' when a patient is subject.", 'pseudocode': ['if voice == passive and aspect == simple:', "    form = stem + 'w' + tense_or_mood_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xwe. | English: It is done. | Note: x- + w + e
- Mirad: Has xwa. | English: It was done. | Note: x- + w + a
- Mirad: Has xwo. | English: It will be done. | Note: x- + w + o
2. [grammar_rules]
Rule ID: pronoun.possessive_add_a_s_si
Description: {'description': 'Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.', 'pseudocode': ["possessive_adjective = pronoun + 'a'", 'if possessed_referent == inanimate_singular:', "    possessive_pronoun = pronoun + 'as'", 'if possessed_referent == inanimate_plural:', "    possessive_pronoun = pronoun + 'asi'", 'if possessed_referent == animate:', '    replace final_s_with_t in possessive_pronoun']}
Pseudocode: 
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: noun.possession.named_person_bi
Description: {'description': "Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.", 'pseudocode': ['if english_possessive.possessor.is_proper_name:', "    mirad = possessed_np + 'bi' + possessor_name"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi
3. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: translation.english_gender_default_neutral
Description: {'description': 'Mirad is gender-neutral by default. Use gender-specific nouns or pronouns only when English explicitly requires gender or when needed to distinguish referents.', 'pseudocode': ['if gender_not_semantically_required and referent_can_be_neutral:', '    use neutral form', 'else:', '    apply w/y gender marking or lexical gendered form']}
Pseudocode: 
Examples:
- Mirad: it | English: he/she | Note: neutral third-person animate
- Mirad: tob | English: person/human being | Note: neutral noun
- Mirad: twob / toyb | English: man / woman | Note: gender-specific when required

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
4. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: noun.linkage.prepositional_and_compound
Description: {'description': 'Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.', 'pseudocode': ['if relation.is_associative_or_possessive:', '    use head + preposition/conjunction + complement', 'if modifier_noun.functions_attributively:', '    use modifier_noun + head_noun or compound(modifier, head)', 'if two_elements_are_equal_or_opposed:', '    hyphenate(element1, element2)']}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: conjunction.subordinate_van_that
Description: {'description': "van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.", 'pseudocode': ['if embedded_clause.is_declarative:', "    introduce_with 'van' when clarity or grammar requires"]}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause
5. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object
6. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.perfect.passive_aw_plus_tense
Description: {'description': 'The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.', 'pseudocode': ['if aspect == perfect and voice == passive:', "    form = stem + 'aw' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o

Rule ID: verb.passive.insert_w_before_tense
Description: {'description': "In finite passive forms, the passive marker w is inserted between the verb stem and the final tense/mood vowel. Passive forms translate English 'be/get + past participle' when a patient is subject.", 'pseudocode': ['if voice == passive and aspect == simple:', "    form = stem + 'w' + tense_or_mood_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xwe. | English: It is done. | Note: x- + w + e
- Mirad: Has xwa. | English: It was done. | Note: x- + w + a
- Mirad: Has xwo. | English: It will be done. | Note: x- + w + o

### s01-007-mir-to-en-locative-be-home

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 7040
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: be-vs-bi, locative
- retrieval_rule_ids: verb.simple.active_suffixes, verb.simple.passive_suffixes, verb.modal_auxiliary_before_infinitive, pronoun.emphatic.personal_plus_reflexive, verb.no_person_number_agreement, preposition.bi_of_possession_partitive, adjective.position.before_noun, verb.motion_communication_omit_direction_preposition, preposition.av_for_beneficiary, preposition.bay_with_company, pronoun.reflexive_insert_u, pronoun.personal.invariant_case, syntax.subject.noun_phrase_structure, determiner.animate_t_thing_s_plural_i
- retrieval_warning: none
- error_summary: none

#### Input

At yexe be tam.

#### Expected Output

I work at home

#### Prediction

I work at home.

#### Word Equivalents

- abode → besam, embesam, tam, tejam
- at → I, me
- at least → gwoay
- atilt → abaea
- atonally → oyseuzay
- atto → goralyi-, goralyu-
- be → at
- dwelling → besam, besea, besen, embesam, embesea, tambesen, toym
- habitation → embesen, tambexen, toom
- hausa → Haud
- home → be tam, taam, tam
- home sweet home → taamif
- homebody → taambesut, tambexlut
- homey → taamyena, yukoma
- house → tam
- housed → embesuwa, tambuwa, tamuwa
- i. → i.
- i.e. → be hyua duni
- i.o.u. → drawa ojvad, ojvada dres.
- iamb → obabkyib
- me → at, ayt
- me myself → at aut
- mealy → mekilyena
- meek → utogxea, yovla
- meitneirum → mitul
- row house → naba tam, nabtam
- tam → abode, home, house
- the house → tim bi avembiuti, yembiutyanim
- the letter i → i
- to have a home → embexer
- to house → embesuer, tambuer, tamuer

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
2. [grammar_rules]
Rule ID: preposition.bi_of_possession_partitive
Description: {'description': 'bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.', 'pseudocode': ["if relation in ['of', 'possessive', 'partitive']:", "    use head + 'bi' + complement"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: preposition.av_for_beneficiary
Description: {'description': "av corresponds to English 'for' in beneficiary or advantage contexts.", 'pseudocode': ['if relation == beneficiary_or_for:', "    use 'av' + beneficiary_np"]}
Pseudocode: 
Examples:
- Mirad: His se av et. | English: This is for you. | Note: av marks beneficiary
- Mirad: Nusbiu dyes av at. | English: Buy a book for me. | Note: prepositional paraphrase

Rule ID: preposition.bay_with_company
Description: {'description': "bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.", 'pseudocode': ['if relation == accompaniment:', "    use 'bay' + companion_np"]}
Pseudocode: 
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company
3. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

### s01-008-mir-to-en-distance-bi-here

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 13117
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: be-vs-bi, distance-relation
- retrieval_rule_ids: verb.infinitive_er_stem, verb.stative_complement_after_ser, verb.no_person_number_agreement, pronoun.emphatic.personal_plus_reflexive, pronoun.reflexive_insert_u, adjective.deintensify_with_y_glide, verb.modal_y_glide_reduces_strength, adjective.degree.quantifier_before_adjective, adverb.degree.same_as_adjectives, preposition.bi_of_possession_partitive, noun.possession.named_person_bi, preposition.av_for_beneficiary, preposition.bay_with_company, verb.motion_communication_omit_direction_preposition, noun.linkage.prepositional_and_compound, pronoun.hybrid_aet_ayet
- retrieval_warning: none
- error_summary: none

#### Input

Et sa gla yib bi him.

#### Expected Output

you were very far from here

#### Prediction

you were very far from here

#### Word Equivalents

- a great deal of → glas bi
- a lot → gla, glas
- a lot of → glas bi
- bi → fro, from, of
- countless → osyaguwa, sagdyofwa
- et → thee, thou, you
- gla → a lot, majorly, many, much, numerous, roundly, super, very
- him → here, hither, this place
- innumerable → sagdyofwa
- mainly → agalay, agnay
- major → agala, agona, gagona, glatesa
- major part → gonag
- majorly → gla
- many- → gla-
- meaning a lot → glatesea
- mostly → gwaay
- much → gla
- numerous → gla, sagaya, sagika
- numerously → sagay
- quite a few → gre
- quite a lot → glays, gre, gres
- round → yuzmep, zyua
- round- → zyu-
- rounded → zyuaxwa
- roundish → zyuya
- roundly → azay, ganay, gla, ijay, ikay, yuzay
- so many → glay, higla, huugla, huuglasi, huuglati, huyengla, huyenglasi
- so much → glay, higla, huugla, huuglas, huyengla, huyenglas
- super → bi fria fin, fria, gla, gwafia
- teehee → hihi, ozivseux
- that many → hugla, huglasi, huglati
- that much → hugla, huglas
- that much/many → hugla
- theca → abnyeb
- thee → et
- thew → yuvat
- thine → eta
- this many → higla, higlasi
- this much → higla, higlas
- thitherto → bu hum
- thou → et
- throe → byook
- throes → byook
- thy → eta
- yib → afar, away, far away
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive
2. [grammar_rules]
Rule ID: adjective.deintensify_with_y_glide
Description: {'description': 'The semantic strength of many qualitative adjectives can be reduced by adding a y-glide after the ordinal or stem vowel.', 'pseudocode': ['if adjective.is_qualitative and target_intensity == mitigated:', "    insert 'y' after relevant_stem_vowel"]}
Pseudocode: 
Examples:
- Mirad: oma → oyma | English: cold → cool | Note: y-glide reduces intensity
- Mirad: ama → ayma | English: hot → warm | Note: y-glide reduces intensity
- Mirad: ifwa → iyfwa | English: loved → liked | Note: weaker affect

Rule ID: verb.modal_y_glide_reduces_strength
Description: {'description': 'Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.', 'pseudocode': ['if modal_or_affective_verb.needs_weaker_meaning:', '    insert_y_after_stem_vowel']}
Pseudocode: 
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: adjective.degree.quantifier_before_adjective
Description: {'description': "Comparative and degree meanings are expressed by placing a quantitative determiner before the adjective. vyel introduces the comparison standard, like English 'than' or 'as'.", 'pseudocode': ['if comparison == more:', "    form = 'ga' + adjective + optional('vyel' + standard)", 'if comparison == equal:', "    form = 'ge' + adjective + optional('vyel' + standard)", 'if comparison == less:', "    form = 'go' + adjective + optional('vyel' + standard)", 'if superlative == most:', "    form = 'gwa' + adjective + optional('bi/be' + set_or_domain)"]}
Pseudocode: 
Examples:
- Mirad: ga fia | English: better / more good | Note: ga marks more
- Mirad: ge fia | English: as good | Note: ge marks equality
- Mirad: Ata tam se ga aga vyel etas. | English: My house is bigger than yours. | Note: vyel introduces standard

Rule ID: adverb.degree.same_as_adjectives
Description: {'description': 'Adverbs are compared by placing quantitative degree words before them, parallel to adjective comparison. vyel introduces the comparison standard.', 'pseudocode': ['if adverb.comparison:', "    form = degree_quantifier + adverb + optional('vyel' + standard)"]}
Pseudocode: 
Examples:
- Mirad: Dalu ge azay vyel et yafe. | English: Speak as loudly as you can. | Note: ge + adverb + vyel
3. [grammar_rules]
Rule ID: preposition.bi_of_possession_partitive
Description: {'description': 'bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.', 'pseudocode': ["if relation in ['of', 'possessive', 'partitive']:", "    use head + 'bi' + complement"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: noun.possession.named_person_bi
Description: {'description': "Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.", 'pseudocode': ['if english_possessive.possessor.is_proper_name:', "    mirad = possessed_np + 'bi' + possessor_name"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi

Rule ID: preposition.av_for_beneficiary
Description: {'description': "av corresponds to English 'for' in beneficiary or advantage contexts.", 'pseudocode': ['if relation == beneficiary_or_for:', "    use 'av' + beneficiary_np"]}
Pseudocode: 
Examples:
- Mirad: His se av et. | English: This is for you. | Note: av marks beneficiary
- Mirad: Nusbiu dyes av at. | English: Buy a book for me. | Note: prepositional paraphrase

Rule ID: preposition.bay_with_company
Description: {'description': "bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.", 'pseudocode': ['if relation == accompaniment:', "    use 'bay' + companion_np"]}
Pseudocode: 
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company

Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted
4. [grammar_rules]
Rule ID: preposition.bi_of_possession_partitive
Description: {'description': 'bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.', 'pseudocode': ["if relation in ['of', 'possessive', 'partitive']:", "    use head + 'bi' + complement"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: noun.linkage.prepositional_and_compound
Description: {'description': 'Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.', 'pseudocode': ['if relation.is_associative_or_possessive:', '    use head + preposition/conjunction + complement', 'if modifier_noun.functions_attributively:', '    use modifier_noun + head_noun or compound(modifier, head)', 'if two_elements_are_equal_or_opposed:', '    hyphenate(element1, element2)']}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: preposition.bay_with_company
Description: {'description': "bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.", 'pseudocode': ['if relation == accompaniment:', "    use 'bay' + companion_np"]}
Pseudocode: 
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

### s01-009-mir-to-en-question-school

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 8606
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: questions, verb-mood
- retrieval_rule_ids: determiner.interrogative_duh_forms, verb.communication_clause_object_van, verb.modal_auxiliary_before_infinitive, syntax.subject.noun_phrase_structure, verb.modal_hypothetical_mitigates, verb.simple.active_suffixes, pronoun.emphatic.personal_plus_reflexive, verb.infinitive_er_stem, verb.no_person_number_agreement, pronoun.reflexive_insert_u, pronoun.personal.invariant_case, syntax.object.after_predicate, adjective.position.before_noun, noun.modifiers.order_no_agreement, syntax.basic_svo, verb.transitive.direct_object_after_verb
- retrieval_warning: none
- error_summary: none

#### Input

Duven et tyoyape tistam?

#### Expected Output

do you walk to school

#### Prediction

Do you walk to school?

#### Word Equivalents

- et → thee, thou, you
- grade school → atistam
- private school → yonota tistam
- school → tistam, tuxam
- school-related → tistama
- schoolhouse → tistam
- schoolroom → tistamim
- teehee → hihi, ozivseux
- theca → abnyeb
- thee → et
- thew → yuvat
- thine → eta
- thitherto → bu hum
- thou → et
- throe → byook
- throes → byook
- thy → eta
- tistam → school, schoolhouse
- to school → tuxer, tyenuer
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: determiner.interrogative_duh_forms
Description: {'description': 'Interrogative deictic determiners are built with duh- plus a category ending: duhot? who/whom, duhos? what, duhota? whose, duhom? where, duhoj? when, duhoyen? how.', 'pseudocode': ["if asking_for_person: use 'duhot?'", "if asking_for_thing: use 'duhos?'", "if asking_for_possessor: use 'duhota?'", "if asking_for_place: use 'duhom?'", "if asking_for_time: use 'duhoj?'", "if asking_for_manner: use 'duhoyen?'"]}
Pseudocode: 
Examples:
- Mirad: Duhot? | English: Who? / Whom? | Note: animate interrogative
- Mirad: Duhos? | English: What? | Note: inanimate interrogative
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
2. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
3. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: syntax.object.after_predicate
Description: {'description': 'In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.', 'pseudocode': ['predicate = finite_verb + optional_adverbs', 'if direct_object: place after predicate', 'if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object']}
Pseudocode: 
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object
4. [grammar_rules]
Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: syntax.basic_svo
Description: {'description': 'Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.', 'pseudocode': ['if clause.is_basic_declarative:', '    order = [subject, verb_predicate, object_or_complement]']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

### s01-010-mir-to-en-weather-dummy-it

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 6310
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: dummy-it, weather, future-tense
- retrieval_rule_ids: verb.infinitive_er_stem, verb.simple.active_suffixes, verb.modal_auxiliary_before_infinitive, verb.no_person_number_agreement, derivation.noun.gerund_en, pronoun.emphatic.personal_plus_reflexive, pronoun.reflexive_insert_u
- retrieval_warning: none
- error_summary: none

#### Input

Mamilo.

#### Expected Output

it will rain

#### Prediction

It will rain.

#### Word Equivalents

None.

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
2. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

### s01-011-mir-to-en-subordinate-van

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 10858
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: subordinate-van, dummy-it, embedded-clause
- retrieval_rule_ids: conjunction.coordinate_ay_ey_oy, verb.modal_y_glide_reduces_strength, pronoun.reciprocal_hyuit_hyuis, verb.communication_clause_object_van, orthography.punctuation.direct_quote_colon, conjunction.subordinate_van_that, noun.linkage.prepositional_and_compound, verb.no_person_number_agreement, verb.infinitive_er_stem, verb.simple.active_suffixes, verb.simple.passive_suffixes, verb.passive.insert_w_before_tense, verb.perfect.passive_aw_plus_tense, pronoun.gender.optional_w_y, noun.gender.w_y_markers, pronoun.reflexive_insert_u, pronoun.hybrid_aet_ayet, pronoun.emphatic.personal_plus_reflexive
- retrieval_warning: none
- error_summary: none

#### Input

Se uva van iyt pia.

#### Expected Output

it is sad that she left

#### Prediction

It is sad that she left.

#### Word Equivalents

- -let → -es
- am → amilk
- amain → bay ika azon, be ika igon
- amen → huuyensu, vla
- amyl → yigsula
- are → se
- areal → neyda
- broken heart → uvtosuwan
- broken-hearted → tiibyonbyexwa, uva
- brokenhearted → uvtosuwa
- does → vay
- heart-broken → tipbyokea
- heartbroken → tipuvxwa
- how sad! → Hoogla uva!, Hwoy!
- i'm sorry that... → At uvtose van...
- is → se
- iyt → her, she
- lachrymal → teabila
- lachrymation → teabilen
- lachrymator → teabilxar
- lachrymose → teabilaya, teabilika, teabilxyea, uva
- lacrimal → teabilaya, teabilika, teabilxyea
- let → afu, ojbuwa
- let's → van
- let... → van
- letting → nasyefuen, ojbuen
- may → afu
- may... → van
- may...not... → von...
- maybe → ve, vey
- sad → uva
- sad-spirited → tipuva
- sadly → uvay
- sadness → uvan, uvtos
- saying sorry → hyoyden
- se → am, are, is
- sorry → hyoy, uva, uvtaxea, uvtexdea, uvtosaya, uvtosika, yantipuva
- sorry! → Hyoy!, Uvtosi!, Yovobu!
- that → ho, hua, hunog, van
- that is → be hyua duni
- that which → hos
- there → be hum
- there are... → Ese...
- to amerce → kyebyukuer
- to let → jobnixer, jobnuxyafwa, nasyefuer, ojbiyafwa, ojbuer, ojnuxier
- to may → afer
- to sorry → oboser
- uva → broken-hearted, lachrymose, sad, sorry
- van → let's, let..., may..., that, the fact that
- whether → ven

#### Retrieval Context

1. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.modal_y_glide_reduces_strength
Description: {'description': 'Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.', 'pseudocode': ['if modal_or_affective_verb.needs_weaker_meaning:', '    insert_y_after_stem_vowel']}
Pseudocode: 
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: pronoun.reciprocal_hyuit_hyuis
Description: {'description': 'hyuit means one another / each other for sentient beings. hyuis means one another / each other for inanimate objects, concepts, or abstractions. These forms do not express gender or number.', 'pseudocode': ['if reciprocal.referents_are_animate:', "    use 'hyuit'", 'else:', "    use 'hyuis'"]}
Pseudocode: 
Examples:
- Mirad: Yat yefe ifer hyuit. | English: We must love one another. | Note: animate reciprocal
- Mirad: Meri glexag yanpyexe hyuis. | English: Planets sometimes crash into each other. | Note: inanimate reciprocal

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: orthography.punctuation.direct_quote_colon
Description: {'description': 'Mirad uses a colon before direct speech where English often uses a comma.', 'pseudocode': ['if clause.introduces_direct_quote:', "    place ':' after reporting clause", '    quote_content = quoted_sentence']}
Pseudocode: 
Examples:
- Mirad: It da: "Van esu man." | English: He said, "Let there be light." | Note: colon introduces the quote
2. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: conjunction.subordinate_van_that
Description: {'description': "van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.", 'pseudocode': ['if embedded_clause.is_declarative:', "    introduce_with 'van' when clarity or grammar requires"]}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: noun.linkage.prepositional_and_compound
Description: {'description': 'Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.', 'pseudocode': ['if relation.is_associative_or_possessive:', '    use head + preposition/conjunction + complement', 'if modifier_noun.functions_attributively:', '    use modifier_noun + head_noun or compound(modifier, head)', 'if two_elements_are_equal_or_opposed:', '    hyphenate(element1, element2)']}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
3. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.passive.insert_w_before_tense
Description: {'description': "In finite passive forms, the passive marker w is inserted between the verb stem and the final tense/mood vowel. Passive forms translate English 'be/get + past participle' when a patient is subject.", 'pseudocode': ['if voice == passive and aspect == simple:', "    form = stem + 'w' + tense_or_mood_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xwe. | English: It is done. | Note: x- + w + e
- Mirad: Has xwa. | English: It was done. | Note: x- + w + a
- Mirad: Has xwo. | English: It will be done. | Note: x- + w + o

Rule ID: verb.perfect.passive_aw_plus_tense
Description: {'description': 'The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.', 'pseudocode': ['if aspect == perfect and voice == passive:', "    form = stem + 'aw' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o
4. [grammar_rules]
Rule ID: pronoun.gender.optional_w_y
Description: {'description': 'The gender-neutral third-person animate pronoun it can become wit for masculine or iyt for feminine. Gender marking is optional and used when needed to distinguish referents.', 'pseudocode': ['if pronoun == third_singular_animate:', "    if gender == masculine: use 'wit'", "    else if gender == feminine: use 'iyt'", "    else: use 'it'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her | Note: gender-neutral animate
- Mirad: wit | English: he/him | Note: masculine
- Mirad: iyt | English: she/her | Note: feminine

Rule ID: noun.gender.w_y_markers
Description: {'description': 'Nouns are gender-neutral by default. To create a male form, prefix the semantically significant vowel with w. To create a female form, suffix that vowel with y. Agent nouns in -ut use -uyt for female, while the male form usually stays -ut.', 'pseudocode': ['if target_gender == masculine:', "    insert 'w' before semantic_vowel", 'if target_gender == feminine and noun.ends_with_agentive_ut:', "    replace_suffix('ut', 'uyt')", 'else if target_gender == feminine:', "    insert 'y' after semantic_vowel"]}
Pseudocode: 
Examples:
- Mirad: tob / twob / toyb | English: person / man / woman | Note: w marks masculine; y marks feminine
- Mirad: ted / twed / teyd | English: parent / father / mother | Note: gendered forms from neutral noun
- Mirad: deuzut / deuzuyt | English: singer / songstress | Note: female agentive -uyt

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

### s01-012-mir-to-en-pronoun-object-reference

- direction: Mirad → English
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 10995
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: pronouns, adverb-placement, vocabulary-fidelity
- retrieval_rule_ids: verb.infinitive_er_stem, verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.emphatic.personal_plus_reflexive, verb.modal_auxiliary_before_infinitive, pronoun.personal.invariant_case, pronoun.reflexive_insert_u, syntax.subject.noun_phrase_structure, determiner.animate_t_thing_s_plural_i, derivation.noun.person_t_thing_s, pronoun.animate_t_inanimate_s, pronoun.english_it.translation_rules, adjective.position.before_noun, noun.modifiers.order_no_agreement, determiner.deictic_adverbs.place_time_manner, verb.transitive.direct_object_after_verb
- retrieval_warning: none
- error_summary: none

#### Input

Yit xa has fi.

#### Expected Output

they did it well

#### Prediction

They did it okay.

#### Word Equivalents

- al → alilk
- alright → fi, fia
- fi → alright, fine, handsomely, nicely, ok, okay, well
- fine → byoyk, fi, fia, gyola
- fine- → vi-
- finely → gyolay, gyoy, zyoay
- fineness → gyolan, gyoyan, vifan, zyoan
- handily → zitay
- handsome → fiteasa, fiteasea, via
- handsomely → fi, viway
- handsomeness → viwan
- has → it, the thing, what
- it → has, his, hus, is
- its → hasa, hisa, husa, isa, ita
- like what → duhogel, duhoyen
- more of it → gas
- nice → fia, fitipa, iyfuwa
- nice- → fi-
- nice-looking → fiteasa, fiteasea, via
- nicely → fi, fiay
- niceness → fitipan
- ok → fi, fia, fiva
- okay → fi
- okra → byivol, vyovol
- passage → ajpem, ajpen, ajpun, ajpyem, dyeun, yagzyotim, zeypen
- some girl's → heyta, heytas, heytasi
- some girls → heyti
- some of it → heglas
- tastefully → fisyenay
- that thing → hus
- the girls → hayti, yit
- the thing → has, hason, hasun
- the thing's → hasa
- their → bi huti, hitia, hutia, huytia, yisa, yita, yota
- theirs → hutias, hutiasi, huytias, huytiasi, yitas, yitasi
- them → hasi, hasoni, hasuni, hati, hayti, hisi, hiti, hiyti, huti, hwiti, yis, yit, yot
- them themselves → iyti iytiut, yit yiut
- these girls → hiyti
- they → hasi, hasoni, hasuni, hati, hayti, hisi, hiti, hiyti, huti, huyti, hwiti, yis, yit, yot
- they themselves → iyti iytiut, yit yiut
- thing → son, sun
- this thing → his, hisun
- those girls → huyti
- to fine → byoykuer, fyuyzuer, nasbyoykuer
- well → fi, fiay, fibaka, mumilzyeg, zyutum
- what → duho, has, hasi ho, hos
- what kind of → heyena, hoyena
- what? → duhos?, duhosi?, duhosun?, duhosuni?
- which → ho-, hoa
- yit → the girls, them, they

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
3. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
4. [grammar_rules]
Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: {'description': 'Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.', 'pseudocode': ['choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal', 'choose category_suffix by circumstance: place/time/manner']}
Pseudocode: 
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object
