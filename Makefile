.PHONY: dev test compile build ci workspace

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

TEST_WORKSPACE_NAME ?= my-workspace

workspace:
	@case "$(TEST_WORKSPACE_NAME)" in */*|*..*|"") echo "invalid TEST_WORKSPACE_NAME: $(TEST_WORKSPACE_NAME)"; exit 1;; esac
	@echo "Recreating examples/$(TEST_WORKSPACE_NAME)"
	rm -rf -- "examples/$(TEST_WORKSPACE_NAME)"
	uv run create-dlthub-workspace "examples/$(TEST_WORKSPACE_NAME)"

ci: compile test build
