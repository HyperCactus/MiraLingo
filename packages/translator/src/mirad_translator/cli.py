import sys
import argparse
import logging
import os
from pathlib import Path

import dspy
from dotenv import load_dotenv

from mirad_translator.translate import DefaultTranslator

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TRANSLATION_MODEL = "deepseek-ai/DeepSeek-V4-Flash"


def _configure_deepinfra_lm(model: str | None = None) -> str:
    """Configure DSPy for the default DeepInfra-backed translator."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPINFRA_API_KEY is not set")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    selected_model = model or os.environ.get("DEEPINFRA_TRANSLATION_MODEL") or os.environ.get(
        "DEEPINFRA_TEACHER_MODEL",
        DEFAULT_TRANSLATION_MODEL,
    )
    dspy.settings.configure(
        lm=dspy.LM(
            model=f"openai/{selected_model}",
            api_key=api_key,
            api_base=api_base,
        )
    )
    return selected_model


def _clean_token(value: str) -> str:
    return value.strip().strip('.,!?;:"\'-()[]{}').lower()


def _ordered_exact_vocab(text: str, *, reverse: bool) -> list[tuple[str, str]]:
    from mirad_translator.lexicon_db import lookup_mirad_word_candidates, lookup_word_candidates

    rows = []
    seen = set()
    for raw in text.split():
        token = _clean_token(raw)
        if not token or token in seen:
            continue
        seen.add(token)
        if reverse:
            targets = lookup_mirad_word_candidates(mirad_word=token)
        else:
            targets = lookup_word_candidates(english_word=token)
        if targets:
            rows.append((token, ", ".join(targets)))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Translate between English and Mirad")
    parser.add_argument('text', nargs='?', help='Text to translate')
    parser.add_argument('--reverse', '-R', action='store_true',
                        help='Reverse direction: Mirad→English (default is English→Mirad)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--retrieve', '-r', action='store_true',
                        help='Show retrieved word equivalents and structured grammar rules')
    parser.add_argument('--vocab-only', action='store_true',
                        help='Return exact-match vocabulary translations only, preserving input word order')
    parser.add_argument('--model', default=None,
                        help='DeepInfra model name (default: DEEPINFRA_TRANSLATION_MODEL or deepseek-ai/DeepSeek-V4-Flash)')

    args = parser.parse_known_args(sys.argv[1:])[0]

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.text:
        direction = "Mirad→English" if args.reverse else "English→Mirad"
        print(f"Error: Please provide text to translate ({direction})")
        sys.exit(1)

    try:
        if args.vocab_only:
            rows = _ordered_exact_vocab(args.text, reverse=args.reverse)
            for src, tgt in rows:
                print(f"{src} → {tgt}")
            return

        _configure_deepinfra_lm(args.model)

        direction = "mir_to_en" if args.reverse else "en_to_mir"
        translator = DefaultTranslator(direction=direction)

        if args.reverse:
            prediction = translator(mirad_text=args.text)
            output_text = prediction.english_text
        else:
            prediction = translator(english_text=args.text)
            output_text = prediction.mirad_text

        if args.retrieve:
            word_eq = getattr(prediction, 'word_equivalents', {}) or {}
            context = getattr(prediction, 'context', []) or []

            print("--- Word equivalents ---")
            if word_eq:
                for src, tgt in sorted(word_eq.items()):
                    print(f"  {src} → {tgt}")
            else:
                print("  (no matches)")

            print("--- Structured grammar rules ---")
            if context:
                for chunk in context:
                    print(f"  {chunk[:120]}...")
            else:
                print("  (no context retrieved)")

            print("--- Translation ---")
        print(output_text)

    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
