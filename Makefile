.PHONY: *
.DEFAULT_GOAL := default

VERSION := $(shell uv run python -c "from cliff import __version__; print(__version__)")

default: lint type test

init:
	uv sync

test:
	uv run pytest -v --cov=cliff --cov-report=term-missing --failed-first --durations=0

tox:
	uv run tox -p auto

clear-deps:
	@uv pip uninstall cliff > /dev/null 2>&1
	@uv pip freeze | xargs uv pip uninstall > /dev/null

coverage:
	uv run pytest --cov=cliff --cov-report=html
	open htmlcov/index.html

lint:
	-uv run ruff check .

type:
	-uv run ty check .

build:
	uv build

update-build: build
	uv pip uninstall cliff-cli
	uv pip install .

clean:
	@rm -rf build \
		dist \
		*.egg-info \
		.pytest_cache \
		.mypy_cache \
		htmlcov \
		.coverage \
		*.lcov
	@find . -type d -name __pycache__ -exec rm -r {} +

publish: clean build
	uv run twine upload dist/*

update-docs:
	uv run scripts/update_docs.py
	./scripts/update_badges.sh
