#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
HOST="${HOST:-127.0.0.1}"

PYTHONPATH_VALUE="packages/webapp/src:packages/translator/src:packages/tts/src:src"

cleanup() {
  local code=$?
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
  exit $code
}
trap cleanup EXIT INT TERM

if [[ ! -d "packages/webapp/frontend/node_modules" ]]; then
  echo "Installing frontend deps..."
  npm --prefix packages/webapp/frontend install
fi

echo "Starting backend on http://${HOST}:${BACKEND_PORT}"
PYTHONPATH="$PYTHONPATH_VALUE" \
MIRALINGO_ENV="${MIRALINGO_ENV:-development}" \
MIRALINGO_ENABLE_LOCAL_ADMIN="${MIRALINGO_ENABLE_LOCAL_ADMIN:-true}" \
python -m uvicorn mirad_webapp.api:app \
  --host "$HOST" \
  --port "$BACKEND_PORT" \
  --app-dir packages/webapp/src \
  > /tmp/miralingo-backend.log 2>&1 &
BACKEND_PID=$!

sleep 1
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "Backend failed to start. Log: /tmp/miralingo-backend.log"
  tail -n 80 /tmp/miralingo-backend.log || true
  exit 1
fi

echo "Starting frontend on http://${HOST}:${FRONTEND_PORT}"
npm --prefix packages/webapp/frontend run dev -- --host "$HOST" --port "$FRONTEND_PORT" &
FRONTEND_PID=$!

echo
echo "MiraLingo running:"
echo "  Frontend: http://${HOST}:${FRONTEND_PORT}/#dashboard"
echo "  Backend : http://${HOST}:${BACKEND_PORT}/health"
echo "  Backend log: /tmp/miralingo-backend.log"
echo "Press Ctrl+C to stop both services."
echo

wait "$FRONTEND_PID"
