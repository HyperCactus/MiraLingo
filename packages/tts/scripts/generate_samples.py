#!/usr/bin/env python3
"""Generate Mirad TTS audio samples.

Usage:
    python generate_samples.py [--backend espeak|piper] [--voice PATH] [--piper-debug] word1 word2 ...

Examples:
    python generate_samples.py Mirad igay cema
    python generate_samples.py --backend piper Mirad cema
    python generate_samples.py --backend piper --piper-debug cema
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mirad_tts.cli import run
from mirad_tts.piper_backend import diagnose_text, synthesize_to_wav as piper_synthesize_to_wav


def generate_piper_sample(
    word: str,
    output_dir: Path,
    voice_path: Path | None = None,
    length_scale: float | None = None,
    noise_scale: float | None = None,
    noise_w_scale: float | None = None,
) -> Path | None:
    """Generate a single Piper audio sample for a word."""
    output_path = output_dir / f"{word.lower()}.wav"
    try:
        wav_path = piper_synthesize_to_wav(
            word,
            str(output_path),
            model_path=voice_path,
            length_scale=length_scale,
            noise_scale=noise_scale,
            noise_w_scale=noise_w_scale,
        )
        size_kb = wav_path.stat().st_size // 1024
        print(f"  ✓ {word.lower()}: {size_kb} KB")
        return wav_path
    except Exception as exc:
        print(f"  ✗ {word}: {exc}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Mirad TTS audio samples")
    parser.add_argument("words", nargs="*", help="Words to generate")
    parser.add_argument("--backend", choices=["espeak", "piper"], default="piper",
                       help="TTS backend (default: piper)")
    parser.add_argument("--voice", type=str, default=None,
                       help="Path to Piper voice .onnx model")
    parser.add_argument("--piper-debug", action="store_true",
                       help="Print per-word Piper diagnostics")
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
    project_root = Path(__file__).resolve().parents[1]
    os.environ["ESPEAK_DATA_PATH"] = str(project_root / ".gsd" / "share" / "espeak-ng-data")
    os.environ["PATH"] = str(project_root / ".gsd" / "bin") + os.pathsep + os.environ.get("PATH", "")

    default_words = [
        "Mirad", "igay", "tejna", "vay", "aymsea", "booka",
        "byoskyin", "auwa", "tixe", "jal", "ya", "wa",
        "yay", "way", "qatar", "ama", "oyse", "akea", "alayn",
        "cema",
    ]

    words = args.words if args.words else default_words

    samples_dir = project_root / "samples"
    if args.backend == "piper":
        samples_dir = samples_dir / "piper"
    else:
        samples_dir = samples_dir / "espeak"
    samples_dir.mkdir(parents=True, exist_ok=True)

    voice_path = Path(args.voice) if args.voice else None

    print(f"Generating {len(words)} sample(s) with {args.backend} backend...\n")

    if args.piper_debug and args.backend == "piper":
        print("=" * 70)
        print("Piper Phoneme Diagnostics")
        print("=" * 70)
        for word in words:
            diags = diagnose_text(word, model_path=voice_path)
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
        for word in words:
            result = generate_piper_sample(
                word, samples_dir, voice_path,
                length_scale=args.length_scale,
                noise_scale=args.noise_scale,
                noise_w_scale=args.noise_w_scale,
            )
            if result:
                success_count += 1
    else:
        for word in words:
            output_path = samples_dir / f"{word.lower()}.wav"
            voice_name = args.voice if args.voice else None
            try:
                from mirad_tts.espeak_backend import synthesize_to_wav as espeak_synth
                wav_path = espeak_synth(
                    word,
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
                    print(f"  ✓ {word.lower()}: {size_kb} KB")
                    success_count += 1
                else:
                    print(f"  ✗ {word}: no output")
            except Exception as exc:
                print(f"  ✗ {word}: {exc}")

    print(f"\nGenerated {success_count}/{len(words)} samples in {samples_dir}/")

    # Write diagnostic log for piper
    if args.backend == "piper":
        log_path = samples_dir / "phoneme_logs.txt"
        print(f"Diagnostic log: {log_path}")


if __name__ == "__main__":
    main()
