import sys
import argparse
import logging

from mirad_translator.translate import DefaultTranslator
from mirad_translator.ollama_lm import OllamaLM
import dspy


def main():
    parser = argparse.ArgumentParser(description="Translate English to Mirad")
    parser.add_argument('text', nargs='?', help='Text to translate')
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
        print("Error: Please provide text to translate")
        sys.exit(1)

    try:
        # Initialize Ollama LM
        lm = OllamaLM()
        dspy.configure(lm=lm)

        # Initialize translator with retrieval built in
        translator = DefaultTranslator()

        # Translate
        prediction = translator.forward(english_text=args.text)
        # Format confidence — may be str or float
        try:
            conf_val = float(prediction.confidence)
            conf_str = f"{conf_val:.2f}"
        except (ValueError, TypeError):
            conf_str = str(prediction.confidence)

        if args.retrieve:
            # Show retrieval details
            word_eq = getattr(prediction, 'word_equivalents', {}) or {}
            context = getattr(prediction, 'context', []) or []

            print("--- Word equivalents ---")
            if word_eq:
                for en, mi in sorted(word_eq.items()):
                    print(f"  {en} → {mi}")
            else:
                print("  (no matches)")

            print("--- Context ---")
            if context:
                for chunk in context:
                    print(f"  {chunk[:120]}...")
            else:
                print("  (no context retrieved)")

            print("--- Mirad ---")
        print(f"{prediction.mirad_text} [{conf_str}]")

    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()