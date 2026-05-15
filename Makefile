.PHONY: dev test compile build ci

PYTHONPYCACHEPREFIX ?= /tmp/create-dlthub-pyc
PACKAGE_MODULES := $(wildcard src/create_dlthub_workspace/*.py)

dev:
	uv sync --extra dev

test:
	uv run python -m unittest discover -s tests

compile:
	PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) uv run python -m compileall $(PACKAGE_MODULES) tests

build:
	uv build

ci: compile test build
