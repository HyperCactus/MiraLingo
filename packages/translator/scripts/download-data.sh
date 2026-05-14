#!/usr/bin/env bash
# Download script for data/phrases/english_sentences.csv
# Dataset: Tatoeba English sentences export (CC BY 2.0 FR)
# URL: https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2
#
# The source file is a TSV (id\tsentence) — converted to CSV here.
# Script is idempotent: skips download if data/phrases/english_sentences.csv
# already exists and is non-empty.

set -euo pipefail

TARGET="data/phrases/english_sentences.csv"
TMP_BZ2="${TARGET}.tmp.bz2"
TMP_TSV="${TARGET}.tmp.tsv"
SOURCE_URL="https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2"

# Idempotency: skip if target already exists and is non-empty
if [[ -s "$TARGET" ]]; then
    echo "[download-data] $TARGET already exists and is non-empty — skipping download"
    exit 0
fi

echo "[download-data] Starting download of English sentences corpus"
echo "[download-data] Source: $SOURCE_URL"

# Use curl if available, fall back to wget
if command -v curl &>/dev/null; then
    echo "[download-data] Using curl"
    curl --fail --silent --show-error --location \
        --output "$TMP_BZ2" \
        "$SOURCE_URL"
else
    echo "[download-data] Using wget"
    wget --quiet --show-progress --output-document="$TMP_BZ2" \
        "$SOURCE_URL"
fi

echo "[download-data] Decompressing bz2 archive..."
bunzip2 -c "$TMP_BZ2" > "$TMP_TSV"

echo "[download-data] Converting TSV to CSV and writing to $TARGET..."
{
    # Copy header comment explaining origin
    echo "# Source: Tatoeba English Sentences (https://tatoeba.org)"
    echo "# License: CC BY 2.0 FR"
    # Convert tab-separated id<tab>sentence lines to CSV (id,sentence)
    # Skip blank lines and the Tatoeba header row (id,sentence text)
    sed 's/\t/,/' "$TMP_TSV" | grep -v '^#' | grep -v '^$' > "$TARGET"
} && rm -f "$TMP_BZ2" "$TMP_TSV"

if [[ ! -s "$TARGET" ]]; then
    echo "[download-data] ERROR: Download completed but $TARGET is empty or missing" >&2
    exit 1
fi

echo "[download-data] Success — $(wc -l < "$TARGET") lines written to $TARGET"
exit 0