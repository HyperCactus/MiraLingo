#!/usr/bin/env python3
"""Create train/val/test splits from english-mirad-sentence-pairs.csv.

Outputs three JSON files in data/eval/:
  - train.json    (70%)
  - val.json      (15%)
  - test.json     (15%)

Each file contains a list of objects:
  { "id": "pair-0001", "source": "...", "target": "..." }

The source/target fields are named generically so either direction can be loaded
by the eval script and renamed to english/mirad or mirad/english as needed.
"""
import csv, json, random
from pathlib import Path

_ROOT   = Path(__file__).resolve().parents[1]
SRC     = _ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
OUT_DIR = _ROOT / "data" / "eval"

SPLITS    = {"train": 330, "val": 330, "test": 330}  # equal-size splits; 330×3=990
RANDOM_SEED = 20260526

def load_pairs(csv_path: Path) -> list[dict]:
    """Load all rows from the CSV. Returns list of {english, mirad} dicts."""
    pairs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            en = row.get("english", "").strip()
            mi = row.get("mirad", "").strip()
            if en and mi:
                pairs.append({"id": f"pair-{i:04d}", "english": en, "mirad": mi})
    return pairs

def split_pairs(pairs: list[dict], sizes: dict, seed: int):
    """Shuffle and split pairs into equal-size buckets."""
    random.seed(seed)
    shuffled = pairs.copy()
    random.shuffle(shuffled)
    n_train = sizes["train"]
    n_val   = sizes["val"]
    return {
        "train": shuffled[:n_train],
        "val":   shuffled[n_train:n_train + n_val],
        "test":  shuffled[n_train + n_val:],
    }

def save_split(data: list[dict], out_path: Path):
    # Bidirectional format: english/mirad fields so either direction works directly
    pairs = [{"id": d["id"], "english": d["english"], "mirad": d["mirad"]} for d in data]
    meta = {
        "description": "Mirad translation pairs.",
        "total": len(pairs),
        "format": "bidirectional: english + mirad fields (no source/target)",
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"metadata": meta, "pairs": pairs}, f, ensure_ascii=False, indent=2)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Loading pairs from {SRC} ...")
    pairs = load_pairs(SRC)
    print(f"  Loaded {len(pairs)} pairs")

    splits = split_pairs(pairs, SPLITS, RANDOM_SEED)
    for name, data in splits.items():
        out_path = OUT_DIR / f"{name}.json"
        save_split(data, out_path)
        print(f"  {name:5s}: {len(data):4d} pairs  →  {out_path.relative_to(_ROOT)}")

    print("\nAll splits saved.")

if __name__ == "__main__":
    main()