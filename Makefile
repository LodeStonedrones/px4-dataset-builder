.PHONY: install format lint typecheck test package check

install:
	python -m pip install -e '.[dev]'

format:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

typecheck:
	mypy src

test:
	pytest

package:
	python -m build

check: lint typecheck test package
