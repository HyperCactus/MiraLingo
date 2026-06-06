# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install speech synthesis runtimes.
RUN sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/g' /etc/apt/sources.list.d/debian.sources \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends espeak-ng mbrola mbrola-de6 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy TTS package source and install with dependencies
COPY packages/tts/pyproject.toml packages/tts/README.md ./
COPY packages/tts/src/ src/

RUN pip install --no-cache-dir .

WORKDIR /app

# Default: show CLI help
CMD ["mirad-tts", "--help"]