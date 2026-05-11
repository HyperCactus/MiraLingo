#!/usr/bin/env python3
"""Generate Mirad TTS audio samples.

Usage:
    python generate_samples.py [--backend espeak|piper|mbrola] [word1 word2 ...]

Examples:
    python generate_samples.py Mirad igay cema
    python generate_samples.py --backend piper Mirad cema
    python generate_samples.py --backend mbrola Mirad
    python generate_samples.py --backend mbrola --mbrola-debug "Ha Mirad."
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mirad_tts.cli import run as cli_run
from mirad_tts.piper_backend import diagnose_text, synthesize_to_wav as piper_synthesize_to_wav
from mirad_tts.mbrola_backend import (
    MbrolaError,
    MbrolaNotFoundError,
    MbrolaVoiceNotFoundError,
    MbrolaSynthesisError,
    diagnose_mbrola,
    generate_pho,
    pho_to_string,
    synthesize_to_wav as mbrola_synthesize_to_wav,
    write_pho,
)

DEFAULT_WORDS = [
    "Mirad", "igay", "tejna", "vay", "aymsea", "booka",
    "byoskyin", "auwa", "tixe", "jal", "ya", "wa",
    "yay", "way", "qatar", "ama", "oyse", "akea", "alayn",
    "cema",
]

# Short sentences/phrases for more comprehensive testing
DEFAULT_SENTENCES = [
    "Ha Mirad.",
    "At tixe.",
    "Igay sa mirad.",
    "Ya, van yoy sa.",
    "Tejna mirad ay ha.",
]


def generate_mbrola_sample(
    text: str,
    output_path: Path,
    mbrola_db: Path | None = None,
) -> Path | None:
    """Generate a single MBROLA audio sample."""
    try:
        wav_path = mbrola_synthesize_to_wav(
            text,
            str(output_path),
            mbrola_db=mbrola_db,
        )
        size_kb = wav_path.stat().st_size // 1024
        print(f"  ✓ {output_path.name}: {size_kb} KB")
        return wav_path
    except (MbrolaNotFoundError, MbrolaVoiceNotFoundError) as exc:
        print(f"  ✗ {text}: {exc}")
        print("     Install with: sudo apt install mbrola mbrola-de6")
        return None
    except (MbrolaError, MbrolaSynthesisError) as exc:
        print(f"  ✗ {text}: {exc}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Mirad TTS audio samples")
    parser.add_argument("words", nargs="*", help="Words or phrases to generate")
    parser.add_argument("--backend", choices=["espeak", "piper", "mbrola"], default="piper",
                       help="TTS backend (default: piper)")
    parser.add_argument("--voice", type=str, default=None,
                       help="Path to Piper voice .onnx model or MBROLA voice name")
    parser.add_argument("--mbrola-db", type=str, default=None,
                       help="Override path to MBROLA de6 voice database")
    parser.add_argument("--piper-debug", action="store_true",
                       help="Print per-word Piper diagnostics")
    parser.add_argument("--mbrola-debug", action="store_true",
                       help="Print per-word MBROLA diagnostics")
    parser.add_argument("--length-scale", type=float, default=None,
                       help="Piper length_scale (< 1 faster, > 1 slower)")
    parser.add_argument("--noise-scale", type=float, default=None,
                       help="Piper noise_scale")
    parser.add_argument("--noise-w-scale", type=float, default=None,
                       help="Piper noise_w_scale")
    parser.add_argument("--speed", type=int, default=None,
                       help="eSpeak speed in WPM (default: 120 for natural Mirad)")
    parser.add_argument("--pitch", type=int, default=None,
                       help="eSpeak pitch 0-99 (default: 40)")
    parser.add_argument("--word-gap", type=int, default=None,
                       help="eSpeak word gap in 10ms units (default: 4)")
    parser.add_argument("--amplitude", type=int, default=None,
                       help="eSpeak amplitude 0-200 (default: 90)")
    parser.add_argument("--final-pause", action="store_true",
                       help="Keep trailing sentence pause (default: removed)")
    args = parser.parse_args()

    # Set up environment for espeak-ng
    # project_root = top-level project dir (where samples/ lives)
    project_root = Path(__file__).resolve().parents[3]
    if args.backend == "espeak":
        os.environ["ESPEAK_DATA_PATH"] = str(project_root / ".gsd" / "share" / "espeak-ng-data")
        os.environ["PATH"] = str(project_root / ".gsd" / "bin") + os.pathsep + os.environ.get("PATH", "")

    # Use default words + sentences for mbrola, just words for other backends
    if args.words:
        items = args.words
    elif args.backend == "mbrola":
        items = DEFAULT_WORDS + DEFAULT_SENTENCES
    else:
        items = DEFAULT_WORDS

    samples_dir = project_root / "samples" / args.backend
    samples_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(items)} sample(s) with {args.backend} backend...\n")

    # --- MBROLA debug ---
    if args.mbrola_debug and args.backend == "mbrola":
        print("=" * 70)
        print("MBROLA Phone Diagnostics")
        print("=" * 70)
        for item in items:
            diags = diagnose_mbrola(item)
            for diag in diags:
                phones_str = " ".join(diag["phones"])
                print(f"WORD: {diag['word']}")
                print(f"  SYLLABLES:      {'.'.join(diag['syllables']) if diag['syllables'] else '<none>'}")
                print(f"  MBROLA PHONES:  {phones_str}")
                print(f"  ERROR:          {diag['error'] or 'none'}")
                print()
        print("=" * 70)
        print()

    # --- Piper debug ---
    if args.piper_debug and args.backend == "piper":
        print("=" * 70)
        print("Piper Phoneme Diagnostics")
        print("=" * 70)
        for item in items:
            diags = diagnose_text(item)
            for diag in diags:
                sym_str = " ".join(diag.piper_symbols)
                print(f"WORD: {diag.word}")
                print(f"  IPA:            {diag.ipa}")
                print(f"  PIPER SYMBOLS:  {sym_str}")
                print(f"  PIPER IDS:      {diag.piper_ids}")
                print(f"  MISSING:        {sorted(set(diag.missing_symbols)) if diag.missing_symbols else 'none'}")
                print()
        print("=" * 70)
        print()

    success_count = 0

    if args.backend == "piper":
        from mirad_tts.piper_backend import synthesize_to_wav as piper_synth
        for item in items:
            # Use safe filename (replace spaces and dots)
            safe_name = item.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("!", "").replace("?", "")
            output_path = samples_dir / f"{safe_name}.wav"
            try:
                wav_path = piper_synth(
                    item,
                    str(output_path),
                    model_path=Path(args.voice) if args.voice else None,
                    length_scale=args.length_scale,
                    noise_scale=args.noise_scale,
                    noise_w_scale=args.noise_w_scale,
                )
                if wav_path and wav_path.exists():
                    size_kb = wav_path.stat().st_size // 1024
                    print(f"  ✓ {safe_name}: {size_kb} KB")
                    success_count += 1
                else:
                    print(f"  ✗ {item}: no output")
            except Exception as exc:
                print(f"  ✗ {item}: {exc}")

    elif args.backend == "mbrola":
        mbrola_db = Path(args.mbrola_db) if args.mbrola_db else None
        for item in items:
            safe_name = item.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("!", "").replace("?", "")
            output_path = samples_dir / f"{safe_name}.wav"
            result = generate_mbrola_sample(item, output_path, mbrola_db)
            if result:
                success_count += 1

    else:  # espeak
        from mirad_tts.espeak_backend import synthesize_to_wav as espeak_synth
        for item in items:
            safe_name = item.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("!", "").replace("?", "")
            output_path = samples_dir / f"{safe_name}.wav"
            voice_name = args.voice if args.voice else None
            try:
                wav_path = espeak_synth(
                    item,
                    str(output_path),
                    voice=voice_name,
                    speed=args.speed if args.speed is not None else 120,
                    pitch=args.pitch if args.pitch is not None else 40,
                    word_gap=args.word_gap if args.word_gap is not None else 4,
                    amplitude=args.amplitude if args.amplitude is not None else 90,
                    no_final_pause=not args.final_pause,
                )
                if wav_path and wav_path.exists():
                    size_kb = wav_path.stat().st_size // 1024
                    print(f"  ✓ {safe_name}: {size_kb} KB")
                    success_count += 1
                else:
                    print(f"  ✗ {item}: no output")
            except Exception as exc:
                print(f"  ✗ {item}: {exc}")

    print(f"\nGenerated {success_count}/{len(items)} samples in {samples_dir}/")


if __name__ == "__main__":
    main()