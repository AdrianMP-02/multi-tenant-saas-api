.PHONY: help install dev install-dev lint format typecheck test test-cov migrate makemigrations shell db-start db-stop db-reset

help:
	@echo "Usage:"
	@echo "  make install         Install production dependencies"
	@echo "  make dev             Install dev dependencies"
	@echo "  make lint            Run ruff linter"
	@echo "  make format          Run ruff formatter"
	@echo "  make typecheck       Run mypy type checking"
	@echo "  make test            Run tests"
	@echo "  make test-cov        Run tests with coverage"
	@echo "  make migrate         Apply alembic migrations"
	@echo "  make makemigrations  Create new migration"
	@echo "  make shell           Open Python shell"
	@echo "  make db-start        Start Docker services"
	@echo "  make db-stop         Stop Docker services"
	@echo "  make db-reset        Reset database"

install:
	pip install -e .

dev: install
	pip install -e ".[dev]"

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/

typecheck:
	mypy app/ tests/

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=term --cov-report=html

migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "$(message)"

shell:
	python -m asyncio

db-start:
	docker compose up -d db redis

db-stop:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d db redis
	sleep 3
	alembic upgrade head
