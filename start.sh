#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV="$SCRIPT_DIR/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
INSTALL_DEPS="${INSTALL_DEPS:-false}"

# Ensure venv exists
if [ ! -f "$PYTHON" ]; then
  echo "→ Creating virtual environment..."
  python3 -m venv "$VENV"
  INSTALL_DEPS="true"
fi

if [ "$INSTALL_DEPS" = "true" ]; then
  echo "→ Installing / updating dependencies..."
  "$PIP" install --upgrade pip -q
  "$PIP" install -r requirements.txt -q
fi

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "→ Running database migrations..."
  "$PYTHON" migrate.py
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"

echo "→ Starting server at http://$HOST:$PORT"
exec "$PYTHON" product/web-app/server.py
