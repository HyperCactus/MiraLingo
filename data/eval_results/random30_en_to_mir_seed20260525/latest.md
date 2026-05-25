# M006 S01 Baseline Inspection Report

## Run Metadata

- started_at: 2026-05-25T12:12:51.287486+00:00
- completed_at: 2026-05-25T12:25:14.398653+00:00
- mode: live
- model: deepseek-ai/DeepSeek-V4-Flash
- api_preflight: ok
- devset_size: 30
- elapsed: 743111 ms (743.11 s)
- failed_example_count: 0
- failed_example_ids: none

## Preflight Call and Cost Estimate

- estimated_total_calls: 30
- estimated_cost_usd: $0.000000
- total_calls_recorded: 30
- english_to_mirad_examples: 30
- mirad_to_english_examples: 0

## Score Summary by Direction

| Direction | Examples | Normalized Matches | Errors | Success Rate |
|-----------|----------|--------------------|--------|--------------|
| English → Mirad | 30 | 18 | 0 | 60.0% |
| Mirad → English | 0 | 0 | 0 | n/a |

## Failure Taxonomy Legend

| Label | Example Count |
|-------|---------------|
| `csv-sentence-pairs` | 30 |
| `csv_index:10` | 1 |
| `csv_index:161` | 1 |
| `csv_index:195` | 1 |
| `csv_index:24` | 1 |
| `csv_index:256` | 1 |
| `csv_index:306` | 1 |
| `csv_index:330` | 1 |
| `csv_index:374` | 1 |
| `csv_index:385` | 1 |
| `csv_index:4` | 1 |
| `csv_index:439` | 1 |
| `csv_index:443` | 1 |
| `csv_index:46` | 1 |
| `csv_index:51` | 1 |
| `csv_index:535` | 1 |
| `csv_index:540` | 1 |
| `csv_index:609` | 1 |
| `csv_index:611` | 1 |
| `csv_index:645` | 1 |
| `csv_index:66` | 1 |
| `csv_index:683` | 1 |
| `csv_index:692` | 1 |
| `csv_index:71` | 1 |
| `csv_index:718` | 1 |
| `csv_index:735` | 1 |
| `csv_index:820` | 1 |
| `csv_index:827` | 1 |
| `csv_index:888` | 1 |
| `csv_index:968` | 1 |
| `csv_index:98` | 1 |
| `random30` | 30 |

## Per-Example Table

| ID | Direction | Status | Phase | Exact | Normalized | Failure Labels | Rule IDs | Elapsed |
|----|-----------|--------|-------|-------|------------|----------------|----------|---------|
| r30-01-csv-0004 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:4 | noun.article.definite_ha, noun.plural.common_countable | 29837 ms |
| r30-02-csv-0010 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:10 | adjective.position.before_noun, noun.plural.common_countable, noun.modifiers.order_no_agreement | 12431 ms |
| r30-03-csv-0024 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:24 | noun.plural.common_countable, noun.article.definite_ha | 19900 ms |
| r30-04-csv-0046 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:46 | noun.article.definite_ha, noun.plural.common_countable | 11325 ms |
| r30-05-csv-0051 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:51 | translation.english_a_an_omit, noun.article.definite_ha, translation.english_gender_default_neutral, noun.gender.w_y_markers | 12874 ms |
| r30-06-csv-0066 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:66 | noun.plural.common_countable | 16586 ms |
| r30-07-csv-0071 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:71 | translation.english_a_an_omit | 12970 ms |
| r30-08-csv-0098 | English → Mirad | ok | complete | no | yes | random30, csv-sentence-pairs, csv_index:98 | pronoun.possessive_add_a_s_si, verb.simple.active_suffixes, verb.no_person_number_agreement | 49788 ms |
| r30-09-csv-0161 | English → Mirad | ok | complete | no | yes | random30, csv-sentence-pairs, csv_index:161 | verb.simple.active_suffixes, verb.no_person_number_agreement | 18417 ms |
| r30-10-csv-0195 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:195 | verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.personal.invariant_case | 15413 ms |
| r30-11-csv-0256 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:256 | verb.conditional_imperative_u_subject, verb.simple.active_suffixes | 17255 ms |
| r30-12-csv-0306 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:306 | verb.motion_communication_omit_direction_preposition, verb.simple.active_suffixes, verb.conditional_imperative_u_subject, determiner.deictic_adverbs.place_time_manner | 48725 ms |
| r30-13-csv-0330 | English → Mirad | ok | complete | no | yes | random30, csv-sentence-pairs, csv_index:330 | verb.progressive.active_ey_plus_tense, verb.no_person_number_agreement, pronoun.animate_t_inanimate_s, verb.motion_communication_omit_direction_preposition | 31586 ms |
| r30-14-csv-0374 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:374 | adjective.degree.quantifier_before_adjective, determiner.demonstrative_hia_hua, verb.no_person_number_agreement | 29296 ms |
| r30-15-csv-0385 | English → Mirad | ok | complete | no | yes | random30, csv-sentence-pairs, csv_index:385 | verb.no_person_number_agreement, verb.simple.active_suffixes | 23717 ms |
| r30-16-csv-0439 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:439 | verb.simple.active_suffixes, verb.motion_communication_omit_direction_preposition | 15803 ms |
| r30-17-csv-0443 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:443 | verb.simple.active_suffixes, preposition.av_for_beneficiary, syntax.object.after_predicate | 34790 ms |
| r30-18-csv-0535 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:535 | orthography.alphabet.roman_no_diacritics, translation.general_concepts_no_article | 11679 ms |
| r30-19-csv-0540 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:540 | noun.plural.common_countable, derivation.noun.person_t_thing_s | 14816 ms |
| r30-20-csv-0609 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:609 | adverb.derive_adjective_plus_y | 15622 ms |
| r30-21-csv-0611 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:611 | adjective.descriptive.ends_a, adverb.derive_adjective_plus_y | 19799 ms |
| r30-22-csv-0645 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:645 | pronoun.possessive_add_a_si, verb.no_person_number_agreement, syntax.basic_svo, noun.modifiers.order_no_agreement, adjective.position.before_noun | 32461 ms |
| r30-23-csv-0683 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:683 | verb.simple.active_suffixes, verb.stative_complement_after_ser, verb.no_person_number_agreement, verb.infinitive_er_stem | 23241 ms |
| r30-24-csv-0692 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:692 | verb.simple.active_suffixes, verb.no_person_number_agreement, verb.stative_complement_after_ser, adjective.descriptive.ends_a | 24747 ms |
| r30-25-csv-0718 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:718 | verb.simple.active_suffixes | 26163 ms |
| r30-26-csv-0735 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:735 | determiner.demonstrative_hia_hua, noun.modifiers.order_no_agreement, adjective.position.before_noun, verb.no_person_number_agreement, syntax.basic_svo | 38599 ms |
| r30-27-csv-0820 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:820 | verb.simple.active_suffixes, verb.infinitive_er_stem, pronoun.gender.optional_w_y, conjunction.coordinate_ay_ey_oy, verb.communication_clause_object_van, syntax.basic_svo | 30523 ms |
| r30-28-csv-0827 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:827 | determiner.interrogative_duh_forms, verb.communication_clause_object_van, verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.possessive_add_a_s_si, conjunction.subordinate_van_that, syntax.basic_svo, verb.motion_communication_omit_direction_preposition | 44838 ms |
| r30-29-csv-0888 | English → Mirad | ok | complete | no | no | random30, csv-sentence-pairs, csv_index:888 | determiner.demonstrative_hia_hua, noun.modifiers.order_no_agreement, verb.no_person_number_agreement, verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy | 25580 ms |
| r30-30-csv-0968 | English → Mirad | ok | complete | yes | yes | random30, csv-sentence-pairs, csv_index:968 | verb.simple.active_suffixes, verb.conditional_imperative_u_subject, determiner.deictic_begin_h, determiner.demonstrative_hia_hua, syntax.object.after_predicate, verb.ditransitive.indirect_before_direct, pronoun.personal.invariant_case, conjunction.coordinate_ay_ey_oy | 34330 ms |

## Detailed Examples

### r30-01-csv-0004

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 29837
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:4
- retrieval_rule_ids: noun.article.definite_ha, noun.plural.common_countable
- retrieval_warning: none
- error_summary: none

#### Input

the houses

#### Expected Output

ha tami

#### Prediction

ha tami

#### Word Equivalents

- hausa → Haud
- house → tam
- row house → naba tam, nabtam
- the house → tim bi avembiuti, yembiutyanim
- to house → embesuer, tambuer, tamuer

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural
2. [grammar_rules]
Rule ID: noun.article.definite_ha
Description: {'description': 'Mirad has one definite article, ha. It precedes the noun and any adjectives. It does not change for gender, number, or case. There is no indefinite article.', 'pseudocode': ['if english_np.definiteness == definite:', "    mirad_np = 'ha' + modifiers + noun", 'else if english_np.has_indefinite_article:', '    omit_article_in_mirad']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: indefinite; no article
- Mirad: ha tam | English: the house | Note: definite marked with ha
- Mirad: ha tami | English: the houses | Note: ha unchanged before plural noun

Rule ID: translation.english_a_an_omit
Description: {'description': 'Mirad has no indefinite article equivalent to English a/an. An unmarked noun is indefinite or general unless made definite by ha or another determiner.', 'pseudocode': ["if english_np.article in ['a','an']:", '    omit article in Mirad', '    translate noun phrase normally']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: no indefinite article
- Mirad: fitejawa tej | English: a life well-lived | Note: indefinite abstraction, no article

Rule ID: translation.general_concepts_no_article
Description: {'description': 'General concepts such as life, love, and freedom do not take ha unless referring to a specific instance. Names of languages, countries, and persons are already specific and normally do not take ha.', 'pseudocode': ['if noun.is_general_abstraction and not specifically_modified:', "    omit 'ha'", 'if noun.is_language_or_country_or_person_name:', "    omit 'ha' unless contrastively specified"]}
Pseudocode: 
Examples:
- Mirad: tej | English: life | Note: general abstraction, no ha
- Mirad: Ferad | English: French | Note: language name, no ha
- Mirad: ha tej ho at bayse | English: the life that I have | Note: specific abstraction takes ha

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

### r30-02-csv-0010

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 12431
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:10
- retrieval_rule_ids: adjective.position.before_noun, noun.plural.common_countable, noun.modifiers.order_no_agreement
- retrieval_warning: none
- error_summary: none

#### Input

big houses

#### Expected Output

aga tami

#### Prediction

aga tami

#### Word Equivalents

- big → aga
- biggish → ayga
- hausa → Haud
- house → tam
- large → aga
- row house → naba tam, nabtam
- super-big → yizaga
- the house → tim bi avembiuti, yembiutyanim
- to get big → agaser
- to house → embesuer, tambuer, tamuer

#### Retrieval Context

1. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: syntax.basic_svo
Description: {'description': 'Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.', 'pseudocode': ['if clause.is_basic_declarative:', '    order = [subject, verb_predicate, object_or_complement]']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
2. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

### r30-03-csv-0024

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 19900
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:24
- retrieval_rule_ids: noun.plural.common_countable, noun.article.definite_ha
- retrieval_warning: none
- error_summary: none

#### Input

the birds

#### Expected Output

ha pati

#### Prediction

ha pati

#### Word Equivalents

- avian → pata
- bird → pat
- birder → patteaxut
- birdie → patog
- birdlike → patyena

#### Retrieval Context

1. [grammar_rules]
Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

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

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er
2. [grammar_rules]
Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel

Rule ID: derivation.adjective_noun_to_adj_suffixes
Description: {'description': 'Noun-derived adjectives use -a for relating to/of, -aya or -ika for full of/-ful/-ous, -oya or -uka for lacking/-less/-free, and -yena for like/-ish/-y.', 'pseudocode': ["if relation == 'relating_to': form = noun + 'a'", "if relation == 'full_of': form = noun + one_of(['aya','ika'])", "if relation == 'empty_of_or_without': form = noun + one_of(['oya','uka'])", "if relation == 'like': form = noun + 'yena'"]}
Pseudocode: 
Examples:
- Mirad: dom → doma | English: city → urban | Note: relational -a
- Mirad: mil → milaya | English: water → watery | Note: full of
- Mirad: tes → tesoya | English: meaning → meaningless | Note: without

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
3. [grammar_rules]
Rule ID: translation.english_a_an_omit
Description: {'description': 'Mirad has no indefinite article equivalent to English a/an. An unmarked noun is indefinite or general unless made definite by ha or another determiner.', 'pseudocode': ["if english_np.article in ['a','an']:", '    omit article in Mirad', '    translate noun phrase normally']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: no indefinite article
- Mirad: fitejawa tej | English: a life well-lived | Note: indefinite abstraction, no article

Rule ID: noun.article.definite_ha
Description: {'description': 'Mirad has one definite article, ha. It precedes the noun and any adjectives. It does not change for gender, number, or case. There is no indefinite article.', 'pseudocode': ['if english_np.definiteness == definite:', "    mirad_np = 'ha' + modifiers + noun", 'else if english_np.has_indefinite_article:', '    omit_article_in_mirad']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: indefinite; no article
- Mirad: ha tam | English: the house | Note: definite marked with ha
- Mirad: ha tami | English: the houses | Note: ha unchanged before plural noun

Rule ID: translation.general_concepts_no_article
Description: {'description': 'General concepts such as life, love, and freedom do not take ha unless referring to a specific instance. Names of languages, countries, and persons are already specific and normally do not take ha.', 'pseudocode': ['if noun.is_general_abstraction and not specifically_modified:', "    omit 'ha'", 'if noun.is_language_or_country_or_person_name:', "    omit 'ha' unless contrastively specified"]}
Pseudocode: 
Examples:
- Mirad: tej | English: life | Note: general abstraction, no ha
- Mirad: Ferad | English: French | Note: language name, no ha
- Mirad: ha tej ho at bayse | English: the life that I have | Note: specific abstraction takes ha

Rule ID: preposition.boy_without
Description: {'description': "boy links a noun phrase to express lack or absence, corresponding to English 'without'.", 'pseudocode': ['if relation == absence_or_without:', "    use head + 'boy' + complement"]}
Pseudocode: 
Examples:
- Mirad: nyandras boy eta dyun | English: a list without your name | Note: boy = without

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

### r30-04-csv-0046

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 11325
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:46
- retrieval_rule_ids: noun.article.definite_ha, noun.plural.common_countable
- retrieval_warning: none
- error_summary: none

#### Input

the people

#### Expected Output

ha tobi

#### Prediction

hati

#### Word Equivalents

- people → tyod, yot
- people's → tyoda, yota, yotas, yotasi
- the people → hati
- these people → hiti, hitobi
- those people → huati, huti

#### Retrieval Context

1. [grammar_rules]
Rule ID: noun.article.definite_ha
Description: {'description': 'Mirad has one definite article, ha. It precedes the noun and any adjectives. It does not change for gender, number, or case. There is no indefinite article.', 'pseudocode': ['if english_np.definiteness == definite:', "    mirad_np = 'ha' + modifiers + noun", 'else if english_np.has_indefinite_article:', '    omit_article_in_mirad']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: indefinite; no article
- Mirad: ha tam | English: the house | Note: definite marked with ha
- Mirad: ha tami | English: the houses | Note: ha unchanged before plural noun

Rule ID: translation.english_a_an_omit
Description: {'description': 'Mirad has no indefinite article equivalent to English a/an. An unmarked noun is indefinite or general unless made definite by ha or another determiner.', 'pseudocode': ["if english_np.article in ['a','an']:", '    omit article in Mirad', '    translate noun phrase normally']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: no indefinite article
- Mirad: fitejawa tej | English: a life well-lived | Note: indefinite abstraction, no article

Rule ID: translation.general_concepts_no_article
Description: {'description': 'General concepts such as life, love, and freedom do not take ha unless referring to a specific instance. Names of languages, countries, and persons are already specific and normally do not take ha.', 'pseudocode': ['if noun.is_general_abstraction and not specifically_modified:', "    omit 'ha'", 'if noun.is_language_or_country_or_person_name:', "    omit 'ha' unless contrastively specified"]}
Pseudocode: 
Examples:
- Mirad: tej | English: life | Note: general abstraction, no ha
- Mirad: Ferad | English: French | Note: language name, no ha
- Mirad: ha tej ho at bayse | English: the life that I have | Note: specific abstraction takes ha

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
2. [grammar_rules]
Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

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

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

### r30-05-csv-0051

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 12874
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:51
- retrieval_rule_ids: translation.english_a_an_omit, noun.article.definite_ha, translation.english_gender_default_neutral, noun.gender.w_y_markers
- retrieval_warning: none
- error_summary: none

#### Input

a woman

#### Expected Output

toyb

#### Prediction

toyb

#### Word Equivalents

- any woman → hyeyt
- some woman → hetoyb
- this woman → hitoyb
- this woman's → hitoyba
- woman → toyb

#### Retrieval Context

1. [grammar_rules]
Rule ID: translation.english_a_an_omit
Description: {'description': 'Mirad has no indefinite article equivalent to English a/an. An unmarked noun is indefinite or general unless made definite by ha or another determiner.', 'pseudocode': ["if english_np.article in ['a','an']:", '    omit article in Mirad', '    translate noun phrase normally']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: no indefinite article
- Mirad: fitejawa tej | English: a life well-lived | Note: indefinite abstraction, no article

Rule ID: noun.article.definite_ha
Description: {'description': 'Mirad has one definite article, ha. It precedes the noun and any adjectives. It does not change for gender, number, or case. There is no indefinite article.', 'pseudocode': ['if english_np.definiteness == definite:', "    mirad_np = 'ha' + modifiers + noun", 'else if english_np.has_indefinite_article:', '    omit_article_in_mirad']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: indefinite; no article
- Mirad: ha tam | English: the house | Note: definite marked with ha
- Mirad: ha tami | English: the houses | Note: ha unchanged before plural noun

Rule ID: translation.general_concepts_no_article
Description: {'description': 'General concepts such as life, love, and freedom do not take ha unless referring to a specific instance. Names of languages, countries, and persons are already specific and normally do not take ha.', 'pseudocode': ['if noun.is_general_abstraction and not specifically_modified:', "    omit 'ha'", 'if noun.is_language_or_country_or_person_name:', "    omit 'ha' unless contrastively specified"]}
Pseudocode: 
Examples:
- Mirad: tej | English: life | Note: general abstraction, no ha
- Mirad: Ferad | English: French | Note: language name, no ha
- Mirad: ha tej ho at bayse | English: the life that I have | Note: specific abstraction takes ha

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
2. [grammar_rules]
Rule ID: translation.english_gender_default_neutral
Description: {'description': 'Mirad is gender-neutral by default. Use gender-specific nouns or pronouns only when English explicitly requires gender or when needed to distinguish referents.', 'pseudocode': ['if gender_not_semantically_required and referent_can_be_neutral:', '    use neutral form', 'else:', '    apply w/y gender marking or lexical gendered form']}
Pseudocode: 
Examples:
- Mirad: it | English: he/she | Note: neutral third-person animate
- Mirad: tob | English: person/human being | Note: neutral noun
- Mirad: twob / toyb | English: man / woman | Note: gender-specific when required

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
3. [grammar_rules]
Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

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

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: noun.article.definite_ha
Description: {'description': 'Mirad has one definite article, ha. It precedes the noun and any adjectives. It does not change for gender, number, or case. There is no indefinite article.', 'pseudocode': ['if english_np.definiteness == definite:', "    mirad_np = 'ha' + modifiers + noun", 'else if english_np.has_indefinite_article:', '    omit_article_in_mirad']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: indefinite; no article
- Mirad: ha tam | English: the house | Note: definite marked with ha
- Mirad: ha tami | English: the houses | Note: ha unchanged before plural noun

### r30-06-csv-0066

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 16586
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:66
- retrieval_rule_ids: noun.plural.common_countable
- retrieval_warning: none
- error_summary: none

#### Input

mothers

#### Expected Output

teydi

#### Prediction

teydi

#### Word Equivalents

- mother → teyd
- mothered → teydxwa
- mothering → teydxen
- motherly → teydyena
- to mother → teydxer
- to toy with → ekarer, ifekarer
- toady → vyofidut
- toy → ekar, ifekar
- toyed → ekarwa
- toying → ekaren, ifekaren

#### Retrieval Context

1. [grammar_rules]
Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

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

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel

Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative
2. [grammar_rules]
Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

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

### r30-07-csv-0071

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 12970
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:71
- retrieval_rule_ids: translation.english_a_an_omit
- retrieval_warning: none
- error_summary: none

#### Input

a teacher

#### Expected Output

tuxut

#### Prediction

tuxut

#### Word Equivalents

- educator → tuuxut, tuxtut
- school teacher → tistam tuxut
- schoolteacher → tistamtuxut
- student teacher → tiea tuxut
- teacher → tuxut

#### Retrieval Context

1. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

Rule ID: orthography.alphabet.roman_no_diacritics
Description: {'description': 'Native Mirad words are written with the Latin alphabet and no diacritics. Capitalization is used like English for sentence starts, proper nouns, and acronyms.', 'pseudocode': ['if token.is_native_mirad:', '    require token.characters subset_of latin_letters', '    reject diacritics', 'if token.is_sentence_initial or token.is_proper_noun or token.is_acronym:', '    capitalize as in English']}
Pseudocode: 
Examples:
- Mirad: Mirad | English: Mirad | Note: proper name capitalized
- Mirad: Ferad | English: French language | Note: language name capitalized

Rule ID: derivation.noun.agent_ut_uyt
Description: {'description': 'Agent nouns meaning one who does X are formed from verb stems with -ut. The female-specific form uses -uyt.', 'pseudocode': ['if target == agent_noun:', "    form = verb_stem + 'ut'", 'if target_gender == feminine:', "    form = verb_stem + 'uyt'"]}
Pseudocode: 
Examples:
- Mirad: poper → poput | English: to travel → traveler | Note: agent -ut
- Mirad: aker → akut | English: to win → winner | Note: agent -ut
- Mirad: beker → bekuyt | English: to treat → nurse | Note: female agent -uyt
2. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: translation.english_a_an_omit
Description: {'description': 'Mirad has no indefinite article equivalent to English a/an. An unmarked noun is indefinite or general unless made definite by ha or another determiner.', 'pseudocode': ["if english_np.article in ['a','an']:", '    omit article in Mirad', '    translate noun phrase normally']}
Pseudocode: 
Examples:
- Mirad: tam | English: a house | Note: no indefinite article
- Mirad: fitejawa tej | English: a life well-lived | Note: indefinite abstraction, no article

Rule ID: translation.general_concepts_no_article
Description: {'description': 'General concepts such as life, love, and freedom do not take ha unless referring to a specific instance. Names of languages, countries, and persons are already specific and normally do not take ha.', 'pseudocode': ['if noun.is_general_abstraction and not specifically_modified:', "    omit 'ha'", 'if noun.is_language_or_country_or_person_name:', "    omit 'ha' unless contrastively specified"]}
Pseudocode: 
Examples:
- Mirad: tej | English: life | Note: general abstraction, no ha
- Mirad: Ferad | English: French | Note: language name, no ha
- Mirad: ha tej ho at bayse | English: the life that I have | Note: specific abstraction takes ha

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: orthography.alphabet.roman_no_diacritics
Description: {'description': 'Native Mirad words are written with the Latin alphabet and no diacritics. Capitalization is used like English for sentence starts, proper nouns, and acronyms.', 'pseudocode': ['if token.is_native_mirad:', '    require token.characters subset_of latin_letters', '    reject diacritics', 'if token.is_sentence_initial or token.is_proper_noun or token.is_acronym:', '    capitalize as in English']}
Pseudocode: 
Examples:
- Mirad: Mirad | English: Mirad | Note: proper name capitalized
- Mirad: Ferad | English: French language | Note: language name capitalized

### r30-08-csv-0098

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 49788
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:98
- retrieval_rule_ids: pronoun.possessive_add_a_s_si, verb.simple.active_suffixes, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

your teacher is bad

#### Expected Output

Eta tuxut se fua.

#### Prediction

eta tuxut se fua

#### Word Equivalents

- bad → fua
- bad thing → fuas
- badly → fu, fuay
- badness → fuan
- dg → dagenak
- educator → tuuxut, tuxtut
- possesser → bexut
- possessional → baysuna, bexuna
- possessive → baysyea, bexena, beyea
- possessively → baysyeay, beyeay
- possessiveness → baysyean, beyean
- s → so
- s. → s.
- school teacher → tistam tuxut
- schoolteacher → tistamtuxut
- sg → sogelk
- something bad → fuas, fusun
- student teacher → tiea tuxut
- teacher → tuxut
- tg → agtogenak
- you → et, eyt
- you yourself → et eut, eyt eut
- your → ayeta, eta, eyta, weta, yeta
- your own → euta, eutas, eutasi, weuta, weutas, weutasi, yeuta, yeutas, yeutasi
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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: noun.possession.named_person_bi
Description: {'description': "Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.", 'pseudocode': ['if english_possessive.possessor.is_proper_name:', "    mirad = possessed_np + 'bi' + possessor_name"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi
2. [grammar_rules]
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

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

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
3. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

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

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

### r30-09-csv-0161

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 18417
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:161
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

we are

#### Expected Output

Yat se.

#### Prediction

yat se

#### Word Equivalents

- be → baelk
- beamed → naudxwa
- behest → avan
- being → sat, sea, sean, seat, sen, zapuen
- our → aeta, ayet, ayita, yata
- to be → ser
- to wee → tiyabiler
- verb → erdun
- verb tense → erdunjob
- verbality → dunan
- verbiage → dunyan
- verbosely → dunikay
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
2. [grammar_rules]
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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

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

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

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

### r30-10-csv-0195

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 15413
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:195
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.personal.invariant_case
- retrieval_warning: none
- error_summary: none

#### Input

I will do

#### Expected Output

At xo.

#### Prediction

At xo.

#### Word Equivalents

- do → vay
- doe → kapoyt, vapoyt, vepoyt, vyapoyt, yupeyt
- doer → xut
- doing → xen
- to do → xer

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

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

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
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

### r30-11-csv-0256

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 17255
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:256
- retrieval_rule_ids: verb.conditional_imperative_u_subject, verb.simple.active_suffixes
- retrieval_warning: none
- error_summary: none

#### Input

we would go

#### Expected Output

Yat pu.

#### Prediction

Yat pu.

#### Word Equivalents

- -y → -ika
- go in → per yeb
- goer → put
- going → pea, pen
- let go → lobexwa, lopexwa, yivafxwa
- our → aeta, ayet, ayita, yata
- per → av, gol
- per- → zye-
- peri- → yuz-
- perk → yiznix
- to go → per
- to perk → mulyonxer
- to wee → tiyabiler
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil
- y. → y.
- yate → dalyofab
- yatter → daler tesukay
- yd → yudanak

#### Retrieval Context

1. [grammar_rules]
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
2. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

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

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o
3. [grammar_rules]
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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

### r30-12-csv-0306

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 48725
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:306
- retrieval_rule_ids: verb.motion_communication_omit_direction_preposition, verb.simple.active_suffixes, verb.conditional_imperative_u_subject, determiner.deictic_adverbs.place_time_manner
- retrieval_warning: none
- error_summary: none

#### Input

come to the grocery store sometime

#### Expected Output

Upu ha tolnam hej.

#### Prediction

Upu telnunam hej.

#### Word Equivalents

- come → upya
- come with → uper bay
- coming → upea, upen, yup
- grocer → tolnamut, tolyanamut
- groceries → telnunyan, tol, tolnuyunyan, tolyan
- grocery item → telnun
- grocery shopping → tolampen, tolnampen
- grocery store → telnunam, tolam, tolnam
- in store → be nyex
- preposition → ebdun
- prepositional → ebduna
- prepositional phrase → ebduna dyanes
- prepositionally → ebdunay
- prepossession → jaembien
- some other time → hehyuj, hyua job, hyuawa job, hyuj
- some time → hegan job, hegla job
- sometime → hej, hejob, hejod
- sometime when → hej ho, hejob ho
- sometimes → hegla jodi, heji, hesag jodi, hexag
- store → nam, nunam, nyebam
- storehouse → nexam, nyebam, nyexam, nyexunam
- storing → nunamben, nyexen
- to → bu
- to and → ayxer
- to come → uper
- to come about → kaxwer, kyeser, vyamser
- to don → aber, tofaber
- to or → eyxer
- to store → nunamber, nyexer
- to sup → telogier

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: verb.conditional_imperative_u_subject
Description: {'description': 'A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.', 'pseudocode': ["if finite_verb.ends_with('u'):", '    if clause.has_explicit_subject:', '        interpret_as conditional_hypothetical', '    else:', '        interpret_as imperative']}
Pseudocode: 
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
2. [grammar_rules]
Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

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

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
3. [grammar_rules]
Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: preposition.bi_of_possession_partitive
Description: {'description': 'bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.', 'pseudocode': ["if relation in ['of', 'possessive', 'partitive']:", "    use head + 'bi' + complement"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted
4. [grammar_rules]
Rule ID: determiner.deictic_adverbs.place_time_manner
Description: {'description': 'Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.', 'pseudocode': ['choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal', 'choose category_suffix by circumstance: place/time/manner']}
Pseudocode: 
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun
5. [grammar_rules]
Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

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

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: {'description': 'Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.', 'pseudocode': ['choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal', 'choose category_suffix by circumstance: place/time/manner']}
Pseudocode: 
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

### r30-13-csv-0330

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 31586
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:330
- retrieval_rule_ids: verb.progressive.active_ey_plus_tense, verb.no_person_number_agreement, pronoun.animate_t_inanimate_s, verb.motion_communication_omit_direction_preposition
- retrieval_warning: none
- error_summary: none

#### Input

he or she is going home

#### Expected Output

It peye tam.

#### Prediction

it peye tam

#### Word Equivalents

- animate → tejea
- animated → tejaya, tejika, tejikxwa, tejuwa, toopika, topika
- animatedly → tejuway
- animation → tejikxen, tejuen
- as → asolk
- as ... as ... as → ge ... vyel
- asap → g.i., gwa ig, gwa igay, gwa jwa
- asp → esepyet
- body motion → bas
- destination → bum, pyum
- go in → per yeb
- goer → put
- going → pea, pen
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- her whom → hoyt
- home → be tam, taam, tam
- home sweet home → taamif
- homey → taamyena, yukoma
- house → tam
- in motion → pana, pansea
- inasmuch as → hanog ho
- it → has, his, hus, is
- its → hasa, hisa, husa, isa, ita
- let go → lobexwa, lopexwa, yivafxwa
- motion → ban, kyap, pan
- motioning → banxea, banxen
- movement → pan, pas, paxen
- she who → hoyt
- to a distant place → bu yibem
- to animate → tejikxer, tejuer
- to arrive at the destination → ujempuer
- to destine → kyeojber, pyumxer
- to go → per
- to have a home → embexer
- vacation destination → ifponem
- verb → erdun
- verb tense → erdunjob
- verbality → dunan
- verbiage → dunyan
- verbosely → dunikay

#### Retrieval Context

1. [grammar_rules]
Rule ID: verb.progressive.passive_ew_plus_tense
Description: {'description': 'The passive progressive inserts e plus passive/buffer w before the final tense/mood vowel: -ewe, -ewa, -ewo, -ewu.', 'pseudocode': ['if aspect == progressive and voice == passive:', "    form = stem + 'ew' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xewe. | English: It is being done. | Note: x- + ew + e
- Mirad: Has xewa. | English: It was being done. | Note: x- + ew + a

Rule ID: verb.progressive.active_ey_plus_tense
Description: {'description': 'The active progressive inserts the present aspect vowel e plus buffer y between the stem and final tense/mood vowel: -eye, -eya, -eyo, -eyu.', 'pseudocode': ['if aspect == progressive and voice == active:', "    form = stem + 'ey' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: at xeye | English: I am doing | Note: x- + ey + e
- Mirad: at xeya | English: I was doing | Note: x- + ey + a
- Mirad: at xeyo | English: I will be doing | Note: x- + ey + o

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
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

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
3. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

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
4. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

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

Rule ID: pronoun.generic_ot_yot
Description: {'description': 'ot means generic one; yot means people/they in a generic unspecific sense.', 'pseudocode': ["if english_subject in ['one', 'generic you']:", "    use 'ot'", "if english_subject in ['people', 'they' generic]:", "    use 'yot'"]}
Pseudocode: 
Examples:
- Mirad: Ot yefe xer ha yakwas. | English: One must do what is expected. | Note: ot as generic one
- Mirad: Yot de van et vyode hyoj. | English: People say you never lie. | Note: yot as generic people

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel
5. [grammar_rules]
Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: determiner.deictic_adverbs.place_time_manner
Description: {'description': 'Correlative deictic adverbs include place: duhom? where, hem somewhere, him here, hum there; time: duhoj? when, hej sometime, hij now, huj then; manner: duhoyen? how, heyen somehow, hiyen this way, huyen that way.', 'pseudocode': ['choose deictic_prefix by deixis_type: interrogative/indefinite/proximal/distal', 'choose category_suffix by circumstance: place/time/manner']}
Pseudocode: 
Examples:
- Mirad: Duhom yit se? | English: Where are they? | Note: place interrogative
- Mirad: Yit tambesa him. | English: They lived here. | Note: proximal place
- Mirad: Xu has hij! | English: Do it now! | Note: proximal time

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

### r30-14-csv-0374

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 29296
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:374
- retrieval_rule_ids: adjective.degree.quantifier_before_adjective, determiner.demonstrative_hia_hua, verb.no_person_number_agreement
- retrieval_warning: none
- error_summary: none

#### Input

this teacher is the least good

#### Expected Output

Hia tuxut se ha gwo fia.

#### Prediction

Hia tuxut se gwo fia.

#### Word Equivalents

- are → se
- does → vay
- doing the least → gwoxea
- educator → tuuxut, tuxtut
- fewest → gwo
- good → fia, nuun, nyuun
- good thing → fis
- good- → fi-
- goodly → ayga
- is → se
- least → gwo, gwoa
- least- → gwo-
- leastwise → gwoy
- school teacher → tistam tuxut
- schoolteacher → tistamtuxut
- since this → ji his
- something good → fis, fisun
- student teacher → tiea tuxut
- teacher → tuxut
- that is → be hyua duni
- this → hi-, hia, hinog
- this kind → hisaun
- this kind of → higela, hisauna, hiyena
- this one → hias, hiat, hiawa, hiawas
- whether → ven

#### Retrieval Context

1. [grammar_rules]
Rule ID: adjective.degree.quantifier_before_adjective
Description: {'description': "Comparative and degree meanings are expressed by placing a quantitative determiner before the adjective. vyel introduces the comparison standard, like English 'than' or 'as'.", 'pseudocode': ['if comparison == more:', "    form = 'ga' + adjective + optional('vyel' + standard)", 'if comparison == equal:', "    form = 'ge' + adjective + optional('vyel' + standard)", 'if comparison == less:', "    form = 'go' + adjective + optional('vyel' + standard)", 'if superlative == most:', "    form = 'gwa' + adjective + optional('bi/be' + set_or_domain)"]}
Pseudocode: 
Examples:
- Mirad: ga fia | English: better / more good | Note: ga marks more
- Mirad: ge fia | English: as good | Note: ge marks equality
- Mirad: Ata tam se ga aga vyel etas. | English: My house is bigger than yours. | Note: vyel introduces standard

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: verb.progressive.passive_ew_plus_tense
Description: {'description': 'The passive progressive inserts e plus passive/buffer w before the final tense/mood vowel: -ewe, -ewa, -ewo, -ewu.', 'pseudocode': ['if aspect == progressive and voice == passive:', "    form = stem + 'ew' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xewe. | English: It is being done. | Note: x- + ew + e
- Mirad: Has xewa. | English: It was being done. | Note: x- + ew + a

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive
2. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

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

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

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
4. [grammar_rules]
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

Rule ID: pronoun.animate_t_inanimate_s
Description: {'description': "Pronouns ending in -t refer to animate beings; pronouns ending in -s refer to inanimate objects, concepts, or abstractions. English 'it/they/them' must be resolved by antecedent animacy.", 'pseudocode': ['if antecedent.is_animate:', "    use pronoun ending '-t'", 'if antecedent.is_inanimate:', "    use pronoun ending '-s'"]}
Pseudocode: 
Examples:
- Mirad: it | English: he/she/him/her/animate it | Note: animate singular
- Mirad: is | English: it | Note: inanimate singular
- Mirad: yit / yis | English: they animate / they inanimate | Note: plural animacy contrast

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

### r30-15-csv-0385

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 23717
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:385
- retrieval_rule_ids: verb.no_person_number_agreement, verb.simple.active_suffixes
- retrieval_warning: none
- error_summary: none

#### Input

you all do not know

#### Expected Output

Yet voy te.

#### Prediction

yet voy te

#### Word Equivalents

- certainly not → vlay voy, vlo, vloy
- know that → ter van
- knowing → tea, ten
- known → trawa, twa
- let not → ofu, von
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- plural → glagona, glasaga, glasuna, yansaga, yanta
- plurality → glagon, glasagan, glasunan, yansagan, yantan
- pluralization → glagonxen, glasagxen, glasunaxen, glasunxen, yansagxen
- pluralized → glagonxwa, glasagxwa, glasunxwa, yansagxwa
- something known → twas
- to know → ter
- to pluralize → glagonxer, glasagxer, glasunaxer, glasunxer, yansagxer
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: {'description': 'Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.', 'pseudocode': ['if adjective.can_take_o_negation and not ambiguous:', "    form = 'o' + adjective", 'else if adjective.begins_with_consonant:', "    form = 'lo' + adjective", 'else:', "    form = 'ol' + adjective", 'if meaning == hostile_or_anti:', "    form = one_of(['lyo' + adjective, 'ov' + adjective])"]}
Pseudocode: 
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: adjective.opposites.vowel_switching
Description: {'description': 'Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.', 'pseudocode': ['if adjective.pattern == i_u_contrast:', "    positive = stem_with('i')", "    negative = stem_with('u')", 'if adjective.pattern == a_e_o_scale:', "    positive = stem_with('a')", "    intermediate = stem_with('e')", "    negative = stem_with('o')"]}
Pseudocode: 
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
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

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive
3. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

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

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

### r30-16-csv-0439

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 15803
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:439
- retrieval_rule_ids: verb.simple.active_suffixes, verb.motion_communication_omit_direction_preposition
- retrieval_warning: none
- error_summary: none

#### Input

go to the store

#### Expected Output

Pe ha nam.

#### Prediction

Pu ha nam.

#### Word Equivalents

- -form → -san
- form → san, sandraf, ukundref
- formative → ijsana, sansea, sanxyea
- formed → sanuwa, sanxwa
- formic → napelta
- go in → per yeb
- goer → put
- going → pea, pen
- imperative → direna, efwa, usan, yefwa, yuvon
- imperatively → direnay, efway, yefway
- imperially → adobay
- imperiously → abdobay
- in store → be nyex
- let go → lobexwa, lopexwa, yivafxwa
- name → dyun
- named → dyuwa
- namely → dyunay
- namer → dyunuut
- store → nam, nunam, nyebam
- storehouse → nexam, nyebam, nyexam, nyexunam
- storing → nunamben, nyexen
- to go → per
- to imprecate → fyodyuer
- to name → dyuer
- to store → nunamber, nyexer

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: verb.conditional_imperative_u_subject
Description: {'description': 'A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.', 'pseudocode': ["if finite_verb.ends_with('u'):", '    if clause.has_explicit_subject:', '        interpret_as conditional_hypothetical', '    else:', '        interpret_as imperative']}
Pseudocode: 
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
2. [grammar_rules]
Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

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

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en
3. [grammar_rules]
Rule ID: preposition.bi_of_possession_partitive
Description: {'description': 'bi translates many English of-relations, including possession by named persons and partitives such as a glass of wine.', 'pseudocode': ["if relation in ['of', 'possessive', 'partitive']:", "    use head + 'bi' + complement"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessive bi
- Mirad: tilzyeb bi vafil | English: a glass of wine | Note: partitive bi

Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: preposition.ayv_about
Description: {'description': "ayv introduces the topic or subject matter of a noun, speech, writing, or thought, corresponding to English 'about'.", 'pseudocode': ['if relation == topic_or_about:', "    use head + 'ayv' + topic_np"]}
Pseudocode: 
Examples:
- Mirad: dyes ayv ha Ea Mira Dropek | English: a book about the Second World War | Note: ayv introduces topic

Rule ID: preposition.bay_with_company
Description: {'description': "bay expresses accompaniment, corresponding to English 'with' in the sense of in the company of.", 'pseudocode': ['if relation == accompaniment:', "    use 'bay' + companion_np"]}
Pseudocode: 
Examples:
- Mirad: Upu eker bay yat. | English: Come play with us. | Note: bay marks company
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

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

### r30-17-csv-0443

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 34790
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:443
- retrieval_rule_ids: verb.simple.active_suffixes, preposition.av_for_beneficiary, syntax.object.after_predicate
- retrieval_warning: none
- error_summary: none

#### Input

buy me a book

#### Expected Output

Nusbiu at dyes.

#### Prediction

Nuxbiu av at dyes.

#### Word Equivalents

- at → atulk
- at least → gwoay
- at the right → zi
- atonally → oyseuzay
- atto → goralyi-, goralyu-
- beneficent → tobifa
- beneficently → tobifay
- beneficial → fixea, fiyixuwa, fiyuxea, fyisea
- beneficially → fiyuxeay, fyiseay
- benefiting → fiyuxen, ifbien
- book → draves, dyes
- booker → nelut
- bought → nuniwa, nuxbiwa
- buying → nunien, nuxbien
- doyen → doyteb
- dy → dayulk
- dyer → voylzilbut
- dyke → milovmas, ovmoub, ummegmas
- dyne → dayuninak
- marked → finsiynxwa, siynbwa, siynxwa
- marker → kyojesea drilar
- marking → finsiynen, siynben, siynbun, siynxen
- me → at, ayt
- me myself → at aut
- mealy → mekilyena
- meek → utogxea, yovla
- meitneirum → mitul
- mile marker → mepnod
- mile-marker → mepnod
- ni → niilk
- nicker → apod
- niger → Nerom
- niter → nikil
- paperback book → drefabaun dyes
- purchase → niun, nuxbiun
- softcover book → yugabaun dyes
- style book → drebyendyes
- to buy → nunier, nuxbier
- to nix → hyosunxer, lojudrer, loxer, onaxer
- to purchase → nunier, nuxbier

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: verb.conditional_imperative_u_subject
Description: {'description': 'A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.', 'pseudocode': ["if finite_verb.ends_with('u'):", '    if clause.has_explicit_subject:', '        interpret_as conditional_hypothetical', '    else:', '        interpret_as imperative']}
Pseudocode: 
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
2. [grammar_rules]
Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: preposition.av_for_beneficiary
Description: {'description': "av corresponds to English 'for' in beneficiary or advantage contexts.", 'pseudocode': ['if relation == beneficiary_or_for:', "    use 'av' + beneficiary_np"]}
Pseudocode: 
Examples:
- Mirad: His se av et. | English: This is for you. | Note: av marks beneficiary
- Mirad: Nusbiu dyes av at. | English: Buy a book for me. | Note: prepositional paraphrase

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: noun.possession.named_person_bi
Description: {'description': "Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.", 'pseudocode': ['if english_possessive.possessor.is_proper_name:', "    mirad = possessed_np + 'bi' + possessor_name"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi
3. [grammar_rules]
Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: syntax.object.after_predicate
Description: {'description': 'In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.', 'pseudocode': ['predicate = finite_verb + optional_adverbs', 'if direct_object: place after predicate', 'if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object']}
Pseudocode: 
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural
4. [grammar_rules]
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

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

### r30-18-csv-0535

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 11679
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:535
- retrieval_rule_ids: orthography.alphabet.roman_no_diacritics, translation.general_concepts_no_article
- retrieval_warning: none
- error_summary: none

#### Input

France

#### Expected Output

Feram

#### Prediction

Feram

#### Word Equivalents

- franc → frank
- france → Feram
- french → Ferama
- french polynesia → Poyufem
- inhabitant of france → Feramat

#### Retrieval Context

1. [grammar_rules]
Rule ID: orthography.alphabet.roman_no_diacritics
Description: {'description': 'Native Mirad words are written with the Latin alphabet and no diacritics. Capitalization is used like English for sentence starts, proper nouns, and acronyms.', 'pseudocode': ['if token.is_native_mirad:', '    require token.characters subset_of latin_letters', '    reject diacritics', 'if token.is_sentence_initial or token.is_proper_noun or token.is_acronym:', '    capitalize as in English']}
Pseudocode: 
Examples:
- Mirad: Mirad | English: Mirad | Note: proper name capitalized
- Mirad: Ferad | English: French language | Note: language name capitalized

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel

Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

Rule ID: translation.general_concepts_no_article
Description: {'description': 'General concepts such as life, love, and freedom do not take ha unless referring to a specific instance. Names of languages, countries, and persons are already specific and normally do not take ha.', 'pseudocode': ['if noun.is_general_abstraction and not specifically_modified:', "    omit 'ha'", 'if noun.is_language_or_country_or_person_name:', "    omit 'ha' unless contrastively specified"]}
Pseudocode: 
Examples:
- Mirad: tej | English: life | Note: general abstraction, no ha
- Mirad: Ferad | English: French | Note: language name, no ha
- Mirad: ha tej ho at bayse | English: the life that I have | Note: specific abstraction takes ha

Rule ID: noun.possession.named_person_bi
Description: {'description': "Possession by a named person is expressed as possessed noun + bi + possessor, equivalent to English 'Y's X' or 'the X of Y'.", 'pseudocode': ['if english_possessive.possessor.is_proper_name:', "    mirad = possessed_np + 'bi' + possessor_name"]}
Pseudocode: 
Examples:
- Mirad: ha tam bi Maria | English: Mary's house / the house of Mary | Note: possessor follows bi

### r30-19-csv-0540

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 14816
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:540
- retrieval_rule_ids: noun.plural.common_countable, derivation.noun.person_t_thing_s
- retrieval_warning: none
- error_summary: none

#### Input

Americans

#### Expected Output

Usomati

#### Prediction

Usomati

#### Word Equivalents

- american → Usoma, Usomat
- americanization → Usomxen
- americanized → Usomxwa
- north america → Ayanmel
- north american → Ayanmela, Ayanmelat
- pro-american → Usomava, avUsoma
- united states → Usom
- united states of america → ADA, Anxwa Doebi bi Ayanmel, Usom
- usa → ADA, Usom

#### Retrieval Context

1. [grammar_rules]
Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

Rule ID: noun.common_singular.ends_consonant
Description: {'description': 'In native Mirad, singular common nouns normally end in a consonant. Proper nouns may end in vowels.', 'pseudocode': ['if noun.is_common and noun.number == singular and noun.is_native:', '    expect final_character is consonant', 'if noun.is_proper:', '    allow final_vowel']}
Pseudocode: 
Examples:
- Mirad: tam | English: house | Note: singular common noun ending in consonant
- Mirad: Roma | English: Rome | Note: proper noun may end in vowel

Rule ID: derivation.adjective_noun_to_adj_suffixes
Description: {'description': 'Noun-derived adjectives use -a for relating to/of, -aya or -ika for full of/-ful/-ous, -oya or -uka for lacking/-less/-free, and -yena for like/-ish/-y.', 'pseudocode': ["if relation == 'relating_to': form = noun + 'a'", "if relation == 'full_of': form = noun + one_of(['aya','ika'])", "if relation == 'empty_of_or_without': form = noun + one_of(['oya','uka'])", "if relation == 'like': form = noun + 'yena'"]}
Pseudocode: 
Examples:
- Mirad: dom → doma | English: city → urban | Note: relational -a
- Mirad: mil → milaya | English: water → watery | Note: full of
- Mirad: tes → tesoya | English: meaning → meaningless | Note: without

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
Rule ID: derivation.noun.person_t_thing_s
Description: {'description': 'The suffix -t often derives a person, while -s derives a thing/object from adjectives or determiner stems.', 'pseudocode': ['if target_referent == person:', "    form = stem + 't'", 'if target_referent == thing:', "    form = stem + 's'"]}
Pseudocode: 
Examples:
- Mirad: fia → fiat / fias | English: good → good person / good thing | Note: -t vs -s
- Mirad: duho- → duhot? / duhos? | English: which → who? / what? | Note: animate vs inanimate interrogative

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

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: derivation.adjective_noun_to_adj_suffixes
Description: {'description': 'Noun-derived adjectives use -a for relating to/of, -aya or -ika for full of/-ful/-ous, -oya or -uka for lacking/-less/-free, and -yena for like/-ish/-y.', 'pseudocode': ["if relation == 'relating_to': form = noun + 'a'", "if relation == 'full_of': form = noun + one_of(['aya','ika'])", "if relation == 'empty_of_or_without': form = noun + one_of(['oya','uka'])", "if relation == 'like': form = noun + 'yena'"]}
Pseudocode: 
Examples:
- Mirad: dom → doma | English: city → urban | Note: relational -a
- Mirad: mil → milaya | English: water → watery | Note: full of
- Mirad: tes → tesoya | English: meaning → meaningless | Note: without

### r30-20-csv-0609

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 15622
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:609
- retrieval_rule_ids: adverb.derive_adjective_plus_y
- retrieval_warning: none
- error_summary: none

#### Input

easy easily

#### Expected Output

gyua gyuay

#### Prediction

yuka yukay

#### Word Equivalents

- ease → yukan, yukbyen, yukom, yukyen
- easily → yukay, yukbyenay
- easiness → yukan
- easy → yuka, yukbyena, yukyena
- facile → yuka
- facilely → yukay

#### Retrieval Context

1. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adverb.derive_adjective_plus_y
Description: {'description': 'A descriptive adjective can often be converted into an adverb by adding -y, corresponding to English -ly.', 'pseudocode': ['if adjective modifies verb/adjective/clause as manner_or_degree:', "    adverb = adjective + 'y'"]}
Pseudocode: 
Examples:
- Mirad: via → viay | English: beautiful → beautifully | Note: adverbial -y
- Mirad: azay | English: loudly / strongly | Note: adverb derived from adjective

Rule ID: derivation.adjective_noun_to_adj_suffixes
Description: {'description': 'Noun-derived adjectives use -a for relating to/of, -aya or -ika for full of/-ful/-ous, -oya or -uka for lacking/-less/-free, and -yena for like/-ish/-y.', 'pseudocode': ["if relation == 'relating_to': form = noun + 'a'", "if relation == 'full_of': form = noun + one_of(['aya','ika'])", "if relation == 'empty_of_or_without': form = noun + one_of(['oya','uka'])", "if relation == 'like': form = noun + 'yena'"]}
Pseudocode: 
Examples:
- Mirad: dom → doma | English: city → urban | Note: relational -a
- Mirad: mil → milaya | English: water → watery | Note: full of
- Mirad: tes → tesoya | English: meaning → meaningless | Note: without

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

### r30-21-csv-0611

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 19799
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:611
- retrieval_rule_ids: adjective.descriptive.ends_a, adverb.derive_adjective_plus_y
- retrieval_warning: none
- error_summary: none

#### Input

personal personally

#### Expected Output

auta autay

#### Prediction

aota aotay

#### Word Equivalents

- personal → aota, yonota
- personalized → aotxwa, utxwa
- personally → aotay
- personalty → aotyen
- private person → yonot
- to sob → azhuhuder, azteabiler, azuvteuder, uvlader, uvteabiler
- tog → kyilaf
- togo → Togom
- toot → awapeid
- tooter → awapeidar, seuxar, seuxarut, voduzaresut

#### Retrieval Context

1. [grammar_rules]
Rule ID: derivation.adjective_noun_to_adj_suffixes
Description: {'description': 'Noun-derived adjectives use -a for relating to/of, -aya or -ika for full of/-ful/-ous, -oya or -uka for lacking/-less/-free, and -yena for like/-ish/-y.', 'pseudocode': ["if relation == 'relating_to': form = noun + 'a'", "if relation == 'full_of': form = noun + one_of(['aya','ika'])", "if relation == 'empty_of_or_without': form = noun + one_of(['oya','uka'])", "if relation == 'like': form = noun + 'yena'"]}
Pseudocode: 
Examples:
- Mirad: dom → doma | English: city → urban | Note: relational -a
- Mirad: mil → milaya | English: water → watery | Note: full of
- Mirad: tes → tesoya | English: meaning → meaningless | Note: without

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

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: adverb.derive_adjective_plus_y
Description: {'description': 'A descriptive adjective can often be converted into an adverb by adding -y, corresponding to English -ly.', 'pseudocode': ['if adjective modifies verb/adjective/clause as manner_or_degree:', "    adverb = adjective + 'y'"]}
Pseudocode: 
Examples:
- Mirad: via → viay | English: beautiful → beautifully | Note: adverbial -y
- Mirad: azay | English: loudly / strongly | Note: adverb derived from adjective
2. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

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

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun
3. [grammar_rules]
Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

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

### r30-22-csv-0645

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 32461
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:645
- retrieval_rule_ids: pronoun.possessive_add_a_si, verb.no_person_number_agreement, syntax.basic_svo, noun.modifiers.order_no_agreement, adjective.position.before_noun
- retrieval_warning: none
- error_summary: none

#### Input

your desk is clean

#### Expected Output

Eta dresem se vyia.

#### Prediction

Eta yexsem se vyia.

#### Word Equivalents

- bureau → diyb, dresim, xab, yexim
- cashier desk → syagnasiut seym
- clean → vyia
- cleaned → vyixwa
- cleaning → vyixen
- desk → dresem, dreutsom, xemsem, yexsem, zyiun
- desktop → abseym
- to clean → vyixer
- to get clean → vyiser
- work desk → yexsem

#### Retrieval Context

1. [grammar_rules]
Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

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
2. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: orthography.punctuation.direct_quote_colon
Description: {'description': 'Mirad uses a colon before direct speech where English often uses a comma.', 'pseudocode': ['if clause.introduces_direct_quote:', "    place ':' after reporting clause", '    quote_content = quoted_sentence']}
Pseudocode: 
Examples:
- Mirad: It da: "Van esu man." | English: He said, "Let there be light." | Note: colon introduces the quote

Rule ID: verb.modal_y_glide_reduces_strength
Description: {'description': 'Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.', 'pseudocode': ['if modal_or_affective_verb.needs_weaker_meaning:', '    insert_y_after_stem_vowel']}
Pseudocode: 
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged
3. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: syntax.basic_svo
Description: {'description': 'Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.', 'pseudocode': ['if clause.is_basic_declarative:', '    order = [subject, verb_predicate, object_or_complement]']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
4. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.modal_y_glide_reduces_strength
Description: {'description': 'Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.', 'pseudocode': ['if modal_or_affective_verb.needs_weaker_meaning:', '    insert_y_after_stem_vowel']}
Pseudocode: 
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

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

### r30-23-csv-0683

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 23241
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:683
- retrieval_rule_ids: verb.simple.active_suffixes, verb.stative_complement_after_ser, verb.no_person_number_agreement, verb.infinitive_er_stem
- retrieval_warning: none
- error_summary: none

#### Input

I was happy

#### Expected Output

At sa iva.

#### Prediction

At sa iva.

#### Word Equivalents

- as if → gel ven, hoyen ven
- at → atulk
- at least → gwoay
- at the right → zi
- atonally → oyseuzay
- atto → goralyi-, goralyu-
- be → baelk
- beamed → naudxwa
- behest → avan
- being → sat, sea, sean, seat, sen, zapuen
- feeling happy → ivtosea, ivtosen
- happily → ivay
- happiness → ivan
- happy → fikyeoja, iva
- if → ven
- if not → ven voy
- if so → ven vay
- iffy → vena
- serape → apetsim suemoyf
- serb → Sorobamat
- sere → grayixwa, uka, uyma
- serge → nailef
- serried → nabalwa
- to be → ser
- to get happy → ivser

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

Rule ID: verb.perfect.passive_aw_plus_tense
Description: {'description': 'The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.', 'pseudocode': ['if aspect == perfect and voice == passive:', "    form = stem + 'aw' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o
2. [grammar_rules]
Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

Rule ID: verb.modal_y_glide_reduces_strength
Description: {'description': 'Adding a y-glide after the modal stem vowel weakens the force of some modal or affective verbs, such as love to like or must to should.', 'pseudocode': ['if modal_or_affective_verb.needs_weaker_meaning:', '    insert_y_after_stem_vowel']}
Pseudocode: 
Examples:
- Mirad: At ife et. | English: I love you. | Note: strong affection
- Mirad: At iyfe et. | English: I like you. | Note: y-glide weakens
- Mirad: Et yefe iper. | English: You must leave. | Note: strong obligation

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
3. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: noun.plural.common_countable
Description: {'description': 'A singular countable common noun becomes plural by suffixing -i. Only the noun is pluralized; articles and adjectives do not agree in number.', 'pseudocode': ['if noun.is_common_countable and target_number == plural:', "    noun.surface = noun.singular + 'i'", '    do_not_pluralize(article)', '    do_not_pluralize(adjectives)']}
Pseudocode: 
Examples:
- Mirad: tam → tami | English: house → houses | Note: plural suffix -i
- Mirad: ha via dom → ha via domi | English: the beautiful city → the beautiful cities | Note: only dom changes

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

### r30-24-csv-0692

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 24747
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:692
- retrieval_rule_ids: verb.simple.active_suffixes, verb.no_person_number_agreement, verb.stative_complement_after_ser, adjective.descriptive.ends_a
- retrieval_warning: none
- error_summary: none

#### Input

we will be happy

#### Expected Output

Yat so iva.

#### Prediction

Yat so iva.

#### Word Equivalents

- be → baelk
- beamed → naudxwa
- behest → avan
- being → sat, sea, sean, seat, sen, zapuen
- happily → ivay
- happiness → ivan
- happy → fikyeoja, iva
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- if → ven
- if so → ven vay
- iffiness → venan
- iffy → vena
- ivied → gravefebuwa
- not yet → voy gaj
- our → aeta, ayet, ayita, yata
- serape → apetsim suemoyf
- serb → Sorobamat
- sere → grayixwa, uka, uyma
- serge → nailef
- serried → nabalwa
- to → bu
- to and → ayxer
- to be → ser
- to could → yayfer
- to don → aber, tofaber
- to get happy → ivser
- to make happy → ivxer
- to or → eyxer
- to wee → tiyabiler
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil
- yet → gaj, gajob, gey bay hus, gey bay van, gey ov hus, ov hus, oy
- yet again → ga awa jod
- yet more → gay ga

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
2. [grammar_rules]
Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

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

Rule ID: derivation.noun.gerund_en
Description: {'description': 'The suffix -en forms present gerunds or action nouns meaning English -ing, -tion, or -ment from verb stems.', 'pseudocode': ['if verb_stem nominalized_as_action:', "    noun = verb_stem + 'en'"]}
Pseudocode: 
Examples:
- Mirad: deuzer → deuzen | English: to sing → singing | Note: verb stem + -en
- Mirad: axer → axen | English: to act → action/acting | Note: verb stem + -en
- Mirad: ifier → ifien | English: to enjoy → enjoyment | Note: verb stem + -en

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
3. [grammar_rules]
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

Rule ID: syntax.object.after_predicate
Description: {'description': 'In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.', 'pseudocode': ['predicate = finite_verb + optional_adverbs', 'if direct_object: place after predicate', 'if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object']}
Pseudocode: 
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: adjective.descriptive.ends_a
Description: {'description': 'All descriptive adjectives end in the adjectival marker -a. Adjectives can be derived from qualitative roots, nouns, passive verb stems, and prepositions.', 'pseudocode': ['if target_part_of_speech == descriptive_adjective:', "    form = stem + 'a'"]}
Pseudocode: 
Examples:
- Mirad: fia | English: good | Note: fi- + -a
- Mirad: pura | English: vehicular | Note: pur 'vehicle' + -a
- Mirad: dalwa | English: spoken | Note: passive verb stem + -a
4. [grammar_rules]
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

Rule ID: pronoun.reflexive_insert_u
Description: {'description': 'Reflexive personal pronouns are formed by placing u before the final -t. Reflexives do not mark gender.', 'pseudocode': ['if pronoun.is_animate_personal and target == reflexive:', "    insert 'u' before final 't'", '    do_not_mark_gender']}
Pseudocode: 
Examples:
- Mirad: at → aut | English: I/me → myself | Note: u before final t
- Mirad: et → eut | English: you → yourself | Note: u before final t
- Mirad: it → iut | English: he/she → himself/herself | Note: gender-neutral reflexive

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

### r30-25-csv-0718

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 26163
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:718
- retrieval_rule_ids: verb.simple.active_suffixes
- retrieval_warning: none
- error_summary: none

#### Input

did you come

#### Expected Output

Duven et upa?

#### Prediction

Duven et pua?

#### Word Equivalents

- come → upya
- come with → uper bay
- coming → upea, upen, yup
- to come → uper
- to come about → kaxwer, kyeser, vyamser
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

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion
2. [grammar_rules]
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

Rule ID: verb.perfect.passive_aw_plus_tense
Description: {'description': 'The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.', 'pseudocode': ['if aspect == perfect and voice == passive:', "    form = stem + 'aw' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o
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

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

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

### r30-26-csv-0735

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 38599
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:735
- retrieval_rule_ids: determiner.demonstrative_hia_hua, noun.modifiers.order_no_agreement, adjective.position.before_noun, verb.no_person_number_agreement, syntax.basic_svo
- retrieval_warning: none
- error_summary: none

#### Input

is that student bad

#### Expected Output

Duven hua tixut se fua?

#### Prediction

Duven hua tixut se fua?

#### Word Equivalents

- are → se
- bad → fua
- bad thing → fuas
- badly → fu, fuay
- badness → fuan
- be → baelk
- beamed → naudxwa
- behest → avan
- being → sat, sea, sean, seat, sen, zapuen
- college student → itistamut, tutaymut
- does → vay
- high school student → etistamut
- is → se
- secondary school student → etistamut
- something bad → fuas, fusun
- student → tixut
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- to → bu
- to and → ayxer
- to be → ser
- to could → yayfer
- to don → aber, tofaber
- to or → eyxer
- university student → utistamat
- whether → ven

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

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion
2. [grammar_rules]
Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion
3. [grammar_rules]
Rule ID: adjective.descriptive.ends_a
Description: {'description': 'All descriptive adjectives end in the adjectival marker -a. Adjectives can be derived from qualitative roots, nouns, passive verb stems, and prepositions.', 'pseudocode': ['if target_part_of_speech == descriptive_adjective:', "    form = stem + 'a'"]}
Pseudocode: 
Examples:
- Mirad: fia | English: good | Note: fi- + -a
- Mirad: pura | English: vehicular | Note: pur 'vehicle' + -a
- Mirad: dalwa | English: spoken | Note: passive verb stem + -a

Rule ID: determiner.deictic_begin_h
Description: {'description': 'All deictic determiners begin with h. Following letters specify category such as interrogative, indefinite, proximal, distal, universal, negative, person, thing, place, time, manner, degree, etc.', 'pseudocode': ['if word.is_deictic_determiner:', "    require word.starts_with('h')", '    parse prefix_after_h for deixis_type', '    parse suffix for semantic_category']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: proximal deictic
- Mirad: hua | English: that | Note: distal deictic
- Mirad: duhot? | English: who? | Note: interrogative animate deictic

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: determiner.demonstrative_hia_hua
Description: {'description': 'hia marks proximal reference, this; hua marks distal reference, that. As adjectives they precede the noun. As pronouns they can take -s/-t and plural -i.', 'pseudocode': ["if referent.is_near_speaker: base = 'hi'", "if referent.is_far_or_contextual: base = 'hu'", "if used_as_adjective: form = base + 'a'", "if used_as_thing_pronoun: form = base + 'as' or base + 'asi'", "if used_as_person_pronoun: form = base + 'at' or base + 'ati'"]}
Pseudocode: 
Examples:
- Mirad: hia tam | English: this house | Note: proximal adjective
- Mirad: hua tam | English: that house | Note: distal adjective
- Mirad: Hias se etas. | English: This one is yours. | Note: proximal thing pronoun

Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun
4. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

Rule ID: syntax.object.after_predicate
Description: {'description': 'In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.', 'pseudocode': ['predicate = finite_verb + optional_adverbs', 'if direct_object: place after predicate', 'if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object']}
Pseudocode: 
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: adjective.position.before_noun
Description: {'description': 'Descriptive adjectives are placed before the nouns they modify.', 'pseudocode': ['mirad_np = optional_article + adjective_list + noun']}
Pseudocode: 
Examples:
- Mirad: aga tam | English: a big house | Note: aga precedes tam
- Mirad: ha fia toyb | English: the good woman | Note: article + adjective + noun

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: adjective.descriptive.ends_a
Description: {'description': 'All descriptive adjectives end in the adjectival marker -a. Adjectives can be derived from qualitative roots, nouns, passive verb stems, and prepositions.', 'pseudocode': ['if target_part_of_speech == descriptive_adjective:', "    form = stem + 'a'"]}
Pseudocode: 
Examples:
- Mirad: fia | English: good | Note: fi- + -a
- Mirad: pura | English: vehicular | Note: pur 'vehicle' + -a
- Mirad: dalwa | English: spoken | Note: passive verb stem + -a
5. [grammar_rules]
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

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object
6. [grammar_rules]
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

Rule ID: determiner.categories
Description: {'description': 'Mirad determiners specify context and may function adjectivally, pronominally, or adverbially. Major types are deictic, pronominal/possessive, quantitative, and numerical.', 'pseudocode': ['classify determiner by semantic_function:', '    deictic | possessive | quantitative | numerical', 'classify by syntactic_function:', '    adjective | pronoun | adverb']}
Pseudocode: 
Examples:
- Mirad: hia | English: this | Note: deictic adjective/pronoun depending on use
- Mirad: ata | English: my | Note: pronominal possessive adjective
- Mirad: ga | English: more | Note: quantitative determiner

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: verb.no_person_number_agreement
Description: {'description': 'The same verb form is used for all subjects regardless of person or number. Subject pronouns carry person and number information.', 'pseudocode': ['verb_form = conjugate(stem, tense, aspect, mood, voice)', 'do_not_modify verb_form for subject.person', 'do_not_modify verb_form for subject.number']}
Pseudocode: 
Examples:
- Mirad: at se | English: I am | Note: se unchanged
- Mirad: et se | English: you are | Note: se unchanged
- Mirad: yit se | English: they are | Note: se unchanged

### r30-27-csv-0820

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 30523
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:820
- retrieval_rule_ids: verb.simple.active_suffixes, verb.infinitive_er_stem, pronoun.gender.optional_w_y, conjunction.coordinate_ay_ey_oy, verb.communication_clause_object_van, syntax.basic_svo
- retrieval_warning: none
- error_summary: none

#### Input

we do not know where he or she went, but we know where you live

#### Expected Output

Yat voy te hom it pa, oy yat te hom et tambese.

#### Prediction

Yat voy te hom it pa, oy yat te hom et besee.

#### Word Equivalents

- alive → teja, tejea
- but → boy, oy
- butch → toobyena
- butting → teyubuxen
- butyl → butyl
- certainly not → vlay voy, vlo, vloy
- go in → per yeb
- go with → per bay
- goer → put
- going → pea, pen
- he → hat, hit, hut, hwat, hwit, hwut, it, wit
- he himself → it iut, wit iut
- her → hayt, hayta, hiyt, hiyta, huyt, huyta, it, ita, iyt, iyta
- here where → him ho
- him → hat, hit, hut, hwat, hwit, hwut, it, wit
- his → hata, hatas, hatasi, hita, hitas, hitasi, huta, hutas, hwata, hwita, hwuta, ita, wita, witas, witasi
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- know that → ter van
- knowing → tea, ten
- known → trawa, twa
- let go → lobexwa, lopexwa, yivafxwa
- let not → ofu, von
- live → teja, tejya
- liveness → tejan
- living → besea, besen, embesea, embesen, tambesen, tejea, tejen
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- our → aeta, ayet, ayita, yata
- seine → pitnef
- she → hayt, hiyt, huyt, it, iyt
- she herself → it iut, iyt iut
- she who → hoyt
- shearing → goflaren, goflen
- something known → twas
- to go → per
- to know → ter
- to live → beser, embeser, tambeser, tejer, tyemer
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil
- where → hem
- where to? → bu duhom?
- where? → du ha nem?, du ham?
- whereto? → bu duhom?
- you → et, eyt
- you and i → aet
- you yourself → et eut, eyt eut
- you yourselves → yet yeut
- your → ayeta, eta, eyta, weta, yeta

#### Retrieval Context

1. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: {'description': 'Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.', 'pseudocode': ['if adjective.can_take_o_negation and not ambiguous:', "    form = 'o' + adjective", 'else if adjective.begins_with_consonant:', "    form = 'lo' + adjective", 'else:', "    form = 'ol' + adjective", 'if meaning == hostile_or_anti:', "    form = one_of(['lyo' + adjective, 'ov' + adjective])"]}
Pseudocode: 
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: adjective.opposites.vowel_switching
Description: {'description': 'Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.', 'pseudocode': ['if adjective.pattern == i_u_contrast:', "    positive = stem_with('i')", "    negative = stem_with('u')", 'if adjective.pattern == a_e_o_scale:', "    positive = stem_with('a')", "    intermediate = stem_with('e')", "    negative = stem_with('o')"]}
Pseudocode: 
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
2. [grammar_rules]
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

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er
3. [grammar_rules]
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

Rule ID: verb.perfect.passive_aw_plus_tense
Description: {'description': 'The passive perfect inserts a plus passive/buffer w before the final tense/mood vowel: -awe, -awa, -awo, -awu.', 'pseudocode': ['if aspect == perfect and voice == passive:', "    form = stem + 'aw' + final_tense_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xawe. | English: It has been done. | Note: x- + aw + e
- Mirad: Has xawa. | English: It had been done. | Note: x- + aw + a
- Mirad: Has xawo. | English: It will have been done. | Note: x- + aw + o
4. [grammar_rules]
Rule ID: conjunction.subordinate_van_that
Description: {'description': "van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.", 'pseudocode': ['if embedded_clause.is_declarative:', "    introduce_with 'van' when clarity or grammar requires"]}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

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
5. [grammar_rules]
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

Rule ID: pronoun.hybrid_aet_ayet
Description: {'description': "aet means 'you and I' dual. ayet means 'you people and I' plural. Use only when the situation explicitly combines first and second person.", 'pseudocode': ['if referent == speaker + one_addressee:', "    use 'aet'", 'if referent == speaker + multiple_addressees:', "    use 'ayet'"]}
Pseudocode: 
Examples:
- Mirad: Aet yeyfe tadser. | English: You and I should get married. | Note: aet = speaker + addressee
- Mirad: Ayet efe yanbeser. | English: You people and I need to stick together. | Note: ayet = speaker + multiple addressees

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
6. [grammar_rules]
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

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

### r30-28-csv-0827

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 44838
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:827
- retrieval_rule_ids: determiner.interrogative_duh_forms, verb.communication_clause_object_van, verb.simple.active_suffixes, verb.no_person_number_agreement, pronoun.possessive_add_a_s_si, conjunction.subordinate_van_that, syntax.basic_svo, verb.motion_communication_omit_direction_preposition
- retrieval_warning: none
- error_summary: none

#### Input

do they know where we went and where you live

#### Expected Output

Duven yit te hom yat pa ay hom et tambese?

#### Prediction

Duven yit te hom yata pen ay hom eta besen?

#### Word Equivalents

- alive → teja, tejea
- and → ay
- and/or → aey
- anded → ayxwa
- anding → ayxen
- at the place → be ham
- both...and → hyaewa...ay, vay...ay
- go in → per yeb
- goer → put
- going → pea, pen
- here where → him ho
- know that → ter van
- knowing → tea, ten
- known → trawa, twa
- let go → lobexwa, lopexwa, yivafxwa
- live → teja, tejya
- liveness → tejan
- living → besea, besen, embesea, embesen, tambesen, tejea, tejen
- our → aeta, ayet, ayita, yata
- place → -em, -om, domned, nem, unkunem, yem, zyim
- something known → twas
- the place → ham
- the places → hami
- to go → per
- to know → ter
- to live → beser, embeser, tambeser, tejer, tyemer
- to place → ber, ember, emxer, nember, yember
- to wee → tiyabiler
- we → aet, ayet, ayit, yat
- we ourselves → yat yaut
- wee → ooga, tiyabil
- where → hem
- where to? → bu duhom?
- where? → du ha nem?, du ham?
- whereto? → bu duhom?
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

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

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
2. [grammar_rules]
Rule ID: verb.communication_clause_object_van
Description: {'description': 'Verbs of knowing, saying, telling, and informing can take a whole clause as direct object. van can introduce a that-clause, and interrogative deictics can introduce embedded questions.', 'pseudocode': ["if verb.class in ['communication','cognition'] and complement.is_declarative_clause:", "    use optional_or_required_subordinator('van') + clause", 'if complement.is_embedded_question:', '    use interrogative_deictic + embedded_clause']}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Duven et te hoa tam se itas? | English: Do you know which house is his? | Note: embedded question
- Mirad: At da it hom et tambee. | English: I told him where you live. | Note: indirect object + clause object

Rule ID: conjunction.subordinate_van_that
Description: {'description': "van introduces a subordinate declarative clause corresponding to English 'that', especially after verbs of cognition, saying, or in complement clauses.", 'pseudocode': ['if embedded_clause.is_declarative:', "    introduce_with 'van' when clarity or grammar requires"]}
Pseudocode: 
Examples:
- Mirad: At ta van et upo. | English: I knew that you would come. | Note: van introduces clause object
- Mirad: Se uva van iyt pia. | English: It is sad that she left. | Note: van introduces complement clause

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: syntax.subject.noun_phrase_structure
Description: {'description': "The subject is the entity responsible for the verb's action or state. It can be a noun phrase or pronoun, with modifiers such as deictic adjectives, quantifiers, and descriptive adjectives before the head noun.", 'pseudocode': ['subject = noun_phrase | pronoun | coordinated_subject', 'noun_phrase = modifiers* + head_noun + optional_post_head_phrases']}
Pseudocode: 
Examples:
- Mirad: Hya domi ayse tebixusi. | English: All cities have things of interest. | Note: hya domi is subject noun phrase

Rule ID: syntax.basic_svo
Description: {'description': 'Mirad is normally SVO: subject + verb predicate + object, similar to English and Romance languages.', 'pseudocode': ['if clause.is_basic_declarative:', '    order = [subject, verb_predicate, object_or_complement]']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
3. [grammar_rules]
Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.motion_communication_omit_direction_preposition
Description: {'description': 'Certain verbs contain inherent directionality or positionality and can take an object without a preposition where English might use to/from/in. This includes motion, residence, origin, and communication verbs.', 'pseudocode': ['if verb.has_inherent_directionality and object.is_directional_or_locative_or_recipient:', '    omit preposition', '    place object according_to verb_complement_rules']}
Pseudocode: 
Examples:
- Mirad: At peye ha nam. | English: I am going to the store. | Note: to omitted
- Mirad: Pu tam! | English: Go home! | Note: to omitted
- Mirad: At byise Ferom. | English: I come from France. | Note: from omitted

Rule ID: verb.simple.active_suffixes
Description: {'description': 'Simple active present uses stem + -e, past stem + -a, future stem + -o, and atemporal hypothetical/imperative stem + -u.', 'pseudocode': ['if aspect == simple and voice == active:', "    if tense == present and mood == indicative: form = stem + 'e'", "    if tense == past and mood == indicative: form = stem + 'a'", "    if tense == future and mood == indicative: form = stem + 'o'", "    if mood == hypothetical or imperative: form = stem + 'u'"]}
Pseudocode: 
Examples:
- Mirad: at xe | English: I do | Note: x- + -e
- Mirad: at xa | English: I did | Note: x- + -a
- Mirad: at xo | English: I will do | Note: x- + -o

Rule ID: verb.passive.insert_w_before_tense
Description: {'description': "In finite passive forms, the passive marker w is inserted between the verb stem and the final tense/mood vowel. Passive forms translate English 'be/get + past participle' when a patient is subject.", 'pseudocode': ['if voice == passive and aspect == simple:', "    form = stem + 'w' + tense_or_mood_vowel"]}
Pseudocode: 
Examples:
- Mirad: Has xwe. | English: It is done. | Note: x- + w + e
- Mirad: Has xwa. | English: It was done. | Note: x- + w + a
- Mirad: Has xwo. | English: It will be done. | Note: x- + w + o

Rule ID: verb.simple.passive_suffixes
Description: {'description': 'Simple passive present is -we, past -wa, future -wo, and hypothetical -wu after the verb stem.', 'pseudocode': ['if aspect == simple and voice == passive:', "    form = stem + {'present':'we','past':'wa','future':'wo','hypothetical':'wu'}[tam]"]}
Pseudocode: 
Examples:
- Mirad: xwe | English: is done | Note: present passive
- Mirad: xwa | English: was done | Note: past passive
- Mirad: xwu | English: would be done | Note: hypothetical passive
4. [grammar_rules]
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

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
5. [grammar_rules]
Rule ID: pronoun.possessive_add_a_s_si
Description: {'description': 'Possessive adjectives are formed by adding -a to the pronoun. Possessive pronouns for things are formed with -as singular and -asi plural. Change s to t when the possessed referent is a person.', 'pseudocode': ["possessive_adjective = pronoun + 'a'", 'if possessed_referent == inanimate_singular:', "    possessive_pronoun = pronoun + 'as'", 'if possessed_referent == inanimate_plural:', "    possessive_pronoun = pronoun + 'asi'", 'if possessed_referent == animate:', '    replace final_s_with_t in possessive_pronoun']}
Pseudocode: 
Examples:
- Mirad: at → ata | English: I/me → my | Note: possessive adjective -a
- Mirad: atas | English: mine | Note: possessive pronoun for thing
- Mirad: Etasi naze ga vyel atasi. | English: Yours are worth more than mine. | Note: plural possessed things

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
6. [grammar_rules]
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

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: derivation.noun.tool_ar_ir_ur
Description: {'description': 'The suffixes -ar, -ir, and -ur form instruments, tools, machines, engines, or vehicles, usually from verb stems. Exact nuance depends on the lexical family.', 'pseudocode': ['if target == tool_or_instrument:', "    form = verb_stem + one_of(['ar','ir','ur']) according_to_instrument_class"]}
Pseudocode: 
Examples:
- Mirad: drer → drar | English: to write → pencil | Note: writing tool
- Mirad: gobler → goblar | English: to cut → knife | Note: cutting tool
- Mirad: per → pur | English: to go → car | Note: vehicle

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper

### r30-29-csv-0888

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 25580
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: no
- normalized_match: no
- failure_labels: random30, csv-sentence-pairs, csv_index:888
- retrieval_rule_ids: determiner.demonstrative_hia_hua, noun.modifiers.order_no_agreement, verb.no_person_number_agreement, verb.simple.active_suffixes, conjunction.coordinate_ay_ey_oy
- retrieval_warning: none
- error_summary: none

#### Input

this teacher is good enough, but that teacher is not good enough

#### Expected Output

Hia tuxut se gre fia, oy hua tuxut se gro fia.

#### Prediction

Hia tuxut se fia gre, oy hua tuxut se voy fia gre.

#### Word Equivalents

- but → boy, oy
- butch → toobyena
- butting → teyubuxen
- butyl → butyl
- certainly not → vlay voy, vlo, vloy
- educator → tuuxut, tuxtut
- enough → gre, grea, greay
- enough of it → gres
- good → fia, nuun, nyuun
- good thing → fis
- good- → fi-
- goodly → ayga
- however → gey ov hus, hyegel, hyenog, hyeyen, hyeyeni, je hus, ov hus, oy
- let not → ofu, von
- not → hyo-, voy
- not a → hyoa, hyoawa, owa
- not that → voy van
- school teacher → tistam tuxut
- schoolteacher → tistamtuxut
- since this → ji his
- something good → fis, fisun
- student teacher → tiea tuxut
- sufficient → grea, gresea, grexea
- sufficiently → gre, greay, greseay, grexeay
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
- to be enough → greser

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural

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
2. [grammar_rules]
Rule ID: adjective.negation_o_lo_ol
Description: {'description': 'Descriptive adjectives can be negated by prefixing o-. If this creates ambiguity or the adjective already begins with o, lo- or ol- may be used. Stronger polar opposition can use lyo- or ov-.', 'pseudocode': ['if adjective.can_take_o_negation and not ambiguous:', "    form = 'o' + adjective", 'else if adjective.begins_with_consonant:', "    form = 'lo' + adjective", 'else:', "    form = 'ol' + adjective", 'if meaning == hostile_or_anti:', "    form = one_of(['lyo' + adjective, 'ov' + adjective])"]}
Pseudocode: 
Examples:
- Mirad: twa → otwa | English: known → unknown | Note: o- negation
- Mirad: fwa → lofwa | English: wanted → unwanted | Note: lo- avoids ambiguity
- Mirad: data → ovdata | English: friendly → hostile | Note: strong polar opposition

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

Rule ID: adjective.opposites.vowel_switching
Description: {'description': 'Many base adjectives form semantic contrasts by switching the stem vowel. In i/u pairs, i is positive and u negative. In a/e/o scales, a is positive, e intermediate, and o negative.', 'pseudocode': ['if adjective.pattern == i_u_contrast:', "    positive = stem_with('i')", "    negative = stem_with('u')", 'if adjective.pattern == a_e_o_scale:', "    positive = stem_with('a')", "    intermediate = stem_with('e')", "    negative = stem_with('o')"]}
Pseudocode: 
Examples:
- Mirad: fia / fua | English: good / bad | Note: i/u contrast
- Mirad: iva / uva | English: happy / sad | Note: i/u contrast
- Mirad: aga / ega / oga | English: big / normal / little | Note: a/e/o scalar set

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
3. [grammar_rules]
Rule ID: noun.modifiers.order_no_agreement
Description: {'description': 'Qualitative, quantitative, deictic, and pronominal adjectives precede the noun. There is no gender or number agreement between modifiers and noun.', 'pseudocode': ['mirad_np = optional_article + determiners + quantitative_modifiers + descriptive_adjectives + noun', 'do_not_inflect_modifiers_for_gender_number_case']}
Pseudocode: 
Examples:
- Mirad: ha ewa aga tami | English: the two big houses | Note: modifiers precede noun; only tami is plural
- Mirad: ata aja teji | English: my past lives | Note: possessive and adjective precede noun

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

Rule ID: verb.infinitive_er_stem
Description: {'description': 'Verbs are listed under the present active infinitive ending in -er. The stem is the infinitive minus -er. All conjugation uses this stem. Passive infinitives ending in -wer may be lexicalized, but the stem is still the infinitive minus -er.', 'pseudocode': ["if verb.infinitive.ends_with('er'):", "    stem = remove_suffix(verb.infinitive, 'er')", 'else:', '    lookup irregular_or_nonstandard_entry']}
Pseudocode: 
Examples:
- Mirad: yexer → yex- | English: to work → work stem | Note: remove -er
- Mirad: poser → pos- | English: to stop → stop stem | Note: remove -er
- Mirad: xwer → xw- | English: to happen/be done → passive stem | Note: remove -er

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can
4. [grammar_rules]
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

Rule ID: verb.stative_complement_after_ser
Description: {'description': "Stative intransitive verbs such as ser 'to be' may be followed by complements: noun, pronoun, adjective, infinitive, gerund, or clause.", 'pseudocode': ['if verb == ser or verb.is_stative_intransitive:', '    complement = noun_or_pronoun_or_adjective_or_infinitive_or_gerund_or_clause', '    clause = subject + verb + complement']}
Pseudocode: 
Examples:
- Mirad: His se fis. | English: This is a good thing. | Note: noun/pronoun complement
- Mirad: His se gla fia. | English: This is very good. | Note: adjective complement
- Mirad: Se fia aker. | English: It is good to win. | Note: infinitive complement

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
5. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: noun.linkage.prepositional_and_compound
Description: {'description': 'Noun relationships may be expressed with prepositions/conjunctions after the head noun, by modifier noun before the head noun, by compounding, or by hyphenating equal/opposed elements.', 'pseudocode': ['if relation.is_associative_or_possessive:', '    use head + preposition/conjunction + complement', 'if modifier_noun.functions_attributively:', '    use modifier_noun + head_noun or compound(modifier, head)', 'if two_elements_are_equal_or_opposed:', '    hyphenate(element1, element2)']}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: conjunction linkage
- Mirad: tej bi nasuk | English: a life of poverty | Note: preposition linkage
- Mirad: dom yuzpur | English: city bus | Note: juxtaposed modifier noun

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

### r30-30-csv-0968

- direction: English → Mirad
- status: ok
- phase: complete
- model: deepseek-ai/DeepSeek-V4-Flash
- elapsed_ms: 34330
- estimated_calls: 1
- estimated_cost_usd: $0.000000
- exact_match: yes
- normalized_match: yes
- failure_labels: random30, csv-sentence-pairs, csv_index:968
- retrieval_rule_ids: verb.simple.active_suffixes, verb.conditional_imperative_u_subject, determiner.deictic_begin_h, determiner.demonstrative_hia_hua, syntax.object.after_predicate, verb.ditransitive.indirect_before_direct, pronoun.personal.invariant_case, conjunction.coordinate_ay_ey_oy
- retrieval_warning: none
- error_summary: none

#### Input

take this telegram and give me that box

#### Expected Output

Biu hia yibdren ay buu at hua nyem.

#### Prediction

Biu hia yibdren ay buu at hua nyem.

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
- since this → ji his
- take → iper belea
- taken → belwa, embiwa, ibexwa
- taking → ibexen, izaypien
- tele- → yib-
- telegram → nyifdras, yibdriras, yibdrirun
- telegraphic → yibdrira
- telegraphically → yibdriray
- that → ho, hua, hunog, van
- that is → be hyua duni
- that kind of → hugela, husauna, huyena
- that one → huawa, huawas
- that which → hos
- this → hi-, hia, hinog
- this kind → hisaun
- this kind of → higela, hisauna, hiyena
- this one → hias, hiat, hiawa, hiawas
- to box → pyexler, tuyeboveker, tuyebyexer
- to give → ayxer, buer, yugsaser
- to gyve → tyoyuvarer
- to take → baysiper, beler, bier, direr, efxer, ibexer, izaypier, pler
- to take in → teaxier, yebier
- to telegram → nyifdrer

#### Retrieval Context

1. [grammar_rules]
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

Rule ID: verb.conditional_imperative_u_subject
Description: {'description': 'A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.', 'pseudocode': ["if finite_verb.ends_with('u'):", '    if clause.has_explicit_subject:', '        interpret_as conditional_hypothetical', '    else:', '        interpret_as imperative']}
Pseudocode: 
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: verb.modal_hypothetical_mitigates
Description: {'description': 'When a modal auxiliary is in the hypothetical -u form, its meaning is softened, similar to English would like, could, ought to.', 'pseudocode': ["if modal_verb.ending == 'u':", '    translate_with_softened_modal_equivalent']}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: direct desire
- Mirad: At fu per. | English: I would like to go. | Note: softened desire
- Mirad: Et yafe aker. | English: You can win. | Note: can

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted
2. [grammar_rules]
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

Rule ID: pronoun.english_it.translation_rules
Description: {'description': "If English 'it' refers to an animate creature, use it/iyt/wit. If it refers to an inanimate object or abstraction, use is or a deictic determiner. If it is a dummy/expletive subject with no antecedent, omit it in Mirad.", 'pseudocode': ['if english_it.has_antecedent:', "    if antecedent.is_animate: use gender_resolved one_of('it','iyt','wit')", "    else: use 'is' or deictic_determiner", 'else if english_it.is_dummy_subject:', '    omit pronoun']}
Pseudocode: 
Examples:
- Mirad: At eke bay ha epet hosav at iyfe it. | English: I play with the dog because I like it. | Note: dog is animate, so it
- Mirad: At teasa ha dyezun ay at iyfa is gla. | English: I saw the movie and I liked it a lot. | Note: movie is inanimate, so is
- Mirad: Mamilo. | English: It will rain. | Note: dummy it omitted

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only
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

Rule ID: pronoun.emphatic.personal_plus_reflexive
Description: {'description': 'Emphatic personal pronouns are formed by following a personal pronoun with the corresponding reflexive pronoun.', 'pseudocode': ['if pronoun.is_emphatic:', "    form = personal_pronoun + ' ' + corresponding_reflexive"]}
Pseudocode: 
Examples:
- Mirad: at aut | English: I myself / me myself | Note: personal + reflexive
- Mirad: yet yeut | English: you yourselves | Note: plural emphatic
- Mirad: iyt iut | English: she herself | Note: gender in personal pronoun only

Rule ID: derivation.noun.tool_ar_ir_ur
Description: {'description': 'The suffixes -ar, -ir, and -ur form instruments, tools, machines, engines, or vehicles, usually from verb stems. Exact nuance depends on the lexical family.', 'pseudocode': ['if target == tool_or_instrument:', "    form = verb_stem + one_of(['ar','ir','ur']) according_to_instrument_class"]}
Pseudocode: 
Examples:
- Mirad: drer → drar | English: to write → pencil | Note: writing tool
- Mirad: gobler → goblar | English: to cut → knife | Note: cutting tool
- Mirad: per → pur | English: to go → car | Note: vehicle

Rule ID: verb.modal_auxiliary_before_infinitive
Description: {'description': 'Modal verbs such as wanting, needing, being able, being obliged, liking, and fearing are conjugated as auxiliaries and followed by an infinitive verb in -er.', 'pseudocode': ['modal = conjugate(modal_stem, tense_aspect_mood_voice)', 'main_verb = infinitive_er_form', "clause_predicate = modal + ' ' + main_verb"]}
Pseudocode: 
Examples:
- Mirad: At fe per. | English: I want to go. | Note: fe + infinitive per
- Mirad: Et yafe aker. | English: You can win. | Note: yafe + infinitive aker
- Mirad: Yet yefe iper. | English: You must leave. | Note: yefe + infinitive iper
4. [grammar_rules]
Rule ID: syntax.object.after_predicate
Description: {'description': 'In ordinary clauses, direct objects and complements follow the finite verb predicate. Indirect objects may precede direct objects with verbs that imply direction.', 'pseudocode': ['predicate = finite_verb + optional_adverbs', 'if direct_object: place after predicate', 'if indirect_object and direct_object and verb.implies_direction: place indirect_object before direct_object']}
Pseudocode: 
Examples:
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: object follows verb
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object before direct object

Rule ID: verb.ditransitive.indirect_before_direct
Description: {'description': 'Many common transitive verbs imply a directional preposition. When both indirect and direct objects are present, the indirect object comes before the direct object without an explicit preposition. A prepositional paraphrase can also be used.', 'pseudocode': ['if verb.implies_direction and has_indirect_object and has_direct_object:', '    order = verb + indirect_object + direct_object', 'else if preposition_needed:', '    order = verb + direct_object + preposition + indirect_object']}
Pseudocode: 
Examples:
- Mirad: Buu at hua nyem. | English: Give me that box. | Note: indirect object at before direct object hua nyem
- Mirad: Du it doler. | English: Tell him to be quiet. | Note: it is indirect object
- Mirad: Nusbiu at dyes. | English: Buy me a book. | Note: indirect before direct

Rule ID: verb.transitive.direct_object_after_verb
Description: {'description': 'A transitive verb can be followed by its direct object. In basic declaratives this follows SVO order.', 'pseudocode': ['if verb.is_transitive:', '    clause = subject + verb + direct_object']}
Pseudocode: 
Examples:
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: subject + verb + object
- Mirad: Biu hia yibdren. | English: Take this telegram. | Note: imperative verb + direct object

Rule ID: pronoun.personal.invariant_case
Description: {'description': 'Mirad personal pronouns have the same form whether subject, direct object, indirect object, or object of a preposition. Syntax and prepositions determine function.', 'pseudocode': ['pronoun_form = lookup_person_number_animacy_gender()', 'do_not_inflect_for_case', 'determine_case_from_position_or_preposition']}
Pseudocode: 
Examples:
- Mirad: At xe. | English: I do. | Note: at as subject
- Mirad: Ha yepet teupixa at. | English: The dog bit me. | Note: at as object
- Mirad: His se av et. | English: This is for you. | Note: et after preposition

Rule ID: determiner.animate_t_thing_s_plural_i
Description: {'description': 'Deictic pronouns ending in -t refer to persons and those ending in -s refer to things. Plural is formed with -i: duhot? who, duhoti? which persons; duhos? what, duhosi? what things.', 'pseudocode': ['if referent.is_person:', "    category_final = 't'", 'else:', "    category_final = 's'", 'if number == plural:', "    add 'i'"]}
Pseudocode: 
Examples:
- Mirad: duhot? / duhoti? | English: who? / which persons? | Note: animate singular/plural
- Mirad: duhos? / duhosi? | English: what? / what things? | Note: inanimate singular/plural
- Mirad: hias / hiasi | English: this one / these ones | Note: inanimate deictic pronoun plus plural
5. [grammar_rules]
Rule ID: conjunction.coordinate_ay_ey_oy
Description: {'description': "ay links elements as 'and'; ey links alternatives as 'or'; oy can express exclusion/contrast such as 'but' or in neither/nor patterns, depending on construction.", 'pseudocode': ["if relation == conjunction: use 'ay'", "if relation == alternative: use 'ey'", "if relation == contrast_or_negative_alternative: use 'oy'"]}
Pseudocode: 
Examples:
- Mirad: Ivan ay Maria | English: Ivan and Maria | Note: ay = and
- Mirad: ha tam ey ha par | English: the house or the car | Note: ey = or
- Mirad: hyati oy ha toybi | English: all but the women | Note: oy expresses exclusion

Rule ID: verb.conditional_imperative_u_subject
Description: {'description': 'A verb ending in -u is atemporal hypothetical. With an overt subject in a main clause it usually means would. Without a subject it is normally interpreted as an imperative command.', 'pseudocode': ["if finite_verb.ends_with('u'):", '    if clause.has_explicit_subject:', '        interpret_as conditional_hypothetical', '    else:', '        interpret_as imperative']}
Pseudocode: 
Examples:
- Mirad: Hus su fia. | English: That would be good. | Note: subject present; conditional
- Mirad: Su baka! | English: Be well! | Note: no subject; command
- Mirad: Xu has hij! | English: Do it now! | Note: imperative

Rule ID: determiner.either_neither_both_patterns
Description: {'description': 'Either A or B is Hyeawa A ey B. Neither A nor B is Hyeowa A oy B. Both A and B is Hyaewa A ay B. Only A, not B is Hawa A, voy B.', 'pseudocode': ["if construction == either_or: use 'Hyeawa' + A + 'ey' + B", "if construction == neither_nor: use 'Hyeowa' + A + 'oy' + B", "if construction == both_and: use 'Hyaewa' + A + 'ay' + B", "if construction == only_not: use 'Hawa' + A + ', voy' + B"]}
Pseudocode: 
Examples:
- Mirad: Hyeawa A ey B | English: either A or B | Note: either-or pattern
- Mirad: Hyeowa A oy B | English: neither A nor B | Note: neither-nor pattern
- Mirad: Hyaewa A ay B | English: both A and B | Note: both-and pattern

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
