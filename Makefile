check: lint check-types

check-types: pyright mypy

format:
	isort .
	black .

format-check: format check-types

init: install-app-dev install-hooks

install-app-dev:
	pip install -e ".[dev]"

install-hooks:
	cp hooks/* .git/hooks
	chmod +x .git/hooks/*

lint:
	isort --check-only .
	black --check .

mypy:
	mypy src
	mypy tests

pyright:
	pyright src
	pyright tests

test:
	pytest

test-coverage:
	pytest --cov=reporting
