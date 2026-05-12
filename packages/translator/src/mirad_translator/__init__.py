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
    MiradContextRetrieve,
    MultiHopTranslatorModule,
    CritiqueAndFixModule,
    DefaultTranslator,
    translate_with_lookup,
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