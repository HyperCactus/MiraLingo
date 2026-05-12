import sys
import argparse
import logging

from mirad_translator.translate import DefaultTranslator
from mirad_translator.ollama_lm import OllamaLM
import dspy


def main():
    parser = argparse.ArgumentParser(description="Translate between English and Mirad")
    parser.add_argument('text', nargs='?', help='Text to translate')
    parser.add_argument('--reverse', '-R', action='store_true',
                        help='Reverse direction: Mirad→English (default is English→Mirad)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--retrieve', '-r', action='store_true',
                        help='Show retrieved word equivalents and context')

    # Parse only known args to handle the module execution
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
        # Initialize Ollama LM
        lm = OllamaLM()
        dspy.configure(lm=lm)

        # Select direction
        direction = "mir_to_en" if args.reverse else "en_to_mir"
        translator = DefaultTranslator(direction=direction)

        # Translate
        if args.reverse:
            prediction = translator(mirad_text=args.text)
            output_text = prediction.english_text
        else:
            prediction = translator(english_text=args.text)
            output_text = prediction.mirad_text

        if args.retrieve:
            # Show retrieval details
            word_eq = getattr(prediction, 'word_equivalents', {}) or {}
            context = getattr(prediction, 'context', []) or []

            print("--- Word equivalents ---")
            if word_eq:
                for src, tgt in sorted(word_eq.items()):
                    print(f"  {src} → {tgt}")
            else:
                print("  (no matches)")

            print("--- Context ---")
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