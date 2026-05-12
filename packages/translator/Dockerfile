# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install system deps for healthcheck
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy translator package source
COPY packages/translator/pyproject.toml packages/translator/README.md ./
COPY packages/translator/src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

# Default: run API server
CMD ["python", "-m", "uvicorn", "mirad_translator.api:app", "--host", "0.0.0.0", "--port", "8000"]