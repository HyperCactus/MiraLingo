#!/bin/bash
# Verify Ollama service is accessible in the compose network.
#
# Expected network paths:
#   - From other compose services: http://ollama:11434
#   - From the host:               http://localhost:11434
#
# In a standard environment, both return JSON with a "version" key.
# The container-sandboxed build environment cannot run real containers,
# so we verify the contract here and document how to validate in production.

set -e

OLLAMA_HOST="${OLLAMA_HOST:-localhost}"
PORT=11434
URL="http://${OLLAMA_HOST}:${PORT}/api/version"

echo "Checking Ollama at ${URL} ..."

response=$(curl -s --max-time 10 "${URL}")
exit_code=$?

if [ $exit_code -eq 0 ]; then
    if echo "${response}" | grep -q '"version"'; then
        echo "Ollama responded with version info."
        echo "${response}"
        exit 0
    else
        echo "Ollama responded but no 'version' key found in response:"
        echo "${response}"
        exit 1
    fi
else
    echo "Ollama did not respond (exit ${exit_code})."
    echo "In a live compose environment, ensure containers are running with:"
    echo "  docker compose up -d"
    echo "then retry this script."
    echo ""
    echo "To validate from inside the compose network instead of the host:"
    echo "  docker compose run --rm tts curl http://ollama:11434/api/version"
    exit 1
fi