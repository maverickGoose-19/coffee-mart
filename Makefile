.PHONY: install dev run prod test lint clean migrate docker-build docker-run

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
PIP    ?= $(VENV)/bin/pip

# ── Setup ──────────────────────────────────────────────────────────────────

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# ── Local dev server (hot-reload on code changes) ─────────────────────────

dev:
	RELOAD=true $(PYTHON) product/web-app/server.py

# ── Production-style local server ─────────────────────────────────────────

run:
	$(PYTHON) product/web-app/server.py

prod:
	HOST=0.0.0.0 WEB_CONCURRENCY=2 $(PYTHON) product/web-app/server.py

migrate:
	$(PYTHON) migrate.py

# ── Docker ────────────────────────────────────────────────────────────────

docker-build:
	docker build -t coffee-platform .

docker-run:
	docker run --env-file product/backend/supabase/.env \
	  -e HOST=0.0.0.0 -p 8000:8000 coffee-platform

# ── Tests ─────────────────────────────────────────────────────────────────

test:
	$(PYTHON) -m pytest tests/ -v

# ── Linting ───────────────────────────────────────────────────────────────

lint:
	$(PYTHON) -m ruff check . || true
	$(PYTHON) -m mypy product/backend/app --ignore-missing-imports || true

# ── Cleanup ───────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
