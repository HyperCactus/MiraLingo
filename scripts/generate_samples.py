#!/usr/bin/env python3
"""Generate Mirad TTS audio samples.

Usage:
    python generate_samples.py word1 word2 word3 ...

This generates .wav files in the samples/ directory for each word.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mirad_tts.cli import run


def generate_sample(word: str, output_dir: Path) -> Path:
    """Generate a single audio sample for a word."""
    output_path = output_dir / f"{word}.wav"

    # Set up environment for espeak-ng
    project_root = Path(__file__).resolve().parents[1]
    os.environ["ESPEAK_DATA_PATH"] = str(project_root / ".gsd" / "share" / "espeak-ng-data")
    os.environ["PATH"] = str(project_root / ".gsd" / "bin") + os.pathsep + os.environ.get("PATH", "")

    # Build argv for the CLI
    argv = ["--wav", str(output_path), word]

    # Run the CLI
    selected, debug_lines, wav_path, voice = run(argv)

    if wav_path and Path(wav_path).exists():
        print(f"✓ Generated: {output_path.name} ({Path(wav_path).stat().st_size // 1024} KB)")
        return output_path
    else:
        print(f"✗ Failed: {word}")
        return None


def main():
    """Generate samples for all words provided as arguments."""
    project_root = Path(__file__).resolve().parents[1]
    samples_dir = project_root / "samples"
    samples_dir.mkdir(exist_ok=True)

    if len(sys.argv) < 2:
        print("Usage: python generate_samples.py word1 word2 ...")
        print("\nExample words from grammar:")
        words = [
            "Mirad", "igay", "tejna", "vay", "aymsea", "booka",
            "byoskyin", "auwa", "tixe", "jal", "ya", "wa",
            "yay", "way", "qatar", "ama", "oyse", "akea", "alayn"
        ]
        print(f"  python generate_samples.py {' '.join(words)}")
        sys.exit(1)

    words = sys.argv[1:]
    print(f"Generating {len(words)} sample(s)...\n")

    success_count = 0
    for word in words:
        if generate_sample(word, samples_dir):
            success_count += 1

    print(f"\nGenerated {success_count}/{len(words)} samples in {samples_dir}/")


if __name__ == "__main__":
    main()
