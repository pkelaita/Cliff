.PHONY: *
.DEFAULT_GOAL := default

VERSION := $(shell python -c "from cliff import __version__; print(__version__)")

default: lint type test

init:
	uv pip install --upgrade pip
	uv pip install -r requirements.txt
	uv pip install -r requirements-dev.txt

test:
	pytest -v --cov=cliff --cov-report=term-missing --failed-first --durations=0

tox:
	tox -p auto

clear-deps:
	uv pip uninstall -y cliff > /dev/null 2>&1
	uv pip freeze | xargs uv pip uninstall -y > /dev/null

coverage:
	pytest --cov=cliff --cov-report=html
	open htmlcov/index.html

lint:
	-ruff check .

type:
	-mypy .

build:
	python -m build

update-build: build
	uv pip uninstall -y cliff-cli
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
	twine upload dist/*