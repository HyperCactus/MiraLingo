# mirad_translator package

__version__ = "0.2.0"

from mirad_translator.translate import (
    EnglishToMiradSignature,
    MiradToEnglishSignature,
    CritiqueSignature,
    FixTranslationSignature,
    FollowUpQuerySignature,
    TranslatorModule,
    MiradToEnglishModule,
    MiradLexiconLookup,
    MiradLexiconReverseLookup,
    MiradSemanticReverseLexiconLookup,
    MiradContextRetrieve,
    MultiHopTranslatorModule,
    CritiqueAndFixModule,
    DefaultTranslator,
    translate_with_lookup,
    load_compiled_translator,
)

from mirad_translator.semantic_lexicon import (
    semantic_lookup,
    semantic_lookup_multi,
    MiradSemanticLexiconLookup,
)

from mirad_translator.evaluate import (
    load_evaluation_set,
    load_reverse_evaluation_set,
    exact_match_metric,
    normalized_match_metric,
    exact_match_reverse_metric,
    normalized_match_reverse_metric,
    evaluate_module,
    compile_with_bootstrap,
    run_baseline_eval,
    run_labeled_fewshot_eval,
    run_mir_to_en_baseline_eval,
)

from mirad_translator.eval_semantic_lexicon import (
    run_semantic_eval,
)