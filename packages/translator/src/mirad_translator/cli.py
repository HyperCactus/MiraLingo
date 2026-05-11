"""
CLI for mirad-translate.
"""

import sys
import argparse

from mirad_translator.translate import TranslateEnToMirad


def main():
    parser = argparse.ArgumentParser(description="Translate English to Mirad")
    parser.add_argument('text', nargs='?', help='Text to translate')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if not args.text:
        print("Error: Please provide text to translate")
        sys.exit(1)
        
    translator = TranslateEnToMirad()
    result = translator.translate(args.text)
    print(result)

if __name__ == "__main__":
    main()
