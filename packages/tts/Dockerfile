# syntax=docker/dockerfile:1
# Stage 1: Assemble pre-built wheel (built on host with pip access)
FROM python:3.10-slim AS builder

WORKDIR /build
COPY packages/tts/mirad-tts-0.1.0-py3-none-any.whl .

# Stage 2: Minimal runtime image with espeak-ng
# Use archive.debian.org + security.debian.org (stable archive)
FROM python:3.10-slim

RUN echo 'Acquire::Retries 3;' > /etc/apt/apt.conf.d/80docker \
 && echo 'deb http://archive.debian.org/debian bullseye main' > /etc/apt/sources.list \
 && echo 'deb http://archive.debian.org/debian-security bullseye/updates main' >> /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends espeak-ng \
 && rm -rf /var/lib/apt/lists/* \
 && rm /etc/apt/apt.conf.d/80docker

# Install wheel from builder stage
COPY --from=builder /build/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

WORKDIR /app

# Default: show CLI help
CMD ["mirad-tts", "--help"]