#!/usr/bin/env python3
"""Compare eSpeak and Piper TTS backends for Mirad text-to-speech.

This script generates audio samples using both backends and provides
information about file sizes and quality differences.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def generate_sample(word: str, backend: str, output_dir: Path) -> tuple[Path, int]:
    """Generate a single audio sample for a word using the specified backend.

    Args:
        word: The Mirad word to synthesize.
        backend: The TTS backend to use ('espeak' or 'piper').
        output_dir: Directory to save the output file.

    Returns:
        Tuple of (output_path, file_size_in_kb).
    """
    output_path = output_dir / f"{word}.wav"

    # Build command
    cmd = [
        "python3", "-m", "mirad_tts.cli",
        "--backend", backend,
        "--wav", str(output_path),
        word
    ]

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    if backend == "espeak":
        env["ESPEAK_DATA_PATH"] = str(Path(__file__).resolve().parents[1] / ".gsd" / "share" / "espeak-ng-data")
        env["PATH"] = str(Path(__file__).resolve().parents[1] / ".gsd" / "bin") + os.pathsep + env.get("PATH", "")

    # Run the command
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ {backend:8s} {word:12s} -> error: {result.stderr.strip()}")
        return None, 0

    # Get file size
    if output_path.exists():
        size_kb = output_path.stat().st_size // 1024
        print(f"✓ {backend:8s} {word:12s} -> {size_kb:3d} KB")
        return output_path, size_kb
    else:
        print(f"✗ {backend:8s} {word:12s} -> failed (no file)")
        return None, 0


def compare_backends(words: list[str]) -> None:
    """Generate samples with both backends and compare results.

    Args:
        words: List of Mirad words to synthesize.
    """
    project_root = Path(__file__).resolve().parents[1]
    espeak_dir = project_root / "samples" / "espeak"
    piper_dir = project_root / "samples" / "piper"

    espeak_dir.mkdir(parents=True, exist_ok=True)
    piper_dir.mkdir(parents=True, exist_ok=True)

    print(f"Comparing backends for {len(words)} word(s)...\n")

    # Generate samples with both backends
    espeak_results = {}
    piper_results = {}

    for word in words:
        # Generate with eSpeak
        _, espeak_size = generate_sample(word, "espeak", espeak_dir)
        espeak_results[word] = espeak_size

        # Generate with Piper
        _, piper_size = generate_sample(word, "piper", piper_dir)
        piper_results[word] = piper_size

    # Print comparison table
    print("\n" + "=" * 50)
    print("COMPARISON TABLE")
    print("=" * 50)
    print(f"{'Word':<12} {'eSpeak':<10} {'Piper':<10} {'Difference':<12}")
    print("-" * 50)

    total_espeak = 0
    total_piper = 0

    for word in words:
        espeak_size = espeak_results.get(word, 0)
        piper_size = piper_results.get(word, 0)
        diff = piper_size - espeak_size
        diff_str = f"{diff:+d} KB" if diff != 0 else "0 KB"

        print(f"{word:<12} {espeak_size:<10} {piper_size:<10} {diff_str:<12}")

        total_espeak += espeak_size
        total_piper += piper_size

    print("-" * 50)
    print(f"{'Total':<12} {total_espeak:<10} {total_piper:<10} {total_piper - total_espeak:+d} KB")
    print("=" * 50)

    # Print summary
    print("\nSUMMARY")
    print("=" * 50)
    print(f"Total samples: {len(words)}")
    print(f"eSpeak total: {total_espeak} KB")
    print(f"Piper total: {total_piper} KB")
    print(f"Average eSpeak: {total_espeak // len(words)} KB")
    print(f"Average Piper: {total_piper // len(words)} KB")

    if total_piper < total_espeak:
        print(f"\nPiper produces {total_espeak - total_piper} KB ({100 * (total_espeak - total_piper) / total_espeak:.1f}%) smaller files on average")
    elif total_piper > total_espeak:
        print(f"\neSpeak produces {total_piper - total_espeak} KB ({100 * (total_piper - total_espeak) / total_piper:.1f}%) smaller files on average")
    else:
        print("\nBoth backends produce similar file sizes")

    print("\nSamples saved to:")
    print(f"  eSpeak: {espeak_dir}/")
    print(f"  Piper:  {piper_dir}/")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python compare_backends.py word1 word2 ...")
        print("\nExample words from grammar:")
        words = [
            "Mirad", "igay", "tejna", "vay", "aymsea", "booka",
            "byoskyin", "auwa", "tixe", "jal", "ya", "wa",
            "yay", "way", "qatar", "ama", "oyse", "akea", "alayn"
        ]
        print(f"  python compare_backends.py {' '.join(words)}")
        sys.exit(1)

    words = sys.argv[1:]
    compare_backends(words)


if __name__ == "__main__":
    main()
