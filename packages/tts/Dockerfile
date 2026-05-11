# syntax=docker/dockerfile:1
# Stage 1: Assemble pre-built wheel (built on host with pip access)
FROM python:3.10-slim AS builder

WORKDIR /build
COPY packages/tts/mirad-tts-0.1.0-py3-none-any.whl .

# Stage 2: Minimal runtime image with espeak-ng
FROM python:3.10-slim

# Use a fast, geographically-distributed Debian mirror
RUN sed -i 's/deb.debian.org/ftp.us.debian.org/g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true \
 && echo 'Acquire::Retries 3;' > /etc/apt/apt.conf.d/80docker \
 && apt-get update \
 && apt-get install -y --no-install-recommends espeak-ng \
 && rm -rf /var/lib/apt/lists/* \
 && rm /etc/apt/apt.conf.d/80docker

# Install wheel from builder stage
COPY --from=builder /build/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# PYTHONPATH allows "python -m mirad_tts" from any directory;
# mirad-tts entry-point script uses sys.executable so works regardless.
ENV PYTHONPATH=/app/src
WORKDIR /app

# Default: show CLI help
CMD ["mirad-tts", "--help"]