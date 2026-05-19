# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Interactive project name prompt with default `my-workspace`, plus tests.

### Changed
- Centralized user-facing strings into `strings.py`; refreshed onboarding and next-steps copy.
- Onboarding guidance now always recommends `dlthub-start@latest`.
- Bumped `WORKBENCH_REF` to `42ddb99` and refreshed the bundled AI workbench scaffold.

### Removed
- Stripped `uv.lock` from the bundled scaffold.

### Fixed
- MCP dependency error in scaffolds.

## [0.2.0] - 2026-05-19

### Added
- Beta classifier on the package.
- MCP dependencies.
- AI integration via `generate-ai` / `check-ai` subcommands (replacing direct `ai` invocation), `--overwrite` flag, and default agents set to "all".
- Unit, integration, and cross-platform e2e tests; CI updated for cross-platform runs; `.codexignore` files.
- File-tree printing with a sync test.
- Company LICENSE.
- `lint` / `format` Make targets and dependencies.
- Prompts to install `uv` and run `uv sync`.
- Scaffolds: `starterpack`, `minimal_workspace`, plus `.gitignore` for `starter-workspace`.
- Selection output, recommendations, and explicit `.venv` mention in toolkit display.
- Make target for test-workspace handling.

### Changed
- **Package renamed** `create-dlthub-workspace` → `dlthub-start` (CLI entrypoint and `pyproject.toml`).
- Default destination for `start_workspace` switched from MotherDuck to DuckDB; stray scaffold removed.
- CLI usage renamed `dlt` → `dlthub`.
- Bumped `dlt[hub]` version in scaffolds.
- Workbench pinned to a specific commit; Windows encoding issue fixed.
- Next-steps copy aligned with scaffolds; `cd` moved to step 1.
- Source switched from `github_api` to a public no-auth API; API limit handling adjusted.
- Plan and execute phases split.
- Stdout/stderr from subprocesses suppressed.
- License pointer updated.
- Lint/format conformed to runtime repo.
- Notebook refactored and moved to `notebooks/` dir; `starter_report` removed.
- `make compile` no longer recurses into bundled scaffolds / generated `.venv`.

### Fixed
- Windows test string issue.
- `dlthub toolkit install` CLI command order.

## [0.1.0] - 2026-05-13

### Added
- Initial scaffold of the `create-dlthub-workspace` CLI.
- Makefile and GitHub Actions setup.
- Recursive `.dlt` files.
