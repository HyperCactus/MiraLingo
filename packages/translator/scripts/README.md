# Scripts

Helper scripts for the Mirad phonemes engine.

## download-data.sh

Downloads the English sentence corpus into `data/phrases/english_sentences.csv`.

**Source:** [Tatoeba](https://tatoeba.org) English sentences export (CC BY 2.0 FR)
**URL:** `https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2`

### Usage

```bash
bash scripts/download-data.sh
```

### Behavior

- **Idempotent:** safe to run multiple times — skips download if
  `data/phrases/english_sentences.csv` already exists and is non-empty.
- Downloads the bz2-compressed TSV export from Tatoeba.
- Decompresses and converts TSV → CSV (id,sentence format).
- Prints status messages to stdout.
- Exits 0 on success, non-zero on failure.

### Why Tatoeba?

The corpus contains tens of thousands of diverse, open-license English
sentences with stable numeric IDs. Useful for phrase-level TTS testing
and IPA generation benchmarks.

### Re-downloading

To re-download even when the file exists, delete it first:

```bash
rm data/phrases/english_sentences.csv
bash scripts/download-data.sh
```