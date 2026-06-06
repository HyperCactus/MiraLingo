# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MIRALINGO_DATABASE_PATH=/app/.miralingo/miralingo.sqlite3 \
    MIRALINGO_PHRASE_CSV_PATH=/app/data/phrases/english-mirad-sentence-pairs.csv \
    MIRALINGO_BEGINNER_JSON_PATH=/app/data/miralingo_modules/beginner.json \
    MIRALINGO_NUMBERS_JSON_PATH=/app/data/miralingo_modules/numbers.json

RUN sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/g' /etc/apt/sources.list.d/debian.sources \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl build-essential espeak-ng mbrola mbrola-de6 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY packages/tts/ packages/tts/
COPY packages/translator/ packages/translator/
COPY packages/webapp/ packages/webapp/
COPY data/ data/

RUN pip install --upgrade pip \
 && pip install --index-url https://download.pytorch.org/whl/cpu torch \
 && pip install -e packages/tts -e "packages/translator[rag]" -e packages/webapp

RUN mkdir -p /app/.miralingo

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
  CMD curl -fsS http://localhost:8000/health >/dev/null || exit 1

CMD ["python", "-m", "uvicorn", "mirad_webapp.api:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "packages/webapp/src"]
