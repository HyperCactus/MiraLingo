# Data Directory Structure

This directory contains reference data used by the Mirad phonemes engine.

## Subdirectories

### `mirad-docs/`
TTS reference documents for the Mirad language:
- `mirad_grammer.md` — Mirad grammar specification
- `mirad_thesaurus.md` — Mirad thesaurus and word forms
- `mirad_lexicon.md` — Mirad lexicon and vocabulary

Used by the TTS synthesis pipeline for reference pronunciation and grammar rules.

### `phrases/`
Sentence corpus for phrase-level processing and testing:
- `english_sentences.csv` — English sentence corpus
- `english-mirad-sentence-pairs.csv` — Paired English-Mirad sentences for translation testing

### `pdfs/`
PDF reference documents (currently empty placeholder).

## Root Files
- `pronunciation_tests.csv` — Test fixtures for pronunciation validation