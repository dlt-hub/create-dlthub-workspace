.PHONY: dev test compile build ci

PYTHONPYCACHEPREFIX ?= /tmp/create-dlthub-pyc

dev:
	uv sync --extra dev

test:
	uv run python -m unittest discover -s tests

compile:
	PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) uv run python -m compileall src tests

build:
	uv build

ci: compile test build

