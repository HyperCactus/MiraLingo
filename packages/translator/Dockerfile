# syntax=docker/dockerfile:1
# Stage 1: Assemble pre-built wheel (built on host with pip access)
FROM python:3.10-slim AS builder

WORKDIR /build
COPY packages/translator/mirad_translator-0.1.0-py3-none-any.whl .

# Stage 2: Minimal runtime image with uvicorn + fastapi + dspy + ollama
FROM python:3.10-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Install wheel from builder stage
COPY --from=builder /build/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Install runtime dependencies (not declared in wheel — pyproject.toml has no runtime deps yet)
RUN pip install --no-cache-dir uvicorn fastapi "dspy-ai>=2.1" ollama

WORKDIR /app

# Default: run API server
CMD ["python", "-m", "uvicorn", "mirad_translator.api:app", "--host", "0.0.0.0", "--port", "8000"]