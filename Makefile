.PHONY: check fix format format-check lint lint-check init install-app-dev install-hooks precommit test test-coverage type-check

check: format-check lint-check type-check

fix: format lint

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

init: install-app-dev install-hooks

install-app-dev:
	uv sync --locked --all-groups

install-hooks:
	cp .githooks/* .git/hooks
	chmod +x .git/hooks/*

lint:
	uv run ruff check --fix .

lint-check:
	uv run ruff check .

precommit: format-check lint-check

test:
	pytest

test-coverage:
	pytest --cov=reporting

type-check:
	uv run pyright
	uv run mypy
