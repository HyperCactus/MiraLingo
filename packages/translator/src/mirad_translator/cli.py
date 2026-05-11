import sys
import argparse
import logging

from mirad_translator.translate import TranslatorModule
from mirad_translator.ollama_lm import OllamaLM
import dspy

def main():
    parser = argparse.ArgumentParser(description="Translate English to Mirad")
    parser.add_argument('text', nargs='?', help='Text to translate')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
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
        
        # Initialize translator
        translator = TranslatorModule()
        
        # Translate
        prediction = translator.forward(english_text=args.text)
        # Format confidence — may be str or float
        try:
            conf_val = float(prediction.confidence)
            conf_str = f"{conf_val:.2f}"
        except (ValueError, TypeError):
            conf_str = str(prediction.confidence)
        print(f"{prediction.mirad_text} [{conf_str}]")
        
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
