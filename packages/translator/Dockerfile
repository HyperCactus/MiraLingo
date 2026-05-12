# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install system deps for healthcheck + ChromaDB build requirements
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy translator package source
COPY packages/translator/pyproject.toml packages/translator/README.md ./
COPY packages/translator/src/ src/

# Install with all optional deps (rag + eval + develop)
RUN pip install --no-cache-dir ".[rag,eval,develop]"

# Copy project data (lexicon, grammar, thesaurus)
COPY data/ /app/data/

EXPOSE 8000

# Default: run API server
CMD ["python", "-m", "uvicorn", "mirad_translator.api:app", "--host", "0.0.0.0", "--port", "8000"]