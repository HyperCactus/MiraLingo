# Mirad Translator

Bidirectional translation between Mirad and natural languages.

## What This Package Does

Provides translation services between Mirad and other languages (English, etc.) using local LLM inference via Ollama.

**Status:** Not yet implemented. This package is in the planning stage.

## Roadmap

- [ ] Ollama integration for local LLM inference
- [ ] English → Mirad translation
- [ ] Mirad → English translation
- [ ] API endpoints for translation services

## Installation

Once implemented, install with:

```bash
pip install -e packages/translator/
```

## Docker

The `ollama` service is defined in `docker-compose.yml`:

```bash
docker compose up -d ollama
```

See root [README.md](../../README.md) for full service configuration.

## Status

Planned — see root [README.md](../../README.md) for roadmap.