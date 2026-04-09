#!/bin/bash
# Coffee-startup dev server launcher
# Kills anything on port 8000, then starts the FastAPI server with hot-reload.

echo "→ Killing any process on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  killed." || echo "  nothing was running."

echo "→ Starting FastAPI dev server..."
cd "$(dirname "$0")"
PYTHONPATH=. RELOAD=true .venv/bin/python product/web-app/server.py
