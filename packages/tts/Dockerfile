# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install espeak-ng for TTS synthesis
RUN apt-get update \
 && apt-get install -y --no-install-recommends espeak-ng \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy TTS package source and install with dependencies
COPY packages/tts/pyproject.toml packages/tts/README.md ./
COPY packages/tts/src/ src/

RUN pip install --no-cache-dir .

WORKDIR /app

# Default: show CLI help
CMD ["mirad-tts", "--help"]