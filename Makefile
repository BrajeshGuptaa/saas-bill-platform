PYTHON=python3
POETRY=$(PYTHON) -m poetry

.PHONY: install dev worker test lint typecheck fmt

install:
	$(POETRY) install

dev:
	$(POETRY) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	$(POETRY) run rq worker --url $${BILLING_REDIS_URL:-redis://localhost:6379/0} billing

test:
	$(POETRY) run pytest

lint:
	$(POETRY) run ruff check .

fmt:
	$(POETRY) run ruff format .

typecheck:
	$(POETRY) run mypy app
